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


from setup import *

def test_modules(module_list,desc,pkg='asd'):
    import os
    import importlib
    import shutil
    import glob

    cwd=os.getcwd()
    os.chdir(os.path.expanduser('~'))
    print ( '\n{0}\nTEST: {1}\n{0}'.format('='*50,desc))
    print ( '{:40s} {:10s}\n{}'.format('MODULE','STATUS','-'*50))
    for mod in module_list:
        try:
            if sys.platform=='linux': mod = mod.replace('/','.')
            elif sys.platform=='win32': mod = mod.replace('\\','.').replace('/','.')
            if '__pytcache__' in mod: continue
            if '__init__'     in mod: continue
            importlib.import_module(mod)
            print('{0:40s} success'.format(mod))
        except:
            print('{0:40s} failed!'.format(mod))
    print('{0}\n'.format('='*50))
    for item in glob.glob('*pyc'): os.remove(item)
    if os.path.isdir('__pycache__'): shutil.rmtree('__pycache__')
    os.chdir(cwd)
 

def test_mpi():
    try:
        import mpi4py.MPI as MPI
        test_modules(mpi_modules,'mpi modules')
    except:
        print ('Fail to import mpi4py')
        print ('Parallel scripts will be skipped')
        print ('Routine scripts can work')




if __name__=='__main__':
    test_modules(core_modules,     'core modules')
    test_modules(util_modules,     'utility_modules')
    test_modules(database_modules, 'materials database')
    test_modules(mpi_modules,      'mpi modules')
 
