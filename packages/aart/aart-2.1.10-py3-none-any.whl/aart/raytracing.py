from aart import *

def raytrace(**params):
    """
    Carries out analytical raytracing and saves the calculations as separate files according to spin-angle combinations.  Requires the 'clb' function in the 'lensingbands' module to have already been called for the correspondsing spins and angles.
    :param spins: an iterable object containing BH spins
    :param i_angles: an iterable object containing BH inclination angles, relative to the observer, in degrees
    :param bvapp: takes on values 0 or 1. If equal to 1, the Beloborodov approximation will also be computed
    :param D_obs: observer's distance in units of M
    :param path: path for saving the output. This should be consistent across the usage of all functions in this package
    """
    
    spins=params.get('spins')
    i_angles=params.get('i_angles')
    bvapp=params.get('bvapp')
    D_obs=params.get('D_obs')
    limits=params.get('limits')
    dx0=params.get('dx0')
    dx1=params.get('dx1')
    dx2=params.get('dx2')
    path=params.get('path')
        
    for a in spins:
        for i in i_angles:
            
            thetao=i*np.pi/180
    
            fnbands=path+"LensingBands_a_%s_i_%s_dx0_%s_dx1_%s_dx2_%s.h5"%(a,i, dx0, dx1, dx2)

            print("Reading file: ",fnbands)

            h5f = h5py.File(fnbands,'r')

            supergrid0=h5f['grid0'][:]
            mask0=h5f['mask0'][:]

            if bvapp!=1:

                supergrid1=h5f['grid1'][:]
                mask1=h5f['mask1'][:]
                supergrid2=h5f['grid2'][:]
                mask2=h5f['mask2'][:]
                h5f.close()

                rt.rt(supergrid0,mask0,supergrid1,mask1,supergrid2,mask2, a, i, **params)
                print("A total of",supergrid0.shape[0]+supergrid1.shape[0]+supergrid2.shape[0],"photons were ray-traced")

            else:

                h5f.close()

                rt.rs_bv(supergrid0,mask0, a, i, **params)
                print("A total of",supergrid0.shape[0],"photons were approximately ray-traced.")
                
