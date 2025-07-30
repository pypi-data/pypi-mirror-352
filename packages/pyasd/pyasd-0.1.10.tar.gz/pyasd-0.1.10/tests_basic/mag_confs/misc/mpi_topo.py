#!/usr/bin/env python

import numpy as np
from asd.core.spin_configurations import *
from asd.core.topological_charge import calc_topo_chg
from asd.mpi.topological_charge import mpi_calc_topo_chg_one_conf
from asd.utility.spin_visualize_tools import *
from asd.core.geometry import *
import asd.mpi.mpi_tools as mt
import time

nx=150
ny=100
nz=1
nat=4
radius=30

comm,size,rank,node = mt.get_mpi_handles()

latt,sites = rectangular_honeycomb_cell(nx,ny,nz,return_neigh=False)
sites_cart = np.dot(sites,latt)

sp_lat=np.zeros((nx,ny,nat,3))
sp_lat[...,2] = 1.
if not rank: sp_lat = init_spin_latt_skyrmion(sp_lat,latt,sites,radius,sk_type='Neel')
sp_lat = comm.bcast(sp_lat,root=0)

stime=time.time()
Q = mpi_calc_topo_chg_one_conf(sp_lat,sites_cart,solid_angle_method=2)

out_fmt = 'Q = {:10.5f}, time used: {:10.5f} s'
if not rank: 
    print ('mpi_calc_topo_chg: '+out_fmt.format(Q,time.time()-stime))
    stime = time.time()
    Q = calc_topo_chg(sp_lat,sites_cart,solid_angle_method=2)
    print ('calc_topo_chg:     '+out_fmt.format(Q,time.time()-stime))
