#!/usr/bin/env python

from asd.utility.mag_thermal import *


def display_log_magnetization_with_varying_beta(betas=None,
    temperatures=np.linspace(0,20,100),Tc=10,show=True):

    fig,ax=plt.subplots(1,1,figsize=(6,4))

    if betas is not None:
        for beta in betas:
            yy = exponent_magnetization(temperatures,Tc,beta)
            ax.plot(temperatures,yy,'--',label='$\\beta\ =\ {:.3f}$'.format(beta))

    """ Critical exponent for Ising and XY models"""
    for beta,label in zip([0.125,np.pi**2*3/128],['Ising','XY']):
        yy = exponent_magnetization(temperatures,Tc,beta)
        ax.plot(temperatures,yy,lw=3,label='$\\beta\ =\ {0:.3f}$'.format(beta)+' 2D {}'.format(label))

    lg = ax.legend()
    ax.set_xlabel(r'$T$ (K)',fontsize=12)
    ax.set_ylabel(r'$M$',fontsize=12)
    fig.tight_layout()
    fig.savefig('Tc_beta_power',dpi=400)
    if show: plt.show()
    return fig


betas = [0.1,0.15,0.3,0.6,1.2,1.8]
 
if __name__=='__main__':
    display_log_magnetization_with_varying_beta(betas,show=True)

