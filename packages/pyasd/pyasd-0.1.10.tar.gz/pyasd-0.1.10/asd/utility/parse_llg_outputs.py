#!/home/zsh/anaconda3/envs/zsh_py3/bin/python


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



#==========================================
# post-process of llg simulation results
# Shunhong Zhang
# szhang2@ustc.edu.cn
# last modified: Nov 12, 2021
#===========================================


import numpy as np
import os
import sys
import matplotlib.pyplot as plt
import matplotlib.tri as tri
import glob
import re
import pickle
import importlib
from asd.core.geometry import build_latt, get_repeated_sites
from asd.core.topological_charge import calc_topo_chg
from asd.utility.spin_visualize_tools import *
from asd.core.llg_simple import *



def plot_E_T(outdir='.',show=False):
    time,ener,diff_E,forc = get_dE_from_out(outdir)
    if time is None : 
        print ('skip plotting diff_E')
        return None,None,None

    fig,ax=plt.subplots(1,1)
    ax.plot(time,ener,'b-')
    ax.set_xlabel('Time (ps)')
    ax.set_ylabel('E (meV/site)',color='b')
    ax.tick_params(axis='y', labelcolor='b')
    if np.max(ener)-np.min(ener) < 0.1: ax.set_ylim(np.min(ener)-0.1,np.max(ener)+0.1)
    if diff_E is not None:
        axx=ax.twinx()
        axx.plot(time,np.log(abs(diff_E))/np.log(10),'r-')
        axx.set_ylabel('log|dE|',color='r')
        axx.tick_params(axis='y', labelcolor='r')
        axx.set_xlim(0,np.max(time))
    fig.tight_layout()
    fig.savefig('{}/E_T'.format(outdir),dpi=500)

    if forc is not None:
        fig1,ax1=plt.subplots(1,1)
        ax1.plot(time,np.log(abs(forc))/np.log(10),'g-')
        ax1.set_xlabel('Time (ps)')
        ax1.set_ylabel('log|forcee|')
        ax1.set_xlim(0,np.max(time))
        fig1.tight_layout()
        fig1.savefig('forc',dpi=500)
    return fig,ax,axx


def ax_plot_magnetization(ax,time,data):
    for i in range(3,6): ax.plot(time,data[:,i],label={3:'$M_x$',4:'$M_y$',5:'$M_z$'}[i])
    ax.plot(time,np.linalg.norm(data[:,3:5],axis=1),label='$M_\perp$')
    ax.plot(time,np.linalg.norm(data[:,3:6],axis=1),label='M')
    ax.legend(ncol=2)
    ax.set_xlim(np.min(time),np.max(time))
    ax.set_ylim(-1.1,1.1)
    ax.set_yticks(np.arange(-1,1.1,0.5))
    ax.set_xlabel('Time (ps)')
    ax.set_ylabel('M')
 


def plot_summary(outdir='.',fil='M.dat',plot_summary=True):
    data=np.loadtxt('{}/{}'.format(outdir,fil),skiprows=1)
    time = data[:,0]
    ener = data[:,1]
    diff_E = data[:,2]
    if not plot_summary: return data,False

    fig,ax=plt.subplots(2,1,sharex=True,figsize=(6,6))

    ax[0].plot(time,ener,'b-')
    ax[0].set_ylabel('E (meV/site)',color='b')
    ax[0].tick_params(axis='y', labelcolor='b')
    if np.max(ener)-np.min(ener) < 0.1: ax[0].set_ylim(np.min(ener)-0.1,np.max(ener)+0.1)

    if diff_E is not None:
        axx=ax[0].twinx()
        axx.plot(time,np.log(abs(diff_E))/np.log(10),'r-')
        axx.set_ylabel('log|dE|',color='r')
        axx.tick_params(axis='y', labelcolor='r')

    ax_plot_magnetization(ax[1],time,data)
    fig.tight_layout()
    fig.savefig('{}/E_M_T'.format(outdir),dpi=500)

    if data.shape[1]==7:
        Qs = data[:,-1]
        fig,ax=plt.subplots(1,1)
        ax.plot(time,Qs)
        ax.set_xlabel('Time (ps)')
        ax.set_ylabel('Q')
        ax.set_xlim(np.min(time),np.max(time))
        ax.set_ylim(min(-1.5,np.min(Qs)*1.05),max(1.5,np.max(Qs)*1.05))
        ax.axhline(0,c='gray',ls='--',lw=0.5,alpha=0.5,zorder=-2)
        fig.tight_layout()
        fig.savefig('topo_chg_evolution',dpi=600)
        calc_Q = False
    else:
        calc_Q = True

    return data,calc_Q



