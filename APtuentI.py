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

Authors: Borja Menéndez Moreno <tuentiup@gmail.com>

Program for the backup of Tuenti, a Spanish social network.
This program downloads all of the photos, comments, private messages and
friends' information of a specific user.
"""

import urllib2, json

class APtuentI:
    """
    The Tuenti API class, called APtuentI.
    
    This class is used for the communication between the program and Tuenti,
    allowing the program to do what it wants to backup a Tuenti account.
    """
    
    def __init__(self):
        self.sid = ''
        self.apiversion = '0.7.1'
        self.api = 'http://api.tuenti.com/api/'
        
    def getResponse(self, data):
        """A method to retrieve a JSON response."""
        request = urllib2.Request(self.api)
        response = urllib2.urlopen(request, json.dumps(data))
        response = json.load(response)
        return response
        
    def setSessionID(self, SID):
        self.sid = SID
        
    def doLogin(self):
        """Do the login in the Tuenti API server"""
        data = {'version':self.apiversion, 'requests':[['getChallenge', \
                {'type':'login'}]]}
        return self.getResponse(data)
        
    def getSession(self, timestamp, seed, passcode, appKey, email):
        """Get the session (the Session ID needed to do everything"""
        data = {'version':self.apiversion, 'requests':[['getSession', \
                {'timestamp':timestamp, 'seed':seed, 'passcode':passcode, \
                'application_key':appKey, 'email':email}]]}
        return self.getResponse(data)
        
    def getUsersData(self, userid):
        """Get the user's data. It returns a JSON response with the
        information."""
        data = {'session_id':self.sid, 'version':self.apiversion, \
                'requests':[['getUsersData', {'ids':[userid], \
                'fields':['name', 'surname', 'phone_number', 'birthday']}]]}
        return self.getResponse(data)
        
    def getFriendsData(self):
        """Get the information about all the user's friends."""
        data = {'session_id':self.sid, 'version':self.apiversion, \
                'requests':[['getFriendsData',{'fields':['name', 'surname', \
                'sex', 'phone_number', 'mvno_subscriber']}]]}
        return self.getResponse(data)
        
    def setUserStatus(self, status):
        """Set the user status."""
        data = {'session_id':self.sid, 'version':self.apiversion, \
                'requests':[['setUserStatus',{'body':status}]]}
        return self.getResponse(data)
        
    def getAlbumPhotos(self, album, page):
        """Get 20 photos of the album specified.""" 
        data = {'session_id':self.sid, 'version':self.apiversion, \
                'requests':[['getAlbumPhotos',{'album_id':album, \
                'page':page, 'photos_per_page':20}]]}
        return self.getResponse(data)
        
    def getUserAlbums(self, page):
        """Get the user's albums."""
        data = {'session_id':self.sid, 'version':self.apiversion, \
                'requests':[['getUserAlbums',{'page':page, \
                'albums_per_page':20}]]}
        return self.getResponse(data)
        
    def sendMessage(self, userid, message):
        """Send a private message to the specified user."""
        data = {'session_id':self.sid, 'version':self.apiversion, \
                'requests':[['sendMessage',{'body':message, \
                'recipient':userid, 'legacy':'false'}]]}
        return self.getResponse(data)
        
    def getInbox(self, page):
        """Get the receive private messages."""
        data = {'session_id':self.sid, 'version':self.apiversion, \
                'requests':[['getInBox',{'page':page}]]}
        return self.getResponse(data)
        
    def getWall(self, page):
        """Get the wall with all the comments."""
        data = {'session_id':self.sid, 'version':self.apiversion, \
                'requests':[['getProfileWall',{'posts_per_page':20, \
                'page':page}]]}
        return self.getResponse(data)
        
    def addPostToProfileWall(self, userid, message):
        """Add a post to the wall's specified user."""
        data = {'session_id':self.sid, 'version':self.apiversion, \
                'requests':[['addPostToProfileWall',{'user_id':userid, \
                'body':message, 'legacy':'false'}]]}
        return self.getResponse(data)
