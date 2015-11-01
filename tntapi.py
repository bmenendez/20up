#! /usr/bin/python
# -*- coding: utf-8 -*-

"""
Copyright (C) 2013 Borja Menendez Moreno

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

Authors: Borja Menéndez Moreno <tuentiup@gmail.com>

This is the API for the 20up backup program. This API allows a client
to retrieve information about his specific Tuenti account.
"""

import mechanize, cookielib
import re, unicodedata
from bs4 import BeautifulSoup

TUENTI_HOST = 'https://m.tuenti.com'
URLS = {
    'login':        TUENTI_HOST + '/?m=login',
    'friends':      TUENTI_HOST + '/?m=friends&page=%s',
    'profile':      TUENTI_HOST + '/?m=profile&user_id=%s',
    'comments':     TUENTI_HOST + '/?m=profile&func=view_wall&user_id=%s&fpi=%s',
    'my_profile':   TUENTI_HOST + '/?m=profile&func=my_profile',
    'albums':       TUENTI_HOST + '/?m=Albums&func=view_album_display&collection_key=%s&photos_page=%s',
    'photo':        TUENTI_HOST + '/?m=Photos&func=view_album_photo&collection_key=%s',
}

def normalize(text):
    t = unicodedata.normalize('NFKD', text.decode('utf-8'))
    t = re.sub('[^a-zA-Z0-9\n\.]', '-', t)
    return t.encode('utf-8')

class API():
    """
    The Tuenti API class.
    This class is used for getting information.
    It only parses html pages and returns the requested information.
    """
    def __init__(self):
        cj = cookielib.LWPCookieJar()
        self.br = mechanize.Browser()
        self.br.set_cookiejar(cj)
        ck = cookielib.Cookie(version=0, name='screen', value='1920-1080-1920-1040-1-20.74', port=None, port_specified=False, domain='m.tuenti.com', domain_specified=False, domain_initial_dot=False, path='/', path_specified=True, secure=False, expires=None, discard=True, comment=None, comment_url=None, rest={'HttpOnly': None}, rfc2109=False)
        cj.set_cookie(ck)
        self.br.set_handle_equiv(True)
        self.br.set_handle_redirect(True)
        self.br.set_handle_referer(True)
        self.br.set_handle_robots(False)
        self.br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)
#        self.br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:40.0) Gecko/20100101 Firefox/40.0')]
#        self.br.addheaders = [('User-agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.2.8) Gecko/20100722 Firefox/3.6.8 GTB7.1 (.NET CLR 3.5.30729)')]
        self.id = ''

    def doLogin(self, email, password):
        """
        The method that starts the connection with Tuenti.

        Args:
            email: the Tuenti user's email address.
            password: the Tuenti user's password.
        """
        self.br.open(URLS['login'])
        self.br.select_form(nr = 0)
        self.br['tuentiemailaddress'] = email
        self.br['password'] = password
        self.br.submit()
        return 'Tuenti-Tuenti' in self.br.title()

    def getAllAlbums(self):
        """
        Get all the albums for the given user.
        An album is a pair of (key, link), where <key> is the identification
        number of the album in Tuenti and <link> is the url of the album.

        Returns:
            A list of albums.
        """
        self.br.open(URLS['my_profile'])
        albums = []
        for link in self.br.links():
            if 'collection_key' in link.url:
                key = link.url.split('collection_key=')[1].split('&stats=')[0]
                albums.append([key, normalize(link.text)])
            if 'm=Profile&func=view_wall&user_id' in link.url:
                self.id = link.url.split('user_id=')[1].split('&')[0]
        return albums

    def getPictures(self, albumid, page):
        """
        Get pictures from a given album.
        A picture is a pair of (key, link), where <key> is the identification
        number of the picture in Tuenti and <link> is the url of the picture.

        Args:
            albumid: the <key> of an album.
            page: the number of the page of the given album.

        Returns:
            A list of pictures for the given album.
        """
        self.br.open(URLS['albums'] % (albumid, str(page)))
        urls = []
        for link in self.br.links():
            if 'collection_key' in link.url and 'photos_page' not in link.url:
                key = link.url.split('collection_key=')[1].split('&stats=')[0]
                urls.append([key, normalize(link.text[:-5])])
        return urls

    def getPicture(self, pictureid, comments=False):
        """
        Get concrete information about a picture.

        Args:
            pictureid: the id number of a concrete picture.
            comments: indicates wether obtain comments of the picture or not.

        Returns:
            A list containing two elements:
                the url for the concrete picture
                a list containing the comments of the picture (this list may
                be empty if there are no comments) (comments are defined below)
        """
        r = self.br.open(URLS['photo'] % pictureid)
        soup = BeautifulSoup(r.read(), 'html.parser')
        returningInfo = []
        try:
            # picture url
            picture = soup.find('div', {'class': 'full_size_photo'}).find('img')['src']
            # date
            date = ''
            info = soup.findAll('div', {'class': 'box'})
            for data in info:
                text = '<span class="time">'
                strData = str(data)
                if text in strData:
                    date = '_'.join(strData.split(text)[1].split()[:4]).replace(',','').replace(':','-')
            # picture comments, if so
            comm = []
            if comments:
                allComments = soup.findAll('li', {'class': 'item inline'})
                if allComments != []:
                    for comment in allComments:
                        info = []
                        info.append(comment.find('a').contents[0]['alt']) # from
                        info.append(comment.find('div', {'class': 'time'}).contents[0]) # at
                        try:
                            info.append(comment.find('div', {'class': 'userContent'}).contents[0]) # comment
                        except:
                            continue
                        comm.append(info)
                        
            returningInfo = [picture, comm, date]
        except:
            pass

        return returningInfo

    def getFriendsIDs(self, page):
        """
        Get the friends' user ID.
        A friend is a pair of (userid, link), where <userid> is the friends'
        user ID and <link> is the friends' user page.

        Args:
            page: the number of the page in the list of friends in steps of 1
                  (starting at 0).

        Returns:
            A list of friends.
        """
        self.br.open(URLS['friends'] % str(page))
        friends = []
        for link in self.br.links():
            if 'user_id' in link.url:
                userid = link.url.split('=')[-1]
                friends.append([userid, link.text])
        return friends

    def getUserData(self, userid):
        """
        Get the data of a given user.

        Args:
            userid: the user ID.

        Returns:
            A string with the birthday of userid
        """
        r = self.br.open(URLS['profile'] % str(userid))
        soup = BeautifulSoup(r.read(), 'html.parser')
        infos = soup.findAll('div', {'class': 'box'})
        
        birthday = ''
        for info in infos:
            strInfo = str(info)
            if 'strong' in strInfo:
                birthday = strInfo.split('</strong>')[1].split('<br')[0]
        
        return birthday

    def getWall(self, page):
        """
        Get the comments in the wall of the user.
        A comment is a 3-tupla of (from, at, comment_itself), where <from> is
        the name of the user who wrote the comment, <at> is the time where the
        user wrote the comment, and <comment_itself> is the text of the comment.

        Args:
            page: the number of the page in the list of comments in steps of 5
                  (starting at 0).

        Returns:
            A list of comments in the wall of the user.
        """
        if self.id == '':
            self.getAllAlbums()
        self.br.open(URLS['comments'] % (self.id, str(page)))
        soup = BeautifulSoup(self.br.response().read(), 'html.parser')
        allComments = soup.find('div', {'id': 'content'}).findAll('li', {'class': 'item inline'})
        comm = []
        if allComments:
            for comment in allComments:
                info = []
                try:
                    info.append(comment.find('div', {'class': 'itemBody'}).find('a').contents[0]) # from
                    info.append(comment.find('span', {'class': 'time'}).contents[0]) # at
                    info.append(comment.find('div', {'class': 'userContent'}).contents[0]) # comment
                except IndexError:
                    info = []

                if info:
                    comm.append(info)

        return comm
