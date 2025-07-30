from aart import *

def gfactor(spins, i_angles, betaphi=1.0, betar=1.0, path='./Results/'):
    """
    :param spins: an iterable object containing the spins of the BH
    :param i_angles: an iterable object containing the inclination angles of the BH relative to the observer, in degrees
    :param betaphi: angular velocity
    :param betar: radial velocity
    :param path: path for saving the output. This should be consistent across the usage of all functions in this package    
    """
    for spin_case in spins:
        for i_case in i_angles:

            print("Computing the redshift factor at each point in the image plane \n")

            fnbands=path+"LensingBands_a_%s_i_%s.h5"%(spin_case,i_case)

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

            fnbands=path+"Rays_a_%s_i_%s.h5"%(spin_case,i_case)

            print("Reading file: ",fnbands)

            h5f = h5py.File(fnbands,'r')

            rs0=h5f['rs0'][:]
            sign0=h5f['sign0'][:]
            #t0=h5f['t0'][:]
            phi0=h5f['phi0'][:]

            rs1=h5f['rs1'][:]
            sign1=h5f['sign1'][:]
            #t1=h5f['t1'][:]
            phi1=h5f['phi1'][:]

            rs2=h5f['rs2'][:]
            sign2=h5f['sign2'][:]
            #t2=h5f['t2'][:]
            phi2=h5f['phi2'][:]

            h5f.close()
            
            isco=rms(spin_case)
            
            thetao=i_case*np.pi/180

            i_g0 = obsint.gfactorf(supergrid0,mask0,sign0,spin_case,isco,rs0,phi0,thetao, betaphi, betar)
            i_g1 = obsint.gfactorf(supergrid1,mask1,sign1,spin_case,isco,rs1,phi1,thetao, betaphi, betar)
            i_g2 = obsint.gfactorf(supergrid2,mask2,sign2,spin_case,isco,rs2,phi2,thetao, betaphi, betar)

            i_g0 = (i_g0).reshape(N0,N0).T
            i_g1 = (i_g1).reshape(N1,N1).T
            i_g2 = (i_g2).reshape(N2,N2).T

            filename=path+"gfactors_a_%s_i_%s.h5"%(spin_case,i_case)

            h5f = h5py.File(filename, 'w')
            h5f.create_dataset('gs0', data=i_g0)
            h5f.create_dataset('gs1', data=i_g1)
            h5f.create_dataset('gs2', data=i_g2)

            h5f.close()
