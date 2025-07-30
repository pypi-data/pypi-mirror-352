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


#=============================================
#
# Monte Carlo simulations
# Parallel version with and without
# parallel-tempering techniques
#
# Shunhong Zhang
# Mar 21, 2021
#
#=============================================

from asd.core.monte_carlo import *
from asd.mpi.topological_charge import *


"""
Suppose the spin Hamiltonian is defined on a large supercell
for instance, a Edwards-Anderson model for spin glass
If the simulated system is structurally ordered
Then we can divide the supercell into "blocks"
so that Monte Carlo updates can be simultaneously
carried out in all blocks
This is beneficial for parallelization
We of course need to ensure that update a spin in one block
does not perturb other blocks
It therefore requires a proper way of
partitioning the sites within the supercell
This function servers this purpose
"""
def divide_supercell_into_blocks(sites_shape, group_x, group_y, group_z):
    if len(sites_shape)==4: nx,ny,nat = sites_shape[:-1]; nz=1
    if len(sites_shape)==5: nx,ny,nz,nat = sites_shape[:-1]
    xx,yy,zz = np.mgrid[0:nx:group_x, 0:ny:group_y, 0:nz:group_z]
    xstarts = xx.flatten()
    ystarts = yy.flatten()
    zstarts = zz.flatten()
    nblock = len(xstarts)
    nat_sc = np.prod(sites_shape[:-1])

    block_site_indices = []
    for iblock in range(nblock):
        block_site_indices.append([])
        for ix0,iy0,iz0,iat in np.ndindex(group_x, group_y, group_z, nat):
            ix = ix0 + xstarts[iblock]
            iy = iy0 + ystarts[iblock]
            iz = iz0 + zstarts[iblock]
            iat_sc = iat + nat * (iz + nz * (iy + ny*ix))
            if iat_sc<nat_sc:
                if len(sites_shape)==4:   site_idx = [0,0,iat_sc]
                elif len(sites_shape)==5: site_idx = [0,0,0,iat_sc]
                block_site_indices[iblock].append(site_idx)

    # If sites coordinates are available, check them
    """
    sites_sc = sites.reshape(1,1,1,-1,sites.shape[-1])
    for iblock in range(nblock):
        for idx in block_site_indices[iblock]:
            print (sites_sc[tuple(idx)])
        print ('\n')
    """
    return block_site_indices




"""
The parallel version of Monte Carlo simulation
The whole supercell is grouped into some blocks
The parameters group_x, group_y and group_z 
describe the dimension of each block

In realistic simulations should be modified 
according to the exchange distance
"""
def run_parallel_monte_carlo(ham,sp_lat,
    temperature=0.1,
    mcs=10,
    verbosity=2,
    sample_method='Gaussian',sigma0=-1,
    adaptive=True,
    target_acceptance_ratio=0.5,
    max_sigma0=60,
    start_conf='as_input',
    spin_coord=None,
    fix_boundary_spin=False,
    pinned_idx=None,
    log_handle = log_handle,
    q_for_Potts=3,
    group_x=3,
    group_y=3,
    group_z=1,
    divide_supercell=False,
    sites_shape=None,
    rank_group=None,
    rank_root=0,
    random_seed=10358):
 
    
    import asd.mpi.mpi_tools as mt
    import mpi4py.MPI as MPI

    comm,size,rank,node = mt.get_mpi_handles()
    group_comm,group_size,group_rank = mt.get_group_handles(rank_group)

    def verbose_one_MC_sweep(imcs, sp_lat):
        acpt_rate = (1 - float(fail_count)/((imcs+1)*nsites)) *100
        if adaptive and sm=='gaussian': adapt_sigma0(sigma0,acpt_rate,max_sigma0)

        if (imcs==0 or (imcs+1)%log_handle._n_log_magnetization==0 or imcs==mcs-1) and verbosity>1:
            mm=np.average(sp_lat.reshape(-1,ndim),axis=0)
            used_time = time.time()-stime
            n_trials = (imcs+1)*nsites
            print (fmt_step.format((imcs+1)*(imcs!=0),Etot,used_time,fail_count,n_trials,acpt_rate,sigma0,*tuple(mm)),file=fw)
            if fw is not None: fw.flush()
            if fa is not None:
                if log_handle._log_topo_chg and log_handle._tri_simplices is not None:
                    fa.write(fmt_step_a.format((imcs+1)*(imcs!=0),Etot,*tuple(mm),Q)+'\n')
                else:
                    fa.write(fmt_step_a.format((imcs+1)*(imcs!=0),Etot,*tuple(mm))+'\n')
                fa.flush()
            sys.stdout.flush()
        if ((imcs+1)%log_handle._n_log_configuration==0 or imcs==mcs-1):
            log_spin_configuration(log_handle,sp_lat,ham._spin_coord,temperature,Etot,imcs)



    if group_comm != MPI.COMM_NULL:
        sm = sample_method.lower()
        if temperature==0: beta = np.inf
        else: beta = 1/(kB*temperature)

        if group_rank == rank_root:  
            if rank_group is not None: random_seed += np.sum(rank_group)
            sp_lat = initialize_spin_lattice(sp_lat,start_conf,random_seed=random_seed)
        sp_lat = group_comm.bcast(sp_lat,root=rank_root)

        shape = sp_lat.shape
        nx,ny,nz,nat,dyn_idx = get_dynamics_sites_indices(shape,fix_boundary_spin,pinned_idx)
        nsites = np.prod(shape[:-1])
        ndim = shape[-1]
        fmt_step, fmt_step_a, fmt_head_a, head_tags_a = set_verbose_format(ndim, log_handle)

        if divide_supercell:
            assert sites_shape is not None, "sites_shape (nx,ny,nz,nat,ndim) should be specified for divide_supercell=True!"
            block_site_indices = divide_supercell_into_blocks(sites_shape, group_x, group_y, group_z)
            nblock = len(block_site_indices)
        else:
            check_block_neigh(ham,sp_lat,group_x,group_y,group_z)
            xx,yy,zz = np.mgrid[0:nx:group_x,0:ny:group_y,0:nz:group_z]
            xstarts = xx.flatten()
            ystarts = yy.flatten()
            zstarts = zz.flatten()
            nblock = len(xstarts)

        start,last = mt.assign_task(nblock,group_size,group_rank)

        if group_rank==rank_root:
            Etot = ham.calc_total_E(sp_lat)
            log_handle.prepare_logging_dir()
            stime = time.time()
            if verbosity>1:
                if log_handle._log_ham: log_spin_hamiltonian(ham,sp_lat,log_handle._log_ham_file)
                fw = print_MC_setup(temperature,mcs,nsites,nblock,group_size,log_handle,
                sample_method,sigma0,adaptive,target_acceptance_ratio,max_sigma0,start_conf,rank_group,ndim=ndim)
                if divide_supercell:
                    with open('{}/block_site_indices.dat'.format(log_handle._outdir),'w') as fb:
                        for iblock, block_iats in enumerate(block_site_indices):
                            fmt = '{:4d} '*len(block_iats)+'\n'
                            iats_sc = [iats[-1] for iats in block_iats]
                            fb.write(fmt.format(*tuple(iats_sc)))
            if verbosity:
                if log_handle._log_file is not None: fw=open(log_handle._log_file,'a')
                else: fw=None
                fa = None
                if log_handle._archive_file is not None: 
                    fa=open(log_handle._archive_file,'w')
                    fa.write(fmt_head_a.format(*tuple(head_tags_a))+'\n')
            if log_handle._log_initial_conf: save_conf_to_ovf(sp_lat,Etot,temperature,log_handle._init_conf_file,'w') 
            log_spin_configuration(log_handle,sp_lat,ham._spin_coord,temperature,Etot,0)

        # J. Phys.: Condens. Matter 26 (2014) 103202, Eq. 24
        if sigma0==-1: sigma0 = np.power(kB*temperature/muB,1/5.)*2/25

        group_comm.barrier()

        fail_count = 0
        fail = 0
        for imcs in range(mcs):
            if divide_supercell:
                max_block_nsite = max([len(indices) for indices in block_site_indices])
                for iat in range(max_block_nsite):
                    update_spins = []
                    for iblock in range(start,last):
                        if iat < len(block_site_indices[iblock]):
                            site_idx = block_site_indices[iblock][iat]
                            n_i = copy.copy(sp_lat[tuple(site_idx)])
                            E1 = ham.calc_local_energy(sp_lat,site_idx)
                            sp_lat[tuple(site_idx)] = propose_one_spin(n_i,sigma0,sample_method,q_for_Potts)
                            E2 = ham.calc_local_energy(sp_lat,site_idx)
                            dE = E2 - E1
                            if dE > 0 and np.random.rand() > np.exp(-beta*dE):
                                update_spins.append(n_i)
                                fail += 1
                            else:
                                update_spins.append(copy.copy(sp_lat[tuple(site_idx)]))
                        else:
                            update_spins.append(None)

                    update_spins = group_comm.gather(update_spins,root=rank_root)
                    if group_rank==rank_root:
                        update_spins = [spin for spins in update_spins for spin in spins]
                        assert len(update_spins)==nblock, '{}# of update spins != # of blocks!'.format(err_text)
                        for iblock in range(nblock):
                            if iat >= len(block_site_indices[iblock]): continue
                            site_idx = block_site_indices[iblock][iat]
                            if update_spins[iblock] is not None:
                                sp_lat[tuple(site_idx)] = update_spins[iblock]
                    group_comm.barrier()
                    sp_lat = group_comm.bcast(sp_lat,root=rank_root)


            else:
                def get_global_site_idx(ix0, iy0, iz0, iblock):
                        ix = ix0 + xstarts[iblock]
                        iy = iy0 + ystarts[iblock]
                        iz = iz0 + zstarts[iblock]

                        if ix<=nx-1 and iy<=ny-1 and iz<=nz-1: 
                            if len(shape)==4: site_idx = (ix,iy,iat)
                            if len(shape)==5: site_idx = (ix,iy,iz,iat)
                        else: 
                            site_idx = None
                        return site_idx

 
                for ix0,iy0,iz0,iat in np.ndindex(group_x, group_y, group_z, nat):
                    update_spins = []
                    for iblock in range(start,last):
                        site_idx = get_global_site_idx(ix0, iy0, iz0, iblock)

                        if site_idx is not None:
                            n_i = copy.copy(sp_lat[tuple(site_idx)])
                            E1 = ham.calc_local_energy(sp_lat,site_idx)
                            sp_lat[tuple(site_idx)] = propose_one_spin(n_i,sigma0,sample_method,q_for_Potts)
                            E2 = ham.calc_local_energy(sp_lat,site_idx)
                            dE = E2 - E1
                            if dE > 0 and np.random.rand() > np.exp(-beta*dE):
                                update_spins.append(n_i)
                                fail += 1
                            else:
                                update_spins.append(copy.copy(sp_lat[tuple(site_idx)]))
                        else:
                            update_spins.append(None)

                    update_spins = group_comm.gather(update_spins,root=rank_root)
                    if group_rank==rank_root:
                        update_spins = [spin for spins in update_spins for spin in spins]
                        assert len(update_spins)==nblock, '{}# of update spins != # of blocks!'.format(err_text)
                        for iblock in range(nblock):
                            if update_spins[iblock] is not None:
                                site_idx = get_global_site_idx(ix0, iy0, iz0, iblock)
                                sp_lat[tuple(site_idx)] = update_spins[iblock]
                    group_comm.barrier()
                    sp_lat = group_comm.bcast(sp_lat,root=rank_root)


            fail_count = group_comm.allreduce(fail)
            log_flag = (imcs==0 or (imcs+1)%log_handle._n_log_magnetization==0 or (imcs+1)%log_handle._n_log_configuration==0 or imcs==mcs-1)
            if log_flag:  Etot = ham.calc_total_E(sp_lat)
            if log_handle._log_topo_chg and log_handle._tri_simplices is not None: 
                Q = mpi_calc_topo_chg_one_conf(sp_lat,tri_simplices = log_handle._tri_simplices)

            if group_rank==rank_root: verbose_one_MC_sweep(imcs, sp_lat)
            sigma0 = group_comm.bcast(sigma0,root=rank_root)

        if group_rank == rank_root: 
            if log_handle._log_final_conf: save_conf_to_ovf(sp_lat,Etot,temperature,log_handle._final_conf_file,'w') 
            if verbosity: print_MC_end(stime,fw)
            if fa is not None: fa.close()
        sp_lat = group_comm.bcast(sp_lat,root=rank_root)
        Etot = group_comm.bcast(Etot,root=rank_root)
        return sp_lat,Etot



class MC_controller(object):
    def __init__(self,
        temperature=0.1,
        mcs=10,
        verbosity=2,
        sample_method='gaussian',sigma0=-1,
        adaptive=True,
        target_acceptance_ratio=0.5,
        max_sigma0=60,
        start_conf='as_input',
        spin_coord=None,
        fix_boundary_spin=False,
        pinned_idx=None,
        log_handle = log_handle,
        q_for_Potts = 3,
        group_x=3,
        group_y=3,
        group_z=1,
        divide_supercell=False,
        sites_shape=None,
        rank_group=None,
        rank_root=0):
 

        self.set_temperature(temperature)
        self.set_mcs( mcs )
        self.set_verbosity( verbosity)
        self._sample_method = sample_method
        self._adaptive = adaptive
        self._target_acceptance_ratio = target_acceptance_ratio
        self._max_sigma0 = max_sigma0
        self._start_conf = start_conf
        self._spin_coord = spin_coord
        self._fix_boundary_spin = fix_boundary_spin
        self._pinned_idx = pinned_idx
        self.set_q_for_Potts( q_for_Potts )
        self.set_log_handle( log_handle )
        self.set_verbosity( verbosity )

        # parameters related to sampling
        # J. Phys.: Condens. Matter 26 (2014) 103202, Eq. 24
        self.set_sigma0(sigma0)
        self._adaptive = adaptive
        self._target_acceptance_ratio = target_acceptance_ratio

        # parameters related to block division and parallelization
        self._group_x = group_x
        self._group_y = group_y
        self._group_z = group_z
        self._divide_supercell = divide_supercell
        self._sites_shape = sites_shape
        self.set_rank_group( rank_group )
        self.set_rank_root( rank_root )


    def set_verbosity(self,verbosity):
        err = 'MC_controller: You try to set verbosity = {}, it should be an non-negative integer!'.format(verbosity)
        assert type(verbosity)==int and verbosity>=0, err
        self._verbosity = verbosity

    def set_mcs(self,mcs):
        self._mcs = mcs

    def set_q_for_Potts(self,q_for_Potts):
        self._q_for_Potts = q_for_Potts

    def set_rank_root(self,rank_root):
        self._rank_root = rank_root

    def set_rank_group(self,rank_group):
        self._rank_group = rank_group

    def set_temperature(self,temperature):
        assert temperature>=0, 'Attempt to set temperature < 0, NOT Allowed!'
        self._temperature = temperature
        if self._temperature<1e-6: self._beta = np.inf
        else: self._beta = 1/(kB*self._temperature)


    def set_sigma0(self,sigma0):
        if sigma0==-1: self._sigma0 = np.power(kB*self._temperature/muB,1/5.)*2/25
        else: self._sigma0 = sigma0
 

    def set_log_handle(self,log_handle):
        self._log_handle = log_handle
        self.__dict__.update(log_handle.__dict__)


    def estimate_nblock(self,sp_lat):
        nx,ny,nz,nat,dyn_idx = get_dynamics_sites_indices(sp_lat.shape,pinned_idx=self._pinned_idx)
        nnx = np.ceil(nx/self._group_x)
        nny = np.ceil(ny/self._group_y)
        nnz = np.ceil(nz/self._group_z)
        nblock = int(nnx*nny*nnz)
        return nblock
 

    @property
    def get_rank_root(self):
        return self._rank_root
    
    @property
    def get_rank_group(self):
        return self._rank_group

    @property
    def get_temperature(self):
        return self._temperature


    def run_parallel_monte_carlo(self,ham,sp_lat):
        #sp_lat, Etot = run_parallel_monte_carlo(ham, sp_lat,
        run_parallel_monte_carlo(ham, sp_lat,
        self._temperature,
        self._mcs,
        self._verbosity,
        self._sample_method,self._sigma0,
        self._adaptive,
        self._target_acceptance_ratio,
        self._sigma0,self._start_conf,
        self._spin_coord,
        self._fix_boundary_spin,
        self._pinned_idx,
        self._log_handle,
        self._q_for_Potts,
        self._group_x,
        self._group_y,
        self._group_z,
        self._divide_supercell,
        self._sites_shape,
        self._rank_group,
        self._rank_root)

        pickle.dump(self, open('{}/MC_controller.pickle'.format(self._outdir), 'wb'))
        pickle.dump(ham, open('{}/ham_spin.pickle'.format(self._outdir), 'wb'))

        #return sp_lat, Etot




class PTMC_controller(MC_controller):
    def __init__(self,
        temperature = 0.1,
        mcs=10,
        verbosity=2,
        sample_method='gaussian',sigma0=-1,
        adaptive=True,
        target_acceptance_ratio=0.5,
        max_sigma0=60,
        start_conf='as_input',
        spin_coord=None,
        fix_boundary_spin=False,
        pinned_idx=None,
        log_handle = log_handle,
        q_for_Potts = 3,
        group_x=3,
        group_y=3,
        group_z=1,
        divide_supercell=False,
        sites_shape=None,
        parallel_temperatures=np.arange(1,10),
        nepoch=3):

        self.set_parallel_temperatures(parallel_temperatures)
        self._nepoch = nepoch

        super().__init__(
        temperature = self._parallel_temperatures[0],
        mcs = mcs,
        verbosity = verbosity,
        sample_method = sample_method,
        sigma0 = sigma0,
        adaptive = adaptive,
        target_acceptance_ratio = target_acceptance_ratio,
        max_sigma0 = max_sigma0,
        start_conf = start_conf,
        spin_coord = spin_coord,
        fix_boundary_spin = fix_boundary_spin,
        pinned_idx = pinned_idx,
        log_handle = log_handle,
        q_for_Potts = q_for_Potts,
        group_x = group_x,
        group_y = group_y,
        group_z = group_z,
        divide_supercell = divide_supercell,
        sites_shape = sites_shape,
        )
            

        self._MC_controller=MC_controller(
        self._parallel_temperatures[0],
        mcs,
        verbosity,
        sample_method,sigma0,
        adaptive,
        target_acceptance_ratio,
        max_sigma0,
        start_conf,
        spin_coord,
        fix_boundary_spin,
        pinned_idx,
        log_handle,
        q_for_Potts,
        group_x,
        group_y,
        group_z,
        divide_supercell,
        sites_shape)


    def set_verbosity(self,verbosity):
        super().set_verbosity(verbosity)

    def set_q_for_Potts(self,q_for_Potts):
        super().set_q_for_Potts(q_for_Potts)


    def set_parallel_temperatures(self,parallel_temperatures):
        self._parallel_temperatures = parallel_temperatures
        self._nimages = len(self._parallel_temperatures)
        self._index_images = list(range(self._nimages))


    def estimate_nblock(self,sp_lat):
        return super().estimate_nblock(sp_lat)


    def suggested_nproc(self,sp_lat):
        nblock = self.estimate_nblock(sp_lat)
        suggested_nproc = nblock * self._nimages
        return suggested_nproc


    def print_PTMC_setup(self,rank_groups,fw=None,suggested_nproc=None):
        size = np.sum([len(group) for group in rank_groups])
        #pkg_info().verbose_info(fw)
        print('\n\n{}'.format('='*60),file=fw)
        print ('{}Parallel Temperature Monte Carlo simulation\n{}\n'.format(pmc_text,'='*60),file=fw)
        print ('{} Images for parallel-tempering'.format(self._nimages),file=fw)
        print ('See temperatures_PTMC.dat for simulated temperatures\n',file=fw)
 
        if suggested_nproc is not None: 
            print ('Suggested No. of processes: {}, or integer times of it'.format(suggested_nproc))
        print ('Parallel on {} cores'.format(size))

        print ('\nTimes (epoches) of exchanging images = {}'.format(self._nepoch),file=fw)
        print ('Set verbosity > 1 to output\nmore details about each simulation\n',file=fw)

        print ('PTMC Started  at {}\n\n'.format(time.ctime()),file=fw)
        log_handle = self.gen_log_handle(0,0)
        log_handle.verbose_logging_info()
        if self._outdir not in ['.','./',os.getcwd()]:
            if os.path.isdir(self._outdir): os.system('rm -r {} 2>/dev/null'.format(self._outdir))
            os.mkdir(self._outdir)
        np.savetxt('{}/temperatures_PTMC.dat'.format(self._outdir),self._parallel_temperatures,fmt='%7.3f')
 
        fh = open('{}/PTMC_swap_images_history.dat'.format(self._outdir),'w')
        fh.write('#Epoch ' + 'Parallel temperatures (K)'.center(7*self._nimages) + '\n')
        fmt = '{:5s} ' + '{:6.2f} '*self._nimages + '\n'
        fh.write(fmt.format('#', *tuple(self._parallel_temperatures)))
        fmt = '{:5d} ' + '{:6d} '*self._nimages + '\n'
        fh.write(fmt.format(0, *tuple(self._index_images)))
        fh.flush()
        return fh


    def gen_log_handle(self,iepoch,itemp):
        log_handle = log_general(
        prefix = 'Epoch_{}_itemp_{}'.format(iepoch,itemp),
        log_file = 'MC.log',
        log_conf_file = 'confs.ovf',
        log_ham = False,
        log_conf = self._log_conf,
        log_topo_chg = self._log_topo_chg,
        log_initial_conf = self._log_initial_conf,
        n_log_conf = self._n_log_configuration,
        n_log_magn = self._n_log_magnetization,
        outdir= self._outdir,
        remove_existing_outdir=False,
        tri_simplices = self._tri_simplices,
        )
        return log_handle


    def run_one_epoch_v1(self,iepoch,ham,sp_lat,rank_groups,rank):
        for itemp,temperature in enumerate(self._parallel_temperatures):
            if rank in rank_groups[itemp]:
                log_handle = self.gen_log_handle(iepoch,itemp)
                super().set_log_handle(log_handle)
                super().set_temperature(temperature)
                super().set_sigma0(self._sigma0)
        comm.barrier()
        for itemp,temperature in enumerate(self._parallel_temperatures):
            super().set_rank_group(rank_groups[itemp])
            #super().set_rank_root(rank_groups[itemp][0]) # may lead to error
            assert self._rank_group is not None, 'Epoch {} itemp {} failed'.format(iepoch,itemp)
            #if rank==rank_groups[ii][0]: print ('{:<20s} lanuched'.format(self._prefix.rstrip('_')))
            super().run_parallel_monte_carlo(ham,sp_lat)
        comm.barrier()
        itemp  = np.where(self._parallel_temperatures == super()._temperature)[0][0]
        new_sp_lat = load_conf_from_ovf(sp_lat,'{}/Epoch_{}_itemp_{}_final_confs.ovf'.format(self._outdir,iepoch,itemp))
        return new_sp_lat
    
 

    def run_one_epoch_v2(self,iepoch,ham,sp_lat,rank_groups,rank):
        for itemp,temperature in enumerate(self._parallel_temperatures):
            if rank in rank_groups[itemp]:
                log_handle = self.gen_log_handle(iepoch,itemp)
                self._MC_controller.set_log_handle(log_handle)
                self._MC_controller.set_temperature(temperature)
                self._MC_controller.set_sigma0(self._sigma0)
        comm.barrier()
        for itemp,temperature in enumerate(self._parallel_temperatures):
            self._MC_controller.set_rank_group(rank_groups[itemp])
            #self._MC_controller.set_rank_root(rank_groups[itemp][0])   # may lead to error
            assert self._MC_controller._rank_group is not None, 'Epoch {} itemp {} failed'.format(iepoch,itemp)
            #if rank==rank_groups[ii][0]: print ('{:<20s} launched'.format(self._MC_controller._prefix.rstrip('_')))
            self._MC_controller.run_parallel_monte_carlo(ham,sp_lat)
        comm.barrier()
        itemp  = np.where(self._parallel_temperatures == self._MC_controller._temperature)[0][0]
        final_ovf = '{}/Epoch_{}_itemp_{}_final_confs.ovf'.format(self._MC_controller._log_handle._outdir,iepoch,itemp)
        new_sp_lat = load_conf_from_ovf(sp_lat, final_ovf)
        return new_sp_lat
  

 
    def swap_images(self,All_Etot,im1,im2,rank_groups):
        temp1 = self._parallel_temperatures[im1]
        temp2 = self._parallel_temperatures[im2]
        ener1 = All_Etot[rank_groups[im1][0]]
        ener2 = All_Etot[rank_groups[im2][0]]
        delta_beta = 1/(kB*temp1) - 1/(kB*temp2)
        delta_ener = ener1 - ener2
        swap_probability = min(1, np.exp(delta_beta*delta_ener))
        dice = np.random.rand(1)
        if dice < swap_probability:
            rank_groups[im1],rank_groups[im2] = rank_groups[im2],rank_groups[im1]
            self._index_images[im1], self._index_images[im2] = self._index_images[im2], self._index_images[im1]
        return rank_groups


    def report_Epoch_results(self,stime,size,rank_groups,All_Etot):
        print ('{}\n{:>8s} {:>14s}    {:<14s}\n{}'.format('='*60, 'T (K)','E(meV/site)','ranks', '-'*60))
        fmt = '{:8.2f} {:14.6f}    {}'
        for im in range(self._nimages):
            Etot = All_Etot[rank_groups[im][0]]
            print (fmt.format(self._parallel_temperatures[im],Etot,rank_groups[im]))
        print ('\nFinished at {}'.format(time.ctime()))
        print ('Time used : {:10.3f} s\n{}'.format(time.time()-stime, '='*60))
        sys.stdout.flush()


    def update_rank_groups(self,iepoch,rank_groups,All_Etot,fh=None):
        for idx_image in range(iepoch%2, self._nimages-1, 2):
            rank_groups = self.swap_images(All_Etot,idx_image,idx_image+1,rank_groups)
        fmt = '{:5d} ' + '{:6d} '*self._nimages + '\n'
        fh.write(fmt.format(iepoch+1, *tuple(self._index_images)))
        if fh is not None: fh.flush()
        return rank_groups


    def run_Parallel_Temperature_Monte_Carlo(self,ham,sp_lat,method=1):
        import asd.mpi.mpi_tools as mt
        comm,size,rank,node = mt.get_mpi_handles()
        err_msg = 'PTMC: No. of processes should not be smaller than No. of Images (temperatures)! Now : {} < {}'
        assert self._nimages <= size, err_msg.format(size,self._nimages)
        rank_groups = []
        for ii in range(self._nimages):
            start,last = mt.assign_task(size,self._nimages,ii)
            rank_groups.append(range(start,last))
        if rank==0: 
            t0 = time.time()
            sugg_np = self.suggested_nproc(sp_lat)
            fh = self.print_PTMC_setup(rank_groups,suggested_nproc=sugg_np)
            pickle.dump(self, open('{}/PTMC.pickle'.format(self._outdir),'wb'))
            pickle.dump(ham, open('{}/ham_spin.pickle'.format(self._outdir),'wb'))
        sp_lat = initialize_spin_lattice(sp_lat,self._start_conf)
        comm.barrier() 
 
        for iepoch in range(self._nepoch):
            if rank==0: 
                print ('\nPTMC: Epoch {}\nStarted  at {}'.format(iepoch,time.ctime()))
                sys.stdout.flush()
            stime = time.time()
            comm.barrier()
            if method==1:  sp_lat = self.run_one_epoch_v1(iepoch,ham,sp_lat,rank_groups,rank)
            if method==2:  sp_lat = self.run_one_epoch_v2(iepoch,ham,sp_lat,rank_groups,rank)
            comm.barrier()
            Etot = ham.calc_total_E(sp_lat)
            comm.barrier()
            All_Etot = comm.gather(Etot)
            if rank==0:
                self.report_Epoch_results(stime,size,rank_groups,All_Etot)
                rank_groups = self.update_rank_groups(iepoch,rank_groups,All_Etot,fh)
            self._MC_controller._start_conf = 'as_input'
            rank_groups = comm.bcast(rank_groups, root=0)
            comm.barrier()
        if rank==0:
            print ('\nPTMC Finished  at {}'.format(time.ctime()))
            print ('Time used : {:10.3f} s\n'.format(time.time()-t0))
            fh.close()


    def get_PTMC_results_one_epoch(self,iepoch,skiprows=3):
        import glob
        all_energies = []
        all_magnetizations = []
        for itemp,temperature in enumerate(self._parallel_temperatures):
            Mfile = '{}/Epoch_{}_itemp_{}_M.dat'.format(self._outdir,iepoch,itemp)
            assert len(glob.glob(Mfile))>0,'When extracting PTMC results, {} not found!'.format(Mfile)
            data = np.loadtxt(Mfile,skiprows=skiprows)
            all_energies.append(data[:,1])
            all_magnetizations.append(data[:,-3:])
        all_energies = np.array(all_energies)
        all_magnetizations = np.array(all_magnetizations)
        return all_energies, all_magnetizations
