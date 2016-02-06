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

This is the API for the 20up backup program. This API allows a client
to retrieve information about his specific account.
"""

import unicodedata
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

INFOS = {
    'email'         :   'email',
    'password'      :   'input_password',
    'submit'        :   'submit_button',
    'albums'        :   'pst-pht-dropwdown',
    'classAlbums'   :   'sel-block',
    'ulFirstPic'    :   'albumBody',
    'idPhotoImage'  :   'photo_image',
    'viewMore'      :   'overlay_wall_view_more',
    'picComments'   :   'wallpost-list-overlay-comments',
    'picDate'       :   'h-date',
    'username'      :   'cmt-username',
    'comment'       :   'wall-delete',
    'next'          :   'photo_nav_next',
    'next2'         :   'pht-nav-next',
}

TWENTY_HOST = 'https://www.tuenti.com/'
TWENTY_HOST_SEC = 'https://www-1.tuenti.com'

URLS = {
    'login'         :   TWENTY_HOST,
    'home'          :   TWENTY_HOST + '#m=Home&func=view_social_home_canvas',
    'my_profile'    :   TWENTY_HOST + '#m=Profile&func=index',
    'my_privates'   :   TWENTY_HOST + '#m=Messages&func=index',
}

APIS = {
    'profile'          :   TWENTY_HOST_SEC + '/?m=Profile&func=index&ajax=1',
    'wall'             :   TWENTY_HOST_SEC + '?m=Walls&func=view_wall_posts_page&entry_type=1&ajax=1&filter=-2',
    'cupcake'          :   TWENTY_HOST_SEC + '/index.cupcake.php'
}
APIS['photos'] = APIS['cupcake'] + '?m=Albums&func=getAlbumPhotos&ajax=1&collection_key='
APIS['photos_more'] = APIS['cupcake'] + '?m=Albums&func=getMorePhotosPage&ajax=1&collection_key='
APIS['photo_info'] = APIS['cupcake'] + '?m=Photo&func=preloadPhotos&ajax=1'


def normalize(text):
    nfkd_form = unicodedata.normalize('NFKD', text)
    only_ascii = nfkd_form.encode('ASCII', 'ignore')
    return only_ascii


class API():
    """
    The API class.
    This class is used for getting information.
    It only parses the information given by the web browser.
    """
    def __init__(self, browser):
        self.driver = ''
        self.csrf = None
        try:
            if browser == 'ch':
                self.driver = webdriver.Chrome()
            elif browser == 'fi':
                self.driver = webdriver.Firefox()
            else:
                raise RuntimeError('El navegador web elegido no esta soportado por 20up')
        except:
            raise RuntimeError('Imposible abrir el navegador web; por favor, elige otro')
            
#        self.driver.implicitly_wait(0.5)
        self.driver.get(URLS['login'])

    def getIsLogged(self):
        tmp_url = self.driver.current_url
        self.driver.get(URLS['home'])
        ret = self.driver.current_url == URLS['home']
        if ret and self.csrf is None:
            self.csrf = self.getCSRFToken()
        self.driver.get(tmp_url)
        return ret

    def getURLApi(self, url):
        return APIS[url]

    def getCSRFToken(self):
        p = self.driver.page_source.index('csrf')
        return self.driver.page_source[p+7:p+15]

    def getAllAlbums(self):
        """
        Get all the albums for the given user.
        An album is a shortlist of three elements (name, number, link), where
        <name> is the name of the album itself, <number> is the number of
        pictures in the album and <link> is the url of the album.

        Returns:
            A list of albums.
        """        
        self.driver.get(URLS['my_profile'])

        trigger = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'albumSelector')))
        trigger.click()
        
        myAlbums = {}
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        allAlbums = soup.find('ul', {'class': INFOS['albums']}).find_all('a', {'class': INFOS['classAlbums']})
        for album in allAlbums:
            withoutSpace = album.getText().split()
            name = normalize(' '.join(withoutSpace[:-1]).replace(' ','_'))
            number = int(withoutSpace[-1][1:-1].replace('.', ''))
            link = album['href']
            albumId = link[36:link.index('&s')]
            myAlbums[albumId] = {
                'id': albumId,
                'name': name,
                'photos': number,
                'link': TWENTY_HOST + link
            }

        return myAlbums
        
    def goToPrivates(self):
        """
        Open the private messages' page.
        """
        self.driver.get(URLS['my_privates'])
