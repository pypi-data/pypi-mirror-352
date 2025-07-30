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


#=========================================================
#
# Matrix representation of spin operators, see
# https://easyspin.org/documentation/spinoperators.html
#
# Shunhong Zhang
# Jan 20 2025
#
#=========================================================



import numpy as np

r2 = np.sqrt(2)
r3 = np.sqrt(3)
r6 = np.sqrt(6)
r5 = np.sqrt(5)
r8 = np.sqrt(8)


def get_spin_matrices(S=1/2, ladder=False):
    """
    Generate the spin matrices for different spin-S particles

    Inputs:
    ----------------
    S: float
    The spin quantum number
    ladder: bool
    If True, ladder operators (L: lower, R: raise) are used
    
    Returns:
    ----------------
    sigmas: list
    The spin matrices
    if ladder == True, sigmas = [sigma_R, sigma_L, sigma_Z]
    if ladder ==False, sigmas = [sigma_X, sigma_Y, sigma_Z]
    """

    ndim = int(S*2) + 1
    sigma_X = np.zeros((ndim,ndim),complex)
    sigma_Y = np.zeros((ndim,ndim),complex)
    sigma_L = np.zeros((ndim,ndim),complex)
    sigma_R = np.zeros((ndim,ndim),complex)

    if   S==1/2: dd = np.array([1])
    elif S==1:   dd = np.diag([1,1])
    elif S==3/2: dd = np.diag([r3,2,r3])
    elif S==2:   dd = np.diag([2,r6,r6,2])
    elif S==5/2: dd = np.diag([r5,r8,3,r8,r5])
    else: raise ValueError ("Spin matrices for S = {} is not yet available!".format(S))

    sigma_X[:-1,1:] = (1./2) * dd
    sigma_X[1:,:-1] = (1./2) * dd
    sigma_Y[:-1,1:] = (1./2j) * dd
    sigma_Y[1:,:-1] = (1./2j) * (-dd)

    sigma_R[:-1,1:] = dd
    sigma_L[1:,:-1] = dd

    sigma_Z = np.array(np.diag(np.arange(S,-S-1,-1)))

    if ladder: sigmas = [sigma_R, sigma_L, sigma_Z]
    else:      sigmas = [sigma_X, sigma_Y, sigma_Z]

    return sigmas




def display_spin_matrices(sigmas, ladder=False):
    """ Display the spin matrices"""

    ndim = sigmas[2].shape[0]
    if ladder: dirs = {0:'+',1:'-',2:'z'}
    else: dirs = {0:'x',1:'y',2:'z'}
    fmt = '{0.real:8.4f} + {0.imag:8.4f}i  '
    S = (ndim-1)/2.
    if int(S*2)%2==0: print ('\n\n{0}\nS = {1:.0f}\n{0}'.format('='*30, S))
    else: print ('\n\n{0}\nS = {1:.0f}/2\n{0}'.format('='*30, S*2))

    for ii in range(3):
        print ('\nsigma_{}'.format(dirs[ii]))
        for i in range(ndim):
            for j in range(ndim):
                print (fmt.format(sigmas[ii][i,j]),end=' ')
            print ('')


class spin_mat(object):
    def __init__(self, S=1/2, ladder=False):
        self._S = S
        self._ladder = ladder
        self._spin_matrices = get_spin_matrices(self._S, self._ladder)

    def display(self):
        display_spin_matrices(self._spin_matrices)
        


ladder=True
ladder=False

if __name__=='__main__':
    """ Use the function """
    for S in [1/2, 1, 3/2, 2, 5/2]:
        sigmas = get_spin_matrices(S, ladder)
        display_spin_matrices(sigmas, ladder)


    """ Use the class """
    sm = spin_mat(S=1, ladder=True)
    sm.display()
 
