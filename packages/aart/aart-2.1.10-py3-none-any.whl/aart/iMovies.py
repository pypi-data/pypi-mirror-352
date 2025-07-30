from aart import *
from multiprocessing import get_context
from functools import partial
              
def mp_worker(supergrid0,mask0,sign0, rs0, phi0, t0, supergrid1,mask1,sign1, rs1, phi1, t1, supergrid2,mask2,sign2, rs2, phi2, t2, spin_case, isco, xtend, interpolated3_R, thetao, betaphi, betar, gfactor, sub_kep, N0, N1, N2, tsnap):
    """
    Helper function for implementing 'movie'.
    """
    
    i_bghts0 = obsint.slow_light(supergrid0,mask0,sign0,spin_case,isco,rs0,phi0,np.mod(t0+tsnap,xtend), interpolated3_R,thetao, betaphi, betar, gfactor, sub_kep)
    
    i_bghts1 = obsint.slow_light(supergrid1,mask1,sign1,spin_case,isco,rs1,phi1,np.mod(t1+tsnap,xtend), interpolated3_R,thetao, betaphi, betar, gfactor, sub_kep)
    
    i_bghts2 = obsint.slow_light(supergrid2,mask2,sign2,spin_case,isco,rs2,phi2,np.mod(t2+tsnap,xtend), interpolated3_R,thetao, betaphi, betar, gfactor, sub_kep)
            
    i_I0 = (i_bghts0).reshape(N0,N0).T
    i_I1 = (i_bghts1).reshape(N1,N1).T
    i_I2 = (i_bghts2).reshape(N2,N2).T

    print("Calculating an image at time t=%s (M)"%np.round(tsnap,5))
    return(i_I0,i_I1,i_I2)

def movie(**params): 
    """
    Ray traces a given equatorial source profile, producing several images. Currently, this function is limited to the use of inoisy files (see https://github.com/AFD-Illinois/inoisy). The inoisy file should be saved in the same directory as the file calling this funciton.
    :param spin_case: BH spin
    :param i_case: BH inclination angle, relative to the observer, in degrees
    :param path: path for saving the output. This should be consistent across the usage of all functions in this package
    :param i_frame: inoisy initial time frame for single images
    :param i_fname: sample equatorial profile    
    :param D_obs: observer's distance in units of M  
    :param psi: BH mass-to-distance ratio (default: 1/psi=6.2e9 Kg)
    :param betaphi: angular velocity
    :param betar: radial velocity
    :param gfactor: power of the redshift factor
    :param sub_kep: sub-kepleniarity    
    :param i_tM: initial time in units of M. Makes sense when the time interval is less than the inoisy temporal length
    :param f_tM: final time in units of M. Makes sense when the time interval is less than the inoisy temporal length
    :param snapshots: number of snapshots in range of times [i_tM, f_tM]
    :param nthreads: number of separate flows of execution
    :param limits: limits for the image in units of M. It should coincide with the source profile used for computing and plotting observables 
    """
    
    spins=params.get('spins')
    i_angles=params.get('i_angles')
    path=params.get('path')
    i_frame=params.get('i_frame')
    i_fname=params.get('i_fname')
    D_obs=params.get('D_obs')
    psi=params.get('psi')
    gfactor=params.get('gfactor')
    i_tM=params.get('i_tM')
    f_tM=params.get('f_tM')
    snapshots=params.get('snapshots')
    nthreads=params.get('nthreads')
    limits=params.get('limits')
    bvapp=params.get('bvapp')
    dx0=params.get('dx0')
    dx1=params.get('dx1')
    dx2=params.get('dx2')
    
    for i in range(len(spins)):
        mask=i
        
        spin_case=spins[mask]
        betaphi=params.get('betaphi')[mask]
        betar=params.get('betar')[mask]
        sub_kep=params.get('sub_kep')[mask]
    
        for i_case in i_angles:
  
            isco=rms(spin_case)
            thetao=i_case*np.pi/180

            print("Movies")

            fnbands=path+"LensingBands_a_%s_i_%s_dx0_%s_dx1_%s_dx2_%s.h5"%(spin_case,i_case, dx0, dx1, dx2)

            print("Reading file: ",fnbands)

            h5f = h5py.File(fnbands,'r')

            supergrid0=h5f['grid0'][:]
            mask0=h5f['mask0'][:]
            N0=int(h5f["N0"][0])

            supergrid1=h5f['grid1'][:]
            mask1=h5f['mask1'][:]
            N1=int(h5f["N1"][0])

            supergrid2=h5f['grid2'][:]
            mask2=h5f['mask2'][:]
            N2=int(h5f["N2"][0])

            h5f.close()

            fnrays=path+"Rays_a_%s_i_%s_bv_%s_dx0_%s_dx1_%s_dx2_%s.h5"%(spin_case,i_case, bvapp, dx0, dx1, dx2)

            print("Reading file: ",fnrays)

            h5f = h5py.File(fnrays,'r')

            rs0=h5f['rs0'][:]
            sign0=h5f['sign0'][:]
            t0=h5f['t0'][:]
            phi0=h5f['phi0'][:]

            rs1=h5f['rs1'][:]
            sign1=h5f['sign1'][:]
            t1=h5f['t1'][:]
            phi1=h5f['phi1'][:]

            rs2=h5f['rs2'][:]
            sign2=h5f['sign2'][:]
            t2=h5f['t2'][:]
            phi2=h5f['phi2'][:]

            h5f.close()

            print("Reading inoisy file: ",i_fname)

            hf = h5py.File(i_fname, 'r')

            data = np.array(hf['data/data_env'])
            #inoisy has periodic boudaries, so we need to copy wrap the data with one frame
            data=np.concatenate((data,data[0,:,:][np.newaxis,:,:]),axis=0)

            nt =data.shape[0] #inoisy time resolution
            ni = data.shape[1] #inoisy x resolution
            nj = data.shape[2] #inoisy y resolution

            xtstart = np.array(hf['params/x0start'])[0]
            xtend = np.array(hf['params/x0end'])[0]

            x1start = np.array(hf['params/x1start'])[0]
            x2start = np.array(hf['params/x2start'])[0]
            x1end = np.array(hf['params/x1end'])[0]
            x2end = np.array(hf['params/x2end'])[0]

            x1 = np.linspace(x1start, x1end, ni) 
            x2 = np.linspace(x2start, x2end, nj)

            times = np.linspace(xtstart, xtend, nt)

            h5py.File.close(hf)

            fact=-(D_obs+2*np.log(D_obs))

            t0-=fact
            t1-=fact
            t2-=fact

            fact2=xtend/2-np.nanmax(t0)

            t0+=fact2
            t1+=fact2
            t2+=fact2

            print("AART starts!")

            i_dt = xtend/nt

            Gc=6.67e-11 # G constant [m^3 kg^-1 s^-2]
            cc= 2.99792458e8 # c constant [m/s]
            Msc=1.988435e30 # Solar Mass [Kg]

            MMkg= 6.2e9*psi*Msc # [Kg]
            MM=MMkg *Gc/cc**2 # Mass of the BH in meters, i.e., for M87(psi*6.2*10^9) psi ("Best fit") Solar Masses 

            timeconversion=i_dt*MMkg*Gc/cc**3/(3600*24) # [days]

            interpolated3_R=RegularGridInterpolator((times,x1,x2),  np.transpose(data,(0,2,1)),fill_value=0,bounds_error=False,method='linear')

            I0s = []
            I1s = []
            I2s = []

            func = partial(mp_worker, supergrid0,mask0,sign0, rs0, phi0, t0, supergrid1,mask1,sign1, rs1, phi1, t1, supergrid2,mask2,sign2, rs2, phi2, t2, spin_case, isco, xtend, interpolated3_R, thetao, betaphi, betar, gfactor, sub_kep, N0, N1, N2)

            p = get_context("fork").Pool(nthreads) #using n threads

            if __name__ == 'aart.iMovies':
                I0s,I1s,I2s = zip(*p.map(func, np.linspace(i_tM+i_frame,f_tM,snapshots)))

            p.close()

            filename=path+"Images_a_%s_i_%s_bv_%s_bphi_%s_br_%s_gfact_%s_sk_%s_itM_%s_ftM_%s_shots_%s.h5"%(spin_case,i_case, bvapp, betaphi, betar, gfactor, sub_kep, i_tM, f_tM, snapshots)

            h5f = h5py.File(filename, 'w')
            h5f.create_dataset('bghts0', data=np.array(I0s))
            h5f.create_dataset('bghts1', data=np.array(I1s))
            h5f.create_dataset('bghts2', data=np.array(I2s))
            h5f.create_dataset('tc', data=np.array([timeconversion]))
            h5f.create_dataset('limits', data=np.array([limits]))

            h5f.close()

            print("Images ",filename," created.\n")