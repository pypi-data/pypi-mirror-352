from aart import *

def cintensity(**params):
    """
    Computes the radial intensity observables of the BH. Requires 'raytracing' and 'clb' from the 'raytracing' and 'lensingbands' modules respectively to have been called for the corresponding spins and angles.
    :param spins: an iterable object containing BH spins
    :param i_angles: an iterable object containing BH inclination angles, relative to the observer, in degrees
    :param mup: Johnson's SU distribution parameter, as a function of the other parameters
    :param sub_kep: sub-kepleniarity
    :param betaphi: angular velocity
    :param betar: radial velocity
    :param gfactor: power of the redshift factor
    :param gammap: Johnson's SU distribution parameter
    :param sigmap: Johnson's SU distribution parameter
    :param bvapp: takes on values 0 or 1. If equal to 1, the Beloborodov approximation will also be computed
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
    gfactor=params.get('gfactor')
    path=params.get('path')

        
    for i in range(len(spins)):
        mask=i
        spin_case=spins[mask]
        
        for i_case in i_angles:
            isco=rms(spin_case)
            thetao=i_case*np.pi/180
            
            fnbands=path+"LensingBands_a_%s_i_%s_dx0_%s_dx1_%s_dx2_%s.h5"%(spin_case,i_case, dx0, dx1, dx2)

            print("Reading file: ",fnbands)

            h5f = h5py.File(fnbands,'r')

            supergrid0=h5f['grid0'][:]
            mask0=h5f['mask0'][:]
            N0=int(h5f["N0"][0])

            if bvapp!=1:

                supergrid1=h5f['grid1'][:]
                mask1=h5f['mask1'][:]
                N1=int(h5f["N1"][0])

                supergrid2=h5f['grid2'][:]
                mask2=h5f['mask2'][:]
                N2=int(h5f["N2"][0])

                fnrays=path+"Rays_a_%s_i_%s_bv_%s_dx0_%s_dx1_%s_dx2_%s.h5"%(spin_case,i_case, bvapp, dx0, dx1, dx2)

                print("Reading file: ", fnrays)

                h5f = h5py.File(fnrays,'r')

                rs0=h5f['rs0'][:]
                sign0=h5f['sign0'][:]
                rs1=h5f['rs1'][:]
                sign1=h5f['sign1'][:]
                rs2=h5f['rs2'][:]
                sign2=h5f['sign2'][:]
                h5f.close()
                
                obsint.br(supergrid0,mask0,N0,rs0,sign0,supergrid1,mask1,N1,rs1,sign1,supergrid2, mask2,N2,rs2,sign2,spin_case, i_case, isco, thetao, mask3=mask, **params)
                
              
            else:

                h5f.close()

                fnrays=path+"Rays_a_%s_i_%s_bv_%s_dx0_%s_dx1_%s_dx2_%s.h5"%(spin_case,i_case, bvapp, dx0, dx1, dx2)
                print("Reading file: ",fnrays)

                h5f = h5py.File(fnrays,'r')

                rs0_bv=h5f['rs0_bv'][:]
                sign0_bv=h5f['sign0_bv'][:]

                h5f.close()

                obsint.br_bv(supergrid0,mask0,N0,rs0,sign0, spin_case, i_case, isco, thetao, mask3=mask, **params)	
                
    
