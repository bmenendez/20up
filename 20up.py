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

Authors: Borja Menéndez Moreno <tuentiup@gmail.com>

Program for the backup of a Spanish social network.
This program downloads all of the photos, comments, and
friends' information of an specific user.
"""

import os, sys, getpass, traceback
from tntwrapper import *

version = '3.1.4'
web = 'http://bmenendez.github.io/20up'
twitter = '@bmenendez_'
email = 'tuentiup@gmail.com'

WINDOWS = 'nt'

def printWelcome():
    os.system('cls' if os.name == WINDOWS else 'clear')
    print '-' * 60
    print '| 20up version ' + version
    print '|'
    print '| 20up es software libre, liberado bajo licencia GPLv3'
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
    print '|'
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
    print '| de informacion sobre tu cuenta...'
    print '|'
    print '| Esta informacion no se almacenara en ningun sitio'
    print '| ni se enviara a ningun lado, solamente se requiere'
    print '| para la conexion con tu cuenta :)'
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
    print '| 20up es una aplicacion para hacer backup de tu red social favorita.'
    print '| 20up no se responsabiliza de los usos derivados que se le'
    print '| puedan dar a esta aplicacion.'
    print '| 20up tiene como proposito poder realizar un backup de tu'
    print '| cuenta de usuario, de forma que tendras todas tus'
    print '| fotos, sus comentarios, comentarios de tablon y datos de tus'
    print '| contactos en tu ordenador.'
    print '| 20up no almacena ni envia tu correo o contrasenya a terceras'
    print '| personas o cuentas de la red social.'
    print '| 20up es software libre, liberado bajo licencia GPLv3.'
    print '| Por favor, si tienes alguna duda, visita la web:'
    print '|'
    print '|           ' + web
    print '|'
    print '| Tambien puedes resolver tus dudas en twitter: ' + twitter
    print '| Asi como por e-mail a traves de: ' + email
    print '-' * 60

def printMenu():
    os.system('cls' if os.name == WINDOWS else 'clear')
    print '-' * 60
    print '| 20up version ' + version
    print '|'
    print '| Pulsa un numero en funcion de lo que quieras hacer:'
    print '| 1 - Backup total (fotos, comentarios de fotos y tablon)'
    print '| 2 - Backup de fotos'
    print '| 3 - Backup de fotos y sus comentarios'
    print '| 4 - Backup de tablon'
    print '| 5 - Backup de amigos'
    print '| 6 - Ayuda'
    print '| 7 - Salir'
    print '-' * 60

def main():
    email, password = getData()
    try:
        wrap = Wrapper(email, password, True)

        respuesta = '0'
        while respuesta != '7':
            printMenu()
            respuesta = raw_input('> ')

            if respuesta == '1':
                printStarting('todo')
                wrap.downloadAllPictures(True)
                wrap.downloadAllComments()
                wrap.downloadFriends()
                printEnding('todo')
            elif respuesta == '2':
                printStarting('fotos sin comentarios')
                wrap.downloadAllPictures(False)
                printEnding('fotos')
            elif respuesta == '3':
                printStarting('fotos con comentarios')
                wrap.downloadAllPictures(True)
                printEnding('fotos y sus comentarios')
            elif respuesta == '4':
                printStarting('tablon')
                wrap.downloadAllComments()
                printEnding('tablon')
            elif respuesta == '5':
                printStarting('amigos')
                wrap.downloadFriends()
                printEnding('amigos')
            elif respuesta == '6':
                printHelp()
                raw_input('> Presiona ENTER para continuar')
            elif respuesta == '7':
                pass
            else:
                print 'No has elegido una opcion valida'

        printGoodBye()

        print '| Hasta pronto :)'
    except RuntimeError, e:
        print e

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
            print '-' * 60
            print '|'
            tb_lines = traceback.format_exc().splitlines()
            for line in tb_lines:
                print '| ' + line
            print '|'
            print '-' * 60
            print '|'
            print '| Ha ocurrido un error inesperado:', e
            print '|'
            raw_input('| Pulsa ENTER para continuar')
