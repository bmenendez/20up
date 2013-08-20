#! /usr/bin/python
# -*- coding: iso-8859-15 -*-

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

@author: Borja Menéndez Moreno
@copyright: Borja Menéndez Moreno (Madrid, Spain)
@license: GNU GPL version 3 or any later version
@version: 0.3 beta

Program for the backup of Tuenti, a Spanish social network.
This program downloads all of the photos, comments, private messages and
friends' information of a specific user.
"""

from HTMLParser import HTMLParser
from htmlentitydefs import name2codepoint

class MyHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.fileToWrite = ''
        self.writeData = False
        self.writeUser = False
        
    def setFile(self, fileName):
        self.fileToWrite = open(fileName + '.txt', 'w')
        
    def handle_starttag(self, tag, attrs):
        if tag == 'small':
            self.writeData = True
            self.writeUser = False
        for attr in attrs:
            if attr[1].encode('utf-8').find('user_id') != -1:
                self.writeData = False
                self.writeUser = True
            elif attr[1].encode('utf-8').find('box') != -1:
                self.writeData = False
                self.writeUser = False
            elif attr[1].encode('utf-8') == 'time':
                self.writeData = True
                self.writeUser = False

    def handle_endtag(self, tag):
        if tag == 'small':
            self.writeData = False
            self.writeUser = False
        elif tag == 'div':
            self.writeData = False
            self.writeUser = False
        elif tag == 'a':
            self.writedata = False
            self.writeUser = False
        elif tag == 'html':
            self.fileToWrite.close()

    def handle_data(self, data):
        if self.writeData:
            self.fileToWrite.write(data.encode('utf-8') + '\r\n')
        elif self.writeUser:
            self.fileToWrite.write('----------------------------------------\r\n')
            self.fileToWrite.write(data.encode('utf-8') + ':\r\n')
