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

import os, requests, re, getpass, sys
import httplib, urllib2
from time import sleep

PATH = os.getcwdu()
BASEURI = "https://m.tuenti.com/"
dirs = ['tagged', 'uploaded']

version = '2.0'
web = 'http://bmenendez.github.io/20up'
twitter = '@borjamonserrano'
email = 'tuentiup@gmail.com'

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
    print '-' * 60
    
def printStarting(text):
    os.system('cls' if os.name == WINDOWS else 'clear')
    print '-' * 60
    print '| 20up version ' + version
    print '|'
    print '| Comenzando el backup de ' + text + '...'
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
    
def getData():
    os.system('cls' if os.name == WINDOWS else 'clear')
    print '-' * 60
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
    
def backupPhotos(email, password):
    printStarting('fotos')
    
    s = requests.Session()

    r = s.get(BASEURI + "?m=Login", verify=False)
    csrf = re.findall('name="csrf" value="(.*?)"', r.text)[0]
    data = {
        "csrf": csrf,
        "tuentiemailaddress": email,
        "password": password,
        "remember": 1}
    r = s.post(BASEURI + "?m=Login&f=process_login", data)

    if 'tuentiemail' in r.cookies:
        return False

    for i in range(1, 3):
        r = s.get(BASEURI + "?m=Profile&func=my_profile", verify=False)
        print '| Descargando fotos ' + dirs[i - 1] + '...'
        album = BASEURI + "?m=Albums&func=index&collection_key=%i-" % i + \
            re.findall('key=%i-(.*?)&' % i, r.text)[0]

        r = s.get(album, verify=False)
        firstPic = BASEURI + "?m=Photos&func=view_album_photo&collection_key=%i-" % i + \
            re.findall('key=%i-(.*?)&' % i, r.text)[0]

        r = s.get(firstPic, verify=False)
        picQuantity = int(
            re.findall('[of|de|\/|sur|di|van|z]\s(\d+)\)', r.text)[0])
            
        photoDownloadUrl = re.findall('img\ssrc="(.*?)"', r.text)[0]
        if picQuantity > 1:
            nextPhotoUrl = re.findall(
                '\)\s\<a href="(.*?)"',
                r.text)[0].replace("&amp;",
                                   "&")  # not loading a whole lib for one single entity
        else:
            nextPhotoUrl = None

        for x in range(1, picQuantity + 1):
            if x != 1:
                r = s.get(
                    nextPhotoUrl,
                    cookies={"screen": "1920-1080-1920-1040-1-20.74"}, verify=False)
                photoDownloadUrl = re.findall('img\ssrc="(.*?)"', r.text)[0]
                if x != picQuantity:
                    nextPhotoUrl = re.findall(
                        '\)\s\<a href="(.*?)"',
                        r.text)[0].replace("&amp;", "&")
                        
            albumPath = os.path.join(PATH, dirs[i - 1])
            
            if not os.path.exists(albumPath):
                os.makedirs(albumPath)
                print "| Creado el directorio %s" % dirs[i - 1]
            
            filename = os.path.join(albumPath, str(x) + '.jpg')
            if not os.path.exists(filename):
                with open(filename, "wb") as handle:
                    r = s.get(photoDownloadUrl, verify=False)

                    for block in r.iter_content(1024):
                        if not block:
                            break

                        handle.write(block)

                percent = (x * 100) / picQuantity
                print '| %s.jpg descargada (%i%%)... (album %i/2)' % (x, percent, i)
                sleep(0.5)  # avoid flooding

    return True

def main():
    done = False
    while not done:
        email, password = getData()
        done = backupPhotos(email, password)
        if not done:
            print
            print '| Ha habido algun error'
            print '| Es posible que el usuario y/o la password sean incorrectos'
            raw_input('| Pulsa ENTER para continuar')
    
    printGoodBye()
        
    print '| Hasta pronto :)'

if __name__ == '__main__':
    printWelcome()
    raw_input('| Pulsa ENTER para continuar')
    while True:
        try:
            main()
            raw_input()
            break
        except KeyboardInterrupt:
            print
            print '|'
            print '| Cerrando aplicacion...'
            print '|'
            raw_input()
            break
        except Exception, e:
            print '|'
            print '| Ha ocurrido un error inesperado:', e
            print '|'
            raw_input('| Pulsa ENTER para continuar')
