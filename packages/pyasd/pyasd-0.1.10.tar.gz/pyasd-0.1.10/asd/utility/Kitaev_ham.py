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



# ===================================================
# Utility to generate Kitaev-type spin Hamiltonian
# Can be implemented to perform
# Classic spin dyanmics simulations (pyasd) or
# Quantum spin simulation (HPhi or quspin)
#
# Shunhong Zhang <szhang2@ustc.edu.cn>
# Last modified: May 14 2024
#
#====================================================
#
#

from asd.data_base.exchange_for_Kitaev import *

# Bloch-type, along bonds
def gen_Bloch_DMI_vecs(DMI):
    DM1 = np.array([r3h,0.5,0])*DMI
    DM2 = np.array([-r3h,0.5,0])*DMI
    DM3 = np.array([0,-1,0])*DMI
    DMI_vecs = [DM1, DM2, DM3]
    return DMI_vecs


# Neel-type normal to bonds, in the plane
def gen_Neel_DMI_vecs(DMI):
    DM1 = np.array([-0.5, r3h,0])*DMI
    DM2 = np.array([-0.5,-r3h,0])*DMI
    DM3 = np.array([1,0,0])*DMI
    DMI_vecs = [DM1, DM2, DM3]
    return DMI_vecs


def params_compressed_CrSiTe3():
    # parameters for CrSiTe3 under -2.34 % compressive strain, 
    # which was demonstrated as a QSL candidate
    # See PRL 124, 087205 (2020), Supplementary Table S1
    # Note that the Kitaev term is antiferromagnetic here
    J_Heis = -0.1019
    Kitaev =  0.2747
    Gamma1 =  0.0204
    Gamma2 = -0.0838
    return J_Heis, Kitaev, Gamma1, Gamma2


# write inputs for standard mode of HPhi
def write_HPhi_exchange(J_XYZ,DMI_vecs=None,file=None,verbosity=1,coord='Global'):
    from asd.core.shell_exchange import DM_vector_to_matrix
    dirs = {0:'x',1:'y',2:'z'}
    nbond = len(J_XYZ)
    J_tots = []
    for ibond in range(nbond):
        J_tot = J_XYZ[ibond]
        if DMI_vecs is not None:
            if coord=='Global':
                J_tot += DM_vector_to_matrix(DMI_vecs[ibond])
            elif coord=='Lowdin':
                print ('\nNote from write_HPhi_exchange:')
                print ('DMI_vecs provided, but ')
                print ('the symmetric exchange is given in Lowdin coord')
                print ('To avoid silly mistakes, DMI will NOT be added')
        J_tots.append(J_tot)
        print ('',file=file)
        for ii,jj in np.ndindex(3,3):
            if ii==jj: component = dirs[ii]
            else: component = '{}{}'.format(dirs[ii],dirs[jj])
            print (('J{}{:<2s} = {:16.12f}').format(ibond,component,J_tot[ii,jj]),file=file)
        print ('',file=file)
        if file is not None and verbosity: print ((('{:16.12f} '*3+'\n')*3).format(*tuple(J_tot.flatten())))

    if verbosity: print ('Sanity check: the three-fold rotational symmetry')
    if coord=='Global': vec = np.array([0,0,2*np.pi/3])
    if coord=='Lowdin': vec = np.array([1,1,1])*2*np.pi/3/np.sqrt(3)
    rot = RT.from_rotvec(vec).as_matrix()
    for ibond in range(3):
        rotated_J = np.dot(np.dot(rot,J_tots[ibond]),rot.T)
        np.testing.assert_allclose(rotated_J,J_tots[(ibond+1)%3],atol=1e-8,rtol=1e-8)
    if verbosity: print ('passed')
    return J_tots



stan_in_head='''model = "SpinGCCMA"
W = 3
L = 2
method = "Lanczos"
lattice = "Honeycomb"
2S=1
EigenvecIO = "out"
'''

job_script='''#!/bin/bash
#SBATCH -p amd_512
#SBATCH -N 2
#SBATCH -n 256
source /public3/soft/modules/module.sh
module load mpi/openmpi/4.1.1-gcc9.3.0
module load intel/2022.1
HPhi -s stan.in
'''

def test_transformation_by_ED(ntest=3,stan_in_head=stan_in_head,job_script=job_script,cmd='sbatch sub.sh'):

    def test_one_Jmat(Jmat,cdir,coord='Global'):
        os.mkdir(cdir)
        os.chdir(cdir)
        with open('stan.in','w') as fw:
            fw.write(stan_in_head)
            write_HPhi_exchange(Jmat,DMI_vecs=None,file=fw,verbosity=0,coord=coord)
        open('sub.sh','w').write(job_script)
        os.system(cmd)
        os.chdir('..')

    cwd = os.getcwd()
    outdir='test_ED'
    if os.path.isdir(outdir): os.system('rm -rf {}'.format(outdir))
    os.mkdir(outdir)
    os.chdir(outdir)
    for itest in range(ntest):
        cdir = 'ED_{}'.format(itest)
        print ('Create testing case at {}'.format(cdir))
        os.mkdir(cdir)
        os.chdir(cdir)
        J_Heis, Kitaev, Gamma1, Gamma2 = np.random.random(4)
        J_Lowdin, J_XYZ = Lowdin_to_global(J_Heis, Kitaev, Gamma1, Gamma2, verbosity=0)
        test_one_Jmat(J_Lowdin,'Lowdin','Lowdin')
        test_one_Jmat(J_XYZ,'Global','Global')
        os.chdir('..')
    os.chdir(cwd)


def compare_results_ED(ntest=3, outdir='test_ED'):
    cdirs = ['Global', 'Lowdin']
    for itest in range(ntest):
         for cdir in cdirs:
            fil = '{}/ED_{}/{}/output/zvo_energy.dat'.format(outdir, itest, cdir)
            E0 = float(open(fil,'r').readline().rstrip('\n').split()[1])
            print ('{:4d} {:10s} {:12.8f}'.format(itest, cdir, E0))



J_Heis = 0
Kitaev = -1
Gamma1 = 0
Gamma2 = 0

DMI = 0.
DMI_vecs = gen_Bloch_DMI_vecs(DMI)
DMI_vecs = gen_Neel_DMI_vecs(DMI)

if __name__=='__main__':
    J_lowdin, J_XYZ = Lowdin_to_global(J_Heis, Kitaev, Gamma1, Gamma2)
    write_HPhi_exchange(J_XYZ,DMI_vecs,file=open('stan.in','w'))
    #test_transformation_by_ED(ntest=3, cmd='HPhi -s stan.in')
    compare_results_ED(ntest=3)
