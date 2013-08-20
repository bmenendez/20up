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
@version: 0.5 beta

Program for the backup of Tuenti, a Spanish social network.
This program downloads all of the photos, comments, private messages and
friends' information of a specific user.
"""

import sys
from distutils.core import setup

kwargs = {}
if 'py2exe' in sys.argv:
    import py2exe
    kwargs = {
        'console' : [{
            'script'         : 'tuentiUp.py',
            'description'    : 'Programa para hacer un backup de tu Tuenti.'
            }],
        'zipfile' : None,
        'options' : { 'py2exe' : {
            'dll_excludes'   : ['w9xpopen.exe'],
            'bundle_files'   : 1,
            'compressed'     : True,
            'optimize'       : 2
            }},
         }

setup(
    name='tuentiUp',
    author='@borjamonserrano',
    author_email='borjamonserrano@gmail.com',
    **kwargs)
