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


#========================================================
#
# bilinear and biquadratic spin exchange couplings
# in generic matrix form
# grouped by shells 
# (usually pairs with the same bond length)
# four-site biquadratic exchanges in scalar form
#
# Shunhong Zhang <szhang2@ustc.edu.cn>
# Nov 21 2022
#
#=========================================================

#*********************************************************
# for the DM vectors we use the rpz coordinate as input
# the definition of rpz coordinate can be found in 
# Xu et al. npj Comput. Mater. 4, 57 (2018)
# r: along the exchange bond
# p: normal to r, and in the basal plane of the 2D lattice
# z: normal to the basal plane
#*********************************************************

#*********************************************************
#
# multi-site spin interactions are included
# but more tests are still under way
#
#*********************************************************

# Important Note: effective fields calculated in this script are in meV
# the spins are normalized to be unit vectors


import os
import numpy as np
from scipy.spatial.transform import Rotation as RT
import copy
from asd.core.geometry import index_shell_bonds, plot_cell
from asd.utility.head_figlet import err_text
try:
    import asd.mpi.mpi_tools as mt
    comm,size,rank,node = mt.get_mpi_handles()
    enable_mpi=True
except:
    enable_mpi=False
 

# If fix_boundary is set to True, index for sites in boundary cells are excluded (for dynamics)
def get_dynamics_sites_indices(shape,fix_boundary=False,pinned_idx=None,savetxt=False,outdir='.'):
    if len(shape)==3:  # 1D case
        nx,nat = shape[:2]
        ny=nz=1
        mgrid = np.mgrid[:nx,:nat]
        idx=np.transpose(mgrid,(1,2,0))
        if fix_boundary: idx = idx[1:-1]
        idx = idx.reshape(-1,2)
 
    elif len(shape)==4:  # 2D case
        nx,ny,nat = shape[:3]
        nz=1
        mgrid = np.mgrid[:nx,:ny,:nat]
        idx=np.transpose(mgrid,(1,2,3,0))
        if fix_boundary: idx = idx[1:-1,1:-1]
        idx = idx.reshape(-1,3)

    elif len(shape)==5:   # 3D case
        nx,ny,nz,nat = shape[:4]
        mgrid = np.mgrid[:nx,:ny,:nz,:nat]
        idx=np.transpose(mgrid,(1,2,3,4,0))
        if fix_boundary: idx = idx[1:-1,1:-1,1:-1]
        idx = idx.reshape(-1,4)
    else:
        print (err_text)
        raise ValueError('get_dynamics_sites_indices: sp_lat with invalid shape!')

    if pinned_idx is not None:
        for idx0 in pinned_idx:
            idx = idx[np.linalg.norm(idx-idx0,axis=1)!=0]
    if savetxt:
        if idx.shape[1]==4: qn = ['nx', 'ny', 'nz', 'nat']
        if idx.shape[1]==3: qn = ['nx', 'ny', 'nat']
        if idx.shape[1]==2: qn = ['nx', 'nat']
 
        fmt = '{:>5s}'+' {:>7s}'*(len(qn)-1)
        if os.path.isdir(outdir)==False: print ('skip saving dyn_idx.dat because {} not found'.format(outdir))
        else: np.savetxt('{}/dyn_idx.dat'.format(outdir),idx,fmt='%7d',header=fmt.format(*tuple(qn)))
    return nx,ny,nz,nat,idx



# get the exchange matrix/vector for all neighbors, from one specific pair
# via symmetric operation (rotation)
def get_exchange_xyz(exch,rotvec_neighbor):
    nat,n_neigh = rotvec_neighbor.shape[:2]
    shape0=[nat,n_neigh]+list(exch.shape[1:])
    exch_xyz = np.zeros(shape0,float)
    for iat,inn in np.ndindex(nat,n_neigh):
        rot = RT.from_rotvec(rotvec_neighbor[iat,inn]).as_matrix()
        if len(exch.shape)==2: exch_xyz[iat,inn] = np.dot(rot,exch[iat])               # vectorial exchange
        if len(exch.shape)==3: exch_xyz[iat,inn] = np.dot(np.dot(rot,exch[iat]),rot.T) # tensorial exchange
    return exch_xyz



# only applicable to periodic boundary condtion case
def calc_neighbors_in_sp_lat(neigh_idx,sp_lat):
    shape = sp_lat.shape
    nx,ny,nz,nat,dyn_idx = get_dynamics_sites_indices(shape)
    n_neigh = neigh_idx.shape[1]
    neigh_idx_all = np.zeros((nx,ny,nz,nat,n_neigh,len(shape)-1),int)
    if len(shape)==4: neigh_idx_all = neigh_idx_all[:,:,0]
    for i,idx0 in enumerate(dyn_idx):
        iat = idx0[-1]
        for j,idx_n in enumerate(neigh_idx[iat]):
            idx1 = [(m+n)%s for m,n,s in zip(idx0[:-1],idx_n[:-1],shape[:-2])] + [idx_n[-1]]
            neigh_idx_all[tuple(idx0)][j] = idx1
    return neigh_idx_all



# suppose a magnetic bond is composed of sites 1 and 2
# idx0 is the index for site 1 of the bond
# idx_n is the neighbor index given in magnetic unit cell
# idx1 is the index for site 2 of the bond 
# if the bond is broken down due to open boundary
# the function returns None
#
# idx0, idx_n and the returned idx1 are in shape of 
# ix,iy    for 2D lattice, and
# ix,iy,iz for 3D lattice
#
# shape is the shape of sp_lat array
# for 2D, it is (nx,ny,nat,3)
# for 3D, it is (nx,ny,nz,nat,3)
def calc_neigh_bond_idx(idx0,idx_n,shape,boundary_condition):
    idx1 = [m+n for m,n in zip(idx0[:-1],idx_n[:-1])]
    for k,item in enumerate(idx1):
        if boundary_condition[k]==0 and (item<0 or item>shape[k]-1): return None
        else: idx1[k] = item%shape[k]
    idx1 += [idx_n[-1]]
    return idx1



def hist_exchange_couplings(J_list, bins=20, save=False, show=False):
    import matplotlib.pyplot as plt
    n_tot = len(J_list)
    fig, ax = plt.subplots(1,1)
    ax.hist(J_list, fc='none', ec='C1', bins=bins)
    hist, edgs = np.histogram(J_list, bins=bins)
    #xbins = (edgs[1:] + edgs[:-1])/2
    #ax.bar(xbins, hist/n_tot, width=np.diff(edgs), fc='none', ec='C1')

    ax.set_xlabel(r"$J$ (meV)",fontsize=12)
    ax.set_ylabel(r"Bond count",fontsize=12)
    title = 'Total {}'.format(n_tot)
    ax.set_title(title,fontsize=12)
    fig.tight_layout()
    if save: fig.savefig('exchanges_histogram',dpi=200)
    if show: plt.show()
    return fig, hist, edgs



def visualize_bond_exchanges(latt, sites, ham, shell_indices=[0], 
    title = 'Exchange bonds',
    scale=2, sites_size=50, sites_colors='C2', 
    bond_colors = ['r','b','g','m'],
    color_bonds_by_sign=False,
    color_bonds_by_shell=True,
    figname=None, show=True):

    import matplotlib.pyplot as plt
    sites_cart = np.dot(sites, latt)

    shape = sites.shape
    if len(shape)==5 and shape[2]>1:
        print ('3D lattice model specified for bond visualization.')
        print ('Currently only 2D models can be visualized.')
        return None

    print ('Currently only visualization of isotropic exchanges is available.')
 
    fig, ax = plt.subplots(1,1)
 
    for ishell in shell_indices:
        shell_exch = ham._BL_exch[ishell]
        if shell_exch._J_iso is not None:
            exchange_xyz = shell_exch._J_iso
        else:
            exchange_xyz = shell_exch._Jmat
        neigh_idx = shell_exch._neigh_idx
        bonds_indices = index_shell_bonds(shell_exch._neigh_idx)

        if exchange_xyz is None:
            print ('No isotropic exchange couplings deteced in ham._BL_exch[{}].'.format(ishell))
            print ('Nothing can be done. Plotting will be skipped.')

        bonds_record = []  # to avoid double-counting of bonds
        for iat in range(len(exchange_xyz)):
            exch = exchange_xyz[iat]
            if exch is None or neigh_idx[iat] is None: continue
            if len(shape)==4: site_idx_i = [0,0,iat]
            if len(shape)==5: site_idx_i = [0,0,0,iat]
            s1 = sites_cart[tuple(site_idx_i)]
            #if type(exch)!=list or type(exch)!=np.ndarray: continue
            #print (iat, exch)

            for inn in range(len(exch)):
                if bonds_indices[iat][inn] in bonds_record: continue
                if neigh_idx[iat] is None: continue
                if np.linalg.norm(exch[inn]):
                    dR = neigh_idx[iat][inn][:-1]
                    jat = neigh_idx[iat][inn][-1]
                    if len(dR)==2: dR = np.append(dR,0)
                    if len(shape)==4: site_idx_j = [0,0,jat]
                    if len(shape)==5: site_idx_j = [0,0,0,jat]
                    s2 = sites_cart[tuple(site_idx_j)] + np.dot(dR, latt)
                    J = exch[inn]
                    if type(J)!=float: 
                        J1 = np.min(J)
                        J2 = np.max(J)
                        if abs(J1)>abs(J2): J = J1
                        else: J = J2
                    if color_bonds_by_sign:
                        sgn = np.sign(J)
                        color = {1:'r',-1:'b', 0:'w'}[sgn]
                        ax.plot([s1[0],s2[0]], [s1[1],s2[1]], lw=np.abs(J)*scale, c=color)
                    elif color_bonds_by_shell:
                        ax.plot([s1[0],s2[0]], [s1[1],s2[1]], lw=np.abs(J)*scale, c=bond_colors[ishell])
 
                    bonds_record.append(bonds_indices[iat][inn])

    ax.scatter(sites_cart[...,0], sites_cart[...,1], s=sites_size, zorder=2, c=sites_colors)

    if title is not None: ax.set_title(title, fontsize=12)
    plot_cell(ax, latt)
    ax.set_aspect('equal')
    ax.set_axis_off()
    fig.tight_layout()
    if figname is not None: fig.saveefig(figname, dpi=200)
    if show: plt.show()
    print("{} bonds are displayed".format(len(bonds_record)))
    return fig



fmt_head = '{:>5s} '*5+'{:>10s}'*3
fm0 = '{:5d} '*2+'{:5.0f} '*3+'{:10.4f}'
fm1 = '{:5d} '*2+'{:5.0f} '*3+'{:10.4f}'*3
fm2 = (' '*30+'{:10.4f}'*3+'\n')*2
head_tags = ['iat','jat','da','db','dc','x','y','z']


def verbose_exchange_scalar(neigh_idx,exchange_xyz,exchange_type,file_handle=None):
    if exchange_xyz is None: return 1
    all_exch = []
    for exch in exchange_xyz:
        if exch!=[]:
            if type(exch)==list: all_exch += exch
            else: all_exch += [exch]
    max_abs_J = np.max(np.abs(all_exch))
    if max_abs_J > 0:
        head_tags = ['iat','jat','da','db','dc','Jij']
        print ('\n{0}\n'.format(exchange_type),file=file_handle)
        print (('{:>5s} '*5+'{:>10s}').format(*tuple(head_tags)),file=file_handle)
    for iat in range(len(exchange_xyz)):
        exch = exchange_xyz[iat]
        if exch is None or neigh_idx[iat] is None: continue
        if type(exch)==list:
            for inn in range(len(exch)):
                if np.linalg.norm(exch[inn]):
                    dR = neigh_idx[iat][inn][:-1]
                    jat = neigh_idx[iat][inn][-1]
                    if len(dR)==1: dR = np.append(dR,[0,0])
                    if len(dR)==2: dR = np.append(dR,0)
                    print (fm0.format(iat,jat,*tuple(np.append(dR,exch[inn]))),file=file_handle)
                if inn==len(exch)-1: print ('',file=file_handle)


def verbose_exchange_vector(neigh_idx,exchange_xyz,exchange_type,file_handle=None):
    if exchange_xyz is None: return 1
    max_exch =  np.max([np.abs(exch) for exch_iat in exchange_xyz for exch in exch_iat])
    if max_exch>0: 
        print ('\n{0}\n'.format(exchange_type),file=file_handle)
        print (fmt_head.format(*tuple(head_tags)),file=file_handle)
        for iat in range(len(exchange_xyz)):
            exch = exchange_xyz[iat]
            if exch is None: continue
            for inn in range(len(exch)):
                if np.linalg.norm(exch[inn]):
                    dR = neigh_idx[iat][inn][:-1]
                    jat = neigh_idx[iat][inn][-1]
                    if len(dR)==1: dR = np.append(dR,[0,0])
                    if len(dR)==2: dR = np.append(dR,0)
                    print (fm1.format(iat,jat,*tuple(np.append(dR,exch[inn]))),file=file_handle)
                if inn==len(exch)-1: print ('',file=file_handle)
    else:
        print ('{} is set but the magnitude is zero'.format(exchange_type),file=file_handle)



def verbose_exchange_matrix(neigh_idx,exchange_xyz,exchange_type,file_handle=None):
    if exchange_xyz is None: return 1
    max_exch =  np.max([np.abs(exch) for exch_iat in exchange_xyz for exch in exch_iat])
    if max_exch>0:
        print ('\n{0}\n'.format(exchange_type),file=file_handle)
        print (fmt_head.format(*tuple(head_tags)),file=file_handle)
        for iat in range(len(exchange_xyz)):
            exch = exchange_xyz[iat]
            if exch is None: continue
            if neigh_idx[iat] is None: continue
            elif len(neigh_idx[iat])==0: continue
            for inn in range(len(exch)):
                if np.max(abs(exch[inn])):
                    dR = neigh_idx[iat][inn][:-1]
                    jat = neigh_idx[iat][inn][-1]
                    if len(dR)==1: dR = np.append(dR,[0,0])
                    if len(dR)==2: dR = np.append(dR,0)
                    print (fm1.format(iat,jat,*tuple(dR),*tuple(exch[inn][0])),file=file_handle)
                    print (fm2.format(*tuple(exch[inn][1:].flatten())),file=file_handle)
    else:
        print ('{} is set but the magnitude is zero'.format(exchange_type),file=file_handle)



def verbose_bond_exchanges_no_double_counting(exchange_xyz, neigh_idx, bonds_indices, verbose_DMI=True, output_form=1, file_handle=None, verbosity=1):
    fmt_1 = '{:5d} '*2+'{:5.0f} '*3+' {:14.8f} '
    if verbose_DMI: fmt_1 += '{:14.8f} '*4
    fmt_2 = '{:4d} '*2 + '    ' + '{:5s} '*2 + '{:14.8f}'
    dirs = {0:'x',1:'y',2:'z'}
    err = 'Invalid output_form = {} for verbose_bond_exchanges_no_double_counting\nShould be 1 or 2'
 
    #if exchange_xyz is None: return None
    nat = len(exchange_xyz)
    bonds_record = []  # to avoid double-counting of bonds
    for iat in range(nat):
        exch = exchange_xyz[iat]
        if exch is None or neigh_idx[iat] is None: continue
        if type(exch)==np.ndarray: exch = list(exch)
        if type(exch)!=list: continue
        for inn, J in enumerate(exch):
            if bonds_indices[iat][inn] in bonds_record: continue
            if np.linalg.norm(exch[inn]):
                dR = neigh_idx[iat][inn][:-1]
                jat = neigh_idx[iat][inn][-1]
                if len(dR)==1: dR = np.append(dR,[0,0])
                if len(dR)==2: dR = np.append(dR,0)
                if type(J)==float:
                    if output_form == 1:
                        print (fmt_1.format(iat,jat,*tuple(dR),J,0,0,0,0), file=file_handle)
                    elif output_form == 2:
                        for idir in range(3):
                            print (fmt_2.format(iat, jat, dirs[idir], dirs[idir], J), file=file_handle)
                    else:
                        raise ValueError (err.format(output_form))

                elif J.shape==(3,3):
                    if output_form == 1:
                        DMI_vec = DM_matrix_to_vector(J)
                        DMI_norm = np.linalg.norm(DMI_vec)
                        if DMI_norm: DMI_vec /= DMI_norm
                        else: DMI_vec = np.zeros(3)
                        J_heis = np.average(np.diag(J))
                        print (fmt_1.format(iat,jat,*tuple(dR),J_heis,DMI_norm,*tuple(DMI_vec)), file=file_handle)
                    elif output_form == 2:
                        for idir in range(3):
                            for jdir in range(3):
                                if abs(J[idir,jdir])<1e-3: continue
                                print (fmt_2.format(iat, jat, dirs[idir], dirs[jdir], J[idir, jdir]), file=file_handle)
                    else:
                        raise ValueError (err.format(output_form))
                else:
                    raise ValueError('Wrong form of exchange! Should be single float number of 3*3 array')
                bonds_record.append(bonds_indices[iat][inn])
            #if inn==len(exch)-1: print ('',file=file_handle)
    Nbonds = len(bonds_record)
    if verbosity and Nbonds>0:  print ("Verbose {} bonds (No double counting)".format(Nbonds))




def DM_vector_to_matrix(DM_vec):
    DM_as_mat = np.zeros((3,3),float)
    for k in range(3):
        i=(k+1)%3
        j=(k+2)%3
        DM_as_mat[i,j] = DM_vec[k]
        DM_as_mat[j,i] =-DM_vec[k]
    return DM_as_mat


def DM_matrix_to_vector(DM_matrix):
    DM_vec = np.zeros(3)
    for k in range(3):
        i=(k+1)%3
        j=(k+2)%3
        DM_vec[k] = (DM_matrix[i,j] - DM_matrix[j,i])/2
    return DM_vec

 

# exchange pairs grouped by shell (e.g. 1st NN, 2nd NN, ...)
class exchange_shell():

    def __init__(self,
        neigh_idx,
        J_iso=None,
        J_sym_xyz=None,
        DM_xyz=None,
        Jmat=None,
        shell_name='shell exch'):

        self._neigh_idx = neigh_idx
        self._J_iso = J_iso
        self._J_sym_xyz = J_sym_xyz
        self._DM_xyz = DM_xyz
        self._Jmat = Jmat
        self._shell_name = shell_name
        self._nat = len(self._neigh_idx) 

        if J_iso is not None:
            if type(J_iso)!=list: J_iso = J_iso.tolist()
            self._J_iso = [[]]*len(J_iso)
            for iat,item in enumerate(J_iso):
                if self._neigh_idx[iat] is None: continue
                if (type(item)==float or type(item)==np.float64) or type(item)==int: 
                    self._J_iso[iat] = [float(item)]*len(self._neigh_idx[iat])
                else:
                    self._J_iso[iat] = J_iso[iat]

        if J_sym_xyz is not None or self._Jmat is None or self._DM_xyz is not None: 
            self._Jmat = self.calc_Jmat()

        if self._Jmat is not None:
            if self._J_sym_xyz is None:
                self._J_sym_xyz = self.calc_sym_mat_from_Jmat()
            if self._DM_xyz is not None:
                self._DM_xyz = self.calc_DM_vectors_from_Jmat()


    def calc_Jmat(self):
        nat = len(self._neigh_idx)
        Jmat = []
        for neigh in self._neigh_idx:
            if neigh is not None:
                Jmat.append(np.zeros((len(neigh),3,3),float))
            else:
                Jmat.append([])
 
        if self._J_sym_xyz is not None:
            Jmat = copy.deepcopy(self._J_sym_xyz)
        else:
            if self._J_iso is not None:
                for iat in range(nat):
                    if self._neigh_idx[iat] is None: continue
                    for inn in range(len(self._neigh_idx[iat])):
                        for i in range(3):
                            Jmat[iat][inn,i,i] += self._J_iso[iat][inn]

        if self._DM_xyz is not None:
            for iat in range(nat):
                neigh_idx = self._neigh_idx[iat]
                if neigh_idx is None: continue
                if self._DM_xyz[iat] is None: continue
                for inn in range(len(neigh_idx)):
                    DM_as_mat = DM_vector_to_matrix(self._DM_xyz[iat][inn])
                    Jmat[iat][inn] += DM_as_mat
        return Jmat


    def calc_sym_mat_from_Jmat(self):
        nat = len(self._neigh_idx)
        J_sym_xyz = []
        for neigh in self._neigh_idx:
            if neigh is not None:
                J_sym_xyz.append(np.zeros((len(neigh),3,3),float))
            else:
                J_sym_xyz.append([])
 
        for iat in range(nat):
            if self._neigh_idx[iat] is None: continue
            for inn in range(len(self._neigh_idx[iat])):
                J0 = self._Jmat[iat][inn]
                J_sym_xyz[iat][inn] = (J0 + J0.T)/2
        return J_sym_xyz


    def calc_DM_vectors_from_Jmat(self):
        nat = len(self._neigh_idx)
        DM_xyz = []
        for neigh in self._neigh_idx:
            if neigh is not None:
                DM_xyz.append(np.zeros((len(neigh),3),float))
            else:
                DM_xyz.append([])
 
        for iat in range(nat):
            if self._neigh_idx[iat] is None: continue
            for inn in range(len(self._neigh_idx[iat])):
                DM_xyz[iat][inn] = DM_matrix_to_vector(self._Jmat[iat][inn])
        return DM_xyz



    def verbose_interactions(self,sym_mat=False,Jmat=False,file_handle=None):
        print ('\n{0}\n{1:20s} : Start\n{0}'.format('*'*65,self._shell_name),file=file_handle)
        if sym_mat:
            verbose_exchange_matrix(self._neigh_idx,self._J_sym_xyz,'symm exch',file_handle=file_handle)
        elif Jmat:
            verbose_exchange_matrix(self._neigh_idx,self._Jmat,'Jmat exch',file_handle=file_handle)
        else:
            verbose_exchange_scalar(self._neigh_idx,self._J_iso,'J_Heisenberg',file_handle=file_handle)
        verbose_exchange_vector(self._neigh_idx,self._DM_xyz,'DMIs',file_handle=file_handle)
        print ('\n{0}\n{1:20s} : End\n{0}'.format('*'*65,self._shell_name),file=file_handle)


    def verbose_shell_exchanges(self, bonds_indices, iso=True, verbose_DMI=True, output_form=1, file_handle=None, verbosity=1):
        if verbosity: print ('\nVerbose bonds in the shell {}'.format(self._shell_name))
        args = (self._neigh_idx, bonds_indices, verbose_DMI, output_form, file_handle, verbosity)
        if iso:  verbose_bond_exchanges_no_double_counting(self._J_iso, *args) 
        else:    verbose_bond_exchanges_no_double_counting(self._Jmat, *args) 



    def shell_isotropic_exch_energy(self,sp_lat,boundary_condition=[1,1,1],parallel=False):
        shape = sp_lat.shape
        nx,ny,nz,nat,dyn_idx = get_dynamics_sites_indices(shape)
        ntask = len(dyn_idx)
        start,last = (0,ntask)
        if parallel and enable_mpi: start,last = mt.assign_task(ntask,size,rank)
        E_iso = 0.
        for ii,idx0 in enumerate(dyn_idx[start:last]):
            iat = idx0[-1]
            n_i = sp_lat[tuple(idx0)]
            if self._neigh_idx[iat] is None: continue
            for j,idx_n in enumerate(self._neigh_idx[iat]):
                idx1 = calc_neigh_bond_idx(idx0,idx_n,shape,boundary_condition)
                if idx1 is not None:
                    n_j = sp_lat[tuple(idx1)]
                    E_iso -= self._J_iso[iat][j]*np.dot(n_i,n_j)
        if parallel: E_iso = comm.allreduce(E_iso)
        return E_iso/2


    def shell_exch_energy(self,sp_lat,boundary_condition=[1,1,1],parallel=False):
        shape = sp_lat.shape
        nx,ny,nz,nat,dyn_idx = get_dynamics_sites_indices(shape)
        ntask = len(dyn_idx)
        start,last = (0,ntask)
        if parallel and enable_mpi: start,last = mt.assign_task(ntask,size,rank)
 
        E_iso = 0.
        E_DMI = 0.
        for idx0 in dyn_idx[start:last]:
            iat = idx0[-1]
            n_i = sp_lat[tuple(idx0)]
            for j,idx_n in enumerate(self._neigh_idx[iat]):
                idx1 = calc_neigh_bond_idx(idx0,idx_n,shape,boundary_condition)
                if idx1 is not None:
                    n_j = sp_lat[tuple(idx1)]
                    E_iso -= self._J_iso[iat][j]*np.dot(n_i,n_j)
                    if self._DM_xyz is not None: 
                        #E_DMI -= np.dot(np.cross(n_i,n_j),self._DM_xyz[iat][j])
                        E_DMI -= np.linalg.det([self._DM_xyz[iat][j],n_i,n_j])
        if parallel: 
            E_iso = comm.allreduce(E_iso)
            E_sym = comm.allreduce(E_sym)
            E_DMI = comm.allreduce(E_DMI)
        return E_iso/2, E_DMI/2


    def shell_exch_energy_from_sym_mat(self,sp_lat,boundary_condition=[1,1,1],parallel=False):
        shape = sp_lat.shape
        nx,ny,nz,nat,dyn_idx = get_dynamics_sites_indices(shape)
        ntask = len(dyn_idx)
        start,last = (0,ntask)
        if parallel and enable_mpi: start,last = mt.assign_task(ntask,size,rank)
        E_sym = 0.
        E_DMI = 0.
        for idx0 in dyn_idx[start:last]:
            iat = idx0[-1]
            if self._neigh_idx[iat] is None: continue
            elif len(self._neigh_idx[iat])==0: continue
            n_i = sp_lat[tuple(idx0)]
            for j,idx_n in enumerate(self._neigh_idx[iat]):
                idx1 = calc_neigh_bond_idx(idx0,idx_n,shape,boundary_condition)
                if idx1 is not None:
                    n_j = sp_lat[tuple(idx1)]
                    if self._J_sym_xyz is not None: E_sym -= np.einsum('a,ab,b', n_i, self._J_sym_xyz[iat][j] ,n_j)
                    if self._DM_xyz is not None: E_DMI -= np.linalg.det([self._DM_xyz[iat][j],n_i,n_j])
        if parallel: 
            E_sym = comm.allreduce(E_sym)
            E_DMI = comm.allreduce(E_DMI)
        return E_sym/2, E_DMI/2


    def shell_exch_energy_from_Jmat(self,sp_lat,boundary_condition=[1,1,1],parallel=False):
        if self._Jmat is None: return 0
        shape = sp_lat.shape
        nx,ny,nz,nat,dyn_idx = get_dynamics_sites_indices(shape)
        ntask = len(dyn_idx)
        start,last = (0,ntask)
        if parallel and enable_mpi: start,last = mt.assign_task(ntask,size,rank)
        E_exch = 0.
        for idx0 in dyn_idx[start:last]:
            iat = idx0[-1]
            if self._neigh_idx[iat] is None: continue
            elif len(self._neigh_idx[iat])==0: continue
            n_i = sp_lat[tuple(idx0)]
            for j,idx_n in enumerate(self._neigh_idx[iat]):
                idx1 = calc_neigh_bond_idx(idx0,idx_n,shape,boundary_condition)
                if idx1 is not None:
                    n_j = sp_lat[tuple(idx1)]
                    E_exch -= np.einsum('a,ab,b', n_i, self._Jmat[iat][j],n_j)
        if parallel: E_exch = comm.allreduce(E_exch)
        return E_exch/2


    def shell_exch_energy_from_Jmat_new(self,sp_lat):
        nat = sp_lat.shape[-2]
        E_exch = 0
        for iat in range(nat):
            for j,idx_n in enumerate(self._neigh_idx[iat]):
                dR = idx_n[:-1]
                jat = idx_n[-1]
                sp_lat_tmp = np.roll(sp_lat,tuple(-dR),axis=range(len(dR)))
                E_exch -= np.einsum('...m,mn,...n',sp_lat[...,iat,:],self._Jmat[iat,j],sp_lat_tmp[...,jat,:]).sum()
        return E_exch/2


    def local_exchange_energy(self,sp_lat,site_idx,boundary_condition=[1,1,1]):
        shape=sp_lat.shape
        E_local = 0.
        iat = site_idx[-1]
        n_i = sp_lat[tuple(site_idx)]
        for inn, idx_n in enumerate(self._neigh_idx[iat]):
            idx1 = calc_neigh_bond_idx(site_idx,idx_n,shape,boundary_condition)
            if idx1 is None: continue
            n_j = sp_lat[tuple(idx1)]
            if self._Jmat is not None: E_local -= np.dot(np.dot(n_i,self._Jmat[iat][inn]),n_j)
            else: E_local -= self._J_iso[iat][inn] * np.dot(n_i,n_j)
        return E_local
 

    def shell_isotropic_exch_field(self,sp_lat,site_idx,boundary_condition=[1,1,1]):
        shape = sp_lat.shape
        B_eff = np.zeros(3,float)
        iat = site_idx[-1]
        n_i = sp_lat[tuple(site_idx)]
        if self._neigh_idx[iat] is None: return B_eff
        for j,idx_n in enumerate(self._neigh_idx[iat]):
            idx1 = calc_neigh_bond_idx(site_idx,idx_n,shape,boundary_condition)
            if idx1 is not None:
                n_j = sp_lat[tuple(idx1)]
                B_eff += self._J_iso[iat][j]*n_j
        return B_eff


    def local_exch_field(self,sp_lat,site_idx,boundary_condition=[1,1,1]):
        shape = sp_lat.shape
        B_eff = np.zeros(3,float)
        iat = site_idx[-1]
        n_i = sp_lat[tuple(site_idx)]
        for inn, idx_n in enumerate(self._neigh_idx[iat]):
            idx1 = calc_neigh_bond_idx(site_idx,idx_n,shape,boundary_condition)
            if idx1 is not None:
                n_j = sp_lat[tuple(idx1)]
                B_eff += self._J_iso[iat][inn]*n_j
                B_eff += np.cross(n_j,self._DM_xyz[iat][inn])
        return B_eff


    def local_exch_field_from_sym_mat(self,sp_lat,site_idx,boundary_condition=[1,1,1]):
        shape = sp_lat.shape
        B_eff = np.zeros(3,float)
        iat = site_idx[-1]
        n_i = sp_lat[tuple(site_idx)]
        for j,idx_n in enumerate(self._neigh_idx[iat]):
            idx1 = calc_neigh_bond_idx(site_idx,idx_n,shape,boundary_condition)
            if idx1 is not None:
                n_j = sp_lat[tuple(idx1)]
                B_eff += np.dot(self._J_sym_xyz[iat][j], n_j)
                B_eff += np.cross(n_j,self._DM_xyz[iat][j])
        return B_eff


    def local_exch_field_from_Jmat(self,sp_lat,site_idx,boundary_condition=[1,1,1]):
        B_eff = np.zeros(3)
        if self._Jmat is None: return B_eff
        iat = site_idx[-1]

 
        n_i = sp_lat[tuple(site_idx)]
        shape = sp_lat.shape
        for j,idx_n in enumerate(self._neigh_idx[iat]):
            idx1 = calc_neigh_bond_idx(site_idx,idx_n,shape,boundary_condition)
            if idx1 is not None:
                n_j = sp_lat[tuple(idx1)]
                B_eff += np.dot(self._Jmat[iat][j], n_j)
        return B_eff


    def local_exch_field_from_Jmat_new(self,sp_lat,site_idx):
        neigh_idx_all = calc_neighbors_in_sp_lat(self._neigh_idx,sp_lat)
        B_eff = np.zeros(3,float)
        iat = site_idx[-1]
        for inn,idx1 in enumerate(neigh_idx_all[tuple(site_idx)]):
            n_j = sp_lat[tuple(idx1)]
            B_eff += np.dot(self._Jmat[iat][inn], n_j)
        return B_eff



# we currently only support scalar biquadratic exchange
# the magnitude is given by BQ
class biquadratic_exchange_shell():
    def __init__(self,neigh_idx,BQ,shell_name):
        self._neigh_idx = neigh_idx
        self._BQ = BQ
        self._shell_name = shell_name
        self._nat = len(self._neigh_idx)


    def verbose_interactions(self,file_handle=None):
        print ('\nBiquadratic exchange {}'.format(self._shell_name),file=file_handle)
        try: print (('{:8.5f} '*len(self._BQ)+'\n').format(*tuple(self._BQ)),file=file_handle)
        except: print ('None',file=file_handle)


    def shell_exch_energy(self,sp_lat,boundary_condition=[1,1,1],parallel=False):
        shape = sp_lat.shape
        nx,ny,nz,nat,dyn_idx = get_dynamics_sites_indices(shape)
        ntask = len(dyn_idx)
        start,last = (0,ntask)
        if parallel and enable_mpi: start,last = mt.assign_task(ntask,size,rank)
        E_bq = 0.
        for idx0 in dyn_idx[start:last]:
            iat = idx0[-1]
            n_i = sp_lat[tuple(idx0)]
            for j,idx_n in enumerate(self._neigh_idx[iat]):
                idx1 = calc_neigh_bond_idx(idx0,idx_n,shape,boundary_condition)
                if idx1 is not None:
                    n_j = sp_lat[tuple(idx1)]
                    E_bq -= self._BQ[iat] * (n_i[2]*n_j[2])**2
        return E_bq/2


    def shell_exch_energy_new(self,sp_lat):
        neigh_idx_all = calc_neighbors_in_sp_lat(self._neigh_idx,sp_lat)
        shape = sp_lat.shape
        E_bq = 0.
        for idx0 in np.ndindex(shape[:-1]):
            n_i = sp_lat[tuple(idx0)]
            iat = idx0[-1]
            for j,idx1 in enumerate(neigh_idx_all[tuple(idx0)]):
                n_j = sp_lat[tuple(idx1)]
                E_bq -= self._BQ[iat] * (n_i[2]*n_j[2])**2
        if parallel: E_bq = comm.allreduce(E_bq)
        return E_bq/2


    def local_exch_field(self,sp_lat,site_idx,boundary_condition=[1,1,1]):
        shape = sp_lat.shape
        iat = site_idx[-1]
        n_i = sp_lat[tuple(site_idx)]
        B_eff = np.zeros(3)
        for j,idx_n in enumerate(self._neigh_idx[iat]):
            idx1 = calc_neigh_bond_idx(site_idx,idx_n,shape,boundary_condition)
            if idx1 is not None:
                n_j = sp_lat[tuple(idx1)]
                B_eff += 2*self._BQ[iat]*n_i[2]*n_j[2]**2
        return B_eff


    def local_exch_field_new(self,sp_lat,site_idx):
        neigh_idx_all = calc_neighbors_in_sp_lat(self._neigh_idx,sp_lat)
        shape = sp_lat.shape
        n_i = sp_lat[tuple(site_idx)]
        iat = site_idx[-1]
        B_eff = np.zeros(3)
        for j,idx1 in enumerate(neigh_idx_all[tuple(site_idx)]):
            n_j = sp_lat[tuple(idx1)]
            B_eff += 2*self._BQ[iat]*n_i[2]*n_j[2]**2
        return B_eff


# A generic form of biquadratic exchange
# in the form of (S_i * B_{ij} * S_j)**2
# the parameter BQ should be an numpy.ndarray
# in shape of (nat,n_neigh,3,3)
# One should note that, for the BQ matrix here
# the zz component is indeed the square root 
# of the BQ exchange in biquadratic_exchange_shell
# the previous class
class biquadratic_exchange_shell_general():
    def __init__(self,neigh_idx,BQ,shell_name):
        self._neigh_idx = neigh_idx
        self._BQ = BQ
        self._shell_name = shell_name
        self._nat = len(self._neigh_idx)


    def verbose_interactions(self,file_handle=None):
        print ('\nBiquadratic exchange {}, in generic matrix form'.format(self._shell_name),file=file_handle)
        verbose_exchange_matrix(self._neigh_idx,self._BQ,'Biquadratic exchange',file_handle=file_handle)


    def shell_exch_energy(self,sp_lat,boundary_condition=[1,1,1],parallel=False):
        shape = sp_lat.shape
        nx,ny,nz,nat,dyn_idx = get_dynamics_sites_indices(shape)
        ntask = len(dyn_idx)
        start,last = (0,ntask)
        if parallel and enable_mpi: start,last = mt.assign_task(ntask,size,rank)
        E_bq = 0.
        for idx0 in dyn_idx[start:last]:
            iat = idx0[-1]
            n_i = sp_lat[tuple(idx0)]
            for j,idx_n in enumerate(self._neigh_idx[iat]):
                idx1 = calc_neigh_bond_idx(idx0,idx_n,shape,boundary_condition)
                if idx1 is not None:
                    n_j = sp_lat[tuple(idx1)]
                    E_bq -= np.einsum('mn,m,n', self._BQ[iat,j], n_i, n_j)**2
        if parallel: E_bq = comm.allreduce(E_bq)
        return E_bq/2


    def shell_exch_energy_new(self,sp_lat):
        E_bq = 0.
        for iat in range(nat):
            for j,idx_n in enumerate(self._neigh_idx[iat]):
                dR = idx_n[:-1]
                jat = idx_n[-1]
                sp_lat_tmp = np.roll(sp_lat,tuple(-dR),axis=range(len(dR)))
                E_bq -= (np.einsum('...m,mn,...n',sp_lat[...,iat,:],self._BQ[iat,j],sp_lat_tmp[...,jat,:])**2).sum()
        return E_bq/2


    def local_exchange_energy(self,sp_lat,site_idx,boundary_condition=[1,1,1]):
        shape = sp_lat.shape
        E_local = 0.
        iat = site_idx[-1]
        n_i = sp_lat[tuple(site_idx)]
        for j,idx_n in enumerate(self._neigh_idx[iat]):
            idx1 = calc_neigh_bond_idx(site_idx,idx_n,shape,boundary_condition)
            if idx1 is None: continue
            n_j = sp_lat[tuple(idx1)]
            E_local -= np.einsum('mn,m,n', self._BQ[iat,j], n_i, n_j)**2
        return E_local


    def local_exch_field(self,sp_lat,site_idx,boundary_condition=[1,1,1]):
        shape = sp_lat.shape
        iat = site_idx[-1]
        n_i = sp_lat[tuple(site_idx)]
        B_eff = np.zeros(3)
        for j,idx_n in enumerate(self._neigh_idx[iat]):
            idx1 = calc_neigh_bond_idx(site_idx,idx_n,shape,boundary_condition)
            if idx1 is not None:
                n_j = sp_lat[tuple(idx1)]
                B_eff += 2*np.einsum('mn,m,n',self._BQ[iat,j],n_i,n_j) * np.dot(self._BQ[iat,j], n_j)
        return B_eff


    def local_exch_field_new(self,sp_lat,site_idx):
        n_i = sp_lat[tuple(site_idx)]
        iat = site_idx[-1]
        B_eff = np.zeros(3)
        for j,idx_n in enumerate(self._neigh_idx[iat]):
            dR = idx_n[:-1]
            jat = idx_n[-1]
            sp_lat_tmp = np.roll(sp_lat,tuple(-dR),axis=range(len(dR)))
            n_j = sp_lat_tmp[tuple(idx_n)]
            B_eff += 2*np.einsum('mn,m,n',self._BQ[iat,j],n_i,n_j) * np.dot(self._BQ[iat,j],n_j)
        return B_eff


    # exchange field over the whole spin lattice
    def shell_exch_field(self,sp_lat):
        B_eff = np.zeros_like(sp_lat)
        nat = sp_lat.shape[-2]
        for iat in range(nat):
            for j,idx_n in enumerate(self._neigh_idx[iat]):
                dR = idx_n[:-1]
                jat = idx_n[-1]
                sp_lat_tmp = np.roll(sp_lat,tuple(-dR),axis=tuple(range(len(dR))))
                B_eff[...,iat,:] += 2*np.einsum('mn,...m,...n->...',self._BQ[iat,j],sp_lat[...,iat,:],sp_lat_tmp[...,jat,:]) * np.dot(self._BQ[iat,j],sp_lat_tmp[...,jat,:])
        return B_eff





# four-site biquadratic exchange coupling
class four_site_biquadratic_exchange_shell():
    def __init__(self,neigh_idx,BQ,shell_name):
        self._neigh_idx = neigh_idx
        self._BQ = BQ
        self._shell_name = shell_name
        self._nat = len(self._neigh_idx)


    def verbose_interactions(self,file_handle=None):
        print ('\nFour-site Biquadratic exchange {}, in generic matrix form'.format(self._shell_name),file=file_handle)
        verbose_exchange_matrix(self._neigh_idx,self._BQ,'Biquadratic exchange',file_handle=file_handle)


    def shell_exch_energy(self,sp_lat,boundary_condition=[1,1,1],parallel=False):
        shape = sp_lat.shape
        nx,ny,nz,nat,dyn_idx = get_dynamics_sites_indices(shape)
        ntask = len(dyn_idx)
        start,last = (0,ntask)
        if parallel and enable_mpi: start,last = mt.assign_task(ntask,size,rank)
        E_bq = 0.
        for idx0 in dyn_idx[start:last]:
            iat = idx0[-1]
            n_i = sp_lat[tuple(idx0)]
            neigh_idx = self._neigh_idx[iat]
            if neigh_idx is None: continue
            for inn,idx_n in enumerate(neigh_idx):
                idx_j = calc_neigh_bond_idx(idx0,idx_n[0],shape,boundary_condition)
                idx_k = calc_neigh_bond_idx(idx0,idx_n[1],shape,boundary_condition)
                idx_l = calc_neigh_bond_idx(idx0,idx_n[2],shape,boundary_condition)
                #if None in [idx_j,idx_k,idx_l]: continue
                if idx_j is None or idx_k is None or idx_l is None: continue
                n_j = sp_lat[tuple(idx_j)]
                n_k = sp_lat[tuple(idx_k)]
                n_l = sp_lat[tuple(idx_l)]
                E_bq -= self._BQ[iat,inn] * np.dot(n_i, n_j) * np.dot(n_k, n_l)
        if parallel:  E_bq = comm.allreduce(E_bq)
        return E_bq


    def shell_exch_energy_new(self,sp_lat):
        E_bq = 0.
        for iat in range(nat):
            for j,idx_n in enumerate(self._neigh_idx[iat]):
                dR = idx_n[:-1]
                jat = idx_n[-1]
                sp_lat_tmp = np.roll(sp_lat,tuple(-dR),axis=range(len(dR)))
                E_bq -= (np.einsum('...m,mn,...n',sp_lat[...,iat,:],self._BQ[iat,j],sp_lat_tmp[...,jat,:])**2).sum()
        return E_bq


    def local_exchange_energy(self,sp_lat,site_idx,boundary_condition=[1,1,1]):
        E_local = 0.
        iat = site_idx[-1]
        n_i = sp_lat[tuple(site_idx)]
        for inn,idx_n in enumerate(self._neigh_idx[iat]):
            idx_j = calc_neigh_bond_idx(idx0,idx_n[0],shape,boundary_condition)
            idx_k = calc_neigh_bond_idx(idx0,idx_n[1],shape,boundary_condition)
            idx_l = calc_neigh_bond_idx(idx0,idx_n[2],shape,boundary_condition)
            if idx_j is None or idx_k is None or idx_l is None: continue
            n_j = sp_lat[tuple(idx_j)]
            n_k = sp_lat[tuple(idx_k)]
            n_l = sp_lat[tuple(idx_l)]
            E_local -= self._BQ[iat,inn] * np.dot(n_i, n_j) * np.dot(n_k, n_l)
        return E_local


    def local_exch_field(self,sp_lat,site_idx,boundary_condition=[1,1,1]):
        shape = sp_lat.shape
        iat = site_idx[-1]
        n_i = sp_lat[tuple(site_idx)]
        B_eff = np.zeros(3)
        for inn,idx_n in enumerate(self._neigh_idx[iat]):
            idx_j = calc_neigh_bond_idx(site_idx,idx_n[0],shape,boundary_condition)
            idx_k = calc_neigh_bond_idx(site_idx,idx_n[1],shape,boundary_condition)
            idx_l = calc_neigh_bond_idx(site_idx,idx_n[2],shape,boundary_condition)
            #if None in [idx_j,idx_k,idx_l]: continue
            if idx_j is None or idx_k is None or idx_l is None: continue
            n_j = sp_lat[tuple(idx_j)]
            n_k = sp_lat[tuple(idx_k)]
            n_l = sp_lat[tuple(idx_l)]
            B_eff += self._BQ[iat,inn] * n_j * np.dot(n_k, n_l)
        return B_eff


    def local_exch_field_new(self,sp_lat,site_idx):
        n_i = sp_lat[tuple(site_idx)]
        iat = site_idx[-1]
        B_eff = np.zeros(3)
        for inn,idx_n in enumerate(self._neigh_idx[iat]):
            dR = idx_n[:-1]
            jat = idx_n[-1]
            sp_lat_tmp = np.roll(sp_lat,tuple(-dR),axis=range(len(dR)))
            n_j = sp_lat_tmp[tuple(idx_n)]
            B_eff += 2*np.einsum('mn,m,n',self._BQ[iat,j],n_i,n_j) * np.dot(self._BQ[iat,inn],n_j)
        return B_eff
