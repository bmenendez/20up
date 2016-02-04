#! /usr/bin/python
# -*- coding: utf-8 -*-

"""
Copyright (C) 2016 Borja Menendez Moreno

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

Authors: Borja Menéndez Moreno <info20up@gmail.com>

This is the API Wrapper for the 20up backup program. This wrapper allows
a client to retrieve information about his specific account.
"""

import os, urllib, string
from time import sleep
from tntapi import *

CONSTANT_FILL = 6
ROOTPATH = os.getcwdu()
PHOTOS = 'fotos'
JPG = '.jpg'
TXT = '.txt'

def getFullName(picture, counter):
    return normalize(string.zfill(counter, CONSTANT_FILL) + '_' + picture[2] + '_' + picture[1])

class Wrapper():
    """
    The wrapper for the tntapi.
    This class eases the connection.

    When constructed, it raises a RuntimeError if it is impossible to log in the
    social network.
    """
    def __init__(self, browser, console=False):
        self.tnt = API(browser)
        self.isLogged = False
        self.console = console
            
    def downloadPicturesFromAlbum(self, album, totalPictures, alreadyDownloaded, comments=False):
        """
        Download pictures from a given album into the given directory.

        Args:
            album: the album.
            comments: indicates wether obtain comments of the picture or not.

        Raises:
            RuntimeError if the user is not already logged in.
        """
        if not self.isLogged:
            raise RuntimeError('Es necesario estar logueado en la red social')
            
        if self.console:
            print '|'
            print '| Album', album[0]
            print '|'
            print '| Obteniendo informacion del album'

        joinPath = os.path.join(ROOTPATH, PHOTOS)
        if not os.path.exists(joinPath):
            if self.console:
                print '| Creando directorio donde se alojaran todas las fotos...'
            os.makedirs(joinPath)
            if self.console:
                print '| Directorio creado'
                
        albumPath = os.path.join(joinPath, album[0])
        if not os.path.exists(albumPath):
            if self.console:
                print '| Creando directorio donde se alojaran las fotos del album...'
            os.makedirs(albumPath)
            if self.console:
                print '| Directorio creado'
        os.chdir(albumPath)

        if self.console:
            print '| Comenzando la descarga de las fotos del album...'
            
        counter = 1
        self.tnt.getFirstPicture(album[2])
        while counter <= album[1]:
            pic = self.tnt.getPicture(comments)
            if counter == 1:
                firstPicture = pic
            elif pic[0] == firstPicture[0]:
                break
            self.savePicture(pic, counter, album[1], totalPictures, alreadyDownloaded + counter)
            if comments:
                self.saveComments(pic, counter)
            self.tnt.getNextPicture()
            counter += 1
            
    def savePicture(self, picture, myCounter, totalAlbum, totalPics, alreadyDown):
        """
        Save a picture.

        Args:
            picture: a picture to be saved.
            myCounter: the counter for the picture.
        """
        picName = getFullName(picture, myCounter) + JPG
        if not os.path.exists(picName):
            if self.console:
                totalPerc = str(100 * alreadyDown / totalPics)
                albumPerc = str(100 * myCounter / totalAlbum)
                print '|'
                print '| [' + totalPerc + '% total] [' + albumPerc + '% album]'
                print '| Descargando foto ' + picName + '...'
            sleep(0.25)
            urllib.urlretrieve(picture[0], picName)
            
    def saveComments(self, picture, myCounter):
        """
        Save a picture's comments.
        
        Args:
            picture: to obtain the comments.
            myCounter: to know the name of the file with comments.
        """
        commentsFileName = getFullName(picture, myCounter) + TXT
        if not os.path.exists(commentsFileName) and picture[3] != []:
            if self.console:
                print '| Descargando sus comentarios...'
            file2write = open(commentsFileName, 'w')
            for comment in picture[3]:
                file2write.write('******************\r\n')
                file2write.write(comment[1].encode('utf-8') + ':\r\n')
                file2write.write(comment[0].encode('utf-8') + '\r\n')
            file2write.close()

    def downloadAllPictures(self, comments=False):
        """
        Download all the pictures for all the albums.

        Args:
            comments: indicates wether obtain comments of the picture or not.

        Raises:
            RuntimeError if the user is not already logged in.
        """
        allAlbums = self.tnt.getAllAlbums()
        self.isLogged = (allAlbums != None)
        if not self.isLogged:
            return -1
            
        totalPictures = 0
        for album in allAlbums:
            totalPictures += album[1]
            
        alreadyDownloaded = 0
            
        for album in allAlbums:
            self.downloadPicturesFromAlbum(album, totalPictures, alreadyDownloaded, comments)
            alreadyDownloaded += album[1]
            
        return 0
        
    def goToPrivates(self):
        """
        Call the API to go to the private messages' page.
        """
        self.tnt.goToPrivates()
