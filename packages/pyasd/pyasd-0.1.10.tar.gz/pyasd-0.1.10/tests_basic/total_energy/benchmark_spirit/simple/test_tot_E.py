#!/usr/bin/env python

from __future__ import print_function
import numpy as np
from spirit import chain,state,geometry,configuration,hamiltonian,system,quantities,io
from asd.utility.ovf_tools import parse_ovf
from asd.utility.spin_visualize_tools import make_ani,quiver_kws
from asd.core.hamiltonian import *
from asd.core.geometry import *
from asd.core.shell_exchange import get_exchange_xyz, exchange_shell
from termcolor import cprint
import os


def gen_boundary_conditions(nimages, bound_type='random'):
    if bound_type=='random': boundary_conditions = np.random.randint(2,size=(nimage,3))
    elif bound_type=='periodic': boundary_conditions = np.ones((nimage,3),int)
    else: raise ValueError('Invalid bound_type = {}'.format(bound_type))
    boundary_conditions[:,2] = 0
    return boundary_conditions
 


def get_Spirit_dataset(SIA,J1,J2,DM1,DM2,Bfield,boundary_conditions,nimage=10,quiet=True):
    en_spirit=[]
    mgs=[]
    bounds = []
    #quiet=False
    with state.State('input.cfg',quiet) as p_state:
        chain.set_length(p_state,nimage)
        for idx in range(nimage):
            chain.jump_to_image(p_state,idx_image=idx)
            geometry.set_n_cells(p_state,[nx,ny,1])

            hamiltonian.set_boundary_conditions(p_state,boundary_conditions[idx])

            hamiltonian.set_anisotropy(p_state,SIA[0],[0,0,1])
            hamiltonian.set_field(p_state,np.linalg.norm(Bfield),Bfield)

            # NN + 2NN, for spirit 2.1.1 or earlier version
            hamiltonian.set_exchange(p_state,2,[J1,J2])
            hamiltonian.set_dmi(p_state,2,[DM1,DM2])


            # NN + 2NN, for spirit 2.2.0 or later version, still under test
            #hamiltonian.set_exchange(p_state,3,[J1,J2,J2])
            #hamiltonian.set_dmi(p_state,2,[DM1,DM2])


            configuration.plus_z(p_state)
            if idx<10: configuration.skyrmion(p_state,radius=10*idx)
            else:      configuration.random(p_state)
            system.update_data(p_state)
            en_spirit.append(system.get_energy(p_state))
            mgs.append(quantities.get_magnetization(p_state))
            io.image_write(p_state,'confs/spin_{0}.ovf'.format(str(idx).zfill(2)))
            bounds.append( hamiltonian.get_boundary_conditions(p_state))

        pos = geometry.get_positions(p_state)
        np.savetxt('pos.dat',pos,fmt='%20.8f')
    en_spirit = np.array(en_spirit)
    return en_spirit,mgs



Spirit_version_note = """
This version has a large change on the defination of exchange
It is not well tested with pyasd for consistency
Please check your results carefully and use them on your own risk.
The version that has been tested is 2.1.1 """
 
def check_spirit_version():
    import spirit
    ver = np.array(spirit.__version__.split('.'),int)
    if ver[0]==2 and ver[1]>=2:
        print ('Detected Spirit version : {}'.format(spirit.__version__))
        print (Spirit_version_note)
        return True
    return False



def benchmark_spin_energy(ham,boundary_conditions,confs):
    nimage,nx,ny,nat = confs.shape[:-1]
    sp_lat = np.zeros((nx,ny,nat,3))
    ham.verbose_all_interactions(verbose_file='ham.dat')
    ham.verbose_reference_energy(sp_lat,file_handle=open('ham.dat','a'))

    nsites=nx*ny*nat
    fmt='{:7.3f}'*3
    tags = ['Mx','My','Mz','E_spirit(meV)','my_E_tot(meV)','diff_E(meV)','diff_E(meV/site)',' |  boundary']

    print (fmt_head.format(*tuple(tags)))
    for i in range(nimage):
        mm=np.average(confs[i],axis=(0,1,2))
        ham._boundary_condition = boundary_conditions[i]
        en=ham.calc_total_E(confs[i],average_on_sites=False)
        print (('{:3d} |'+fmt).format(i+1,*tuple(mm)),end=' | ')
        print (('{:14.7f} '*2+'{:16.7e} {:20.8e}').format(en_spirit[i],en,en-en_spirit[i],(en-en_spirit[i])/nsites),end = '    | ')
        print(('{:3d} '*3).format(*tuple(boundary_conditions[i])))
    print ('='*120)


nimage=10

fmt_head='\n'+'='*120+'\n' + 'idx |'+'{:>7s}'*3+' | '+'{:>14s} '*2+'{:>16s} {:>20s}' + '{:>15s}\n'+'-'*120

nx=30
ny=30
lat_type='honeycomb'
latt_choice=2
latt,sites,neigh_idx,rotvecs = build_latt(lat_type,nx,ny,1,latt_choice=latt_choice,latt_const=7)
sites_cart = np.dot(sites,latt)
nat=2

quiver_kws.update(
units='xy',
scale=0.2,
width=0.5,
headwidth=5,
)

kws = dict(
quiver_kws=quiver_kws,
superlatt=np.dot(np.diag([nx,ny]),latt),
colorbar_shrink=0.3,
colorbar_axes_position=[0.7,0.5,0.01,0.3],
colorbar_orientation='vertical',
scatter_size=10,
titles=['config {}'.format(iconf) for iconf in range(nimage)])


S_values = np.array([3./2,4./2])

Bfield=np.array([1.5, 2, 4])
SIA=np.array([0.5,0.5])

J1 = 1 
J2 = -0.2

J1_iso = np.ones(2)*J1
J2_iso = np.ones(2)*J2

DM1 = 0.5
DM2 = 0

if latt_choice==1:
    DM1_rpz = np.array([[r3h,0.5,0],[-r3h,-0.5,0]]) * DM1
elif latt_choice==2:
    DM1_rpz = np.array([[0,-1,0],[0,1,0]]) * DM1

DM1_xyz = get_exchange_xyz(DM1_rpz,rotvecs[0])

exch_1 = exchange_shell( neigh_idx[0], J1_iso, DM_xyz = DM1_xyz, shell_name = '1NN')
exch_2 = exchange_shell( neigh_idx[1], J2_iso, shell_name = '2NN')


gen_boundary_conditions(nimages, bound_type='periodic')
 
 
ham = spin_hamiltonian(
Bfield=Bfield,
S_values=S_values,
BL_SIA=[SIA],
BL_exch=[exch_1,exch_2],
exchange_in_matrix=False,
)


spirit_version_warning = '''
We found that for new version of Spirit (>= 2.2.0)
This version is not yet well tested and fully understood
DM interaction is not well tested for this and later version\n
'''

if __name__=='__main__':
    is_new_version = check_spirit_version()
    if os.path.isdir('confs'): os.system('rm -rf confs')
    os.mkdir('confs')

    if is_new_version:
        cprint(spirit_version_warning,'red')
        J1 *= 3
        J2 *= 6
        DM1 *= 6
    else:
        print ('Spirit 2.1.1 or earlier version detected.')
        print ('This version has been tested.\n')


    en_spirit,mgs =get_Spirit_dataset(SIA,J1,J2,DM1,DM2,Bfield,boundary_conditions,nimage)

    fils_ovf = ['confs/spin_{0}.ovf'.format(str(i).zfill(2)) for i in range(nimage)]
    confs = np.array([parse_ovf(fil_ovf)[1] for fil_ovf in fils_ovf])
    confs = np.swapaxes(confs.reshape(-1,ny,nx,nat,3),1,2)

    pos = np.loadtxt('pos.dat')
    pos = np.swapaxes(pos.reshape(ny,nx,nat,3),0,1)
    np.testing.assert_allclose(sites_cart,pos[...,:2],atol=1e-7,rtol=1e-7)
    #make_ani(sites_cart,confs,**kws)

    benchmark_spin_energy(ham,boundary_conditions,confs)
