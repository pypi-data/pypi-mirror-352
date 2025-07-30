#!/usr/bin/env python

#=======================================================
# 
# A simple way to construct the spin-glass model
# namely, Edwards-Anderson model
#
# By default it is built on the simple-cubic lattice
# with random nearest hopping
# You can change it to other lattice in need
#
# Copyright @ Shunhong Zhang 2024-2025
# zhangshunhong.pku@gmail.com
#
#=========================================================

import numpy as np
from asd.core.hamiltonian import *
from asd.core.geometry import *
from asd.core.shell_exchange import exchange_shell


# Gaussian distribution, with mean of 0, and standard deviation J_std
# bimodal: J = 1 or -1 with probablity of p and q (default: p = q = 0.5)
def generate_random_exchanges(Nbonds, J_mean=0., J_std=1., random_type='Gaussian', random_seed=10358, p_positive=0.5):
    np.random.seed(random_seed)
    if random_type=='Gaussian':    J_random = np.random.normal(loc=J_mean, scale=J_std, size=int(Nbonds))
    elif random_type=='bimodal':   J_random = np.sign(np.random.random(Nbonds)-(1-p_positive))
    else:  raise ValueError ("Wrong random_type of {}".format(random_type))
    return J_random



def hist_exchange_couplings_gaussian(J_list, J_mean=None, J_std=None, save=False, show=False):
    import matplotlib.pyplot as plt
    fig, hist, bins = hist_exchange_couplings(J_list, show=False)
    ax = fig.axes[0]
    if J_mean is not None and J_std is not None:
        xx = np.linspace(J_mean-5*J_std, J_mean+5*J_std, 201)
        fac = 1/np.sqrt(2*np.pi*J_std**2) 
        yy = fac * np.exp(-(xx - J_mean)**2/2/J_std**2)
        #yy *= np.sqrt(n_tot)
        #yy *= len(J_list)
        int_g = np.trapz(yy, x=xx)
        print (int_g)
        ax.plot(xx, yy, alpha=0.5)
    fig.tight_layout()
    if save: fig.savefig('exchanges_histogram',dpi=200)
    if show: plt.show()
    return fig, hist, bins



def build_EA_model_ham(all_neigh_idx_sc, J_mean=0., J_std=1., random_type='Gaussian', 
    random_seed=10358, p_positive=0.5, ishell=0, ham_kws={}):

    """
    Build the Edwards-Anderson model
    with random exchange couplings subject to Gaussian or bimodal distribution

    Inputs:
    ------------------
    all_neigh_idx_sc: list of lists
    each list represents a shell of neighbors for each atom

    The neighbors of an atom (index by iat) is 
    stored in the form [d_a, d_b, jat] or [d_a, d_b, d_c, jat]
    d_a, d_b, and d_c specify the lattice vector R = d_a*R_a + d_b*R_b + d_c*R_c
    R_a, R_b, and R_c are unit lattice vectors
    jat is the index of the neighboring atom in the home cell


    ishell: int
    Index of the shell for which exchange couplings are set as random numbers

    Returns:
    -----------------
    ham: instance of spin_hamiltonian class
    The spin Hamiltonian containing random exchange couplings
    """


    neigh_idx = all_neigh_idx_sc[ishell]
    bonds_indices = index_shell_bonds(neigh_idx)
    Nsites = len(neigh_idx)
    Nbonds = np.sum([len(neigh_iat) for neigh_iat in neigh_idx if neigh_iat is not None])
    shell_name = 'Shell {}: random'.format(ishell)

    """ For sanity check"""
    #print ("Generate {} bonds for {} sites".format(Nbonds, Nsites))
    #bond_vectors = generate_bond_vectors(latt_sc, sites_sc, neigh_idx)
    #verbose_bond_vectors(bond_vectors)

    J_random = generate_random_exchanges(Nbonds, J_mean, J_std, random_type, random_seed, p_positive)
    J_iso_random = []
    for iat, bonds_iat in enumerate(bonds_indices):
        J_iso_random.append([])
        if bonds_iat is None: continue
        for ibond, bond_index in enumerate(bonds_iat):
            J_iso_random[iat].append(J_random[bond_index])

    exch_EA = exchange_shell(neigh_idx, J_iso = J_iso_random, shell_name=shell_name)
    if 'BL_exch' in ham_kws.keys():   ham_kws.update( BL_exch = ham_kws['BL_exch'] + [exch_EA] )
    else: ham_kws.update( BL_exch = [exch_EA] )
    ham = spin_hamiltonian(**ham_kws)
    return J_random, ham




"""
Here we use the simple-cubic lattice as an example to demonstrate the usage
You can build the Edwards-Anderson model on other lattices similarly
"""

nx=2
ny=2
nz=1

lat_type='simple cubic'
#lat_type = 'square'
lat_type='kagome'
lat_type='honeycomb'

latt, sites, all_neigh_idx, rotvecs = build_latt(lat_type,nx,ny,nz, vacuum=10)
nat=sites.shape[-2]
Bfield=np.array([0,0,0])

""" Indices for neighboring atoms of each atom within the nx*ny*nz supercell. """
all_neigh_idx_sc = gen_neigh_idx_for_supercell(all_neigh_idx, nx, ny, nz)

""" Convert the atom position into the fractional coordinate of the supercell. """
sites_cart = np.dot(sites, latt).reshape(-1,3)
latt_sc = np.dot(np.diag([nx,ny,nz]), latt)
latt_sc_inv = np.linalg.inv(latt_sc)
sites_sc = np.dot(sites_cart, latt_sc_inv)
sites_sc = sites_sc.reshape(1,1,1,-1,sites.shape[-1])


nat = sites.shape[-2]
S_values = np.tile( [1], (nx*ny*nz,nat)).flatten()
SIA = np.tile( [0.5], (nx*ny*nz,nat) ).flatten()

if lat_type=='simple cubic': boundary_condition=[1,1,1]
else: boundary_condition=[1,1,0]


J_mean = 0.
J_std = 1.

ham_kws = dict(
Bfield=Bfield,
S_values=S_values,
BL_SIA=[SIA],
iso_only=True,
boundary_condition=boundary_condition
)


if __name__ == '__main__':
    # Example of building a bimodal EA model with unbalanced positive (FM) and negative (AFM) exchanges
    #J_random, ham = build_EA_model_ham(all_neigh_idx_sc, random_type='bimodal', random_seed=10358, p_positive=0.8, ham_kws=ham_kws, ishell=0)

    # Example of building a Gaussian-random EA model with zero mean and unity variance
    J_random, ham = build_EA_model_ham(all_neigh_idx_sc, J_mean, J_std, random_type='Gaussian', random_seed=10358, ham_kws=ham_kws, ishell=0)

    #fig, hist, bins = hist_exchange_couplings_gaussian(J_random, J_mean, J_std, show=True)
    #fig, hist, bins = hist_exchange_couplings(J_random, show=True)

    #ham.verbose_all_interactions()

    if lat_type in ['square','honeycomb','kagome','triangular']:
        visualize_bond_exchanges(latt_sc, sites_sc, ham, shell_indices=[0], sites_size=10)

