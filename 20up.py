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

Program for the backup of Tuenti, a Spanish social network.
This program downloads all of the photos, comments, private messages and
friends' information of a specific user.
"""

import math, os, httplib, requests, string, sys
import re, getpass, urllib2, hashlib, unicodedata
from time import sleep

from APtuentI import APtuentI
from MyHTMLParser import MyHTMLParser

version = '1.2'
web = 'http://bmenendez.github.io/20up'
twitter = '@borjamonserrano'
email = 'tuentiup@gmail.com'
appkey = 'MDI3MDFmZjU4MGExNWM0YmEyYjA5MzRkODlmMjg0MTU6MC4xMzk0ODYwMCAxMjYxMDYwNjk2'

statusText = 'Utilizando 20p para descargarme todas '
statusText += 'mis fotos de Tuenti :) ' + web

WINDOWS = 'nt'

def printWelcome():
    os.system('cls' if os.name == WINDOWS else 'clear')
    print '-' * 60
    print '| 20up version ' + version
    print '|'
    print '| Gracias por descargar esta aplicacion'
    print '| Espero que te sea de gran utilidad :)'
    print '| Si tienes alguna duda, tienes toda la info en:'
    print '|'
    print '|           ' + web
    print '|'
    print '| Tambien puedes resolver tus dudas en twitter: ' + twitter
    print '| Asi como por e-mail a traves de: ' + email
    print '-' * 60
    
def printGoodBye():
    os.system('cls' if os.name == WINDOWS else 'clear')
    print '-' * 60
    print '| 20up version ' + version
    print '| Gracias por haber utilizado 20up ' + version
    print '| Espero que te haya sido de gran utilidad :)'
    print '| Si tienes alguna duda, tienes toda la info en:'
    print '|'
    print '|           ' + web
    print '|'
    print '| Tambien puedes resolver tus dudas en twitter: ' + twitter
    print '| Asi como por e-mail a traves de: ' + email
    print '|'
    print '| Si quieres, puedo cambiar tu estado Tuenti para advertir que'
    print '| has utilizado 20up y que tus contactos conozcan la aplicacion.'
    print '| El mensaje que se pondra sera: ' + statusText
    print '| 1 - Si'
    print '| Otro - No'
    print '-' * 60
    
def printMenu():
    os.system('cls' if os.name == WINDOWS else 'clear')
    print '-' * 60
    print '| 20up version ' + version
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
    os.system('cls' if os.name == WINDOWS else 'clear')
    print '-' * 60
    print '| 20up version ' + version
    print '|'
    print '| Comenzando el backup de ' + text + '...'
    print '-' * 60
    
def printEnding(text):
    os.system('cls' if os.name == WINDOWS else 'clear')
    print '-' * 60
    print '| 20up version ' + version
    print '|'
    print '| Terminado el backup de ' + text + '...'
    raw_input('| Pulsa ENTER para continuar')
    print '-' * 60
    
def printHelp():
    os.system('cls' if os.name == WINDOWS else 'clear')
    print '-' * 60
    print '| 20up version ' + version
    print '|'
    print '| 20up es una aplicacion para hacer un backup de tu Tuenti.'
    print '| 20up no se responsabiliza de los usos derivados que se le'
    print '| puedan dar a esta aplicacion.'
    print '| 20up tiene como proposito poder realizar un backup de tu'
    print '| cuenta de usuario de Tuenti, de forma que tendras todas tus'
    print '| fotos, mensajes privados, comentarios de tablon y datos de tus'
    print '| contactos en tu ordenador.'
    print '| 20up no almacena ni envia tu correo o contrasenya a terceras'
    print '| personas o cuentas de Tuenti.'
    print '| Por favor, si tienes alguna duda, visita la web:'
    print '|'
    print '|           ' + web
    print '|'
    print '| Tambien puedes resolver tus dudas en twitter: ' + twitter
    print '| Asi como por e-mail a traves de: ' + email
    print '-' * 60

def winGetpass(prompt='Password: ', stream=None):
    """Prompt for password with echo off, using Windows getch()."""
    if sys.stdin is not sys.__stdin__:
        return fallback_getpass(prompt, stream)
    
    import msvcrt
    for c in prompt:
        msvcrt.putch(c)
    
    pw = ""
    while 1:
        c = msvcrt.getch()
        if c == '\r' or c == '\n':
            break
        if c == '\003':
            raise KeyboardInterrupt
        if c == '\b':
            if pw == '':
                pass
            else:
                pw = pw[:-1]
                msvcrt.putch('\b')
                msvcrt.putch(" ")
                msvcrt.putch('\b')
        else:
            pw = pw + c
            msvcrt.putch("*")
    msvcrt.putch('\r')
    msvcrt.putch('\n')
    
    return pw
    
def getData(withError):
    os.system('cls' if os.name == WINDOWS else 'clear')
    print '-' * 60
    if withError:
        print '| Parece que no has introducido bien tus datos'
        print '| Por favor, escribe de nuevo...'
    else:
        print '| Para poder hacer el backup necesito un poco mas'
        print '| de informacion sobre tu cuenta de Tuenti...'
        print '|'
        print '| Esta informacion no se almacenara en ningun sitio'
        print '| ni se enviara a ningun lado, solamente se requiere'
        print '| para la conexion con tu cuenta de Tuenti :)'
    print
    email = raw_input('E-mail: ')
    while not re.match(r'[^@]+@[^@]+\.[^@]+', email):
        email = raw_input('El e-mail no es valido, intenta de nuevo: ')
    if os.name == WINDOWS:
        password = winGetpass()
    else:
        password = getpass.getpass()
    print '-' * 60
    
    return email, password
    
def backupTotal(myTuenti, email, password):
    backupPrivateMessages(myTuenti, email, password)
    backupComments(myTuenti)
    backupUsers(myTuenti)
    backupPhotos(myTuenti)
    
def backupPhotos(myTuenti):
    printStarting('fotos')
    
    print '| Obteniendo los nombres de tus albumes...'
    dicPhotos = {}
    i = 0
    totalPhotos = 0
    while True:
        albums = myTuenti.getUserAlbums(i)
        counter = 0
        for album in albums[0]:
            counter += 1
            dicPhotos[album] = [albums[0][album]['name'], albums[0][album]['size']]
            totalPhotos += int(albums[0][album]['size'])
            
        if counter < 20:
            break
           
        sleep(0.5) 
        i += 1
    print '| Nombre de los albumes obtenido'
        
    rootPath = os.getcwdu()
    theJoinPath = os.path.join(rootPath, 'fotos')
    if not os.path.exists(theJoinPath):
        print '| Creando directorio donde se alojaran las fotos...'
        os.makedirs(theJoinPath)
        print '| Directorio creado'
    
    s = requests.Session()
    
    totalCounter = 0
    for album in dicPhotos:
        albumName = unicodedata.normalize('NFKD', dicPhotos[album][0])
        albumName = re.sub('[^a-zA-Z0-9\n\.]', '-', albumName)
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
        iters = myCounter / 20.0
        if math.fmod(iters, 1) != 0.0:
            iters += 1
        iters = int(iters)
        totalPhotosAlbum = myCounter
        
        print '|'
        print '| Descargando fotos del album ' + albumName + '...'
        print '|'
        
        partialCounter = 0
        for i in range(0, iters):
            mf = myTuenti.getAlbumPhotos(album, i)
            for elem in mf[0]['album']:
                url = elem['photo_url_600']
                title = unicodedata.normalize('NFKD', elem['title']) 
                title = re.sub('[^a-zA-Z0-9\n\.]', '-', title)
                partialCounter += 1
                totalCounter += 1
                
                fileName = string.zfill(myCounter, maxFill) + '_' + title + '.jpg'
                if not os.path.exists(fileName):
                    partialPerc = 100 * partialCounter / totalPhotosAlbum
                    totalPerc = 100 * totalCounter / totalPhotos
                    percs = '[' + str(totalPerc) + '% total] ['
                    percs += str(partialPerc) + '% album] '
                    print '| ' + percs + 'Descargando foto ' + title + '...'
                    while not os.path.exists(fileName):
                        with open(fileName, 'wb') as handle:
                            r = s.get(url, verify=False)
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
    print '| (esto llevara algun tiempo)'
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
        
        sleep(0.5)
    
    s = requests.Session()
    r = s.get('https://m.tuenti.com/?m=Login', verify=False)
    csrf = re.findall('name="csrf" value="(.*?)"', r.text)[0]

    data = { 'csrf': csrf, 'tuentiemailaddress': email, 'password': password, 'remember': 1 }
    s.post('https://m.tuenti.com/?m=Login&f=process_login', data)
    
    r = s.get("https://m.tuenti.com/?m=Profile&func=my_profile", verify=False)
    if r.text.find('email') != -1:
        print '| E-mail o password incorrectos'
        raw_input('| Pulsa ENTER para continuar')
        return
    
    rootPath = os.getcwdu()
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
        print '| [' + str(percent) + '%] Descargando mensaje ' + \
              str(counter) + ' de ' + str(totalMessages) + '...'
        urlName = 'https://m.tuenti.com/?m=messaging&func=view_thread&thread_id='
        urlName += key + '&box=inbox&view_full=1'
        
        r = s.get(urlName, verify=False)
        
        sleep(0.5)

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
        try:
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
            
            sleep(0.5)    
            i += 1
        except:
            break
    
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
        
        sleep(0.5)
        
    fileToWrite.write(text.encode('utf-8'))
    fileToWrite.close()

def main():
    email, password = getData(False)
    myTuenti = APtuentI()
    while True:
        try:
            login = myTuenti.doLogin()
            passcode = hashlib.md5(login[0]['challenge'] + \
                            hashlib.md5(password).hexdigest()).hexdigest()
            out = myTuenti.getSession(login[0]['timestamp'], \
                                login[0]['seed'], passcode, appkey, email)
            myTuenti.setSessionID(out[0]['session_id'])
            break
        except:
            email, password = getData(True)
            
    respuesta = '0'
    while respuesta != '7':
        printMenu()
        respuesta = raw_input('> ')
        
        if respuesta == '1':
            backupTotal(myTuenti, email, password)
            printEnding('todo')
        elif respuesta == '2':
            backupPhotos(myTuenti)
            printEnding('fotos')
        elif respuesta == '3':
            backupPrivateMessages(myTuenti, email, password)
            printEnding('mensajes privados')
        elif respuesta == '4':
            backupComments(myTuenti)
            printEnding('comentarios')
        elif respuesta == '5':
            backupUsers(myTuenti)
            printEnding('usuarios')
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
        myTuenti.setUserStatus(statusText)
        
    print '| Hasta pronto :)'

if __name__ == '__main__':
    printWelcome()
    raw_input('| Pulsa ENTER para continuar')
    while True:
        try:
            main()
            break
        except urllib2.URLError:
            print '|'
            print '| No hay conexion a internet'
            print '|'
            break
        except KeyboardInterrupt:
            print
            print '|'
            print '| Cerrando aplicacion...'
            print '|'
            break
        except Exception, e:
            print '|'
            print '| Ha ocurrido un error inesperado:', e
            print '|'
            raw_input('| Pulsa ENTER para continuar')
