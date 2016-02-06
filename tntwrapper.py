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
from bs4 import BeautifulSoup
import shutil
from time import sleep
from tntapi import *

CONSTANT_FILL = 6
ROOTPATH = os.getcwdu()
BACKUP = 'backup'
PHOTOS = 'fotos'
CONTACTS = 'contactos'
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


def createBackupFolder():
    joinPath = os.path.join(ROOTPATH, BACKUP)
    if not os.path.exists(joinPath):
        os.makedirs(joinPath)


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
        createBackupFolder()

    def writeWallComment(self, post, fd):
        c = post.get('contents')
        n = normalize(post.get('author').get('shortName'))
        t = post.get('timestamp')
        if isinstance(t, unicode) or isinstance(t, str):
            t = int(t)
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
        file_w = open(ROOTPATH + '/' + BACKUP + '/wall.txt', 'w')

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

    def writeContact(self, friend, fd, folder):
        fd.write('- - - - - - - - - \n')
        id = str(friend.get('id'))
        fd.write('Id: ' + id)
        fd.write(' | User: ' + normalize(friend.get('string')))
        if 'firstName' in friend.get('info'):
            fd.write(' | First Name: ' + normalize(friend.get('info').get('firstName')))
        if 'lastName' in friend.get('info'):
            fd.write(' | Last Name: ' + normalize(friend.get('info').get('lastName')))
        g = 'Male' if friend.get('info').get('isMale') else 'Female'
        fd.write(' | Gender: ' + g + '\n')
        if not 'static' in friend.get('info').get('avatarUrl'):
            r = requests.get(friend.get('info').get('avatarUrl'), stream=True)
            with open(folder + '/' + id + '.jpg' , 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)


    def downloadContacts(self):
        """
        Download all contacts

        Raises:
            RuntimeError if the user is not already logged in.
        """
        if not self.tnt.getIsLogged():
            return -1

        if self.console:
            print '|'
            print '| Obteniendo informacion de contactos'

        joinPath = os.path.join(ROOTPATH, BACKUP + '/' + CONTACTS)
        if not os.path.exists(joinPath):
            if self.console:
                print '| Creando directorio donde se alojaran todos los contactos...'
            os.makedirs(joinPath)
            if self.console:
                print '| Directorio creado'

        if self.console:
            print '| Creando fichero donde se alojaran todos los datos de los contactos...'
        file_w = open(joinPath + '/contacts.txt', 'w')

        cookiej = convertCookiesSelenium(self.tnt.driver.get_cookies())
        s = requests.Session()
        s.cookies = cookiej

        if self.console:
            print '| Comenzando la descarga de los contactos...'

        r_csrf = self.tnt.csrf
        r_data = 'req=%5B%7B%22csfr%22%3A%22' + r_csrf + '%22%7D%2C%7B%22'
        r_data += 'Search%22%3A%7B%22getTypes%22%3A%7B%22types%22%3A%5B%22u1%22%5D%7D'
        r_data += '%7D%7D%5D&cup=1&csfr=' + r_csrf + '&csrf=' + r_csrf
        r = s.post(self.tnt.getURLApi('cupcake'), r_data)
        r = json.loads(r.text[8:])
        r = r.get('responseMetadata').get('jsonData').get('u1')
        r = r.get('results')
        [self.writeContact(x, file_w, joinPath) for x in r]
        print '| * Descargados: ' + str(len(r)) + ' contactos ... '
        file_w.close()
        return 0

    def getPhotoInformation(self, pictureId):
        cookiej = convertCookiesSelenium(self.tnt.driver.get_cookies())
        s = requests.Session()
        s.cookies = cookiej
        r_csrf = self.tnt.csrf
        r_url = self.tnt.getURLApi('photo_info')
        r_data = 'itemKey=' + pictureId + '&backgrounded=false&prefetchDirection=10'
        r_data += '&offset=0&source=25&pc=%7B%22wt%22%3A3%7D&csfr=' + r_csrf
        r_data += '&csrf=' + r_csrf
        r = s.post(r_url, r_data)
        r = json.loads(r.text[8:])
        r = r.get('responseMetadata').get('jsonData').get(pictureId)
        return {
            'photo': r.get('getPhoto'),
            'comments' :r.get('getWall')
        }

    def getFirstAlbumPhotos(self, albumId):
        cookiej = convertCookiesSelenium(self.tnt.driver.get_cookies())
        s = requests.Session()
        s.cookies = cookiej
        r_csrf = self.tnt.csrf
        r_url = self.tnt.getURLApi('photos') + albumId
        r_data = 'collection_key=' + albumId + '&csfr=' + r_csrf + '&csrf=' + r_csrf
        r = s.post(r_url, r_data)
        r = json.loads(r.text[8:])
        r = r.get('renderOutput').get('albumPhotosContainer').get('html')
        soup = BeautifulSoup(r, 'html.parser')
        ph_tmp = soup.find_all(attrs={'class': 'thumb'})
        ph = set()
        for i in ph_tmp:
            if 'href' in i.attrs:
                ph.add(i.attrs.get('href')[40:i.attrs.get('href').index('&s')])
        next = soup.find(attrs={'id': 'albumsViewMoreButton'})
        if next is not None:
            next = next.attrs.get('data-href')[86:]
        return ph, next

    def getNextAlbumPhotos(self, albumId, nextId, page):
        cookiej = convertCookiesSelenium(self.tnt.driver.get_cookies())
        s = requests.Session()
        s.cookies = cookiej
        r_url = self.tnt.getURLApi('photos_more') + albumId
        r_url += '&last_item=' + nextId + '&photos_page=' + str(page)
        r = s.get(r_url)
        res = json.loads(r.text[8:])
        r = res.get('renderOutput').get('albumBody').get('html')
        soup = BeautifulSoup(r, 'html.parser')
        ph_tmp = soup.find_all(attrs={'class': 'thumb'})
        ph = set()
        for i in ph_tmp:
            if 'href' in i.attrs:
                ph.add(i.attrs.get('href')[40:i.attrs.get('href').index('&s')])
        r = res.get('renderOutput').get('albumsViewMore').get('html')
        if r is None:
            return ph, None
        soup = BeautifulSoup(r, 'html.parser')
        next = soup.find(attrs={'id': 'albumsViewMoreButton'})
        next = next.attrs.get('data-href')[86:]
        return ph, next

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

        albumName = album['name'].lower()

        if self.console:
            print '|'
            print '| Album', albumName
            print '|'
            print '| Obteniendo informacion del album'

        joinPath = os.path.join(ROOTPATH, BACKUP + '/' + PHOTOS)
        if not os.path.exists(joinPath):
            if self.console:
                print '| Creando directorio donde se alojaran todas las fotos...'
            os.makedirs(joinPath)
            if self.console:
                print '| Directorio creado'
                
        albumPath = os.path.join(joinPath, albumName)
        if not os.path.exists(albumPath):
            if self.console:
                print '| Creando directorio donde se alojaran las fotos del album...'
            os.makedirs(albumPath)
            if self.console:
                print '| Directorio creado'

        if self.console:
            print '| Comenzando la descarga de las fotos del album...'

        photos, next = self.getFirstAlbumPhotos(album['id'])

        ids_album = {}
        if os.path.exists(albumPath + '/ids.txt'):
            file_r = open(albumPath + '/ids.txt', 'r')
            ids_album = json.loads(file_r.read())
            file_r.close()

        for i in photos:
            if i not in ids_album or comments:
                fn = self.savePicture(i, albumPath, comments, ids_album.get(i, None))
                ids_album[i] = fn
                file_r = open(albumPath + '/ids.txt', 'w')
                file_r.write(json.dumps(ids_album))
                file_r.close()

        page = 1
        while next is not None:
            photos, next = self.getNextAlbumPhotos(album['id'], next, page)
            page +=1
            for i in photos:
                if i not in ids_album or comments:
                    fn = self.savePicture(i, albumPath, comments, ids_album.get(i, None))
                    ids_album[i] = fn
                    file_r = open(albumPath + '/ids.txt', 'w')
                    file_r.write(json.dumps(ids_album))
                    file_r.close()

    def savePicture(self, pictureId, path, comments, saved):
        """
        Save a picture.

        Args:
            pictureId: a picture identifier to be saved.
            path: folder where picture will be saved.
            comments: flag to determinate if comments will be saved.
            saved: file_name saved.
        """
        if saved is not None:
            if not comments:
                return
            else:
                sleep(0.25)
                pic_com = saved.replace('jpg', 'txt')
                if os.path.exists(path + '/' + pic_com):
                    return saved
                info = self.getPhotoInformation(pictureId)
                self.saveComments(path + '/' + saved, info.get('comments'))
                print '| Comentarios descargados: ' + pic_com
                return saved
        else:
            sleep(0.25)
            info = self.getPhotoInformation(pictureId)
            picName = datetime.datetime.fromtimestamp(
                info.get('photo').get('uploaderDate')
            ).strftime('%Y_%m_%d_%H_%M_%S')
            number_photo = 1
            pic_tmp = picName
            while os.path.exists(path + '/' + pic_tmp + '.jpg'):
                pic_tmp = picName + '_' + str(number_photo)
                number_photo += 1
            picName = pic_tmp + '.jpg'
            urllib.urlretrieve(info.get('photo').get('url'), path + '/' + picName)

            if comments and not info.get('comments').get('isEmpty'):
                pic_com = picName.replace('jpg', 'txt')
                if not os.path.exists(path + '/' + pic_com):
                    self.saveComments(path + '/' + picName, info.get('comments'))
                    if self.console:
                        print '| Comentarios descargados: ' + pic_com

            if self.console:
                    print '| Foto descargada: ' + picName

            return picName
            
    def saveComments(self, file_name, comments_info):
        """
        Save a picture's comments.
        
        Args:
            file_name: file_name from picture to be saved.
            comments_info: comments from photo information.
        """
        fcom = file_name.replace('jpg', 'txt')
        file_w = open(fcom, 'w')
        r = comments_info.get('wallData')
        [self.writeWallComment(x, file_w) for x in r.get('wallPosts')]
        file_w.close()

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
        alreadyDownloaded = 0

        for album in allAlbums:
            totalPictures += allAlbums[album]['photos']

        for album in allAlbums:
            self.downloadPicturesFromAlbum(
                allAlbums[album], totalPictures, alreadyDownloaded, comments
            )
            alreadyDownloaded += allAlbums[album]['photos']
            
        return 0
        
    def goToPrivates(self):
        """
        Call the API to go to the private messages' page.
        """
        self.tnt.goToPrivates()
