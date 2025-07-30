from aart import *

# default form of Johnson's SU distribution parameter mu_p
def mu_p(spin_case):
    return 1-np.sqrt(1-spin_case**2)

def generate_dict(spins, i_angles, fudge, dBH=5.214795112e23, psi=1.07473555940836, D_obs=10000, sub_kep=[1.0], betar=[1.0], betaphi=[1.0], radonfile=0, bvapp=0, p_image=1, limits=25, dx0=0.02, dx1=0.02, dx2=0.02, radonangles=[0,90], i_fname="inoisy.h5", disk="dynamical", i_frame=0, i_tM=0, f_tM=12, snapshots=12, mup=[1.0], gammap=[-3/2], sigmap=[1/2], gfactor=3, maxbaseline=500, npointsS=100, nthreads=4, Ncut=0, path = './Results/'):
     
    """
    Produces a dictionary containing all the parameters for the simulations.
    :param spins: an iterable object containing BH spins
    :param i_angles: an iterable object containing BH inclination angles, relative to the observer, in degrees
    :param fudge: array of fudge factors (for n>0), indexed according to spins array
    :param dBH: distance to the BH in meters (default: M87)
    :param psi: BH mass-to-distance ratio (default: 1/psi=6.2e9 Kg)
    :param D_obs: observer's distance in units of M
    :param sub_kep: array of sub-kepleniarity values, indexed according to spins array
    :param betar: array of radial velocity values, indexed according to spins array
    :param betaphi: array of angular velocity values, indexed according to spins array
    :param radonfile: takes on values 0 or 1. If equal to 1, the radon cut profiles will be stored
    :param bvapp: takes on values 0 or 1. If equal to 1, the Beloborodov approximation will be computed
    :param p_image: takes on values 0 or 1. If equal to 1, the sizes of the grids will be equal and an image can be computed
    :param limits: limits for the image in units of M. It should coincide with the source profile used for computing and plotting observables
    :param dx0: resolution for the n=0 image in units of M
    :param dx1: resolution for the n=1 image in units of M
    :param dx2: resolution for the n=2 image in units of M   
    :param radonangles: iterable object containing the projection angles for the radon transformation
    :param i_fname: sample equatorial profile    
    :param disk: takes on values "stationary", which assumes a single inoisy frame, or "dyamical"
    :param i_frame: inoisy initial time frame for single images
    :param i_tM: initial time in units of M. Makes sense when the time interval is less than the inoisy temporal length
    :param f_tM: final time in units of M. Makes sense when the time interval is less than the inoisy temporal length
    :param snapshots: number of snapshots in range of times [i_tM, f_tM]
    :param gammap: array of values for Johnson's SU distribution parameter, indexed according to spins array
    :param mup: array of values for Johnson's SU distribution parameter, indexed according to spins array
    :param sigmap: array of values for Johnson's SU distribution parameter, indexed according to spins array
    :param gfactor: power of the redshift factor
    :param maxbaseline: max baseline in G\lambda
    :param npointsS: number of points in the critical curve
    :param nthreads: number of separate flows of execution  
    :param Ncut: Ncut==0 to use the same x-axis baselines for each case
    :param path: path for saving the output. This should be consistent across the usage of all functions in this package
    """
    

    
    #Disk's inclination  
    #Current version is just implemented for equatorial models   
    i_disk=90    
    thetad=i_disk*np.pi/180
    
#     # constants
#     Gc=6.67e-11 # G constant [m^3 kg^-1 s^-2]
#     cc= 2.99792458e8 # c constant [m/s]
#     Msc=1.988435e30 # Solar Mass [Kg]

#     MMkg= 6.2e9*psi*Msc # [Kg]
#     MM=MMkg *Gc/cc**2 # Mass of the BH in meters, i.e., for M87(psi*6.2*10^9) psi ("Best fit") Solar Masses 

#     # Size of the real image in meters
#     sizeim_Real=(limits)*MM 
#     #1 microarcsec in radians
#     muas_to_rad = np.pi/648000 *1e-6 
#     fov_Real=np.arctan(sizeim_Real/(dBH))/muas_to_rad #muas
    
    params = {
        "spins": spins,
        "i_angles": i_angles,
        "fudge": fudge,
        "dBH": dBH,
        "psi":psi,
        "D_obs": D_obs,
        "sub_kep": sub_kep,
        "betar": betar,
        "betaphi": betaphi,
        "radonfile": radonfile,
        "bvapp": bvapp,
        "p_image": p_image,
        "limits": limits,
        "dx0": dx0,
        "dx1": dx1,
        "dx2": dx2, 
        "radonangles": radonangles,
        "i_fname": i_fname,
        "disk": disk,
        "i_frame": i_frame,
        "i_tM": i_tM,
        "f_tM": f_tM,
        "snapshots": snapshots,
        "gammap": gammap,
        "mup": mup,
        "sigmap": sigmap,
        "gfactor": gfactor,
        "maxbaseline": maxbaseline,
        "npointsS": npointsS,
        "nthreads": nthreads, 
        "path": path,
        "thetad": thetad,
        "Ncut":Ncut
    }
    return params
