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
MAX_TRIES = 10
ROOTPATH = os.getcwdu()
PHOTOS = 'fotos'
COMMENTS = 'comentarios'
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
        
    def waitForLogin(self):
        self.tnt.waitForLogin()
            
    def downloadPicturesFromAlbum(self, album, totalPictures, alreadyDownloaded, oldFirstPicture, comments=False):
        """
        Download pictures from a given album into the given directory.

        Args:
            album: the album.
            totalPictures: the total number of pictures of the user.
            alreadyDownloaded: the number of pictures already downloaded.
            oldFirstPicture: the first picture of the previous album.
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
        newFirstPicture = self.tnt.getFirstPicture(album[2], oldFirstPicture)
        firstPicture = ''
        lastPicture = ['']
        while counter <= album[1]:
            pic = self.tnt.getPicture(comments)
            if counter == 1:
                firstPicture = pic
            elif pic[0] == firstPicture[0]:
                break
            if lastPicture[0] != pic[0]:
                self.savePicture(pic, counter, album[1], totalPictures, alreadyDownloaded + counter)
                if comments:
                    self.saveComments(pic, counter)
                counter += 1
                lastPicture = pic
            self.tnt.getNextPicture()
            
        return newFirstPicture
            
    def savePicture(self, picture, myCounter, totalAlbum, totalPics, alreadyDown):
        """
        Save a picture.

        Args:
            picture: a picture to be saved.
            myCounter: the counter for the picture.
            totalAlbum: the number of pictures of the album.
            totalPics: the number of pictures of the user.
            alreadyDown: the number of pictures already downloaded.
        """
        sleep(0.25)
        picName = getFullName(picture, myCounter) + JPG
        if not os.path.exists(picName):
            if self.console:
                totalPerc = str(100 * alreadyDown / totalPics)
                albumPerc = str(100 * myCounter / totalAlbum)
                print '|'
                print '| [' + totalPerc + '% total] [' + albumPerc + '% album]'
                print '| Descargando foto ' + picName + '...'
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
                file2write.write(comment.encode('utf-8') + '\r\n')
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
        oldFirstPicture = ''
        for album in allAlbums:
            oldFirstPicture = self.downloadPicturesFromAlbum(album, totalPictures, alreadyDownloaded, oldFirstPicture, comments)
            alreadyDownloaded += album[1]
            
        return 0
        
    def goToPrivates(self):
        """
        Call the API to go to the private messages' page.
        """
        self.tnt.goToPrivates()
        
    def downloadAllComments(self):
        """
        Download all the comments in the wall.
        """
        os.chdir(ROOTPATH)
        file2write = open(COMMENTS + TXT, 'w')
        
        tries = 0
        discard = 0
        while True:
            comments = self.tnt.loadMoreComments(discard)
            if not comments:
                if tries < MAX_TRIES:
                    tries += 1
                    sleep(0.3)
                else:
                    break
            else:
                tries = 1
                discard += len(comments)
                if self.console:
                    print '| Descargados ', discard, 'comentarios'
                self.saveWall(comments, file2write)
        file2write.close()
            
    def saveWall(self, comments, file2write):
        """
        Write the comments in the file.
        
        Args:
            comments: the list of comments to be saved.
            file2write: the file to write in.
        """
        for comment in comments:
            file2write.write(comment.encode('utf-8') + '\r\n\r\n')
