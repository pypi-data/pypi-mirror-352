#!/usr/bin/env python

#===================================
#
# Visualize the rhombus plaqutte
# on which the four-site exchanges
# are defined by the spirit code
#
# Shunhong Zhang 
# zhangshunhong.pku@gmail.com
# Jan 18 2025
#
#===================================

import numpy as np
import matplotlib.pyplot as plt


def build_polygons(four_site):
    polygons = []
    for ii,pla in enumerate(four_site):
        polygon = [[0,0]]
        for jj in range(3):
            R = pla[np.array([2+4*jj,3+4*jj],int)]
            Rc = np.dot(sites[int(pla[1+4*jj])]+R, latt)
            polygon.append(Rc)
        polygons.append(polygon)
    polygons = np.array(polygons)
    return polygons


def display_polygons(polygons, show=True):
    fig,axes=plt.subplots(1,2,sharey=True,figsize=(6,3))
    for ii in range(2):
        ax = axes[ii]
        for polygon in polygons[ii::2]:
            ax.fill(*tuple(polygon.T),alpha=0.5)
        ax.set_aspect('equal')
        ax.set_axis_off()
    if show: plt.show()
    return fig


latt = np.array([[1,0],[-0.5,np.sqrt(3)/2]])
sites = np.array([[0,0]])

outdir = 'triangular'
outdir = 'honeycomb'

if __name__=='__main__':
    fil_qd = '{}/quadruplet'.format(outdir)
    print ('Reading quadruplet from {}'.format(fil_qd))
    four_site = np.loadtxt(fil_qd,skiprows=2)
    print (four_site)
    polygons = build_polygons(four_site)
    display_polygons(polygons)
