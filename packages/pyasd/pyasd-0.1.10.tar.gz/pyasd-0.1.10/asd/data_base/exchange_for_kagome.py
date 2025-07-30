#!/usr/bin/env python

# DM interactions only exist in NN exchange
# with only non-vanishing out-of-plane component

import numpy as np
from asd.core.shell_exchange import get_exchange_xyz,exchange_shell
from asd.core.geometry import build_latt
from asd.core.constants import muB
from asd.core.hamiltonian import spin_hamiltonian
 
ref = '''
# Phys. Rev. Lett. 104, 066403 (2010)
# Phys. Rev. B      94, 174444 (2016)'''

lat_type='kagome'
latt,sites,neigh_idx,rotvecs = build_latt(lat_type,1,1,1)

S_values = np.array([1./2,1./2,1./2])
SIA = - np.array([0.,0.,0.])*S_values**2

def build_kagome_ham(J1=0.3, J2=0., J3=0., D1=0.045, D2=0., D3=0., SIA=0., H=0.):
    J1_iso = np.ones(3)*J1*S_values[0]**2
    J2_iso = np.ones(3)*J2*S_values[0]**2
    J3_iso = np.ones(3)*J3*S_values[0]**2

    DM = np.array([0,0,1]) * D1*S_values[0]*S_values[1]
    DM1_xyz = np.tile(np.array([DM,-DM,DM,-DM]).reshape(4,3),(3,1,1))

    exch_1 = exchange_shell( neigh_idx[0], J1_iso, DM_xyz = DM1_xyz, shell_name = '1NN')
    exch_2 = exchange_shell( neigh_idx[1], J2_iso, shell_name = '2NN')
    exch_3 = exchange_shell( neigh_idx[2], J3_iso, shell_name = '3NN')
    BL_exch=[exch_1,exch_2,exch_3]

    H0 = H/(2*S_values[0]*muB)
    Bfield=np.array([0,0,H0])
    SIA = np.array([0.,0.,1.])*SIA*S_values**2

    ham_kws = dict(
    name='kagome',
    Bfield=Bfield,
    S_values=S_values,
    BL_SIA=[SIA],
    BL_exch=BL_exch)
 
    ham = spin_hamiltonian(**ham_kws)
    return ham

 
if __name__ == '__main__':
    print ('exchange interaction for the Kagome lattice\n{}'.format(ref))
    ham = build_kagome_ham(J1=1.)
    ham.verbose_all_interactions()
    sp_lat = np.zeros((1,1,3,3))
    ham.verbose_reference_energy(sp_lat)
    ham.map_MAE(sp_lat,show=True)
