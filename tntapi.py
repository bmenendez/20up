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
from time import sleep
import re, unicodedata
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
    'albumDisplay'  :   'album-display',
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
URLS = {
    'login'         :   TWENTY_HOST,
    'home'          :   TWENTY_HOST + '#m=Home&func=view_social_home_canvas',
    'my_profile'    :   TWENTY_HOST + '#m=Profile&func=index',
    'my_privates'   :   TWENTY_HOST + '#m=Messages&func=index',
}

def normalize(text):
    t = unicodedata.normalize('NFKD', text)
    t = re.sub('[^a-zA-Z0-9\n\.]', '-', t)
    return t

class API():
    """
    The API class.
    This class is used for getting information.
    It only parses the information given by the web browser.
    """
    def __init__(self, browser):
        self.driver = ''
        try:
            if browser == 'ch':
                self.driver = webdriver.Chrome()
            elif browser == 'fi':
                self.driver = webdriver.Firefox()
            else:
                raise RuntimeError('El navegador web elegido no esta soportado por 20up')
        except:
            raise RuntimeError('Imposible abrir el navegador web; por favor, elige otro')

        self.driver.get(URLS['login'])
        
    def waitForLogin(self):
        """
        Wait for the user to be logged into the social network.
        """
        logged = False
        while not logged:
            try:
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'sideBarPlaceHolder')))
                logged = True
            except:
                pass
            
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
        
        if self.driver.current_url != URLS['my_profile']:
            return None
        
        trigger.click()
        
        myAlbums = []
        
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        allAlbums = soup.find('ul', {'class': INFOS['albums']}).find_all('a', {'class': INFOS['classAlbums']})
        for album in allAlbums:
            withoutSpace = album.getText().split()
            name = normalize(' '.join(withoutSpace[:-1]).replace(' ','-'))
            intNumber = withoutSpace[-1][1:-1]
            if intNumber.find('.') != -1:
                intNumber = intNumber.split('.')
            else:
                intNumber = intNumber.split(',')
            finalNumber = ''
            for num in intNumber:
                finalNumber += num
            number = int(finalNumber)
            link = album['href']
            
            nnl = [name, number, TWENTY_HOST + link]
            myAlbums.append(nnl)

        return myAlbums
        
    def getFirstPicture(self, linkAlbum, oldFirstPictureLink=''):
        """
        Get the first picture from a given album.
        
        Args:
            linkAlbum: the <link> of the album to be downloaded.
            oldFirstPictureLink: the <link> of the first picture of the
                                 previous album.
            
        Returns:
            A <link> to the picture.
        """
        self.driver.get(linkAlbum)

        picture = oldFirstPictureLink
        while picture == oldFirstPictureLink:
            element = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, INFOS['ulFirstPic'])))
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            try:
                picture = soup.find('div', {'class' : INFOS['albumDisplay']}).find('ul', {'id' : INFOS['ulFirstPic']}).find_all('li')[0].find('a')
                picture = TWENTY_HOST + picture['href']
            except:
                pass
            sleep(0.2)

        self.driver.get(picture)
        
        return picture
        
    def getPicture(self, comments=False):
        """
        Get the picture to be downloaded and the comments, if so.
        
        Args:
            linkPicture: the link to the picture.
            comments: indicates wether obtain comments of the picture or not.
            
        Returns:
            A shortlist of four elements of (link, title, date, comments),
            where <link> is the image to be downloaded, <title> is the title
            of the picture, <date> is the submission's date and <comments> is
            a list of comments.
        """        
        element = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, INFOS['idPhotoImage'])))
        
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        pic = soup.find('img', {'id': INFOS['idPhotoImage']})
        image = pic['src']
        title = pic['alt']
        date = soup.find('em', {'class': INFOS['picDate']}).getText()
        date = date.replace(':','-').replace(',','').replace(' ','-')
        allComments = []
        if comments:
            allComments = self.getComments()
            
        return [image, title, date, allComments]
        
    def getComments(self):
        """
        Get the comments of the current picture.
            
        Returns:
            A list of comments of the picture, where a <comment> is a shortlist
            with the comment itself (<user date: comment>).
        """
        while True:
            try:
                more = WebDriverWait(self.driver, 1).until(EC.presence_of_element_located((By.ID, INFOS['viewMore'])))
                more.click()
            except:
                break
        
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        myComments = []
        allComments = soup.find('ol', {'id': INFOS['picComments']}).find_all('li')
        for comment in allComments:
            try:
                myComments.append(comment.get_text(separator=' ').replace(' Eliminar', ':'))
            except:
                pass
            
        return myComments
    
    def getNextPicture(self):
        """
        Get the next picture to the given picture.
        """
        WebDriverWait(self.driver, 0.1).until(EC.presence_of_element_located((By.ID, INFOS['next'])))
        WebDriverWait(self.driver, 0.1).until(EC.presence_of_element_located((By.CLASS_NAME, INFOS['next2'])))
        
        try:
            next = self.driver.find_element_by_id(INFOS['next'])
            self.driver.execute_script("document.getElementById('" + INFOS['next'] + "').focus();")
            next.click()
        except:
            next = self.driver.find_element_by_class_name(INFOS['next2'])
            self.driver.execute_script("document.getElementById('" + INFOS['next2'] + "').focus();")
            next.click()
        
    def goToPrivates(self):
        """
        Open the private messages' page.
        """
        self.driver.get(URLS['my_privates'])
        
    def loadMoreComments(self, discards):
        """
        Load more comments of the wall.
        
        Args:
            discards: the number of comments to be discarded.
        """
        self.driver.get(URLS['my_profile'])
        
        trigger = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, 'albumSelector')))
        
        if self.driver.current_url != URLS['my_profile']:
            raise RuntimeError('Es necesario entrar primero a la red social')

        self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        try:
            className = "//*[contains(@class, 'act-L')]"
            triggers = self.driver.find_elements_by_xpath(className)
            for trigger in triggers:
                if 'Ver' in trigger.text:
                    trigger.click()
                    sleep(0.5)
                    break
        except:
            pass
        
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        
        listComments = soup.find('ol', {'id' : 'wallpost-list'}).find_all('li', {'class' : 'item'})
        
        counter = 0
        returnedList = []
        for comment in listComments:
            if counter < discards:
                counter += 1
                continue
            returnedList.append(comment.get_text(separator=' '))
        
        return returnedList
