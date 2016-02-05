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

import os, urllib, string, requests
import json, cookielib, datetime
from time import sleep
from tntapi import *

CONSTANT_FILL = 6
ROOTPATH = os.getcwdu()
PHOTOS = 'fotos'
JPG = '.jpg'
TXT = '.txt'

def getFullName(picture, counter):
    return normalize(string.zfill(counter, CONSTANT_FILL) + '_' + picture[2] + '_' + picture[1])

def convertCookiesSelenium(cookies):
    cj = cookielib.LWPCookieJar()
    for s_cookie in cookies:
        cj.set_cookie(cookielib.Cookie(
            version=0,
            name=s_cookie['name'],
            value=s_cookie['value'],
            port='80',
            port_specified=False,
            domain=s_cookie['domain'],
            domain_specified=True,
            domain_initial_dot=False,
            path=s_cookie['path'],
            path_specified=True,
            secure=s_cookie['secure'],
            expires=s_cookie['expiry'],
            discard=False,
            comment=None,
            comment_url=None,
            rest=None,
            rfc2109=False)
        )
    return cj

class Wrapper():
    """
    The wrapper for the tntapi.
    This class eases the connection.

    When constructed, it raises a RuntimeError if it is impossible to log in the
    social network.
    """
    def __init__(self, browser, console=False):
        self.tnt = API(browser)
        self.console = console

    def writeWallComment(self, post, fd):
        c = post.get('contents')
        n = normalize(post.get('author').get('shortName'))
        t = post.get('timestamp')
        t = datetime.datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M:%S')
        for i in c:
            if i.get('type') == 'String':
                con = normalize(i.get('string'))
                fd.write(t + ' | ' + n + ': ' + con + '\n')

    def downloadAllComments(self):
        """
        Download all text posts from your wall

        Raises:
            RuntimeError if the user is not already logged in.
        """
        if not self.tnt.getIsLogged():
            return -1

        if self.console:
            print '|'
            print '| Obteniendo informacion del wall'

        if self.console:
            print '| Creando fichero donde se alojaran todos los comentarios...'
        file_w = open(ROOTPATH + '/wall.txt', 'w')

        cookiej = convertCookiesSelenium(self.tnt.driver.get_cookies())
        s = requests.Session()
        s.cookies = cookiej

        if self.console:
            print '| Comenzando la descarga de los comentarios...'

        r = s.get(self.tnt.getURLApi('profile'))
        r = json.loads(r.text[8:])
        r = r.get('responseMetadata').get('jsonData').get('wall').get('wallData')
        w_id = r.get('wallId')
        num = 0
        total_post = 0
        actual_post = len(r.get('wallPosts'))
        wall_url = self.tnt.getURLApi('wall')
        while actual_post > 0:
            r = s.get(wall_url + '&wall_id=' + w_id + '&page_num=' + str(num))
            r = json.loads(r.text[8:])
            r = r.get('responseMetadata').get('jsonData').get('wall').get('wallData')
            [self.writeWallComment(x, file_w) for x in r.get('wallPosts')]
            if len(r.get('wallPosts')):
                total_post += len(r.get('wallPosts'))
                num += 1
                if self.console:
                    print '| * Descargados: ' + str(total_post) + ' posts ... '
            actual_post = len(r.get('wallPosts'))
        file_w.close()

        return 0


    def downloadPicturesFromAlbum(self, album, totalPictures, alreadyDownloaded, comments=False):
        """
        Download pictures from a given album into the given directory.

        Args:
            album: the album.
            comments: indicates wether obtain comments of the picture or not.

        Raises:
            RuntimeError if the user is not already logged in.
        """
        if not self.tnt.getIsLogged():
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
        if not self.tnt.getIsLogged():
            raise RuntimeError('Es necesario estar logueado en la red social')

        allAlbums = self.tnt.getAllAlbums()
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
