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
@version: 0.1 beta

Program for the backup of Tuenti, a Spanish social network.
This program downloads all of the photos, comments, private messages and
friends' information of a specific user.
"""

import math, os, httplib, requests, string
import re, getpass
from time import sleep

from APtuentI import APtuentI
from MyHTMLParser import MyHTMLParser

version = '0.1 beta'
web = 'http://bmenendez.github.io/tuentiUp'
twitter = '@borjamonserrano'

def printWelcome():
    os.system('cls' if os.name=='nt' else 'clear')
    print '-' * 60
    print '| TuentiUp version ' + version
    print '|'
    print '| Gracias por descargar esta aplicacion'
    print '| Espero que te sea de gran utilidad :)'
    print '| Si tienes alguna duda, tienes toda la info en:'
    print '|'
    print '|           ' + web
    print '|'
    print '| Tambien puedes seguirme en twitter: ' + twitter
    print '-' * 60
    
def printGoodBye():
    os.system('cls' if os.name == 'nt' else 'clear')
    print '-' * 60
    print '| TuentiUp version ' + version
    print '| Gracias por haber utilizado TuentUp ' + version
    print '| Espero que te haya sido de gran utilidad :)'
    print '| Si tienes alguna duda, tienes toda la info en:'
    print '|'
    print '|           ' + web
    print '|'
    print '| Tambien puedes seguirme en twitter: ' + twitter
    print '|'
    print '| Si quieres, puedo mandar un mensaje privado a todos tus'
    print '| contactos para que conozcan la aplicacion:'
    print '| 1 - Si'
    print '| Otro - No'
    print '-' * 60
    
def printMenu():
    os.system('cls' if os.name == 'nt' else 'clear')
    print '-' * 60
    print '| TuentiUp version ' + version
    print '|'
    print '| Pulsa un numero en funcion de lo que quieras hacer:'
    print '| 1 - Backup total (fotos, privados, comentarios y usuarios)'
    print '| 2 - Backup de fotos'
    print '| 3 - Backup de privados'
    print '| 4 - Backup de comentarios'
    print '| 5 - Backup de usuarios'
    print '| 6 - Ayuda'
    print '| 7 - Salir'
    print '-' * 60
    
def printStarting(text):
    os.system('cls' if os.name=='nt' else 'clear')
    print '-' * 60
    print '| TuentiUp version ' + version
    print '|'
    print '| Comenzando el backup de ' + text + '...'
    print '-' * 60
    
def printHelp():
    os.system('cls' if os.name == 'nt' else 'clear')
    print '-' * 60
    print '| TuentiUp version ' + version
    print '|'
    print '| TuentiUp es una aplicacion para hacer un backup de tu Tuenti.'
    print '| TuentiUp no se responsabiliza de los usos derivados que se le'
    print '| puedan dar a esta aplicacion.'
    print '| TuentiUp tiene como proposito poder realizar un backup de tu'
    print '| cuenta de usuario de Tuenti, de forma que tendras todas tus'
    print '| fotos, mensajes privados, comentarios de tablon y datos de tus'
    print '| contactos en tu ordenador.'
    print '| Por favor, si tienes alguna duda, visita la web:'
    print '|'
    print '|           ' + web
    print '|'
    print '| Tambien puedes seguirme en twitter: ' + twitter
    print '-' * 60
    
def getCookie(witherror):
    print '-' * 60
    if witherror:
        print '| La cookie que has introducido no es valida'
        print '| Asegurate de que la cookie es nueva (inicia sesion en Tuenti)'
    else:
        print '| Primero de todo, necesito un dato para poder hacer'
        print '| la mayoria del backup...'
    print '-' * 60

    cookie = raw_input('Cookie: ')
    
    return cookie
    
def getData():
    print '-' * 60
    print '| Para poder hacer un backup de los privados'
    print '| necesito un poco mas de informacion sobre ti...'
    print
    email = raw_input('E-mail: ')
    while not re.match(r'[^@]+@[^@]+\.[^@]+', email):
        email = raw_input('El e-mail no es correcto, intenta de nuevo: ')
    password = getpass.getpass()
    print '-' * 60
    
    return email, password
    
def backupTotal(myTuenti):
    email, password = getData()
    backupPhotos(myTuenti)
    backupPrivateMessages(myTuenti, email, password)
    backupComments(myTuenti)
    backupUsers(myTuenti)
    
def backupPhotos(myTuenti):
    printStarting('fotos')
    
    print '| Obteniendo los nombres de tus albumes...'
    dicPhotos = {}
    i = 0
    while True:
        albums = myTuenti.getUserAlbums(i)
        counter = 0
        for album in albums[0]:
            counter += 1
            dicPhotos[album] = [albums[0][album]['name'], albums[0][album]['size']]
            
        if counter < 20:
            break
            
        i += 1
    print '| Nombre de los albumes obtenido'
        
    rootPath = os.getcwd()
    theJoinPath = os.path.join(rootPath, 'fotos')
    if not os.path.exists(theJoinPath):
        print '| Creando directorio donde se alojaran las fotos...'
        os.makedirs(theJoinPath)
        print '| Directorio creado'
    
    s = requests.Session()
    
    for album in dicPhotos:
        albumName = dicPhotos[album][0]
        albumName = albumName.replace('/', '-')
        albumName = albumName.replace('\\', '-')
        size = dicPhotos[album][1]
        
        albumPath = os.path.join(theJoinPath, albumName)
        if not os.path.exists(albumPath):
            print '| Creando directorio donde se alojaran las fotos'
            print '| del album ' + albumName + '...'
            os.makedirs(albumPath)
            print '| Directorio creado'
        os.chdir(albumPath)
        
        myCounter = int(size)
        maxFill = len(str(size))
        iters = size / 20.0
        if math.fmod(iters, 1) != 0.0:
            iters += 1
        iters = int(iters)
        
        print '|'
        print '| Descargando fotos del album ' + albumName + '...'
        print '|'
        
        for i in range(0, iters):
            mf = myTuenti.getAlbumPhotos(album, i)
            for elem in mf[0]['album']:
                url = elem['photo_url_600']
                title = elem['title']
                title = title.replace(' ', '_')
                title = title.replace('/', '_')
                title = title.replace('>', '_')
                
                fileName = string.zfill(myCounter, maxFill) + '_' + title + '.jpg'
                if not os.path.exists(fileName):
                    print '| Descargando foto ' + title + '...'
                    with open(fileName, 'wb') as handle:
                        r = s.get(url)
                        for block in r.iter_content(1024):
                            if not block:
                                break
                            handle.write(block)
                        
                    sleep(0.5)
                    
                myCounter -= 1

        os.chdir(theJoinPath)
        
    os.chdir(rootPath)
    
def backupPrivateMessages(myTuenti, email, password):
    printStarting('mensajes privados')
    
    print '| Obteniendo identificadores de tus mensajes privados'
    messages = myTuenti.getInbox(0)
    totalMessages = int(messages[0]['num_threads'])
    keys = []
    
    maxFill = len(str(totalMessages))
    iters = totalMessages / 10.0
    if math.fmod(iters, 1) != 0.0:
        iters += 1
    iters = int(iters)
    
    for i in range(0, iters):
        messages = myTuenti.getInbox(i)
        for message in messages[0]['threads']:
            keys.append(message['key'])
    
    s = requests.Session()
    r = s.get('https://m.tuenti.com/?m=Login')
    csrf = re.findall('name="csrf" value="(.*?)"', r.text)[0]

    data = { 'csrf': csrf, 'tuentiemailaddress': email, 'password': password, 'remember': 1 }
    s.post('https://m.tuenti.com/?m=Login&f=process_login', data)
    
    r = s.get("https://m.tuenti.com/?m=Profile&func=my_profile")
    if r.text.find('email') != -1:
        print '| E-mail o password incorrectos'
        raw_input('| Pulsa ENTER para continuar')
        return
    
    rootPath = os.getcwd()
    theJoinPath = os.path.join(rootPath, 'privados')
    if not os.path.exists(theJoinPath):
        print '| Creando directorio donde se alojaran los mensajes privados...'
        os.makedirs(theJoinPath)
        print '| Directorio creado'
    os.chdir(theJoinPath)
    
    counter = 0
    parser = MyHTMLParser()
    for key in keys:
        counter += 1
        percent = 100 * counter / totalMessages
        print '| Descargando mensaje ' + str(counter) + ' de ' + \
              str(totalMessages) + ' [' + str(percent) + '%]' + '...'
        urlName = 'https://m.tuenti.com/?m=messaging&func=view_thread&thread_id='
        urlName += key + '&box=inbox&view_full=1'
        
        r = s.get(urlName)

        parser.setFile(string.zfill(counter, maxFill))
        parser.feed(r.text)
        
    os.chdir(rootPath)
    
def backupComments(myTuenti):
    printStarting('comentarios')
    
    i = 0
    counter = 0
    totalCount = 0
    fileToWrite = open('comentarios.txt', 'w')
    while True:
        mes = myTuenti.getWall(i)
        counter = 0
        for post in mes[0]['posts']:
            totalCount += 1
            print '| Descargando comentario ' + str(totalCount) + '...'
            text = '*' * 60
            text += '\r\n'
            counter += 1
            for anElem in post['body']:
                text += post['author']['name'] + ' '
                text += post['author']['surname'] + ': '
                text += anElem['plain']
                text += '\r\n'
            try:
                if post['parent']['body']:
                    text += '-' * 20
                    text += '\r\n'
                for elem in post['parent']['body']:
                    text += elem['plain']
                    text += '\r\n'
                counter += 1
            except:
                pass
                
            fileToWrite.write(text.encode('utf-8'))
        
        if counter == 0:
            break;
                
        i += 1
    
    fileToWrite.close()
    
def backupUsers(myTuenti):
    printStarting('usuarios')
    
    print '| Obteniendo todos tus contactos'
    totalFriends = myTuenti.getFriendsData()
    
    fileToWrite = open('usuarios.txt', 'w')
    text = ''
    
    for friend in totalFriends[0]['friends']:
        name = friend['name']
        surname = friend['surname']
        text += name + ' ' + surname
        print '| Obteniendo datos de ' + name + ' ' + surname + '...'
        friendId = friend['id']
        
        data = myTuenti.getUsersData(friendId)
        if data[0]['users'][0]['birthday']:
            text += ' (' + data[0]['users'][0]['birthday'] + ')'
        if data[0]['users'][0]['phone_number']:
            text += ': ' + data[0]['users'][0]['phone_number']
        
        text += '\r\n'
        
    fileToWrite.write(text.encode('utf-8'))
    fileToWrite.close()
    
def sendPrivateMessageToFriends(myTuenti):
    print 'enviando un privado a todos tus contactos'

def main(cookie):
    while True:
        myTuenti = APtuentI(cookie)
        try:
            myTuenti.getFriendsData()[0]['error']
            cookie = getCookie(True)
        except KeyError:
            break
            
    respuesta = '0'
    while respuesta != '7':
        printMenu()
        respuesta = raw_input('> ')
        
        if respuesta == '1':
            backupTotal(myTuenti)
        elif respuesta == '2':
            backupPhotos(myTuenti)
        elif respuesta == '3':
            email, password = getData()
            backupPrivateMessages(myTuenti, email, password)
        elif respuesta == '4':
            backupComments(myTuenti)
        elif respuesta == '5':
            backupUsers(myTuenti)
        elif respuesta == '6':
            printHelp()
            raw_input('> Presiona ENTER para continuar')
        elif respuesta == '7':
            pass
        else:
            print 'No has elegido una opcion valida'
            
    printGoodBye()
    respuesta = raw_input('> ')
    
    if respuesta == '1':
        sendPrivateMessageToFriends(myTuenti)

if __name__ == '__main__':
    printWelcome()
    main(getCookie(False))
