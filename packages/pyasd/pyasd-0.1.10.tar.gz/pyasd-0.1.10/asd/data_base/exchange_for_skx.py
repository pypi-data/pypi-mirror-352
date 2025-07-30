#!/usr/bin/env python

#=========================================================
# A simple spin Hamiltonian on a honeycomb lattice
# which can produce skyrmion lattice under small B field
#
# only NN exchanges are included
# J: isotropic Heisenberg 
# D: DM interactions
# A: Single-ion anisotropy 
# S: spin number
#
# Shunhong Zhang
# zhangshunhong.pku@gmail.com
# Mar 08 2025
#
#=========================================================


from asd.core.geometry import *
from asd.core.shell_exchange import *
from asd.core.hamiltonian import spin_hamiltonian
import numpy as np


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


def build_ham_skx(latt, sites, all_neigh_idx,
    J = 4.5,
    D = 2.25,
    S = 1.0,
    A = 0.09,
    B = 2.0,
    DMI_type='Bloch',
    ):

    all_bond_vectors = [generate_bond_vectors(latt, sites, neigh_idx) for neigh_idx in all_neigh_idx]

    nat = sites.shape[-2]
    S_values = np.ones(nat) * S
    SIA = np.ones(nat)*A
    J1_iso = np.ones(nat)*J

    D1_xyz = calc_DM_vectors(all_bond_vectors[0], D, DMI_type)
    exch_1 = exchange_shell( all_neigh_idx[0], J1_iso, DM_xyz = D1_xyz, shell_name = '1NN')

    ham_kws=dict(
    Bfield = np.array([0,0,1])*B,
    S_values=S_values,
    BL_SIA=[SIA],
    BL_exch=[exch_1])
 
    ham = spin_hamiltonian(**ham_kws)
    return ham




lat_type='honeycomb'
#lat_type='square'
latt, sites, all_neigh_idx, rotvecs = build_latt(lat_type,1,1,1)
nat = sites.shape[-2]


 
if __name__=='__main__':
    print ('exchange interactions for skyrmion lattice on {} lattice'.format(lat_type))
    sp_lat = np.zeros((1,1,nat,3))
    ham = build_ham_skx(latt, sites, all_neigh_idx, DMI_type='Bloch')
    ham.save_ham_for_spirit()
    ham.verbose_all_interactions()
    ham.verbose_reference_energy(sp_lat)
    ham.map_MAE(sp_lat,show=True)
