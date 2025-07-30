#!/usr/bin/env python

#=====================================================
#
# Monolayer NiI2, exchange coupling up to the 3NN 
# Calculated by the four-state method
# Ref. Nat. Commun. 11, 5784 (2020)
#
#======================================================


import numpy as np
from asd.core.shell_exchange import exchange_shell
from asd.core.geometry import build_latt
from scipy.spatial.transform import Rotation as RT

lat_type='triangular'
latt,sites,neigh_idx,rotvecs = build_latt(lat_type,1,1,1)


# momoment for Ni2+ ions (1 muB/site)
S_values = np.array([2./2])

# single-ion anisotropy, negative value for easy-plane nature
SIA = - np.array([0.6])*S_values**2

# Heiserberg isotropic exchange couplings
J1_iso = -7.0
J2_iso = -0.3
J3_iso =  5.8


J1_sym = - np.array([
[   -1.0000 ,    0.0000 ,    0.0000 ],
[    0.0000 ,    1.4000 ,   -1.4000 ],
[    0.0000 ,   -1.4000 ,   -0.3000 ]])

J1_sym += -J1_iso*np.eye(3)
J2_sym = -J2_iso*np.eye(3)
J3_sym = -J3_iso*np.eye(3)


J1_sym = np.array([J1_sym])*S_values[0]**2
J2_sym = np.array([J2_sym])*S_values[0]**2
J3_sym = np.array([J3_sym])*S_values[0]**2

# important change: the adjacent bonds subject to a mirror symmetry
# not a 180 degree rotation, so rotvecs[0] is wrong here
J1_sym_xyz = np.zeros((1,6,3,3),float)
mat1 = RT.from_rotvec(np.array([0,0,2/3.])*np.pi).as_matrix()
mat2 = RT.from_rotvec(np.array([0,0,4/3.])*np.pi).as_matrix()
J1_sym_xyz[0,0] = J1_sym[0]
J1_sym_xyz[0,2] = np.dot(np.dot(mat1,J1_sym[0]) , mat1.T)
J1_sym_xyz[0,4] = np.dot(np.dot(mat2,J1_sym[0]) , mat2.T)
J1_sym_xyz[0,3] = J1_sym[0]
J1_sym_xyz[0,3,0] *= -1
J1_sym_xyz[0,3,:,0] *= -1
J1_sym_xyz[0,1] = np.dot(np.dot(mat2,J1_sym[0]) , mat2.T)
J1_sym_xyz[0,5] = np.dot(np.dot(mat1,J1_sym[0]) , mat1.T)

J2_sym_xyz = np.tile(J2_sym,(1,6,1,1))
J3_sym_xyz = np.tile(J3_sym,(1,6,1,1))


#exch_1 = exchange_shell( neigh_idx[0], J1_iso, J1_sym_xyz, shell_name = '1NN')
#exch_2 = exchange_shell( neigh_idx[1], J2_iso, J2_sym_xyz, shell_name = '2NN')
#exch_3 = exchange_shell( neigh_idx[2], J3_iso, J3_sym_xyz, shell_name = '3NN')

exch_1 = exchange_shell( neigh_idx[0], None, J1_sym_xyz, shell_name = '1NN')
exch_2 = exchange_shell( neigh_idx[1], None, J2_sym_xyz, shell_name = '2NN')
exch_3 = exchange_shell( neigh_idx[2], None, J3_sym_xyz, shell_name = '3NN')




def local_axis_J1():
    print ('\n'+'='*50)
    print (('{:>8s} '*4).format('lambda','v_x','v_y','v_z'))
    print ('-'*50)
    for i in range(6):
        Jmat = exch_1._Jmat[0,i]
        evals,evec = np.linalg.eigh(Jmat)
        evec = evec.T
        for j in range(3):
            print (('{:8.4f} '*4).format(evals[j],*tuple(evec[j])))
        print ('')
    print ('='*50)


if __name__=='__main__':
    from asd.core.hamiltonian import spin_hamiltonian

    sp_lat = np.zeros((1,1,1,3))

    ham_kws = dict(S_values=S_values,
    BL_SIA=[SIA],BL_exch=[exch_1,exch_2,exch_3],
    exchange_in_matrix=True, name='NiI2')

    ham = spin_hamiltonian(**ham_kws)
    ham.verbose_all_interactions()
    ham.verbose_reference_energy(sp_lat)
    ham.map_MAE(sp_lat,show=True,savefig=False)
    local_axis_J1()
