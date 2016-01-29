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

MAX_PICTURES_IN_PAGE = 12
MAX_COMMENTS_IN_WALL = 5
CONSTANT_FILL = 6
ROOTPATH = os.getcwdu()
PHOTOS = 'fotos'
JPG = '.jpg'
TXT = '.txt'

class Wrapper():
    """
    The wrapper for the tntapi.
    This class eases the connection.

    When constructed, it raises a RuntimeError if it is impossible to log in the
    social network.
    """
    def __init__(self, email, password, console=False):
        self.tnt = API()
        self.isLogged = False
        if not self.tnt.doLogin(email, password):
            raise RuntimeError('Imposible hacer login en la red social')
        self.console = console
        self.isLogged = True

    def downloadPicturesFromAlbum(self, albumid, directory, comments=False):
        """
        Download pictures from a given album into the given directory.

        Args:
            albumid: the ID number of the album.
            directory: the directory where the pictures are going to be
                       downloaded.
            comments: indicates wether obtain comments of the picture or not.

        Raises:
            RuntimeError if the user is not already logged in.
        """
        if not self.isLogged:
            raise RuntimeError('Es necesario estar logueado en la red social')

        if self.console:
            print '|'
            print '| Album', directory
            print '|'
            print '| Obteniendo informacion del album'

        joinPath = os.path.join(ROOTPATH, PHOTOS)
        if not os.path.exists(joinPath):
            if self.console:
                print '| Creando directorio donde se alojaran todas las fotos...'
            os.makedirs(joinPath)
            if self.console:
                print '| Directorio creado'

        albumPath = os.path.join(joinPath, directory)
        if not os.path.exists(albumPath):
            if self.console:
                print '| Creando directorio donde se alojaran las fotos del album...'
            os.makedirs(albumPath)
            if self.console:
                print '| Directorio creado'
        os.chdir(albumPath)

        if self.console:
            print '| Comenzando la descarga de las fotos del album...'
        page = 0
        first = ''
        counter = 1
        while True:
            sleep(0.5)
            pictures = self.tnt.getPictures(albumid, page)
            if page == 0:
                first = pictures[0][0]
            if pictures[0][0] != first or page == 0:
                if self.console:
                    print '| Pagina', (page+1)
                self.savePictures(albumPath, counter, pictures, comments)
            else:
                break
            page += 1
            counter += MAX_PICTURES_IN_PAGE

    def savePictures(self, albumPath, myCounter, pictures, comments=False):
        """
        Save a list of pictures.

        Args:
            albumPath: the path to the album in the directory tree.
            myCounter: the counter of the pic to download.
            pictures: a list of pictures, where the first element is the url
                      and the second is a list of comments.
            comments: indicates wether obtain comments of the picture or not.
        """
        for pic in pictures:
            sleep(0.5)
            picInfo = self.tnt.getPicture(pic[0], comments)
            if not picInfo:
                continue
            fullName = string.zfill(myCounter, CONSTANT_FILL) + '_' + pic[1]
            picName = normalize(fullName + '_' + picInfo[2] + JPG)
            fileName = os.path.join(albumPath, picName)
            if not os.path.exists(fileName):
                if self.console:
                    print '| Descargando foto ' + picName + '...'
                sleep(0.5)
                urllib.urlretrieve(picInfo[0], fileName)

            commentsFileName = fullName + TXT
            if comments and not os.path.exists(commentsFileName) and picInfo[1] != []:
                if self.console:
                    print '| Descargando sus comentarios...'
                file2write = open(commentsFileName, 'w')
                for comment in picInfo[1]:
                    file2write.write('******************\r\n')
                    file2write.write(comment[0].encode('utf-8') + ' (' + comment[1].encode('utf-8') + '):\r\n')
                    file2write.write(comment[2].encode('utf-8') + '\r\n')
                file2write.close()

            myCounter += 1

    def downloadAllPictures(self, comments=False):
        """
        Download all the pictures for all the albums.

        Args:
            comments: indicates wether obtain comments of the picture or not.

        Raises:
            RuntimeError if the user is not already logged in.
        """
        if not self.isLogged:
            raise RuntimeError('Es necesario estar logueado en la red social')

        allAlbums = self.tnt.getAllAlbums()
# just for testing allAlbums = allAlbums[2:]
        for album in allAlbums:
            self.downloadPicturesFromAlbum(album[0], album[1], comments)

    def downloadAllComments(self):
        """
        Download all the comments for the wall.

        Raises:
            RuntimeError if the user is not already logged in.
        """
        if not self.isLogged:
            raise RuntimeError('Es necesario estar logueado en la red social')

        os.chdir(ROOTPATH)
        file2write = open('comentarios.txt', 'w')
        
        ended = False
        page = 0
        if self.console:
            print '| Comenzando la descarga de comentarios...'
        while not ended:
            if self.console:
                print '| Pagina', page
            sleep(0.5)
            comments = self.tnt.getWall(page)
            if comments != []:
                self.saveComments(comments, file2write)
                page += 5
            else:
                ended = True

        file2write.close()
        
    def saveComments(self, comments, file2write):
        """
        Save a list of comments
        
        Args:
            comments: a list of comments
            file2write: the file where the info must be written
        """
        
        for comment in comments:
            file2write.write('******************\r\n')
            file2write.write(comment[0].encode('utf-8') + ' (' + comment[1].encode('utf-8') + ' ):\r\n')
            file2write.write(comment[2].encode('utf-8') + '\r\n')
            
    def downloadFriends(self):
        """
        Save information about your friends
        
        Raises:
            RuntimeError if the user is not already logged in.
        """
        if not self.isLogged:
            raise RuntimeError('Es necesario estar logueado en la red social')
        
        os.chdir(ROOTPATH)
        file2write = open('contactos.txt', 'w')
        
        page = 0
        while True:
            if self.console:
                print '| Pagina', (page+1)
            sleep(0.5)
            listFriends = self.tnt.getFriendsIDs(page)
            if not listFriends:
                break
                
            for friend in listFriends:
                sleep(0.5)
                birthday = self.tnt.getUserData(friend[0])
                if birthday != '':
                    text = friend[1] + ':' + birthday + '\r\n'
                    file2write.write(text)
                
            page += 1
            
        file2write.close()
