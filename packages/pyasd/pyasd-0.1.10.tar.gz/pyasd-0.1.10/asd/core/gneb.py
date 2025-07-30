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


#==============================================================
# Geodesic Nudged Elastic Band (GNEB)
# Estimate barriers of transition between two 
# stable of metastable magnetic states
# Shunhong Zhang
# Mar 05, 2022
#==============================================================

# TODO: try to make the energy and gradient calculation more generic
# probably without involve the spin_hamiltonian object
# to realize this we may need 
# en_calc_func, en_calc_func_args
# en_grad_func, en_grad_func_args
# which can be passed to the run_gneb function 
# as positional arguments


import numpy as np
import time
import copy, os, sys
import pickle
from asd.core.constants import muB
from asd.utility.head_figlet import neb_text,pkg_info
from asd.utility.ovf_tools import gen_params_for_ovf,write_ovf,parse_ovf
from scipy.spatial.transform import Rotation as RT
from asd.core.shell_exchange import get_dynamics_sites_indices
from asd.core.log_general import log_general

log_fmt = '{:10d} {:10.3f} {:10d}'


log_handle = log_general(
prefix='GNEB',
n_log_conf = 10,
n_log_ener = 10)


def rot_vec_small_angle(vec,delta=0.001):
    new_vec = copy.copy(vec)
    for i in range(3):
        j = (i+1)%3
        if vec[i]!=0 or vec[j]!=0:
            rr = np.linalg.norm([vec[i],vec[j]])
            angle = np.angle(vec[i]+1.j*vec[j])
            new_vec[i] = rr*np.cos(angle+delta)
            new_vec[j] = rr*np.sin(angle+delta)
            return new_vec


def linear_interpolate_images(conf_init,conf_finl,nimage=10,pinned_idx=None,final_image_from_interpolation=True):
    shape = conf_init.shape
    assert shape==conf_finl.shape,'initial and final configs should be in the same shape!'
    nx,ny,nz,nat,dyn_idx = get_dynamics_sites_indices(shape, pinned_idx=pinned_idx)
    confs = np.zeros((nimage+2,*tuple(shape)))
    confs[0]  = conf_init
    confs[-1] = conf_finl
    for idx in dyn_idx:
        n1 = conf_init[tuple(idx)]
        n2 = conf_finl[tuple(idx)]
        if np.linalg.norm(n1-n2)<1e-3:
            for ii in range(1,nimage+2): confs[ii][tuple(idx)] = n1
        else:
            vec = np.cross(n1,n2)
            norm = np.linalg.norm(vec)
            if norm < 1e-3:
                n2_new = rot_vec_small_angle(n2)
                vec = np.cross(n1,n2_new)
            vec = vec/np.linalg.norm(vec)
            dot_prod = np.dot(n1,n2)
            angle = np.arccos(dot_prod/np.linalg.norm(n1)/np.linalg.norm(n2))
            angle_step = angle/(nimage+1)
            for ii in range(1,nimage+2):
                mat = RT.from_rotvec(vec*angle_step*ii).as_matrix()
                confs[ii][tuple(idx)] = np.dot(mat,n1)
    if final_image_from_interpolation == False: confs[-1] = conf_finl
    return confs



# conventional defination of tangent, may lead to kinks on path
def get_tangent_vec(image_1,image_2):
    diff = image_2 - image_1
    tangent = diff - np.einsum('...,...i->...i',np.einsum('...i,...i->...',diff,image_1),image_1)
    norm = np.linalg.norm(tangent,axis=-1)
    norm[norm==0]=1
    return  np.einsum('...i,...->...i',tangent, 1/norm)


# improved defination of tangent to path, 
# see J Chem Phys 113, 9978 (2000)
# and  Appendix A, Computer Physics Communications 196, 335 (2015)
# requires knowledges of left and right neighboring images
# and their corresponding energies
def get_tangent_vec_improved(image_left,image_current,image_right,
    en_left,en_current,en_right):

    diffE = [abs(en_left-en_current), abs(en_right-en_current)]
    dE_max, dE_min = ( max(diffE), min(diffE) )
    t_p = image_right - image_current
    t_m = image_current - image_left
    if   en_left < en_current < en_right:  tangent = t_p
    elif en_left > en_current > en_right:  tangent = t_m
    else:
        if  en_right > en_left: tangent = dE_max*t_p + dE_min*t_m
        else:                   tangent = dE_min*t_p + dE_max*t_m
    tangent_proj = tangent - np.einsum('...,...i->...i',np.einsum('...i,...i->...',tangent,image_current),image_current)
    norm = np.linalg.norm(tangent_proj,axis=-1)
    norm[norm==0]=1
    return  np.einsum('...i,...->...i',tangent_proj, 1/norm)


# assume all spin vectors with the norm 1
def get_geodesic_distance_cosines(image_1,image_2):
    dist = np.arccos(np.einsum('...i,...i->...',image_1,image_2))
    return np.linalg.norm(dist)


def get_geodesic_distance_haversine(image_1,image_2):
    x = np.einsum('...i,...i->...',image_1,image_2)
    g = 2*np.arcsin((1-x)/2)
    return np.linalg.norm(g)


def arctan2(y,x):
    if x>0: return np.arctan(y/x)
    elif y>=0 and x<0: return np.arctan(y/x)+np.pi
    elif y<0 and x<0 : return np.arctan(y/x)-np.pi
    elif y>0 and x==0: return np.pi/2
    elif y<0 and x==0: return -np.pi/2
    else: return None


def get_geodesic_distance_Vincenty(image_1,image_2):
    y = np.linalg.norm(np.cross(image_1,image_2),axis=-1)
    x = np.einsum('...i,...i->...',image_1,image_2)
    g = np.zeros_like(x)
    for idx,xx in np.ndenumerate(x):
        g[tuple(idx)] = arctan2(y[tuple(idx)],xx)
    return np.linalg.norm(g)


def get_geodesic_distance(image_1,image_2,method='Vincenty'):
    if method=='cosines':      return get_geodesic_distance_cosines(image_1,image_2)
    elif method=='haversine':  return get_geodesic_distance_haversine(image_1,image_2)
    elif method=='Vincenty':   return get_geodesic_distance_Vincenty(image_1,image_2)
    else: raise ValueError("Wrong method of get_geodesic_distance: {}".format(method))



# geodesic distance in unit of rad
# so the spring constant is in unit of meV/rad
# the local B_eff calculated from ham is converted
# from T to meV, by multiplying g_factor*S_value*muB
def calc_spring_force(ic,ham,confs,dists,eners,spring_const):
    shape = confs.shape
    nimage = shape[0]-2
    if ic == 0:
        tangent = get_tangent_vec(confs[ic],confs[ic+1]) # init conf, only right neighbor
        F_S = spring_const*dists[0]*tangent # Spring force 
    elif ic == nimage+1:
        tangent = get_tangent_vec(confs[ic],confs[ic-1]) # final conf, only left neighbor
        F_S = spring_const*dists[-1]*tangent # Spring force 
    else:
        tangent = get_tangent_vec_improved(confs[ic-1],confs[ic],confs[ic+1],*tuple(eners[ic-1:ic+2]))
        F_S = spring_const*(dists[ic] - dists[ic-1])*tangent # Spring force 
    return tangent,F_S


# only sites within the dyn_idx array are calculated
def calc_energy_gradient_force(ham,conf,tangent,dyn_idx,climb_image,dyn_only=False):
    F_E = np.zeros((len(dyn_idx),3))
    for ii,idx in enumerate(dyn_idx):
        B_eff = ham.calc_local_B_eff(conf,idx)  # B_eff = -grad(E) in unit of Tesla
        B_eff *= ham._g_factor * ham._S_values[idx[-1]]*muB  # convert to meV
        tangent_projection = np.dot(B_eff,tangent[tuple(idx)])*tangent[tuple(idx)]
        F_E[ii] = B_eff - tangent_projection
        if climb_image: F_E[ii] -= tangent_projection
    if dyn_only:
        return F_E
    else: 
        F_E_full = np.zeros_like(conf)  # Energy gradient force in full shape
        for ii,idx in enumerate(dyn_idx): F_E_full[tuple(idx)] = F_E[ii]
        return F_E_full


def calc_total_force(ic,ham,confs,dists,eners,dyn_idx,spring_const,idx_climb_image):
    tangent,F_S = calc_spring_force(ic,ham,confs,dists,eners,spring_const)
    F_E = calc_energy_gradient_force(ham,confs[ic],tangent,dyn_idx,(ic == idx_climb_image))
    if ic==idx_climb_image: return F_E
    return F_S + F_E


def verbose_GNEB_setup(head,nimage,niter,pre_ci_niter,relax_init_final_images,fix_boundary,
    rot_step,spring_const,geodesic_method,ncore=-1,parallel_mode='sites',read_images_from_file=None,fw=None):

    pkg_info().verbose_info(fw)
    print ('\n{0}\n{1}{2}\n{0}\n'.format('='*60,neb_text,'\nGeodesic Nudged Elastic Band'),file=fw)

    print ("\n{}\nGNEB setup\n{}\n".format('='*80, '-'*80),file=fw)
    print ('Initial and final images will be',end = ' ',file=fw)
    if relax_init_final_images: print ('relaxed during GNEB',file=fw)
    else: print ('fixed during GNEB',file=fw)
    if fix_boundary: print ('Spins at the boundary are fixed during GNEB',file=fw)
    print ('The step of a GNEB move is {:6.3f} rad'.format(rot_step),file=fw)
    print ('Number of Iterations = {}'.format(niter),file=fw)
    if pre_ci_niter>=0: print ('{} will start after {} iterations'.format(head, pre_ci_niter),file=fw)
    print ('Method to calculate geodesic distance (in rad): {}'.format(geodesic_method),file=fw)
    print ('Spring constant = {:8.4f} meV/rad'.format(spring_const),file=fw)
    print ('='*80, file=fw)
 
    print ("\n{}\nParallelization\n{}\n".format('='*80, '-'*80),file=fw)
    if ncore>0:
        print ('Parallel on {} cores'.format(ncore),file=fw)
        print ('Parallel_mode = {}'.format(parallel_mode),file=fw)
        if parallel_mode == 'images':
            print ('For high efficiency we recommend the invoked number of cores',file=fw)
            print ('satisfies that nimage+2 = {} is divisible by ncore\n'.format(nimage+2),file=fw)
        if parallel_mode == 'sites':
            print ('If you have a small system with only a few spin sites',file=fw)
            print ('We recommend you to set parallel_mode = images',file=fw)
    else:
        print ('Run in serial mode',file=fw)
    print ('\n'+'='*80, file=fw)

    print ("\n{}\nInterpolation\n{}\n".format('='*80, '-'*80),file=fw)
    print ('Number of Images = {} (including initial and final)'.format(nimage+2),file=fw)
    if read_images_from_file is not None: 
        print ('\nStarted from images in the file\n{}\n\n'.format(read_images_from_file),file=fw)
    else: 
        print ('\nLinear interpolation of images between initial and final configurations',file=fw)
        print ('Done. {} Images are interpolated between the initial and final states.'.format(nimage), file=fw)
    print ('Image {:3d} is the initial configuration'.format(0),file=fw)
    print ('Image {:3d} is the final   configuration'.format(nimage+1),file=fw)
    print ('\n'+'='*80, file=fw)

    print ('\n{}\nstarted at {}\n'.format(head, time.ctime()),file=fw)
    print ('Note: CI_idx is index of the climbing image in the chain',file=fw)
    print ('CI_idx = {} means NO climbing image'.format(nimage+2),file=fw)
    print ('',file=fw)
    if fw is None: sys.stdout.flush()
    else: fw.flush()


def write_dists_eners(dists,eners,fw,fd,ite,finalize=False):
    fw.write(('{:4d} '+'{:16.5f}'*len(eners)+'\n').format(ite,*tuple(eners)))
    fd.write(('{:4d} '+'{:16.5f}'*len(dists)+'\n').format(ite,*tuple(dists)))
    fw.flush()
    fd.flush()
    if finalize:
        fw.close()
        fd.close()


def write_single_image(params,conf,log_conf_file):
    moveaxis = np.arange(len(conf.shape)-2)
    spins = np.moveaxis(conf,moveaxis,moveaxis[::-1]).reshape(-1,3)
    write_ovf(params,spins,filename=log_conf_file)


def write_images(params,confs,log_conf_file,ite):
    shape = confs.shape
    if params['nsegment']!=shape[0]: confs = confs[1:-1]
    nimage = confs.shape[0]
    filename = log_conf_file.replace('.ovf','_iter_{}.ovf'.format(str(ite).zfill(3)))
    moveaxis = np.arange(1,len(confs.shape)-2)
    spins = np.moveaxis(confs,moveaxis,moveaxis[::-1]).reshape(nimage,-1,3)
    write_ovf(params,spins,filename=filename)

    # Under test
    """
    desc_str = params['desc']
    for idx in range(nimage):
        if idx==0: mode='w'
        else: mode='a'
        params.update(desc = ['Image {}'.format(idx)] + desc_str)
        write_ovf(params,spins[idx],filename=filename,mode=mode)
    """


def load_images_from_file(read_images_from_file,shape,nimage):
    spins = parse_ovf(read_images_from_file)[1]
    fmt_err = 'No. of images in {} ({}) != nimage+2 ({}) or nimage ({})!'
    assert spins.shape[0] in [nimage+2,nimage],fmt_err.format(read_images_from_file,spins.shape[0],nimage+2,nimage)
    spins = spins.reshape(-1,*tuple(shape[:-2][::-1]),*tuple(shape[-2:]))
    moveaxis = np.arange(1,len(shape)-2)
    confs = np.moveaxis(spins,moveaxis,moveaxis[::-1])
    return confs


# rot_step is the rotation angle factor of the spin under the total torque F_tot
# it is in unit of radian, the rotation angle is F_tot*rot_step
def run_gneb(ham,
    conf_init,conf_finl,
    nimage=10,
    spring_const=0.2,
    rot_step = 0.01,
    niter=10,  
    log_fmt = log_fmt,
    pre_ci_niter=-1,
    relax_init_final_images=False,
    geodesic_method='Vincenty',
    fix_boundary=False,
    pinned_idx=None,
    average_energy_on_sites = False,
    check_conf_norm = False,
    read_images_from_file=None,
    final_image_from_interpolation=True,
    log_handle = log_handle):

    head_fmt = '{:>10s} ' * 3
    head_tags = ['Iteration', 'Time (s)', 'CI_index']
    if log_handle._log_force: 
        head_fmt += '{:>15s}'
        head_tags += ['max_Force (meV/rad)']
        log_fmt += '{:15.7e}'

    shape = conf_init.shape
    assert shape==conf_finl.shape,'shapes for initial and final configurations should be consistent!'
    log_handle.prepare_logging_dir()
    nx,ny,nz,nat,dyn_idx = get_dynamics_sites_indices(shape,fix_boundary,pinned_idx,savetxt=True,outdir=log_handle._outdir)

    if read_images_from_file is not None:
        confs = load_images_from_file(read_images_from_file,shape,nimage)
        if confs.shape[0]==nimage: confs = np.concatenate(([conf_init],confs,[conf_finl]),axis=0)
    else:
        confs = linear_interpolate_images(conf_init,conf_finl,nimage,final_image_from_interpolation)

    head = 'GNEB'
    if pre_ci_niter>=0: 
        head = 'climb-image GNEB'
        log_handle._log_ener_file = log_handle._log_ener_file.replace('.dat','_ci.dat')
        log_handle._log_dist_file = log_handle._log_dist_file.replace('.dat','_ci.dat')
        log_handle._log_conf_file = log_handle._log_conf_file.replace('.ovf','_ci.ovf')
        log_handle._log_Q_file    = log_handle._log_Q_file.replace('.dat','_ci.dat')
    if log_handle._log_topo_chg: fq = open(log_handle._log_Q_file,'w')
    fw = open(log_handle._log_ener_file,'w')
    fd = open(log_handle._log_dist_file,'w')

    #eners = np.array([ham.calc_total_E(conf,average_on_sites=False) for conf in confs])
 
    if pre_ci_niter>=0: add_desc = ['Climb-image GNEB']
    else: add_desc = ['GNEB images']
    add_desc += [
    'nx   = {:4d}'.format(nx),
    'ny   = {:4d}'.format(ny),
    'nz   = {:4d}'.format(nz),
    'nat  = {:4d}'.format(nat)]

    if relax_init_final_images == False: 
        params = gen_params_for_ovf(nx,ny,nz,nsegment=1,additional_desc=add_desc)
        write_single_image(params,conf_init,log_handle._init_conf_file)
        write_single_image(params,conf_finl,log_handle._final_conf_file)
        params = gen_params_for_ovf(nx,ny,nz,nsegment=nimage,additional_desc=add_desc)
    else: 
        params = gen_params_for_ovf(nx,ny,nz,nsegment=nimage+2,additional_desc=add_desc)
    write_images(params,confs,log_handle._log_conf_file,0)

    stime = time.time()
    verbose_GNEB_setup(head,nimage,niter,pre_ci_niter,relax_init_final_images,fix_boundary,
    rot_step,spring_const,geodesic_method,read_images_from_file=read_images_from_file)

    idx0 = nimage+2  # never reached for a (nimage+2) chain
    print ('='*50)
    print (head_fmt.format(*tuple(head_tags)))
    print ('-'*50)
    for ite in range(niter):
        eners = np.array([ham.calc_total_E(conf,average_on_sites=False) for conf in confs])
        dists = np.array([get_geodesic_distance(confs[ic-1],confs[ic],geodesic_method) for ic in range(1,nimage+2)])
        if ite%log_handle._n_log_energy==0: write_dists_eners(dists,eners,fw,fd,ite)
        if ite==pre_ci_niter: idx0 = np.where(eners==np.max(eners))[0][0]  # idx0 only changes its value once during a GNEB run
        idx_climb_image = idx0
        max_force = 0

        F_tot = np.zeros((nimage+2,*tuple(shape)))
        for ic in range(nimage+2):
            if not relax_init_final_images and ic in [0,nimage+1]: continue
            F_tot[ic] = calc_total_force(ic,ham,confs,dists,eners,dyn_idx,spring_const,idx_climb_image)

        for ic in range(nimage+2):
            if not relax_init_final_images and ic in [0,nimage+1]: continue
            for idx in dyn_idx:
                n_i = confs[ic][tuple(idx)]
                F_i = F_tot[ic][tuple(idx)]
                vec = np.cross(n_i,F_i)
                norm = np.linalg.norm(vec)
                if 0<ic<nimage+1: max_force = max(max_force,norm)
                if norm<1e-5: continue
                mat = RT.from_rotvec(vec*rot_step).as_matrix()
                confs[ic][tuple(idx)] = np.dot(mat,n_i)
        if ite==0: print (log_fmt.format(ite,time.time()-stime,idx0,max_force))
        if (ite+1)%log_handle._n_log_configuration==0 or ite==niter-1: 
            if log_handle._log_topo_chg: 
                Qs = np.array([calc_topo_chg(image,tri_simplices=log_handle._tri_simplices) for image in confs])
                fq.write(('{:4d} '+'{:10.5f}'*(nimage+2)+'\n').format(ite+1,*tuple(Qs)))
                fq.flush()
            print (log_fmt.format(ite+1,time.time()-stime,idx_climb_image,max_force))
            write_images(params,confs,log_handle._log_conf_file,ite+1)
    eners = np.array([ham.calc_total_E(conf,average_on_sites=False) for conf in confs])
    dists = np.array([get_geodesic_distance(confs[ic-1],confs[ic],geodesic_method) for ic in range(1,nimage+2)])
    write_dists_eners(dists,eners,fw,fd,ite+1,finalize=True)
    if log_handle._log_topo_chg: 
        Qs = np.array([calc_topo_chg(image,tri_simplices=log_handle._tri_simplices) for image in confs])
        fq.write(('{:4d} '+'{:10.5f}'*(nimage+2)+'\n').format(ite+1,*tuple(Qs)))
        fq.close()
    print ('-'*80)
    if pre_ci_niter>=0: print ('\nImage {} is the climbing image'.format(idx_climb_image))
    print ('\nFinished at {}\nTime used: {:8.3f} s\n'.format(time.ctime(),time.time()-stime))
    print ('='*80)
    return confs,dists,eners


def interpolate_energy_along_path(dists,energies,npoint=100):
    lam = np.append(0,np.cumsum(dists))
    path = np.linspace(0,lam[-1],npoint)
    d = energies - np.min(energies)
    c = np.gradient(d, lam)
    b = -(c[1:] + 2*c[:-1])/dists    + 3*(d[1:] - d[:-1])/dists**2
    a =  (c[1:] +   c[:-1])/dists**2 - 2*(d[1:] - d[:-1])/dists**3
    Ens = np.zeros(npoint)
    for i,x in enumerate(path):
        nu = max(0, np.where(lam-x>=0)[0][0]-1)
        dd = x-lam[nu]
        Ens[i] = a[nu]*dd**3 + b[nu]*dd**2 + c[nu]*dd + d[nu]

    return path, Ens


def ax_plot_en_profile(ax,dists=[],eners=[],labels=[],style='o-',interpolate=True,legend=True,legend_title=None):
    if len(dists)>0 and len(labels)==0: labels = [None for i in range(len(dists))]
    for dists0,eners0,label0 in zip(dists,eners,labels):
        coord = np.append(0,np.cumsum(dists0))
        if interpolate:
            path,Ens = interpolate_energy_along_path(dists0,eners0)
            if style not in ['-','--','-.']: 
                ax.plot(path,Ens)
                ax.scatter(coord,eners0-np.min(eners0),label=label0)
            else:
                ax.plot(path,Ens,label=label0)
        else:
            ax.plot(coord,eners0-np.min(eners0),style,label=label0)
    if legend: 
        lg = ax.legend()
        if legend_title is not None: lg.set_title(legend_title)
    ax.set_xlabel(r'Reaction Coordinate',fontsize=12)
    ax.set_ylabel(r'$E$ (meV)',fontsize=12)
    ax.axhline(0,ls='--',c='gray',alpha=0.5,zorder=-2)
 
 
def view_en_profile(dists=[],eners=[],labels=[],style='o-',
    interpolate=True,legend=True,title=None,legend_title=None,
    show=True,save=False,figname='GNEB_energy_file'):
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(1,1)
    ax_plot_en_profile(ax,dists,eners,labels,style,interpolate,legend,legend_title)
    if title is not None: ax.set_title(title, fontsize=12)
    fig.tight_layout()
    if save: fig.savefig(figname,dpi=400)
    if show: plt.show()
    return fig


def animate_NEB_evolution(ite,latt,sites,climb_image=True,kwargs=dict(),outdir='.',prefix='GNEB'):
    from asd.core.geometry import build_latt
    from asd.utility.spin_visualize_tools import quiver_kws,make_ani
    import glob

    shape = sites.shape
    fil_key = '{}/'.format(outdir)
    if prefix=='': fil_key += 'spin_confs'
    else: fil_key += '{}_spin_confs'.format(prefix)
    print (fil_key)
    if climb_image: fil = glob.glob('{}_ci_iter_{}.ovf'.format(fil_key,str(ite).zfill(3)))[0]
    else: fil = glob.glob('{}_iter_{}.ovf'.format(fil_key,str(ite).zfill(3)))[0]
    spins = parse_ovf(fil)[1]
    if len(shape)==4: 
        nx,ny,nat = shape[:-1]
        confs = np.swapaxes(spins.reshape(-1,ny,nx,nat,3),1,2)
    elif len(shape)==5: 
        nx,ny,nz,nat = shape[:-1]
        confs = np.transpose(spins.reshape(-1,nz,ny,nx,nat,3),(0,3,2,1,4,5))
        exit('confs in shape of {}, 3D system cannot be animated'.format(confs.shape))

    nimage = len(confs)
    nsites = np.prod(sites.shape[:-1])
    sites_cart = np.dot(sites,latt)
    quiver_kws.update(scale=1.5,width=0.1,headlength=5,)

    fil_en = 'ener{}.dat'.format({True:'_ci',False:''}[climb_image])
    head = '{}GNEB'.format({True:'ci-',False:''}[climb_image])
    try: eners = np.loadtxt(fil_en)[ite,1:]
    except: eners = None
    if eners is not None: titles = ['{}: Image {}, E = {:7.3f} meV/site'.format(head,ii+1,eners[ii]/nsites) for ii in range(nimage)]
    else: titles = ['{}: Image {}'.format(head,ii+1) for ii in range(nimage)]

    kwargs.update(
    quiver_kws=quiver_kws,
    latt=latt,
    titles = titles,
    )

    make_ani(sites_cart,confs,**kwargs)



class serial_GNEB_controller():
    def __init__(self,
        nimage=10,
        spring_const=0.2,
        rot_step = 0.01,
        niter=10,  
        log_fmt = log_fmt,
        pre_ci_niter=5,
        relax_init_final_images=False,
        geodesic_method = 'Vincenty',
        fix_boundary=False,
        pinned_idx=None,
        average_energy_on_sites = False,
        check_conf_norm = False,
        read_images_from_file = None,
        final_image_from_interpolation=True,
        log_handle = log_handle,
        verbosity=1):

        self._nimage = nimage
        self._spring_const = spring_const
        self._rot_step = rot_step
        self._niter = niter
        self._log_fmt = log_fmt
        self._pre_ci_niter = pre_ci_niter
        self._relax_init_final_images = relax_init_final_images
        self._geodesic_method = geodesic_method
        self._fix_boundary = fix_boundary
        self._pinned_idx = pinned_idx
        self._average_energy_on_sites = average_energy_on_sites
        self._check_conf_norm = check_conf_norm
        self._read_images_from_file = read_images_from_file
        self._final_image_from_interpolation = final_image_from_interpolation
        self.set_log_handle(log_handle)
        self.set_verbosity(verbosity)


    def set_verbosity(self,verbosity):
        err = 'GNEB_controller: You try to set verbosity = {}, it should be an non-negative integer!'.format(verbosity)
        assert type(verbosity)==int and verbosity>=0, err
        self._verbosity = verbosity


    def verbose_GNEB_setup(self):
        verbose_GENB_setup(head,self._nimage,self._niter,self._pre_ci_niter,self._relax_init_final_images,self._fix_boundary,
        self._rot_step,self._spring_const,self._geodesic_method,-1)


    def set_log_handle(self,log_handle):
        self._log_handle = log_handle
        self.__dict__.update(log_handle.__dict__)
 

    def run_gneb(self,ham,conf_init,conf_finl):
        confs, dists, eners = run_gneb(ham,
        conf_init,
        conf_finl,
        self._nimage,
        self._spring_const,
        self._rot_step,
        self._niter,  
        self._log_fmt,
        self._pre_ci_niter,
        self._relax_init_final_images,
        self._geodesic_method,
        self._fix_boundary,
        self._pinned_idx,
        self._average_energy_on_sites,
        self._check_conf_norm,
        self._read_images_from_file,
        self._final_image_from_interpolation,
        self._log_handle)

        pickle.dump(self, open('{}/GNEB_controller.pickle'.format(self._outdir),'wb'))
        return confs, dists, eners
 
