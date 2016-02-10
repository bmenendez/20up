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

Program for the backup of a Spanish social network.
This program downloads all of the photos, comments, and
friends' information of an specific user.
"""

import os, traceback
from tntwrapper import *

version = '4.2'
web = 'http://bmenendez.github.io/20up'
twitter = '@bmenendez_'
email = 'info20up@gmail.com'

BOPTIONS = {
    '1':    'ch',
    '2':    'fi'
}

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
    
def getBrowser():
    os.system('cls' if os.name == WINDOWS else 'clear')
    print '-' * 60
    print '| Que navegador web utilizas habitualmente?'
    print '| 1 - Google Chrome (necesitas ChromeDriver, mira las instrucciones en ' + web + ')'
    print '| 2 - Mozilla Firefox'
    print '-' * 60
    return raw_input('> ')
    
def printErrorBrowser():
    print '|'
    print '| Por favor, elige una opcion valida (numeros del 1 al 5)'
    raw_input('| Pulsa ENTER para continuar')
    
def printErrorLogin():
    print '|'
    print '| Primero debes entrar en la red social'
    raw_input('> Presiona ENTER para continuar')

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
    print '| Ni 20up ni su desarrollador se responsabilizan de los usos'
    print '| derivados que se le puedan dar a esta aplicacion.'
    print '| 20up tiene como proposito poder realizar un backup de tu'
    print '| cuenta de usuario, de forma que tendras todas tus'
    print '| fotos y sus comentarios, y comentarios de tablon.'
    print '| 20up no compromete ni tu seguridad ni tu privacidad.'
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
    print '| 5 - Ayuda'
    print '| 6 - Salir'
    print '-' * 60
    
def printAlert():
    os.system('cls' if os.name == WINDOWS else 'clear')
    print '-' * 60
    print '| 20up version ' + version
    print '|'
    print '| ATENCION: ahora se abrira un navegador web, el que hayas elegido.'
    print '|           1 - NO cierres esta ventana.'
    print '|           2 - NO cierres el navegador.'
    print '|           3 - Entra a la red social desde el navegador como harias'
    print '|               normalmente.'
    print '|           4 - Es altamente recomendable NO usar el navegador'
    print '|               mientras 20up hace su trabajo'
    print '|           5 - Una vez estes dentro de la red, sigue las'
    print '|               instrucciones que te apareceran aqui :-)'
    print '-' * 60

def main():
    browser = getBrowser()
    while browser not in BOPTIONS:
        printErrorBrowser()
        browser = getBrowser()
        
    printAlert()
    print '| Esperando a que entres en la red social...'
    wrap = Wrapper(BOPTIONS[browser], True)
    wrap.waitForLogin()
    raw_input('> Dentro! :D Presiona ENTER para continuar')
    try:
        respuesta = '0'
        while respuesta != '6':
            printMenu()
            respuesta = raw_input('> ')

            if respuesta == '1':
                printStarting('todo')
                ret = wrap.downloadAllPictures(True)
                if ret == -1:
                    printErrorLogin()
                else:
                    wrap.downloadAllComments()
                    printEnding('todo')
            elif respuesta == '2':
                printStarting('fotos sin comentarios')
                ret = wrap.downloadAllPictures(False)
                if ret == -1:
                    printErrorLogin()
                else:
                    printEnding('fotos')
            elif respuesta == '3':
                printStarting('fotos con comentarios')
                ret = wrap.downloadAllPictures(True)
                if ret == -1:
                    printErrorLogin()
                else:
                    printEnding('fotos y sus comentarios')
            elif respuesta == '4':
                printStarting('tablon')
                ret = wrap.downloadAllComments()
                if ret == -1:
                    printErrorLogin()
                else:
                    printEnding('tablon')
            elif respuesta == '5':
                printHelp()
                raw_input('> Presiona ENTER para continuar')
            elif respuesta == '6':
                wrap.goToPrivates()
                print '|'
                print '| Antes de salir, mira el regalito del navegador ;-)'
                print '|'
                raw_input('> Presiona ENTER para continuar')
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
