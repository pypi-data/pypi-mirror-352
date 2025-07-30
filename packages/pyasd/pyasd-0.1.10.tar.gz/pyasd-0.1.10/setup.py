#!/usr/bin/env python

#=========================================================
#
# This script is part of the pyasd package
# Copyright @ Shunhong Zhang 2022 - 2025
#
# Redistribution and use in source and binary forms, 
# with or without modification, are permitted provided 
# that the MIT license is consented and obeyed
# A copy of the license is available in the home directory
#
#=========================================================



#===========================================================================
#                                                                           
#  File:       setup.py                                                     
#  Usage:      pip install . --user 
#  or          python setup.py install --user
#
#  Author:     Shunhong Zhang                                               
#  Email:      zhangshunhong.pku@gmail.com
#  Date:       Jun 04, 2023                                                 
#                                                                           
#===========================================================================


import sys
import glob
import setuptools


def set_build_time_stamp(kwargs_setup, home_dir='asd'):
    import time, locale
    platform = sys.platform

    with open('{}/__init__.py'.format(home_dir),'r') as fw: lines = fw.readlines()
    __doc__ = '{:<20s}  =  "built at {}'.format('__built_time__',time.ctime())
    if locale.getdefaultlocale()[0]=='en_US': __doc__ += '_{}"\n'.format(time.tzname[1])
    else: __doc__ += '"\n'
    lines = [__doc__] + [line for line in lines if '__built_time__' not in line]
    keys = ['__name__','__version__','__author__','__author_email__','__url__','__license__','__platform__']
         
    with open('{}/__init__.py'.format(home_dir),'w') as fw: 
        fw.write(__doc__)
        for key in keys:
            fw.write('{:<20s}  =  "{}"\n'.format(key,kwargs_setup[key.strip('__')]))
 


home_dir = 'asd'

database_modules = [item.removesuffix('.py') for item in glob.glob('{}/data_base/*py'.format(home_dir))]
core_modules     = [item.removesuffix(".py") for item in glob.glob('{}/core/*py'.format(home_dir))     ]
util_modules     = [item.removesuffix(".py") for item in glob.glob('{}/utility/*py'.format(home_dir))  ]
mpi_modules      = [item.removesuffix('.py') for item in glob.glob('{}/mpi/*py'.format(home_dir))      ]
init_files = ['{}/__init__'.format(home_dir)]



kwargs_setup = dict(
name='pyasd',
version='0.1.10',
author='Shunhong Zhang',
author_email='zhangshunhong.pku@gmail.com',
platform=sys.platform,
url='https://pypi.org/project/pyasd/',
download_url='https://pypi.org/project/pyasd/',
keywords='spin dynamics simulation',
py_modules = core_modules + util_modules + database_modules + mpi_modules + init_files,
packages = setuptools.find_packages(),
license='MIT LICENSE',
license_file='LICENSE',
description='A python-based spin dynamics simulator',
long_description='LLG/Monte Carlo/GNEB simulators for classical spin systems',
platforms=[sys.platform],
classifiers=[
'Programming Language :: Python :: 3',],
)

      
if __name__=='__main__':
    set_build_time_stamp(kwargs_setup)
    setuptools.setup(**kwargs_setup)
