#!/usr/bin/env python

#======================================
#
# Spin hamiltonian for an altermagnet
#
# Shunhong Zhang 
# Mar 05 2025
#
#======================================

import numpy as np
import copy
from asd.core.geometry import build_latt, generate_bond_vectors
from asd.core.shell_exchange import *
from asd.core.hamiltonian import spin_hamiltonian


def calc_DM_vectors(bond_vectors, D=1., DM_type='Bloch'):
    z_vec = np.array([0,0,1])
    DM_vecs = []
    for iat, bonds_iat in enumerate(bond_vectors):
        DM_vecs.append([])
        if bonds_iat == [] or bonds_iat is None: continue
        if len(bonds_iat)%2==1 and DM_type==1: 
            raise ValueError('DM_type="z" cannot apply for odd number of neighbors!')

        for ibond, vec in enumerate(bonds_iat):
            norm = np.linalg.norm(vec)
            assert norm>0, "The bond vector should be non-zero! {}".format(vec)
            vec /= norm
            if DM_type=='Bloch':   DM_vec = vec
            elif DM_type=='Neel':  DM_vec = np.cross(z_vec, vec) 
            elif DM_type=='z':     DM_vec = z_vec * {0:1,1:-1}[ibond%2]
            else: raise ValueError('Invalid DM_type = {}, should be Bloch/Neel/z.'.format(DM_type))
            DM_vecs[iat].append(DM_vec * D)
    return DM_vecs



def build_altermagnet_ham(S_values, J1 = -1.0, J2a = 0.2, J2b = 0.1, 
    D1=0.5, D2=0.1, D1_type='Bloch', D2_type='Bloch',
    lat_type='square', latt_choice=1, latt_const=1):

    if lat_type=='square' and latt_choice==2:
        raise ValueError('square lattice require latt_choice=2 to be bipartite. Now latt_choice=1')

    latt, sites, all_neigh_idx, rotvecs = build_latt(lat_type, 1,1,1,
    vacuum=10, latt_choice=latt_choice, latt_const=latt_const)

    all_bond_vectors = [generate_bond_vectors(latt, sites, neigh_idx) for neigh_idx in all_neigh_idx]

    S_values = np.ones(2)
    ham_kws = dict(
    name='altermagnet',
    S_values = S_values, 
    boundary_condition=[1,1,0], 
    iso_only=True)

    Nbond_1NN = [len(neigh_iat) for neigh_iat in all_neigh_idx[0]]
    Nbond_2NN = [len(neigh_iat) for neigh_iat in all_neigh_idx[1]]

    for Nbond in Nbond_2NN:
        Nbond_err = "Number of bonds for 2NN should be even! Fail to build altermagnetic Hamilonian with Nbond = {}"
        assert Nbond%2==0, Nbond_err.format(Nbond)
 
    if D1 == D2 == 0:
        J1_iso = [[J1]*Nbond for Nbond in Nbond_1NN]
        J2_iso = []
        if Nbond_2NN[0]==4:   J2_iso.append([J2a, J2b]*2)
        elif Nbond_2NN[0]==6: J2_iso.append([J2a, J2a, J2b]*2)
        else: raise ValueError('Invalid number of bonds {} for atom 0'.format(Nbond_2NN[iat]))
        if Nbond_2NN[0]==4:   J2_iso.append([J2b, J2a]*2)
        elif Nbond_2NN[0]==6: J2_iso.append([J2b, J2b, J2a]*2)
        else: raise ValueError('Invalid number of bonds {} for atom 0'.format(Nbond_2NN[iat]))


        exch_1 = exchange_shell(all_neigh_idx[0], J_iso=J1_iso, shell_name='1NN')
        exch_2 = exchange_shell(all_neigh_idx[1], J_iso=J2_iso, shell_name='2NN')
    else:
        e3 = np.eye(3)
        J1_sym = [[J1*e3]*Nbond for Nbond in Nbond_1NN]
        D1_xyz = calc_DM_vectors(all_bond_vectors[0], D1, D1_type)
        exch_1 = exchange_shell(all_neigh_idx[0], J_sym_xyz=J1_sym, DM_xyz=D1_xyz, shell_name='1NN')
 
        #J2_sym = [ [J2a*e3, J2b*e3]*(Nbond_2NN[0]//2), [J2b*e3, J2a*e3]*(Nbond_2NN[1]//2) ]
        J2_sym = []
        if Nbond_2NN[0]==4:   J2_sym.append([J2a*e3, J2b*e3]*2)
        elif Nbond_2NN[0]==6: J2_sym.append([J2a*e3, J2a*e3, J2b*e3]*2)
        else: raise ValueError('Invalid number of bonds {} for atom {}'.format(Nbond_2NN[iat], 0))
        if Nbond_2NN[1]==4:   J2_sym.append([J2b*e3, J2a*e3]*2)
        elif Nbond_2NN[1]==6: J2_sym.append([J2b*e3, J2b*e3, J2a*e3]*2)
        else: raise ValueError('Invalid number of bonds {} for atom {}'.format(Nbond_2NN[iat], 1))

        D2_xyz = calc_DM_vectors(all_bond_vectors[1], D2, D2_type)
        exch_2 = exchange_shell(all_neigh_idx[1], J_sym_xyz=J2_sym, DM_xyz=D2_xyz, shell_name='2NN')

        ham_kws.update(iso_only=False, exchange_in_matrix=True)
 
    ham_kws.update( BL_exch = [exch_1, exch_2], )
    ham_ALM = spin_hamiltonian(**ham_kws)
    return ham_ALM, latt, sites




# Bilayer model is akin to "synthetic antiferromagnets", 
# but with altermagnetic modulation here
# See the model description in, e.g.
# Yan et al. arxiv.2307.00909v1
# Yan et al. Phys. Rev. Lett. 133, 196701 (2024)

def build_bilayer_altermagnet_ham(S_values, J1a = 0.8, J1b = 0.6, J_inter=-0.5,
    D1a=0.4, D1b=0.3, D1_type='Bloch', 
    lat_type='square', latt_choice=2, latt_const=1):

    latt = np.diag([1,1,10])
    sites = np.array([[ [[0.5,0.5,0.45],[0.5,0.5,0.55]] ]])

    all_neigh_idx = [
    [ [[1,0,0],[0,1,0],[-1,0,0],[0,-1,0]], [],],
    [ [], [[1,0,1],[0,1,1],[-1,0,1],[0,-1,1]],], 
    [ [[0,0,1]],[[0,0,0]]] ]

    for neigh_idx in all_neigh_idx:
        generate_bond_vectors(latt, sites, neigh_idx) 
    all_bond_vectors = [generate_bond_vectors(latt, sites, neigh_idx) for neigh_idx in all_neigh_idx]

    S_values = np.ones(2)
    ham_kws = dict(
    name='altermagnet',
    S_values = S_values, 
    boundary_condition=[1,1,0], 
    iso_only=True)

    Nbond_1NN_top = [len(neigh_iat) for neigh_iat in all_neigh_idx[0]]
    Nbond_1NN_bot = [len(neigh_iat) for neigh_iat in all_neigh_idx[1]]

    for Nbond in Nbond_1NN_top:
        Nbond_err = "Number of bonds for 2NN should be even! Fail to build altermagnetic Hamilonian with Nbond = {}"
        assert Nbond%2==0, Nbond_err.format(Nbond)
 
    if D1a == D1b == 0:
        J1_iso_top = [[J1a,J1b,J1a,J1b], []]
        J1_iso_bot = [[], [J1b,J1a,J1b,J1a]]
        J2_iso = [[J_inter], [J_inter]]

        exch_1a = exchange_shell(all_neigh_idx[0], J_iso=J1_iso_top, shell_name='1NN_top')
        exch_1b = exchange_shell(all_neigh_idx[1], J_iso=J1_iso_bot, shell_name='1NN_bot')
        exch_2  = exchange_shell(all_neigh_idx[2], J_iso=J2_iso, shell_name='inter_layer_coupling')
 
    else:
        e3 = np.eye(3)
        J1_sym = [[J1a*e3, J1b*e3, J1a*e3, J1b*e3], []]  # top layer
        D1_xyz = calc_DM_vectors(all_bond_vectors[0], D1a, D1_type)
        exch_1a = exchange_shell(all_neigh_idx[0], J_sym_xyz=J1_sym, DM_xyz=D1_xyz, shell_name='1NN_top')

        J1_sym = [[], [J1b*e3, J1a*e3, J1b*e3, J1a*e3]]  # bottom layer, subject to 90-degree rotation of the top layer
        D1_xyz = calc_DM_vectors(all_bond_vectors[1], D1b, D1_type)
        exch_1b = exchange_shell(all_neigh_idx[1], J_sym_xyz=J1_sym, DM_xyz=D1_xyz, shell_name='1NN_bot')
 
        J2_sym = [ [J_inter*e3], [J_inter*e3] ]
        exch_2 = exchange_shell(all_neigh_idx[2], J_sym_xyz=J2_sym, shell_name='inter_layer_coupling')

        ham_kws.update(iso_only=False, exchange_in_matrix=True)
 
    ham_kws.update( BL_exch = [exch_1a, exch_1b, exch_2], )
    ham_ALM = spin_hamiltonian(**ham_kws)
    return ham_ALM, latt, sites


lat_type='square'
lat_type='honeycomb'

latt_choice=1
latt_const=1
S_values = np.ones(2)


if __name__=='__main__':

    """ Bilayer altermagnetic model """
    BL_alm_kws = dict( J1a = 1.0, J1b = 0.8, J_inter=-0.5,
    D1a=0.5, D1b=0.4, D1_type='Bloch')

    ham_ALM, latt, sites = build_bilayer_altermagnet_ham(S_values,**BL_alm_kws)
    ham_ALM.add_axial_single_ion_anisotropy(np.ones(2)*0.1, np.array([0,0,1]))
    ham_ALM.verbose_all_interactions()
    ham_ALM.save_ham_for_spirit(latt, sites, latt_const, input_file='input_bilayer.cfg', verbosity=1)

 

    """ monolayer altermagnetic model """
    alm_kws = dict(lat_type=lat_type, latt_choice=latt_choice, latt_const=latt_const, 
    D1_type='Neel', D2_type='Bloch')
    ham_ALM, latt, sites = build_altermagnet_ham(S_values, **alm_kws)

    #ham_ALM.verbose_all_interactions()
    ham_ALM.save_ham_for_spirit(latt, sites, latt_const, input_file='input.cfg', verbosity=1)

    alm_kws.update(D1=0, D2=0)
    ham_ALM, latt, sites = build_altermagnet_ham(S_values, **alm_kws)
    ham_ALM.verbose_all_interactions()
    #ham_ALM.save_ham_for_spirit(latt, sites, latt_const, input_file='input.cfg', verbosity=1)
