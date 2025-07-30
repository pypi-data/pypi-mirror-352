from aart import *

def image(**params):
    """
    Ray traces a given equatorial source profile, producing a single image. Currently, this function is limited to the use of inoisy files (see https://github.com/AFD-Illinois/inoisy). The inoisy file should be saved in the same directory as the file calling this funciton.
    :param spins: an iterable object containing BH spins
    :param i_angles: an iterable object containing BH inclination angles, relative to the observer, in degrees
    :param bvapp: takes on values 0 or 1. If equal to 1, the Beloborodov approximation will also be computed
    :param D_obs: observer's distance in units of M    
    :param path: path for saving the output. This should be consistent across the usage of all functions in this package
    :param i_fname: sample equatorial profile    
    :param psi: BH mass-to-distance ratio (default: 1/psi=6.2e9 Kg)
    :param disk: takes on values "stationary", which assumes a single inoisy frame, or "dyamical"
    :param betaphi: angular velocity
    :param betar: radial velocity
    :param gfactor: power of the redshift factor
    :param sub_kep: sub-kepleniarity    
    :param i_frame: inoisy initial time frame for single images
    :param i_tM: initial time in units of M
    """
    
    spins=params.get('spins')
    i_angles=params.get('i_angles')
    bvapp=params.get('bvapp')
    D_obs=params.get('D_obs')
    path=params.get('path')
    i_fname=params.get('i_fname')
    psi=params.get('psi')
    disk=params.get('disk')
    gfactor=params.get('gfactor')
    i_frame=params.get('i_frame')
    i_tM=params.get('i_tM')
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
            data=np.flip(data,axis=(2))

            nt = data.shape[0] #inoisy time resolution
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
            
            Gc=6.67e-11 # G constant [m^3 kg^-1 s^-2]
            cc= 2.99792458e8 # c constant [m/s]
            Msc=1.988435e30 # Solar Mass [Kg]

            MMkg= 6.2e9*psi*Msc # [Kg]

            i_dt = xtend/nt
            timeconversion=i_dt*MMkg*Gc/cc**3/(3600*24) # [days]

            maxintensity=np.nanmax(data)

            if disk=="dynamical":

                print("Using all the available inoisy frames")

                interpolated3_R=RegularGridInterpolator((times,x1,x2), np.transpose(data,(0,2,1)),fill_value=0,bounds_error=False,method='linear')

                print("Computing lensed image using all inoisy frames")

                i_bghts0 = obsint.slow_light(supergrid0,mask0,sign0,spin_case,isco,rs0,phi0,np.mod(t0+i_tM+i_frame,xtend), interpolated3_R,thetao, betaphi, betar, gfactor, sub_kep);
                i_bghts1 = obsint.slow_light(supergrid1,mask1,sign1,spin_case,isco,rs1,phi1,np.mod(t1+i_tM+i_frame,xtend), interpolated3_R,thetao, betaphi, betar, gfactor, sub_kep);
                i_bghts2 = obsint.slow_light(supergrid2,mask2,sign2,spin_case,isco,rs2,phi2,np.mod(t2+i_tM+i_frame,xtend), interpolated3_R,thetao, betaphi, betar, gfactor, sub_kep);                

                i_I0 = (i_bghts0).reshape(N0,N0).T
                i_I1 = (i_bghts1).reshape(N1,N1).T
                i_I2 = (i_bghts2).reshape(N2,N2).T

                filename=path+"Dynamical_Image_a_%s_i_%s_bv_%s_bphi_%s_br_%s_gfact_%s_sk_%s_itM_%s.h5"%(spin_case,i_case, bvapp, betaphi, betar, gfactor, sub_kep, i_tM)
               

                h5f = h5py.File(filename, 'w')
                h5f.create_dataset('bghts0', data=i_I0)
                h5f.create_dataset('bghts1', data=i_I1)
                h5f.create_dataset('bghts2', data=i_I2)

                h5f.close()

                print("Images file ",filename," created.")

            else:

                print("Using a single inoisy frame")

                interpolated2_R=RegularGridInterpolator((x1,x2), data[i_frame,:,:].T,fill_value=0,bounds_error=False,method='linear')

                print("Computing a lensed image")

                i_bghts0 = obsint.fast_light(supergrid0,mask0,sign0,spin_case,isco,rs0,phi0, interpolated2_R,thetao, betaphi, betar, gfactor, sub_kep)
                i_bghts1 = obsint.fast_light(supergrid1,mask1,sign1,spin_case,isco,rs1,phi1, interpolated2_R,thetao, betaphi, betar, gfactor, sub_kep)
                i_bghts2 = obsint.fast_light(supergrid2,mask2,sign2,spin_case,isco,rs2,phi2, interpolated2_R,thetao, betaphi, betar, gfactor, sub_kep)
                

                i_I0 = (i_bghts0).reshape(N0,N0).T
                i_I1 = (i_bghts1).reshape(N1,N1).T
                i_I2 = (i_bghts2).reshape(N2,N2).T

                filename=path+"Dynamical_Image_a_%s_i_%s_bv_%s_bphi_%s_br_%s_gfact_%s_sk_%s_itM_%s.h5"%(spin_case,i_case, bvapp, betaphi, betar, gfactor, sub_kep, i_tM)

                h5f = h5py.File(filename, 'w')
                h5f.create_dataset('bghts0', data=i_I0)
                h5f.create_dataset('bghts1', data=i_I1)
                h5f.create_dataset('bghts2', data=i_I2)

                h5f.close()

                print("Single image file ",filename," created.\n")