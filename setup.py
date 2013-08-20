# -*- coding: utf-8 -*-

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