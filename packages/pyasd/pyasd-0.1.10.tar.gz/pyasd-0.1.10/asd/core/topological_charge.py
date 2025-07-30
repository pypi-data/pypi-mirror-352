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
# calculation of topological charge
# of classic spin systems
# Shunhong Zhang
# Last modified: Mar 11 2022
#
#=============================================

import numpy as np
import pickle
from asd.core.spin_configurations import check_sp_lat_norm

Solid_angle_err = """
Error from calc_solid_angle:
two spins in a triangle are anti-parallel
This might happen if you are calculating an antiferromagnet
Or a Skyrmion/Bimeron with very small size
In these cases this function cannot be applied, Sorry!
Try using solid_angle_method = 2 """
 
def verbose_collinear_error(n1,n2,n3):
    print (Solid_angle_err)
    print (('n1 = ['+'{:10.5f} '*len(n1)+']').format(*tuple(n1)))
    print (('n2 = ['+'{:10.5f} '*len(n2)+']').format(*tuple(n2)))
    print (('n3 = ['+'{:10.5f} '*len(n3)+']').format(*tuple(n3)))

 

def calc_solid_angle_1(n1,n2,n3):
    """
    see Phys. Rev. B 99, 224414 (2019)
    for the defination of solid angle

    Inputs:
    ---------------
    n1, n2, n3: numpy.ndarray in shape of (3,)
 
    Returns:
    --------------
    ang: float
    The solid angle spanned by n1, n2 and n3
    """

    n1 /= np.linalg.norm(n1)
    n2 /= np.linalg.norm(n2)
    n3 /= np.linalg.norm(n3)
    dps = np.array([np.dot(n1,n2),np.dot(n2,n3),np.dot(n3,n1)])
    if np.min(abs(1+dps))<1e-5: 
        verbose_collinear_error(n1,n2,n3)
        exit()
    cc  = (1+np.sum(dps))/np.sqrt(2*np.prod(1+dps))
    if 1<abs(cc)<1+1e-4: cc = np.sign(cc)   # tolerance to "-1" and "1"
    ang = 2*np.arccos(cc)
    y = np.linalg.det([n1,n2,n3])
    ang = np.sign(y)*abs(ang)
    return ang


def calc_solid_angle_2(n1,n2,n3):
    """
    Using the solid angle formula by Oosterom and Strackee 
    https://en.wikipedia.org/wiki/Solid_angle#Tetrahedron

    Inputs:
    ---------------
    n1, n2, n3: numpy.ndarray in shape of (3,)
 
    Returns:
    --------------
    ang: float
    The solid angle spanned by n1, n2 and n3
    """

    n1 /= np.linalg.norm(n1)
    n2 /= np.linalg.norm(n2)
    n3 /= np.linalg.norm(n3)
    dps = np.array([np.dot(n1,n2),np.dot(n2,n3),np.dot(n3,n1)])
    y = np.linalg.det([n1,n2,n3])
    x  = 1+np.sum(dps)
    ang = 2*np.angle(x+1.j*y)
    return ang


def get_tri_simplices(sites_cart):
    """
    Triangular tesselation of the 2D lattice

    Inputs:
    ---------------
    sites_cart: numpy.ndarray
    site positions in Cartesian coordinates

    Returns:
    ---------------
    tri_simplices: list of tuples
    each tuple contains three integers indexing the sites of a triangle plaquette
    """

    from scipy.spatial import Delaunay
    all_sites_cart = sites_cart.reshape(-1,sites_cart.shape[-1])
    assert len(all_sites_cart)>=3, 'get_tri_simplices: at least three sites needed!'
    tri_simplices = Delaunay(all_sites_cart).simplices
    return tri_simplices



def calc_topo_chg(spins,sites_cart=None,tri_simplices=None,pbc=[0,0,0],spatial_resolved=False,solid_angle_method=2):
    """
    For a given spin configuration on a 2D lattice, calculate the topological charge
    Inputs:
    ----------------
    spins: numpy.ndarray
    the spin configuration given as a vector field

    sites_cart: numpy.ndarray
    site positions in Cartesian coordinate

    Returns:
    ----------------
    tri_simplices: list of tuples
    returned if spatial_resolved = True

    Q_distri: numpy.ndarray
    topological charge density (solid angle on each triangle plaquette)
    returned i fspatial_resolved = True

    Q: float
    The total topological charge of the 2D lattice
    """

    check_sp_lat_norm(spins)
    all_spins=spins.reshape(-1,3)
    if tri_simplices is None and sites_cart is not None: 
        n1 = np.prod(spins.shape[:-1])
        n2 = np.prod(sites_cart.shape[:-1])
        assert n1==n2,'No. of spins {} and sites {} inconsistent!'.format(n1,n2)
        tri_simplices = get_tri_simplices(sites_cart[...,:2])
    assert solid_angle_method in [1,2], 'valid value for solid_angle_method: 1 or 2'
    if solid_angle_method==1:   Q_distri = np.array([calc_solid_angle_1(*tuple(all_spins[idx])) for idx in tri_simplices])
    if solid_angle_method==2:   Q_distri = np.array([calc_solid_angle_2(*tuple(all_spins[idx])) for idx in tri_simplices])
    Q = np.sum(Q_distri)/4/np.pi
    if spatial_resolved: return tri_simplices,Q_distri,Q
    else: return Q
