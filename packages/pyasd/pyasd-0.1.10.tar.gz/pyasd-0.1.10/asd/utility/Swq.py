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
# structure factors of spin configurations
# in real space lattices
#
# Shunhong Zhang
# Last modified: Nov 27, 2021
#
#=============================================

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec
from asd.core.spin_correlations import *



def subplot_struct_factor(ax,
    qpt_cart,S_vector,colormap='parula',
    scatter_size=10,nqx=None,nqy=None,comp='normal',nn=1):

    if colormap=='parula':
        from asd.utility.auxiliary_colormaps import parula
        colormap=parula

    vmin = np.min(S_vector)/nn
    vmax = np.max(S_vector)/nn
    S_normal = S_vector[...,0] + S_vector[...,1]
    S_parall = S_vector[...,2]

    if comp=='normal': SS = S_normal
    if comp=='parall': SS = S_parall

    if nqx is not None and nqy is not None:
        extent = [np.min(qpt_cart[...,0]),np.max(qpt_cart[...,0]),np.min(qpt_cart[...,1]),np.max(qpt_cart[...,1])]
        SS = SS.reshape(nqx,nqy)
        kwargs = dict(origin='lower',extent=extent,cmap=colormap,vmin=vmin,vmax=vmax)
        scat = ax.imshow(SS.T,**kwargs)
    else:
        kwargs = dict(marker='o',s=scatter_size,cmap=colormap,vmin=vmin,vmax=vmax)
        scat = ax.scatter(*tuple(qpt_cart.T),c=SS,**kwargs)

    component = {'normal':'$S_\perp$','parall':'$S_\parallel$'}

    top=ax.get_ylim()[1]
    left=ax.get_xlim()[0]
    ax.text(left,top,component[comp],va='top',ha='left',fontsize=14,bbox=dict(facecolor='w'))
    ax.set_ylabel('$q_y$')
    ax.set_xlabel('$q_x$')
    ax.set_xlim(np.min(qpt_cart[:,0]),np.max(qpt_cart[:,0]))
    ax.set_ylim(np.min(qpt_cart[:,1]),np.max(qpt_cart[:,1]))
    ax.set_aspect('equal')
    ax.set_axis_off()

    return scat


def plot_struct_factor(qpt_cart,S_vector,figname='Struct_factor',colormap='parula',share_colorbar=False,
    scatter_size=10,align='vertical',show=True,nqx=None,nqy=None):

    if colormap=='parula':
        from asd.utility.auxiliary_colormaps import parula
        colormap=parula

    if share_colorbar:
        gs = {
        'vertical':   gridspec.GridSpec(3,1,height_ratios=(5,5,1)),
        'horizontal': gridspec.GridSpec(1,3,width_ratios =(5,5,1)) }
        figsize =  {'vertical':(5,10),'horizontal':(10,5)}

        fig=plt.figure(figsize=figsize[align])
        ax= [ fig.add_subplot(gs[align][i]) for i in range(3)]

    else:
        if align=='horizontal':
            fig, ax = plt.subplots(1,2,sharey=True,figsize=(10,5))
        elif align=='veritcal':
            fig, ax = plt.subplots(2,1,sharex=True,figsize=(5,10))

    vmin = np.min(S_vector)
    vmax = np.max(S_vector)
    S_normal = S_vector[:,0]+S_vector[:,1]
    S_parall = S_vector[:,2]
    if nqx is not None and nqy is not None:
        extent = [np.min(qpt_cart[:,0]),np.max(qpt_cart[:,0]),np.min(qpt_cart[:,1]),np.max(qpt_cart[:,1])]
        S_normal = S_normal.reshape(nqx,nqy)
        S_parall = S_parall.reshape(nqx,nqy)
        kwargs = dict(origin='lower',extent=extent,cmap=colormap,vmin=vmin,vmax=vmax)
        if share_colorbar==False: kwargs.update(vmin=np.min(S_normal),vmax=np.max(S_normal))
        scat1 = ax[0].imshow(S_normal.T,**kwargs)
        if share_colorbar==False: kwargs.update(vmin=np.min(S_parall), vmax=np.max(S_parall))
        scat2 = ax[1].imshow(S_parall.T,**kwargs)
    else:
        kwargs = dict(marker='o',s=scatter_size,cmap=colormap,vmin=vmin,vmax=vmax)
        if share_colorbar==False: kwargs.update(vmin=np.min(S_normal),vmax=np.max(S_normal))
        scat1 = ax[0].scatter(*tuple(qpt_cart.T),c=S_normal,**kwargs)
        if share_colorbar==False: kwargs.update(vmin=np.min(S_parall), vmax=np.max(S_parall))
        scat2 = ax[1].scatter(*tuple(qpt_cart.T),c=S_parall,**kwargs)

    component = {0:'$S_\perp$',1:'$S_\parallel$'}

    ori={'vertical':'horizontal','horizontal':'vertical'}[align]

    for i,ax0 in enumerate(ax[:2]):
        top=ax0.get_ylim()[1]
        left=ax0.get_xlim()[0]
        ax[i].text(left,top,component[i],va='top',ha='left',fontsize=14,bbox=dict(facecolor='w'))
        if align=='vertical':   ax0.set_ylabel('$q_y$')
        if align=='horizontal': ax0.set_xlabel('$q_x$')
        ax0.set_xlim(np.min(qpt_cart[:,0]),np.max(qpt_cart[:,0]))
        ax0.set_ylim(np.min(qpt_cart[:,1]),np.max(qpt_cart[:,1]))
        ax0.set_aspect('equal')
        ax0.set_axis_off()
    if align=='vertical':   ax[1].set_xlabel('$q_x$')
    if align=='horizontal': ax[0].set_ylabel('$q_y$')

    cb_kws = dict(orientation=ori, shrink=0.6)
    if share_colorbar:
        ax[2].set_axis_off()
        fig.colorbar(scat1, ax=ax[2], **cb_kws)
    else:
        fig.colorbar(scat1, ax=ax[0], **cb_kws)
        fig.colorbar(scat2, ax=ax[1], **cb_kws)
    fig.tight_layout()
    fig.savefig(figname,dpi=500)
    if show: plt.show()
    return fig


def animate_S_vectors(S_vectors,times,nqx,nqy,bound=2,comp='vertical',save=False,gif_name='S_vec'):
    from matplotlib.animation import FuncAnimation, PillowWriter
    def update(i,im,tl,SS,titles): 
        im.set_data(SS[i].T)
        tl.set_text(titles[i])

    nconf = S_vectors.shape[0]
    S_vectors = S_vectors.reshape(nconf,nqx,nqy,3)
    if comp=='vertical': SS = S_vectors[...,0] + S_vectors[...,1]
    if comp=='parallel': SS = S_vectors[...,2]

    fig,ax=plt.subplots(1,1)
    component = {'vertical':'$S_\perp$','parallel':'$S_\parallel$'}

    #kwargs = dict(cmap='hot',vmin=np.min(SS),vmax=np.max(SS))
    kwargs = dict()
    kwargs.update(origin='lower',extent=[-bound,bound,-bound,bound],aspect='equal')
    im = ax.imshow(SS[0].T,**kwargs)
    ax.set_xlabel('$q_x$')
    ax.set_ylabel('$q_y$')
    tl = ax.set_title('t = {:6.3f} ps'.format(times[0]))
    cbar = fig.colorbar(im,shrink=0.6)
    fig.tight_layout()
    titles = ['t = {:6.3f} ps'.format(tt) for tt in times]
    anim = FuncAnimation(fig, update, frames=range(nconf), interval=5e2, repeat=False,
    fargs=[im, tl, SS, titles])
    if save:
        print ('save animation to {0}.gif'.format(gif_name))
        anim.save('{0}.gif'.format(gif_name), dpi=gif_dpi, writer='imagemagick')
    else: plt.show()
    return anim



# analytic solution of magnon of 2D spin lattice
# within the framework of linear spin wave theroy
# Here Z1, Z2, ... are the coordination number
# J1, J2, ... are the heisenberg exchange of shells sorted by distance
# SIA is the single-ion anistropy which is assumed to be unified
# Here we assume the lattice constants of the real space magnetic unit cell to be 1
# The ground state should be Ferromagnetic along the z direction
def analytic_spin_wave_FM(lat_type,qpt_cart,J1,J2,SIA,DMI=0,S=1,freq_unit='meV'):

    def get_structure_factor_from_disp(qpt_cart,disp):
        ndim = disp.shape[1]
        struct_factor = np.sum(np.exp(2.j*np.pi*np.dot(qpt_cart[:,:ndim],disp.T)),axis=1).real/len(disp)
        return struct_factor

    def get_chiral_structure_factor_from_disp(qpt_cart,disp):
        nn = len(disp)//2
        f1 = np.sum(np.exp(2.j*np.pi*np.dot(qpt_cart, disp[:nn].T)),axis=1).real/len(disp)
        f2 = np.sum(np.exp(2.j*np.pi*np.dot(qpt_cart, disp[nn:].T)),axis=1).real/len(disp)
        return f1-f2


    r3=np.sqrt(3)
    r3h=r3/2
    nq = len(qpt_cart)
    if lat_type=='honeycomb':
        disp_1 = np.array([[r3h,-0.5],[-r3h,-0.5],[0,1]])/r3
        disp_2 = np.array([[1,0],[0.5,r3h],[-0.5,r3h],[-0.5,r3h],[-1,0],[-0.5,-r3h]])
    elif lat_type=='square':
        disp_1 = np.array([[1,0],[0,1],[-1,0],[0,-1]])
        disp_2 = np.array([[1,1],[-1,1],[-1,-1],[1,-1]])
    elif lat_type=='triangular':
        disp_1 = np.array([[1,0],[0.5,r3h],[-0.5,r3h],[-1,0],[-0.5,-r3h],[0.5,-r3h]])
        disp_2 = np.array([[3/2,r3h],[0,r3],[-3/2,r3h],[-3/2,-r3h],[0,-r3],[3/2,r3h]])
    elif lat_type=='chain':
        disp_1 = np.array([[-1],[1]])
        disp_2 = np.array([[-2],[2]])

    if lat_type!='kagome':
        Z1 = len(disp_1)
        Z2 = len(disp_2)
    if lat_type=='honeycomb':   # two bands for diatomic latice
        gamma_k_1 = get_structure_factor_from_disp(qpt_cart,disp_1)
        gamma_k_2 = get_structure_factor_from_disp(qpt_cart,disp_2)
        ham = np.zeros((nq,2,2))
        ham[:,0,1] = - Z1*J1*S*gamma_k_1 - Z2*J2*S*gamma_k_2
        ham[:,1,0] = ham[:,0,1].conj()
        for i in range(2): ham[:,i,i] = Z1*J1*S + Z2*J2*S + 2*SIA*S
        magnon = np.linalg.eigh(ham)[0].T
    elif lat_type=='kagome':
        Z1 = 2
        Z2 = 2
        disp_1_ab = np.array([[1,0],[-1,0]])/2
        disp_1_bc = np.array([[0.5, r3h],[-0.5,-r3h]])/2
        disp_1_ca = np.array([[0.5,-r3h],[-0.5, r3h]])/2
        disp_2_ab = np.array([[0,1],[0,-1]])/r3h
        disp_2_bc = np.array([[-r3h,0.5],[r3h,-0.5]])/r3h
        disp_2_ca = np.array([[-r3h,-0.5],[r3h,0.5]])/r3h

        gamma_k_1_ab = get_structure_factor_from_disp(qpt_cart,disp_1_ab) 
        gamma_k_1_bc = get_structure_factor_from_disp(qpt_cart,disp_1_bc) 
        gamma_k_1_ca = get_structure_factor_from_disp(qpt_cart,disp_1_ca) 
        gamma_k_2_ab = get_structure_factor_from_disp(qpt_cart,disp_2_ab)
        gamma_k_2_bc = get_structure_factor_from_disp(qpt_cart,disp_2_bc)
        gamma_k_2_ca = get_structure_factor_from_disp(qpt_cart,disp_2_ca)

        ham = np.zeros((nq,3,3))
        ham[:,0,1] = - Z1*J1*S*gamma_k_1_ab - Z2*J2*S*gamma_k_2_ab
        ham[:,1,2] = - Z1*J1*S*gamma_k_1_bc - Z2*J2*S*gamma_k_2_bc
        ham[:,2,0] = - Z1*J1*S*gamma_k_1_ca - Z2*J2*S*gamma_k_2_ca
        ham += np.swapaxes(ham.conj(),1,2)
        for i in range(3): ham[:,i,i] = 2*Z1*J1 + 2*Z2*J2 + 2*SIA*S
        magnon = np.linalg.eigh(ham)[0].T
    else: 
        gamma_k_1 = get_structure_factor_from_disp(qpt_cart,disp_1)
        gamma_k_2 = get_structure_factor_from_disp(qpt_cart,disp_2)
        magnon1 = 2*Z1*J1*S*(1-gamma_k_1) + 2*Z2*J2*S*(1-gamma_k_2) + 4*SIA*S
        if DMI!=0:
            chiral_gamma_k_1 = get_chiral_structure_factor_from_disp(qpt_cart,disp_1)
            magnon1 += 2*Z1*DMI*S * chiral_gamma_k_1
        magnon = np.array([magnon1])
    if freq_unit=='THz': freqs = magnon*meV_to_THz
    elif freq_unit=='meV': freqs = magnon
    return freqs



def bandmap(dynS,q_dists,q_nodes,labels,max_omega,comp='xy',show=True,
    analytic_spectra=None,figname='dyn_struct_factor',plot_en_axis=True):
    from .auxiliary_colormaps import parula
    dirs = {'x':0,'y':1,'z':2}
    if len(comp)==2: SS = np.linalg.norm(dynS[...,[dirs[comp[0]],dirs[comp[1]]]],axis=-1)
    else: SS = dynS[...,dirs[comp]]
    griddata = SS.T.real
    griddata = np.log(abs(griddata))/np.log(10)
    fig,ax=plt.subplots(1,1,figsize=(6,6))
    kwargs=dict(origin='lower',extent=[q_dists[0],q_dists[-1],0,max_omega],aspect='auto',cmap=parula)
    im = ax.imshow(griddata,**kwargs)
    ax.set_xticks(q_nodes)
    ax.set_xticklabels(['${}$'.format(item) for item in labels.split()])
    ax.set_ylabel('$\omega\ \mathrm{(THz)}$')
    cbar = fig.colorbar(im,shrink=0.6,orientation='horizontal')
    cbar.ax.set_title('$\mathrm{Log}\ \\vert S_{'+comp+'}\ (\mathbf{q},\omega) \\vert$')
    colors=['r','g','b','c']
    if analytic_spectra is not None:
        for i,sw in enumerate(analytic_spectra): ax.plot(q_dists,sw,c=colors[i])
    if plot_en_axis:
        tax=ax.twinx()
        ylim=ax.get_ylim()
        tax.set_ylim(ylim[0]/meV_to_THz,ylim[1]/meV_to_THz)
        tax.set_ylabel('$\\hbar \omega\ \mathrm{(meV)}$')
    fig.tight_layout()
    fig.savefig(figname,dpi=400)
    if show: plt.show()
    return fig



# Autocorrelations of spins, defined as C(t, t_w) = <S_{t+t_w, i} \cdot S_{t,i}>/N
# N is number of sites and S_{i, t} is the spin vector of the i-th site at the moment t
# <...> means site average, t_w is a waiting time after which correlations are calculated
# See asd.core.spin_correlations for the function "calculate_auto_correlation"
def plot_auto_correlation(auto_corr, dt, tw_index, title=None, figname='auto_correlation', show=True):
    #print ('Time spacing between adjacent configurations : {:6.3f} ps'.format(dt))
    fig, ax = plt.subplots(1,1)
    if len(tw_index)==1:
        dyn_times = dt*np.arange(len(auto_corr))
        ax.plot(dyn_times, auto_corr)
    else:
        for iw,tw in enumerate(tw_index):
            dyn_times = dt*np.arange(len(auto_corr[iw]))
            ax.plot(dyn_times, auto_corr[iw], label='{:5.3f}'.format(tw*dt))
        lg = ax.legend(fontsize=12)
        lg.set_title(r'$t_w$ (ps)')
    ax.set_xscale('log')
    ax.set_xlabel(r'$t$ (ps)',fontsize=12)
    ax.set_ylabel(r'$C\ (t, t_w$)',fontsize=12)
    ax.set_ylim(-0.1,1.1)
    note = r'$C(t, t_w) = \frac{1}{N} \sum_i^N{< \mathbf{m}_i(t+t_w) \cdot \mathbf{m}_i(t_w) >}$'
    #ax.text(0.5, 0., note, fontsize=12, ha='left', va='center')
    if title is not None: ax.set_title(title, fontsize=12)
    fig.tight_layout()
    fig.savefig(figname,dpi=300)
    if show: plt.show()
    return fig

