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


#=============================================
#
# A simple script for Monte Carlo simulations
# Currently only 2D systems supported
# in serial version
#
# More advanced options under development
#
# Shunhong Zhang
# Mar 21, 2021
#=============================================

import os, sys
import pickle
import numpy as np
from asd.core.shell_exchange import *
from asd.core.log_general import log_general
from asd.core.hamiltonian import spin_hamiltonian, log_spin_hamiltonian
from asd.core.spin_configurations import *
from asd.core.topological_charge import *
from asd.core.random_vectors import *
from asd.utility.ovf_tools import *
from asd.utility.head_figlet import *
from asd.core.constants import muB,kB
from asd.core.shell_exchange import get_dynamics_sites_indices
import time
import copy

fmt_head = '\n{}\n'+'{:>12s} '+'{:>12s} '*9+'\n{}'
head_tags = ('='*130,'MCS','E(mev/site)','time(s)','failure','trial','r_acpt(%)','sigma0','mx','my','mz','-'*130)


def set_verbose_format(ndim, log_handle):
    fmt_step = '# {:10d} {:12.4f} {:12.3f} {:12d} {:12d} {:12.3f} {:12.5f} '+'{:12.6f} '*ndim
    fmt_step_a = '{:12d} {:12.4f} '+'{:12.6f} '*ndim
    fmt_head_a = '{}\n'+'{:>12s} '*(ndim+2)+'\n{}'
    head_tags_a = ['='*13*(ndim+2),'MCS','E(mev/site)'] + ['M_x','M_y','M_z'][:ndim] + ['-'*13*(ndim+2)]
    if log_handle._log_topo_chg and log_handle._tri_simplices is not None: 
        fmt_step_a += '{:12.6f}'
        fmt_head_a = '{}\n'+'{:>12s} '*(ndim+3)+'\n{}'
        head_tags_a = ['='*13*(ndim+3),'MCS','E(mev/site)'] + ['M_x','M_y','M_z'][:ndim] + ['Q','-'*13*(ndim+3)]
    return fmt_step, fmt_step_a, fmt_head_a, head_tags_a


sample_method_note='''
available sample methods
1. random
2. Ising
3. XY
4. Gaussian
5. small_step

For details please refer to
J. Phys. Condens. Matter 
26, 103202 (2014)
31, 095802 (2019)

The adaptive algorithm is formulated
in the latter reference
'''


parallel_advice = '''
{0}\n{1}\n{0}
*  To make the parallelization more efficient    *
*  Try setting as many blocks as possible        *
*  if your memory is sufficiently large          *
*  Based on our preliminary tests,               *
*  setting ncore approx. = sqrt(nblock)          *
*  may give you a high simulation efficiency     *
*  Do more tests before simulating large systems *
{0}\n'''.format('*'*50,'*'+'Advice to parallel users'.center(48)+'*')



log_handle = log_general(
prefix='MCS',
outdir='snapshots',
log_ham_file='Hamiltonian.dat',
)


Note_for_adaptive_Gaussian_sampling = """
Gaussian sampling method is used
The standard deviation of Gaussian distribution function
Sigma0 is set to -1

In the adaptive case it will be adjusted on the fly
acccording to the temperature
sigma0 = 2/25*(kB*T/muB)^(1/5)

For details please refer to Eq. (24) of
J. Phys.: Condens. Matter 26, 103202 (2014)
"""


Alert_for_non_uniform_random_vector = """
This method generates random vectors distributed non-uniformly
On the 2-sphere, which might lead to wrong predictions
Check your results carefully and report them with caution
"""
 
 
def print_MC_setup(temp,mcs,nsites,nblock=1,ncore=1,
    log_handle=log_handle,
    sample_method='Gaussian',sigma0=-1,
    adaptive=True,target_acceptance_ratio=0.5,max_sigma0=60,
    start_conf = 'as_input', rank_group=None, ndim=3):

    if temp!=0: beta = 1/(kB*temp) 
    else: beta = np.inf

    if log_handle._log_file is not None: fw=open(log_handle._log_file,'w')
    else: fw=None
    pkginfo = pkg_info().verbose_info(fw)
    print('\n\n{}'.format('='*60),file=fw)
    print ('{}Monte Carlo simulation\n{}\n'.format(mcs_text,'='*60),file=fw)

    print ("\n{}\nModeling system\n{}\n".format('='*80, '-'*80),file=fw)
    print ('{} spin sites'.format(nsites),file=fw)
    print ('\n{}-component spin vectors simulated'.format(ndim),file=fw)
    if ndim==1: print ('Ising-like spins?',file=fw)
    elif ndim==2: print ('XY-like spins?',file=fw)
    elif ndim==3: print ('Heisenberg-like spins?',file=fw)
    elif ndim>3: print ('high-component spins?',file=fw)
    else: raise ValueError("Invalid spin component ndim = {}".format(ndim))
    print ('\nStart configuration: {}\n'.format(start_conf),file=fw)
    print ('='*80, file=fw)

    print ("\n{}\nModeling setup\n{}\n".format('='*80, '-'*80),file=fw)
    print ('\nTarget temperature',file=fw)
    print ('T = {:8.4f} K'.format(temp),file=fw)
    print ('Beta = 1/(kB*T) = {:8.4f} mev^-1'.format(beta),file=fw)
    print ('\nMetropolis-Hasting algorithm for detailed-balance equilibrium',file=fw)
    print ('Number of Monte Carlo Sweeps (MCS) = {}'.format(mcs),file=fw)

    print ('\n\n{}\nSampling method for random spin: {}'.format('*'*50,sample_method),file=fw)
    print (sample_method_note,file=fw)
    sm = sample_method.lower()
    #if sm == 'ising': assert ndim==1, 'shape of spin should be 1 for Ising-type sampling'
    #if sm == 'xy':    assert ndim==2, 'shape of spin should be 2 for XY-type sampling'

    if sm in ['spherical_random','cubic_random']:
        print ('\nImportant Wawrning: your are using {} sampling method'.format(sample_method),file=fw)
        print (Alert_for_non_uniform_random_vector, file=fw)
    print ('*'*50+'\n',file=fw)
    if sm in ['gaussian','small_step']:
        if sm=='gaussian': print (Note_for_adaptive_Gaussian_sampling,file=fw)
        if sigma0==-1:  print ('sigma0 = {:8.4f}'.format(np.power(kB*temp/muB,1/5.)*2/25),file=fw)
        else:           print ('sigma0 = {:8.4f}'.format(sigma0),file=fw)
        if adaptive:
            print ('\nAdaptive algorithm is used',file=fw)
            print ('sigma0 will be adjusted according to the acceptance ratio',file=fw)
            print ('target acceptance ratio = {:6.3f} %'.format(target_acceptance_ratio*100),file=fw)
            print ('Find sigma0 > {0:8.3f}\nRe-adjust sigma0 to {0:8.3f}'.format(max_sigma0),file=fw)
    print ('\n'+'='*80, file=fw)

    log_handle.verbose_logging_info(fw=fw)

    print ("\n{}\nParallelization\n{}\n".format('='*80, '-'*80),file=fw)
    if ncore>1:    
        print ('parallel on {} cores'.format(ncore),file=fw)
    elif ncore==1: 
            print ('Run in serial mode.\nOr',file=fw)
            print ('Run in parallel mode, but only one core is invoked.',file=fw)
    else:
        raise Exception('Wrong number of cores ({}) in parallelization!'.format(ncore))
 
    if rank_group is not None:  
        ncore_invoked = len(rank_group)
        nn = 10
        nline = ncore_invoked//nn
        fmt = ('{:4d} '*nn+'\n')*nline + '{:4d} '*(ncore_invoked%nn)
        print ('{}\nrank of invoked cores\n{}'.format('='*50,'-'*50),file=fw)
        print (fmt.format(*tuple(rank_group)),file=fw)
        print ('{}\n'.format('='*50),file=fw)
    else:
        ncore_invoked = ncore

    if nblock>1: 
        print ('\nSpin lattice divided into  {:4d} blocks'.format(nblock),file=fw)
        print ('Average:        {:7.0f} sites/block\n'.format(np.ceil(nsites/nblock)),file=fw)
        print (parallel_advice,file=fw)
        print ('Current setup: N_cores = {}, N_blocks = {}'.format(ncore_invoked, nblock),file=fw)
    print ('='*80, file=fw)

    print ('\nMonte Carlo Sweeps (Total: {})'.format(mcs),file=fw)
    print ('Started  at {}'.format(time.ctime()),file=fw)
    print ('',file=fw)
    print (fmt_head.format(*tuple(head_tags)),file=fw)
    if fw is not None: fw.flush()
    sys.stdout.flush()
    if log_handle._log_file is not None: fw.close()
    return fw


def print_MC_end(stime,fw):
    print ('='*130,file=fw)
    print ('\nMC simulation terminated normally',file=fw)
    print ('Finished at {}'.format(time.ctime()),file=fw)
    print ('Total time used: {:10.5f} s'.format(time.time()-stime),file=fw)
    print ('='*130+'\n',file=fw)
    if fw is not None: fw.close()


def save_conf_to_ovf(sp_lat,Etot,temperature,fil_ovf,mode,spin_coord=None):
    shape = sp_lat.shape
    if len(shape)==5: nx,ny,nz,nat,ndim = shape
    elif len(shape)==4: nx,ny,nat,ndim = shape; nz=1
    desc_mc = 'Monte Carlo simulation'
    desc_en = 'Etot = {:16.10f} meV/site'.format(Etot)
    desc_T  = 'Temp = {:8.4f} K'.format(temperature)
    desc_tm = 'Written at {}'.format(time.ctime())
    params = gen_params_for_ovf(nx,ny,nz,additional_desc=[desc_mc,desc_T,desc_en,desc_tm])
    spins = np.swapaxes(sp_lat,0,1).reshape(-1,ndim)
    if spin_coord is not None: log_spins = np.dot(spins,spin_coord)
    else: log_spins = copy.copy(spins)
    write_ovf(params,log_spins,fil_ovf,mode)


def propose_one_spin(old_spin,sigma0,sample_method='Gaussian',q_for_Potts=3):
    sm = sample_method.lower()
    if   sm=='random':     new_spin = gen_normal_random_spin()
    elif sm=='ising':      new_spin = gen_Ising_random_spin()*old_spin
    elif sm=='xy':         new_spin = gen_XY_random_spin()
    elif sm=='potts':      new_spin = gen_Potts_random_spin(q=q_for_Potts)
    elif sm=='gaussian':   new_spin = gen_Gaussian_random_spin(old_spin,sigma0)
    elif sm=='small_step': new_spin = gen_small_step_random_spin(old_spin,sigma0)
    elif sm=='spherical_random': new_spin = gen_spherical_random_spin()
    elif sm=='cubic_random':     new_spin = gen_cubic_random_spin()
    else: exit('Unrecognized sample_method: {}'.format(sample_method))
    return new_spin



def log_spin_configuration(log_handle,sp_lat,spin_coord=None,temperature=0,Etot=0,imcs=0):
    if imcs==0: mode='w'
    else: mode='a'
    if log_handle._single_ovf:   fil_ovf = log_handle._log_conf_file
    else:  fil_ovf = '{}/MCS_{}_spin_confs.ovf'.format(outdir,str(imcs+1).zfill(6))
    if log_handle._log_conf: save_conf_to_ovf(sp_lat,Etot,temperature,fil_ovf,mode)



def adapt_sigma0(sigma0,acpt_rate,max_sigma0):
    if acpt_rate==100: return max_sigma0
    sigma0 = min(sigma0*0.5/(1-acpt_rate/100), max_sigma0)
    return sigma0



def run_monte_carlo(ham,sp_lat,
    temperature=0.1,
    mcs=10,
    verbosity=2,
    sample_method='Gaussian',sigma0=-1,
    adaptive=True,
    target_acceptance_ratio=0.5,
    max_sigma0 = 60,
    start_conf = 'as_input',
    spin_coord=None,
    fix_boundary_spin=False,
    pinned_idx=None,
    log_handle = log_handle,
    q_for_Potts=3):

    # J. Phys.: Condens. Matter 26 (2014) 103202, Eq. 24
    if sigma0==-1: sigma0 = np.power(kB*temperature/muB,1/5.)*2/25
    log_handle.prepare_logging_dir()
    stime = time.time()

    shape = sp_lat.shape
    nx,ny,nz,nat,dyn_idx = get_dynamics_sites_indices(shape,fix_boundary_spin,pinned_idx,savetxt=True,outdir=log_handle._outdir)
    nsites = np.prod(shape[:-1])
    ndim = shape[-1]
    fmt_step, fmt_step_a, fmt_head_a, head_tags_a = set_verbose_format(ndim, log_handle)

    sp_lat = initialize_spin_lattice(sp_lat,start_conf)
    check_sp_lat_norm(sp_lat)

    fail_count = 0
    if verbosity>1:
        if log_handle._log_ham: log_spin_hamiltonian(ham,sp_lat,log_handle._log_ham_file)
        print_MC_setup(temperature,mcs,nsites,1,1,log_handle,
        sample_method,sigma0,adaptive,target_acceptance_ratio,max_sigma0,start_conf,ndim=ndim)
        if log_handle._log_file is not None: fw=open(log_handle._log_file,'a')
        else: fw=None
        fa = None
        if log_handle._archive_file is not None: 
            fa=open(log_handle._archive_file,'w')
            fa.write(fmt_head_a.format(*tuple(head_tags_a))+'\n')
    Etot = ham.calc_total_E(sp_lat)
    if log_handle._log_initial_conf: save_conf_to_ovf(sp_lat,Etot,temperature,log_handle._init_conf_file,'w') 
    log_spin_configuration(log_handle,sp_lat,ham._spin_coord,temperature,Etot,0)

    if temperature==0: beta = np.inf
    else: beta = 1/(kB*temperature)

    def log_snapshot(imcs, sp_lat):
        log_flag = (imcs==0 or (imcs+1)%log_handle._n_log_magnetization==0 or (imcs+1)%log_handle._n_log_configuration==0 or imcs==mcs-1)
        if log_flag:  Etot = ham.calc_total_E(sp_lat)
        if log_handle._log_topo_chg and log_handle._tri_simplices is not None: 
            Q = calc_topo_chg(sp_lat_log,tri_simplices = log._tri_simplices)

        if (imcs==0 or (imcs+1)%log_handle._n_log_magnetization==0 or imcs==mcs-1) and verbosity:
            mm=np.average(sp_lat.reshape(-1,ndim),axis=0)
            print (fmt_step.format((imcs+1)*(imcs!=0),Etot,time.time()-stime,fail_count,(imcs+1)*nsites,acpt_rate,sigma0,*tuple(mm)),file=fw)
            if fa is not None: 
                if log_handle._log_topo_chg and log_handle._tri_simplices is not None: 
                    fa.write(fmt_step_a.format((imcs+1)*(imcs!=0),Etot,*tuple(mm),Q)+'\n')
                else:
                    fa.write(fmt_step_a.format((imcs+1)*(imcs!=0),Etot,*tuple(mm))+'\n')
                fa.flush()
            if fw is not None: fw.flush()
            sys.stdout.flush()
        if ((imcs+1)%log_handle._n_log_configuration==0 or imcs==mcs-1):
            log_spin_configuration(log_handle,sp_lat,ham._spin_coord,temperature,Etot,imcs)



    sm = sample_method.lower()
    for imcs in range(mcs):

        for ii,idx0 in enumerate(dyn_idx):
            n_i = copy.copy(sp_lat[tuple(idx0)])
            E1 = ham.calc_local_energy(sp_lat,idx0)
            sp_lat[tuple(idx0)] = propose_one_spin(n_i,sigma0,sample_method,q_for_Potts)
            E2 = ham.calc_local_energy(sp_lat,idx0)
            dE = E2 - E1
            if dE > 0 and np.random.rand() > np.exp(-beta*dE):
                sp_lat[tuple(idx0)] = n_i
                fail_count += 1

        acpt_rate = (1 - float(fail_count)/((imcs+1)*nsites)) *100
        if adaptive and sm=='gaussian': adapt_sigma0(sigma0,acpt_rate,max_sigma0)

        log_snapshot(imcs, sp_lat)

    if verbosity:  print_MC_end(stime,fw)
    if log_handle._log_final_conf: save_conf_to_ovf(sp_lat,Etot,temperature,log_handle._final_conf_file,'w') 
    if fa is not None: fa.close()
    return sp_lat,Etot
 


def check_block_neigh(ham,sp_lat,group_x,group_y,group_z):
    shape = sp_lat.shape
    if len(shape)==5: nx,ny,nz,nat,ndim = shape
    elif len(shape)==4: nx,ny,nat,ndim = shape; nz=1
    block_image = np.mgrid[-group_x:2*group_x:group_x,-group_y:2*group_y:group_y,-group_z:2*group_z:group_z,:nat]
    block_image = np.transpose(block_image,(4,1,2,3,0))
    block_image = block_image.reshape(nat,-1,block_image.shape[-1])
    flag = True
    corr_pairs = []
    for iat in range(nat):
        for exch in ham._BL_exch+ham._BQ_exch:
            for neigh in exch._neigh_idx[iat]:
                ndim = len(neigh)-1
                if neigh[-1]!=iat: continue
                dist = np.linalg.norm(block_image[iat,:,:ndim] - neigh[:-1],axis=1)
                if np.min(dist)==0: 
                    flag=False
                    idx = np.argmin(dist)
                    corr_pairs.append([iat,block_image[iat][idx][:-1]])

    if len(corr_pairs)>0:
        print ('\n{}\nAlert from check_block_neigh:'.format('*'*60))
        print ('some sites and their images in neighboring block')
        print ('have exchange couplings')
        for pair in corr_pairs:
            if len(pair[1])==3: f1 = '[Rx, Ry] = '+'{:3d} '*2
            if len(pair[1])==4: f1 = '[Rx, Ry, Rz] = '+'{:3d} '*3
            print (('iat = {:3d}, '+f1).format(pair[0],*tuple(pair[1])))
        print ('*'*60)
    assert flag, '{}Dividing blocks for MC simulation: block too small\n'.format(err_text)
    return flag




class serial_MC_controller(object):
    def __init__(self,
        temperature=0.1,
        mcs=10,
        verbosity=2,
        sample_method='gaussian',sigma0=-1,
        adaptive=True,
        target_acceptance_ratio=0.5,
        max_sigma0=60,
        start_conf='as_input',
        spin_coord=None,
        fix_boundary_spin=False,
        pinned_idx=None,
        log_handle = log_handle,
        q_for_Potts = 3,
        group_x=3,
        group_y=3,
        group_z=1,
        rank_group=None,
        rank_root=0):
 

        self.set_temperature(temperature)
        self.set_mcs( mcs )
        self.set_verbosity( verbosity)
        self._sample_method = sample_method
        self._adaptive = adaptive
        self._target_acceptance_ratio = target_acceptance_ratio
        self._max_sigma0 = max_sigma0
        self._start_conf = start_conf
        self._spin_coord = spin_coord
        self._fix_boundary_spin = fix_boundary_spin
        self._pinned_idx = pinned_idx
        self.set_q_for_Potts( q_for_Potts )
        self.set_log_handle( log_handle )

        # parameters related to sampling
        # J. Phys.: Condens. Matter 26 (2014) 103202, Eq. 24
        self.set_sigma0(sigma0)
        self._adaptive = adaptive
        self._target_acceptance_ratio = target_acceptance_ratio

        # parameters related to block division and parallelization
        self._group_x = group_x
        self._group_y = group_y
        self._group_z = group_z
        self.set_rank_group( rank_group )
        self.set_rank_root( rank_root )


    def set_verbosity(self,verbosity):
        err = 'MC_controller: You try to set verbosity = {}, it should be an non-negative integer!'.format(verbosity)
        assert type(verbosity)==int and verbosity>=0, err
        self._verbosity = verbosity

    def set_mcs(self,mcs):
        self._mcs = mcs

    def set_q_for_Potts(self,q_for_Potts):
        self._q_for_Potts = q_for_Potts

    def set_rank_root(self,rank_root):
        self._rank_root = rank_root

    def set_rank_group(self,rank_group):
        self._rank_group = rank_group

    def set_temperature(self,temperature):
        assert temperature>=0, 'temperature <0 not allowed!'
        self._temperature = temperature
        if self._temperature<1e-6: self._beta = np.inf
        else: self._beta = 1/(kB*self._temperature)


    def set_sigma0(self,sigma0):
        if sigma0==-1: self._sigma0 = np.power(kB*self._temperature/muB,1/5.)*2/25
        else: self._sigma0 = sigma0
 

    def set_log_handle(self,log_handle):
        self._log_handle = log_handle
        self.__dict__.update(log_handle.__dict__)

    def estimate_nblock(self,sp_lat):
        shape = sp_lat.shape
        if len(shape)==5: nx,ny,nz,nat,ndim = shape
        elif len(shape)==4: nx,ny,nat,ndim = shape; nz=1
        nnx = np.ceil(nx/self._group_x)
        nny = np.ceil(ny/self._group_y)
        nnz = np.ceil(nz/self._group_z)
        nblock = int(nnx*nny*nnz)
        return nblock
 

    @property
    def get_rank_root(self):
        return self._rank_root
    
    @property
    def get_rank_group(self):
        return self._rank_group

    @property
    def get_temperature(self):
        return self._temperature


    def run_monte_carlo(self,ham,sp_lat):
        sp_lat, Etot = run_monte_carlo(ham,sp_lat,self._temperature,self._mcs,
        self._verbosity,
        self._sample_method,self._sigma0,
        self._adaptive,self._target_acceptance_ratio,
        self._sigma0,self._start_conf,
        self._spin_coord,
        self._fix_boundary_spin,
        self._pinned_idx,
        self._log_handle,
        self._q_for_Potts)

        pickle.dump(self, open('{}/MC_controller.pickle'.format(self._outdir),'wb'))
 
        return sp_lat, Etot
