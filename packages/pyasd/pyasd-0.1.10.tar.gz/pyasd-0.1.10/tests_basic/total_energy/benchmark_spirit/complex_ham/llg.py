#!/usr/bin/env python

#======================================
#
# LLG simulation for spin Hamiltonian
# with four-site exchange couplings
#
# Warning: This function has NOT
# yet been well tested.
#
# Shunhong Zhang
# zhangshunhong.pku@gmail.com
# Jan 18 2025
#
#=======================================



import numpy as np
from asd.core.hamiltonian import *
from asd.core.geometry import *
from asd.core.shell_exchange import *
from asd.core.llg_simple import *
from asd.core.log_general import *
import asd.mpi.mpi_tools as mt
import os


def test_one_lattice(LLG, outdir='honeycomb',nx=30,ny=30):
    lat_type=outdir
    latt,sites,neigh_idx,rotvecs = build_latt(lat_type,nx,ny,1,latt_choice=1)
    nat=sites.shape[-2]

    if rank==0:
        print ('{0}\nTesting quadruplet under directory:\n{1}\n{0}'.format('='*60, outdir))
    four_site = np.loadtxt('{}/quadruplet'.format(outdir),skiprows=2)

    S_values = np.ones(nat)*2
    SIA = [np.array([0.2]*nat),np.array([0.2]*nat),np.array([0.4]*nat)]
    SIA_axis = [np.array([1,0,0]), np.array([0,1,0]), np.array([0,0,1])]

    BQ = four_site[:,-1]
    BQs = np.array([BQ]*nat)
    neigh_idx = [ [[item[2+jj*4],item[3+jj*4],item[1+jj*4]] for jj in range(3)] for item in four_site]
    neigh_idx = [np.array(neigh_idx, int)] + [[]]*(nat-1)
    bq_four_site = four_site_biquadratic_exchange_shell(neigh_idx, BQs, 'four-site-BQ')
     
    ham_kws = dict(S_values=S_values,
    BL_SIA=SIA,
    BL_SIA_axis=SIA_axis
    )
    ham = spin_hamiltonian(**ham_kws)
    ham.add_shell_exchange(bq_four_site,'general')

    sp_lat = np.zeros((nx,ny,nat,3))
    LLG = llg_solver(**llg_kws)
    LLG.set_S_values(S_values)
    LLG.set_lat_type(lat_type)
    log_handle.set_outdir('Spin_dynamics_{}'.format(outdir))
    LLG.set_log_handle(log_handle)
    LLG.mpi_llg_simulation_shared_memory(ham,sp_lat)


nx=2
ny=2
lat_type='triangular'
latt,sites,neigh_idx,rotvecs = build_latt(lat_type,nx,ny,1,latt_choice=1)
nat=sites.shape[-2]

log_handle = log_general(
n_log_conf=1000,
n_log_magn=1000,
log_topo_chg=False,
log_file='LLG.out',
)

llg_kws = dict(
alpha=0.1,
dt=1e-3,
nstep=100000,
temperature=0,
conv_ener=1e-8,
log_handle = log_handle,
start_conf='random',
)

LLG = llg_solver(**llg_kws)
 

if __name__=='__main__':
    test_one_lattice(LLG, 'triangular',nx=2,ny=2)
    #test_one_lattice(LLG, 'honeycomb')
