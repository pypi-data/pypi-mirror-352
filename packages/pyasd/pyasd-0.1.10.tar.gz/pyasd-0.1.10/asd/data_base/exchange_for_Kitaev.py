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



# ===================================================
# Utility to generate Kitaev-type spin Hamiltonian
# Can be implemented to perform
# Classic spin dyanmics simulations (pyasd) or
# Quantum spin simulation (HPhi or quspin)
#
# Shunhong Zhang
# zhangshunhong.pku@gmail.com
# Last modified: Feb 27 2025
#
#====================================================
#
#
# suppose we have a honeycomb lattice, and consider Kitaev interactions between neighboring sites
# for one site in A sublattice, we have three neighboring sites in B sublattice
# the exchange interation is called bond
# for each bond, there is an easy magnetization axis call Kitaev axis
# From symmetry consideration, we can asssume that each Kitaev axis has its in-plane component along the bond
# now we want to calculate the out-of-plane cosine of the Kitaev axis, so that
# the three Kitaev axes subject to three bonds from the same site are perpendicular to each other

import os
import matplotlib.pyplot as plt
import numpy as np
from scipy.spatial.transform import Rotation as RT
from asd.core.shell_exchange import exchange_shell,index_shell_bonds,verbose_bond_exchanges_no_double_counting, visualize_bond_exchanges
from asd.core.geometry import build_latt, gen_neigh_idx_for_supercell
from asd.core.hamiltonian import spin_hamiltonian

r2h = np.sqrt(2)/2
r3h = np.sqrt(3)/2


# Here, K1, K2, and K3 are mutually orthogonal
# they defines the Kitaev axis foe each bond in the honeycomb lattice
# see Fig. 1 of Phys. Rev. Lett. 124, 087205 (2020) for illustration
# of the local coordinate system obtained from Lowdin orthogonalization
# of the tensorial exchange couplings between nearest neighbors
#
# Note: here the honeycom lattice is defined following HPhi
# cell: [[1,0,0],[0.5,r3h,0],[0,0,c]]
# atom: [[1/3,1/3,1/2],[2/3,2/3,1/2]]
# bond: three bonds denoted as X, Y, and Z respectively
# The IN-PLANE components of each bond and its Kitaev axis are orthogonal
#
def get_axes_vec():
    K1 = np.array([-0.5, r3h,r2h])
    K2 = np.array([-0.5,-r3h,r2h])
    K3 = np.array([1,0,r2h])
    return [K/np.linalg.norm(K) for K in [K1, K2, K3]]


def Lowdin_to_global(J_Heis, Kitaev, Gamma1, Gamma2, verbosity=1):
    # the three Kitaev axes
    # they form a matrix which is the transform matrix between two coordinate systems
    K1,K2,K3 = get_axes_vec()
    if verbosity:
        print ('\nKitaev axes')
        for K in (K1,K2,K3):  print (('{:10.6f} '*3).format(*tuple(K)))
    Kvecs = np.array([K1, K2, K3])

    # the three bond-dependent exchange matrices (3*3)
    J_Lowdin = np.zeros((3,3,3))
    if verbosity: print ('\nExchange matrices in the local alpha-beta-gamma (XYZ) coordinate')

    J_Lowdin[0] = np.array([
    [J_Heis + Kitaev, Gamma2, Gamma2],
    [Gamma2,          J_Heis, Gamma1],
    [Gamma2,          Gamma1, J_Heis]])

    J_Lowdin[1] = np.array([
    [J_Heis, Gamma2,          Gamma1],
    [Gamma2, J_Heis + Kitaev, Gamma2],
    [Gamma1, Gamma2,          J_Heis]])

    J_Lowdin[2] = np.array([
    [J_Heis , Gamma1, Gamma2         ],
    [Gamma1,  J_Heis, Gamma2         ],
    [Gamma2,  Gamma2, J_Heis + Kitaev]])

    for ibond in range(3):
        assert np.allclose(J_Lowdin[ibond], J_Lowdin[ibond].T), 'J matrix of bond {} not symmetryic!'.format(ibond)
        assert np.allclose(np.linalg.norm(Kvecs[ibond]),1,atol=1e-6), 'Kitaev vectors should be normalized'
        if verbosity: print ((('{:10.6f} '*3+'\n')*3).format(*tuple(J_Lowdin[ibond].flatten())))

    if verbosity: print ('\nExchange matrices in the global xyz coordinate')
    J_trans = []
    for ibond in range(3):
        J_mat = J_Lowdin[ibond]
        J_tran = np.dot(np.dot(Kvecs.T,J_mat),Kvecs)
        assert np.allclose(J_tran,J_tran.T), 'J matrix should be symmetric here!'
        J_trans.append( J_tran )
        if verbosity: print ((('{:10.6f} '*3+'\n')*3).format(*tuple(J_trans[ibond].flatten())))

    return J_Lowdin, J_trans


J_Heis = 0
Kitaev = -1
Gamma1 = 0
Gamma2 = 0

S1 = 1./2
S2 = 2./2
S_values = np.array([S1, S2],float)

latt, sites, all_neigh_idx, rotvecs = build_latt('honeycomb',1,1,1,vacuum=10)
J_lowdin, J_XYZ = Lowdin_to_global(J_Heis, Kitaev, Gamma1, Gamma2, verbosity=0)
exch_1 = exchange_shell(all_neigh_idx[0], Jmat=[J_lowdin,J_lowdin], shell_name='1NN_Kitaev_Lowdin')
exch_2 = exchange_shell(all_neigh_idx[0], Jmat=[J_XYZ,J_XYZ], shell_name='1NN_Kitaev_XYZ')


ham_kws = dict(
S_values = S_values,
BL_exch=[exch_1],
#BL_exch=[exch_2],
)

ham = spin_hamiltonian(**ham_kws)

latt_rect, sites_rect, all_neigh_idx_rect, rotvecs_rect = build_latt('honeycomb',1,1,1,vacuum=10,latt_choice=3)
exch_1_rect = exchange_shell(all_neigh_idx_rect[0], Jmat=[J_lowdin]*4, shell_name='1NN_Kitaev_Lowdin')
exch_2_rect = exchange_shell(all_neigh_idx_rect[0], Jmat=[J_XYZ]*4, shell_name='1NN_Kitaev_XYZ')
S_values_rect = np.tile(S_values,(2,1)).T.flatten()

ham_rect_kws = dict(
S_values = S_values_rect,
BL_exch=[exch_1_rect],
#BL_exch=[exch_2_rect],
)

ham_rect = spin_hamiltonian(**ham_rect_kws)

if __name__=='__main__':
    #ham.verbose_all_interactions()
    bonds_indices = index_shell_bonds(all_neigh_idx[0])
    #fd = open('Pairs.txt','w')
    #exch_1.verbose_shell_exchanges(bonds_indices, output_form=2, iso=False, file_handle=fd)
    #fd = open('Pairs_global.txt','w')
    #exch_2.verbose_shell_exchanges(bonds_indices, output_form=2, iso=False, file_handle=fd)



    """ Build from the hexagonal unit cell """
    ncell_dic = {'12a': (2,3,1), '18b':(3,3,1), '24a':(3,4,1)}
    for cell_name in ncell_dic.keys():
        print ('\nBuild the {} geometry'.format(cell_name))
 
        nx, ny, nz = ncell_dic[cell_name]
        all_neigh_idx_sc = gen_neigh_idx_for_supercell(all_neigh_idx, nx, ny, nz)
        bonds_indices_sc = index_shell_bonds(all_neigh_idx_sc[0])
        #exch_1._neigh_idx = all_neigh_idx_sc[0]
     
        fd = open('Pairs_{}.txt'.format(cell_name),'w')
        Jmat_sc = np.tile(exch_1._Jmat, (nx*ny*nz,1,1,1))
        verbose_bond_exchanges_no_double_counting(Jmat_sc, all_neigh_idx_sc[0], bonds_indices_sc, output_form=2, file_handle=fd)
      
        S_values_sc = np.tile(S_values, (nx,ny,nz))
        sites_size = S_values_sc**2 * 200
        color_dict = {1/2:'C0', 1:'C1', 3./2: 'C2'}
        sites_colors = [color_dict[key] for key in S_values_sc.flatten()]
        kws = dict(sites_size=sites_size, sites_colors=sites_colors,title=cell_name)
        latt, sites_sc, all_neigh_idx, rotvecs = build_latt('honeycomb',nx,ny,nz,vacuum=10,latt_choice=2)
        #sites_sc = sites_sc.reshape(1,1,-1,3)
        visualize_bond_exchanges(latt, sites_sc, ham, shell_indices=[0], **kws)



    """ Build from the rectangular unti cell """
    ncell_dic = {'12b': (3,1,1), '20b':(5,1,1), '16b':(2,2,1), '24b':(3,2,1)}
    for cell_name in ncell_dic.keys():
        print ('\nBuild the {} geometry'.format(cell_name))
        nx, ny, nz = ncell_dic[cell_name]
        all_neigh_idx_rect_sc = gen_neigh_idx_for_supercell(all_neigh_idx_rect, nx, ny, nz)
        bonds_indices_rect_sc = index_shell_bonds(all_neigh_idx_rect_sc[0])
     
        fd = open('Pairs_{}.txt'.format(cell_name),'w')
        Jmat_rect_sc = np.tile(exch_1_rect._Jmat, (nx*ny*nz,1,1,1))
        verbose_bond_exchanges_no_double_counting(Jmat_rect_sc, all_neigh_idx_rect_sc[0], bonds_indices_rect_sc, output_form=2, file_handle=fd)
     
        S_values_sc = np.tile(S_values_rect, (nx,ny,nz))
        sites_size = S_values_sc**2 * 200
        color_dict = {1/2:'C0', 1:'C1', 3./2: 'C2'}
        sites_colors = [color_dict[key] for key in S_values_sc.flatten()]
        latt_rect, sites_rect_sc, all_neigh_idx_rect, rotvecs_rect = build_latt('honeycomb',nx,ny,nz,vacuum=10,latt_choice=3)
        kws = dict(sites_size=sites_size, sites_colors=sites_colors)

        visualize_bond_exchanges(latt_rect, sites_rect_sc, ham_rect, shell_indices=[0], **kws)

