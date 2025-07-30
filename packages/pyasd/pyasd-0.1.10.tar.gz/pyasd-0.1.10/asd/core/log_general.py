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




import os
import copy

class log_general(object):
    def __init__(self,
        outdir='.',
        prefix='',
        subfix='',
        
        n_log_conf=100,
        n_log_magn=100,
        n_log_ener=100,

        log_initial_conf = True,
        log_final_conf = True,
        log_topo_chg = False,
        log_force = False,
        log_ham = True,
        log_conf = True,
        single_ovf = True,
        
        log_conf_file = 'spin_confs.ovf',
        log_ener_file = 'ener.dat',
        log_dist_file = 'dist.dat',
        log_ham_file  = 'Hamiltonian.dat',
        log_Q_file    = 'topo_chg.dat',
        log_file      = None,
        archive_file = 'M.dat',

        tri_simplices = None,
        remove_existing_outdir = False,
        verbosity = 2,
        ):

        self._log_initial_conf = log_initial_conf
        self._log_final_conf   = log_final_conf
        self._log_topo_chg     = log_topo_chg
        self._log_force        = log_force
        self._log_ham          = log_ham
        self._log_conf         = log_conf
        self._single_ovf       = single_ovf

        if outdir=='.' or outdir=='./': outdir = os.getcwd()
        if prefix != '': prefix = '{}_'.format(prefix)
        if subfix != '': subfix = '_{}'.format(subfix)
        self._outdir=outdir

        if n_log_ener != n_log_magn:
            n_log_ener = n_log_magn = min(n_log_ener, n_log_magn)
 
        self._prefix = prefix
        self._n_log_configuration = n_log_conf
        self._n_log_magnetization = n_log_magn
        self._n_log_energy        = n_log_ener
        self._tri_simplices = tri_simplices
        init_conf_file  = 'initial_{}'.format(log_conf_file)
        final_conf_file = 'final_{}'.format(log_conf_file)
        self._log_conf_file   = log_conf_file
        self._init_conf_file  = init_conf_file
        self._final_conf_file = final_conf_file
        self._log_ener_file = log_ener_file
        self._log_dist_file = log_dist_file
        self._log_ham_file  = log_ham_file
        self._log_Q_file    = log_Q_file
        self._archive_file = archive_file
        if log_file is not None: self._log_file = '{}/{}{}'.format(outdir,prefix,log_file)
        else: self._log_file = log_file
        self.set_logging_files(self._outdir)
        self.set_outdir(outdir)
        self._remove_existing_outdir = remove_existing_outdir
        self.set_verbosity( verbosity )
        
    #def __deepcopy__(self,memo):
    #    print('__deepcopy__({})'.format(memo))
    #    return log_general(copy.deepcopy(memo))


    def set_verbosity(self,verbosity):
        err = 'log_general: You try to set verbosity = {}, it should be an non-negative integer!'.format(verbosity)
        assert type(verbosity)==int and verbosity>=0, err
        self._verbosity = verbosity


    def add_attr(self,key,value):
        self.__dict__.setdefault(key,value)


    def set_logging_files(self,outdir):
        self._log_conf_file   = '{}/{}{}'.format(outdir,self._prefix,self._log_conf_file)
        self._init_conf_file  = '{}/{}{}'.format(outdir,self._prefix,self._init_conf_file)
        self._final_conf_file = '{}/{}{}'.format(outdir,self._prefix,self._final_conf_file)
        self._log_ener_file = '{}/{}{}'.format(outdir,self._prefix,self._log_ener_file)
        self._log_dist_file = '{}/{}{}'.format(outdir,self._prefix,self._log_dist_file)
        self._log_ham_file  = '{}/{}{}'.format(outdir,self._prefix,self._log_ham_file)
        self._log_Q_file    = '{}/{}{}'.format(outdir,self._prefix,self._log_Q_file)
        self._archive_file = '{}/{}{}'.format(outdir,self._prefix,self._archive_file)


    def verbose_logging_info(self,fw=None):
        print ('\n{0}\nLogging setup: Start\n{0}\n'.format('-'*80),file=fw)
        print ('Log data to the directory\n{}\n'.format(self._outdir),file=fw)
        print ('='*80,file=fw)
        print ('{:<30s}  {:>8s}   {:<40s}'.format('Quantity', 'Log freq', 'Saved to file'),file=fw)
        print ('-'*80,file=fw)
        fmt = '{:<30s}  {:8d}   {:<40s}'
        if self._log_initial_conf: 
            print (fmt.format('initial  configuration', 0, self._init_conf_file.split('/')[-1]),file=fw)
        if self._log_final_conf: 
            print (fmt.format('final    configuration', 0, self._final_conf_file.split('/')[-1]),file=fw)
        print (fmt.format('snapshot configurations', self._n_log_configuration, self._log_conf_file.split('/')[-1]),file=fw)
        print (fmt.format('total spin energy', self._n_log_energy, self._archive_file.split('/')[-1]),file=fw)
        print (fmt.format('magnetization', self._n_log_magnetization, self._archive_file.split('/')[-1]),file=fw)
        if self._log_topo_chg:
            print (fmt.format('topological charge', self._n_log_configuration, self._archive_file.split('/')[-1]),file=fw)
            if self._tri_simplices is None: 
                print ('Simplices not provided\nTopological charge won\'t be calculated',file=fw)
        print ('='*80,file=fw)
        print ('\n{0}\nLogging setup:   End\n{0}\n'.format('-'*80),file=fw)


    def set_outdir(self,outdir):
        self._log_conf_file   = self._log_conf_file.replace(self._outdir,outdir)
        self._init_conf_file  = self._init_conf_file.replace(self._outdir,outdir)
        self._final_conf_file = self._final_conf_file.replace(self._outdir,outdir)
        self._log_ener_file   = self._log_ener_file.replace(self._outdir,outdir) 
        self._log_dist_file   = self._log_dist_file.replace(self._outdir,outdir)
        self._log_ham_file    = self._log_ham_file.replace(self._outdir,outdir)
        self._log_Q_file      = self._log_Q_file.replace(self._outdir,outdir)
        self._archive_file    = self._archive_file.replace(self._outdir,outdir)
        if self._log_file is not None: self._log_file = self._log_file.replace(self._outdir,outdir)
        self._outdir = outdir


    def prepare_logging_dir(self):
        if self._outdir not in ['.','./',os.getcwd()]:
            if os.path.isdir(self._outdir) and self._remove_existing_outdir: 
                os.system('rm -r {} 2>/dev/null'.format(self._outdir))
            if not os.path.isdir(self._outdir): os.mkdir(self._outdir)


if __name__=='__main__':
    log_handle = log_general()
    fmt = '{:>25s}  =  {:<20s}'
    for key in log_handle.__dict__.keys():
        value = log_handle.__dict__[key]
        if value is not None: print (fmt.format(key,str(value)))
    log_handle.verbose_logging_info()
