
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


#====================================================================
# Classic spin configurations are normalized vector fields
# The OVF file is a widely used, human-readable format
#
# The ovf package can be installed conveniently via pip
# The functions in this script can take its place
#
# Shunhong Zhang
# Nov 26 2022
#=====================================================================

ovf_exception = '''
ovf not installed! 
Install it via 
pip install ovf
'''

import numpy as np
import os
import re

###################################
# Following: the new part
# invoking the ovf package
# still under development and test
##################################


# convert an instance of python class into an dictionary
# attributes are converted into keys
def props(obj):
    import inspect
    pr = {}
    for name in dir(obj):
        value = getattr(obj, name)
        if not name.startswith('__') and not inspect.ismethod(value):
            pr[name] = value
    return pr


def parse_ovf_1(fil,parse_params=False,verbosity=0):
    try: from ovf import ovf
    except: raise Exception(ovf_exception)

    segments = []
    spins = []
    with ovf.ovf_file(fil) as ovf_file:
        if verbosity: print ('{} segments found'.format(ovf_file.n_segments))
        for iseg in range(ovf_file.n_segments):
            if verbosity: print ('\n{0}\nReading segment {1}\n{0}\n'.format('-'*30,iseg))
            segment = ovf.ovf_segment()
            ovf_file.read_segment_header(iseg,segment)
            data = np.zeros((segment.N,segment.valuedim))
            ovf_file.read_segment_data(iseg,segment,data)
            segments.append(segment)
            spins.append(data)
    spins = np.array(spins)
    params = props(segments[0])
    return params,spins



###################################
# Following: the old part
# without invoking the ovf package
##################################


def get_param(lines,pname,datatype='float'):
    idx = np.where([re.search(pname,line) for line in lines])[0][0]
    pa = lines[idx].split(':')[-1]
    if datatype=='float': pa = float(pa)
    elif datatype=='int': pa = int(pa)
    else: pa = pa.rstrip('\n')
    return pa



parse_ovf_error='''
Error from parse_ovf
data size for different segments are inconsistent
This might be due to multiple runs with results written to the same file
Check your ovf file carefully\n'''


def parse_ovf(fil,parse_params=False):
    assert os.path.isfile(fil), 'parse_ovf: file {} not found!'.format(fil)    
    lines=open(fil).readlines()
    if parse_params:
        keys_float = [a+b for a in ['x','y','z'] for b in ['base','stepsize','min','max']]
        keys_int = ['xnodes','ynodes','znodes']
        params = dict([(key,get_param(lines,key,'float')) for key in keys_float])
        for key in keys_int: params.setdefault(key,get_param(lines,key,'int'))
        params.setdefault('meshtype',get_param(lines,'meshtype','str'))
        try:    params.setdefault('nsegment',get_param(lines,'Segment count','int'))
        except: params.setdefault('nsegment',get_param(lines,'Segment count','str'))
    else:
        params=None
    idx0 = np.where([re.search('Begin: Data Text',line) for line in lines])[0]+1
    idx1 = np.where([re.search('End: Data Text',line) for line in lines])[0]
    nline_block = idx1-idx0
    if len(set(nline_block))>1:
        print (parse_ovf_error)
        exit ('number of lines for blocks: {}'.format(set(nline_block)))
    if len(idx0)>1: 
        spins_archive = np.array([[line.rstrip('\n').split() for line in lines[start:end]] for (start,end) in zip(idx0,idx1)],float)
        return params,spins_archive
    start=idx0[0]
    end=idx1[0]
    spins = np.array([line.rstrip('\n').split() for line in lines[start:end]],float)
    return params,spins


def gen_params_for_ovf(xnodes,ynodes,znodes,xstepsize=0.1,ystepsize=0.1,zstepsize=0.1,Iter=0,max_force=1e-9,additional_desc=[],nsegment=1):
    desc1='Iteration: {}'.format(Iter)
    desc2='Maximum force component: {}'.format(max_force)
    desc_str = additional_desc + [desc1,desc2]

    params = dict(
    xnodes=xnodes,
    ynodes=ynodes,
    znodes=znodes,
    xbase=0,ybase=0,zbase=0,
    xstepsize=xstepsize,
    ystepsize=ystepsize,
    zstepsize=zstepsize,
    xmin=0,ymin=0,zmin=0,
    xmax=xstepsize*(xnodes-1),
    ymax=ystepsize*(ynodes-1),
    zmax=zstepsize*(znodes-1),
    meshtype='rectangular',
    desc=desc_str,
    nsegment=nsegment)

    return params



def write_ovf(params,spins,filename='spins.ovf',mode='w'):
    valuedim=spins.shape[-1]
    fmt0='{:22.12f}'*valuedim+'\n'

    def write_one_segment(fw,params,spins):
        fw.write('#\n# Begin: Segment\n')
        fw.write('# Begin: Header\n')
        fw.write('#\n# Title: file generated by Shunhong Zhang\'s code in OOMMF format\n#\n')
        if 'desc' in params.keys():
            for desc in params['desc']:  fw.write('# Desc:     {}\n'.format(desc))
        fw.write('#\n')
        fw.write('# valuedim: {}   ## field dimensionality\n'.format(valuedim))
        fw.write('# valueunits: none none none\n')
        fw.write('# valuelabels: spin_x spin_y spin_z\n#\n')
        fw.write('## Fundamental mesh measurement unit. Treated as a label:\n')
        fw.write('# meshunit: nm\n#\n')

        keys_float = [a+b for b in ['min','max'] for a in ['x','y','z']]

        for key in keys_float: fw.write('# {}: {:6.2f}\n'.format(key,params[key]))
        fw.write('#\n')
        fw.write('# meshtype: {}\n'.format(params['meshtype']))

        keys_float = [a+b for b in ['base','stepsize','nodes'] for a in ['x','y','z']]
        for key in keys_float: fw.write('# {}: {}\n'.format(key,params[key]))
        fw.write('#\n# End: Header\n#\n')
        fw.write('# Begin: Data Text\n')
        fw.write((fmt0*spins.shape[0]).format(*tuple(spins.flatten())))
        fw.write('# End: Data Text\n#\n')
        fw.write('# End: Segment\n')

    if 'nsegment' in params.keys():
        nseg = params['nsegment']
        spins = spins.reshape(nseg,-1,valuedim)
 
    with open(filename,mode) as fw:
        if mode=='w':
            fw.write('# OOMMF OVF 2.0\n')
            if 'nsegment' in params.keys():
                fw.write('#\n# Segment count: {}\n#\n'.format(nseg))
        for iseg in range(nseg): write_one_segment(fw,params,spins[iseg])


def get_spins_from_ovf_fast(fil_ovf,return_spins=True,verbosity=1,fil_mag='mags.dat'):
    import itertools
    import time
    start_idx = np.array([line.split(':')[0] for line in os.popen('grep -n "Begin: Data" {}'.format(fil_ovf)).readlines()],int)
    final_idx = np.array([line.split(':')[0] for line in os.popen('grep -n "End: Data" {}'.format(fil_ovf)).readlines()],int)
    nconf = len(start_idx)
    start = start_idx[0]
    final = final_idx[0]
    mags = np.zeros((nconf,3))
    spins = []
    stime = time.time()
    if verbosity: print (('{:>7s} '*4+'{:>12s}').format('Now','Total','Start','Last','used time'))
    fmt = '{:7d} '*4+'  {:8.2f} s    {}'
    with open(fil_ovf) as f_input:
        for ii in range(nconf):
            if ii==0: FH = np.loadtxt(itertools.islice(f_input, start, final))
            else: FH = np.loadtxt(itertools.islice(f_input, start-2, final-2))
            if verbosity and ii%(nconf//20): print (fmt.format(ii,start,final,final-start,time.time()-stime,FH.shape))
            mags[ii] = np.average(FH,axis=0)
            if return_spins: spins.append(FH)
    np.savetxt(fil_mag,mags,fmt='%14.6f')
    spins = np.array(spins)
    return spins, mags
