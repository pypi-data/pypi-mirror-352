import numpy as np
import pickle
import h5py
from scipy.signal import find_peaks
from scipy.interpolate import CubicSpline
from scipy.optimize import curve_fit
from scipy.signal import savgol_filter
from aart import *
import linecache
import sys

## defining constants for unit conversions (makes sin functinon dimensionless when fitting to V_fit)
dM=5.214795112e23  # Distance to M87 in meters
psi=1.07473555940836 # Mass of M87 1 /psi= 6.2e9 Kg
Gc=6.67e-11 # G constant [m^3 kg^-1 s^-2]
cc= 2.99792458e8 # c constant [m/s]
Msc=1.988435e30 # Solar Mass [Kg]
MMkg= 6.2e9*psi*Msc # [Kg]
MM87=MMkg *Gc/cc**2 # Mass of M87 in meters, i.e., (psi*6.2*10^9) psi ("Best fit") Solar Masses 
sizeim=MM87 # Size of M in meters
muas_to_rad = np.pi/648000 *1e-6 #1 microarcsec in radians
unitfact=1/(muas_to_rad*1e9)
M_to_muas=np.arctan(sizeim/(dM))/muas_to_rad

def PrintException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))
    

## gets calculated visibility amplitudes stored in directory 'path'
def get_visamps(mask1, mask2, norm, **params):
    spin_case=params.get('spins')[mask1]
    i_case=params.get('i_angles')[mask2]
    
    radonangles=params.get('radonangles')
    path=params.get('path')
    radonfile=params.get('radonfile')
    dx0=params.get('dx0')
    dx1=params.get('dx1')
    dx2=params.get('dx2')
    Ncut=params.get('Ncut')    
    gfactor=params.get('gfactor')
    fudge=params.get('fudge')[mask1]
    fudge=params.get('fudge')[mask1]
    bvapp=params.get('bvapp')
    betaphi=params.get('betaphi')[mask1]
    betar=params.get('betar')[mask1]
    gfactor=params.get('gfactor')
    gammap=params.get('gammap')[mask1]
    sigmap=params.get('sigmap')[mask1]
    path=params.get('path')
    mup=params.get('mup')[mask1]
    sub_kep=params.get('sub_kep')[mask1]
    fudge=params.get('fudge')[mask1]
    
    visamps = []
    radial_norm = 0
    for i in range(len(radonangles)):
        radonangle=radonangles[i]
        fnvisamps=path+"Visamp_%s_a_%s_i_%s_dx0_%s_dx1_%s_dx2_%s_sk_%s_bphi_%s_br_%s_bvapp_%s_gfact_%s_mup_%s_gp_%s_sp_%s_fudge_%s_Ncut_%s.h5"%(radonangle,spin_case,i_case, dx0, dx1, dx2, sub_kep, betaphi, betar,  bvapp, gfactor, np.round(mup, 3), gammap, sigmap, fudge, int(Ncut))
        
        h5f = h5py.File(fnvisamps,'r')
        
        visamps.append(h5f['visamp'][:])

        maxvis = np.max(np.abs(h5f['visamp'][:]))   # max norm for some baseline angle
        if maxvis > radial_norm:
            radial_norm = maxvis 
        
        h5f.close()        
    #     return np.array(visamps), np.array(norms)  
    return norm * np.array(visamps) / radial_norm    # return normalized visibility

## gets calculated visibility amplitudes stored in directory 'path'
def get_visibilities(mask1, mask2, norm, **params):
    spin_case=params.get('spins')[mask1]
    i_case=params.get('i_angles')[mask2]
    
    radonangles=params.get('radonangles')
    path=params.get('path')
    radonfile=params.get('radonfile')
    dx0=params.get('dx0')
    dx1=params.get('dx1')
    dx2=params.get('dx2')
    Ncut=params.get('Ncut')    
    gfactor=params.get('gfactor')
    fudge=params.get('fudge')[mask1]
    fudge=params.get('fudge')[mask1]
    bvapp=params.get('bvapp')
    betaphi=params.get('betaphi')[mask1]
    betar=params.get('betar')[mask1]
    gfactor=params.get('gfactor')
    gammap=params.get('gammap')[mask1]
    sigmap=params.get('sigmap')[mask1]
    path=params.get('path')
    mup=params.get('mup')[mask1]
    sub_kep=params.get('sub_kep')[mask1]
    fudge=params.get('fudge')[mask1]
    
    vis = []
    radial_norm = 0
    for i in range(len(radonangles)):
        radonangle=radonangles[i]
        fnvis=path+"Visibility_%s_a_%s_i_%s_dx0_%s_dx1_%s_dx2_%s_sk_%s_bphi_%s_br_%s_bvapp_%s_gfact_%s_mup_%s_gp_%s_sp_%s_fudge_%s_Ncut_%s.h5"%(radonangle,spin_case,i_case, dx0, dx1, dx2, sub_kep, betaphi, betar,  bvapp, gfactor, np.round(mup, 3), gammap, sigmap, fudge, int(Ncut))
        
        h5f = h5py.File(fnvis,'r')
        
        vis.append(h5f['visibility'][:])

        maxvis = np.max(np.abs(h5f['visibility'][:]))   # max norm for some baseline angle
        if maxvis > radial_norm:
            radial_norm = maxvis 
        
        h5f.close()        
    #     return np.array(vis), np.array(norms)  
    return norm * np.array(vis) / radial_norm    # return normalized visibility

## gets frequencies used in visbility amplitude file stored in directory 'path'
def get_freqs(mask1, mask2, **params):
    
    spin_case=params.get('spins')[mask1]
    i_case=params.get('i_angles')[mask2]
    radonangles=params.get('radonangles')
    path=params.get('path')
    radonfile=params.get('radonfile')
    dx0=params.get('dx0')
    dx1=params.get('dx1')
    dx2=params.get('dx2')
    Ncut=params.get('Ncut')    
    gfactor=params.get('gfactor')
    fudge=params.get('fudge')[mask1]
    bvapp=params.get('bvapp')
    betaphi=params.get('betaphi')[mask1]
    betar=params.get('betar')[mask1]
    gfactor=params.get('gfactor')
    gammap=params.get('gammap')[mask1]
    sigmap=params.get('sigmap')[mask1]
    path=params.get('path')
    mup=params.get('mup')[mask1]
    sub_kep=params.get('sub_kep')[mask1]
    fudge=params.get('fudge')[mask1]
    fnvisamps=path+"Visamp_%s_a_%s_i_%s_dx0_%s_dx1_%s_dx2_%s_sk_%s_bphi_%s_br_%s_bvapp_%s_gfact_%s_mup_%s_gp_%s_sp_%s_fudge_%s_Ncut_%s.h5"%(0,spin_case,i_case, dx0, dx1, dx2, sub_kep, betaphi, betar,  bvapp, gfactor, np.round(mup, 3), gammap, sigmap, fudge, int(Ncut))

    h5f = h5py.File(fnvisamps,'r')
    
    freqs=h5f['freqs'][:]

    h5f.close()
        
    return freqs

## returns points (x, y) corresponding to maxima in y, with a y value greater than minval
def filter_maxima(x, y, minval):
    x_new = []
    y_new = []
    for k in range(1, len(x)-1):
            if (y[k+1]-y[k]<0) and (y[k]-y[k-1]>0):
                if y[k]>minval:
                    x_new.append(x[k])
                    y_new.append(y[k])
    return x_new, y_new

## finds argument of element in 'array' with value closest to 'value'
def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx

## given arrays of arrays x and y, returns a set of curves beginning at each element in x[0], where the next point in the ith curve is that in x[1] closest to x[0][i], and so on
def generate_curves(x, y):
    x_curves = []   ## x-values for the curves
    y_curves = []   ## y-values for the curves
        
    Lx = len(x)
    
    for j in range(0,len(x[0])):
        x_curve=[x[0][j]]
        y_curve=[y[0][j]]
        
        x_new=x_curve
        for i in range(1,Lx):
            closest=find_nearest(x[i], x_new)
            x_curve.append(x[i][closest])
            y_curve.append(y[i][closest])
            x_new=x[i][closest]
            
        x_curves.append(x_curve)
        y_curves.append(y_curve)
    return x_curves, y_curves

def circlipse(x, r0, r1, r2, phi0):
        return 2*r0 + 2*np.sqrt((r1**2)*(np.sin(x-phi0)**2)+(r2**2)*(np.cos(x-phi0)**2))
    
## takes in a clean 1d signal x, and outputs a corresponding signal with gaussian noise profile (mean=mu, std=s)
def gaussian_noise(x, mu, s):
    noise = np.random.normal(mu,s,len(x))
    #return x + noise
    return np.abs(x + noise)

## takes in a clean complex signal x, and outputs a corresponding signal with an added gaussian complex noise profile (mean=mu, std=s)
def gaussian_complex_noise(x, mu, s):
    n_points=len(x)
    noisee = np.random.multivariate_normal(np.ones(2)*mu, 0.5*np.eye(2)*(s**2), size=n_points).view(np.complex128)
    noise = [s[0] for s in noisee]
    return np.abs(x + noise)

## define a function to add noise to each snapshot of the visibility spectrum and average into one profile
def average_snapshots(visamps, mu_n, s_n, norms):
    """
    :param norms: nested array containing 36 norms for each snapshot in the ns=0.0 visamp file corresponding to "visamps"
    """
    noisy_visamps=[]
    normmax=np.max([np.max(norms[i]) for i in range(len(norms))])
    for i in range(len(visamps)):
        ## normalize so that the zero astro noise profile at snaphshot i starts at 1 for all baseline angles
        visampss=visamps[i]/normmax

        ## add noise to each visibility profile across the 36 baseline angles
        visampss=np.array([rf.gaussian_noise(vis, mu_n, s_n) for vis in visampss])
        noisy_visamps.append(visampss)

    ## now average the snapshots that now have both instrumental and astrophysical noise
    visamps_n=np.zeros(noisy_visamps[0].shape) 
    for i in range(len(noisy_visamps)):
        visamps_n+=noisy_visamps[i]/len(noisy_visamps)
    return visamps_n, normmax

### PERFORM RADIAL FIT ACROSS ONE BASELINE ANGLE USING SEVERAL METHODS ###
def visamp_func_GLM(u, aL, aR, dphi):
    return np.sqrt(aL**2+aR**2+2*aL*aR*np.sin(2*np.pi*dphi*u/unitfact))

def compute_visamp_GLM_fit(freqs, visamp, ulim1_fit, ulim2_fit):
    pmax_fs = []
    pmin_fs = []
    peaksmax=[]
    peaksmin=[]
    power=np.array([])
    ## find cubic envelopes of visibility
    max_p=find_peaks(visamp)[0]
    min_p=find_peaks(-visamp)[0]

    fmax=freqs[max_p]
    visampmax=visamp[max_p]

    fmin=freqs[min_p]
    visampmin=visamp[min_p]

    # interpolation of maxima and minima respectively by polynomial to the third order
    pmax=CubicSpline(fmax,visampmax)
    pmin=CubicSpline(fmin,visampmin)
    upower=(ulim2_fit+ulim1_fit)/2
    np.append(power,(pmax(upower)+pmin(upower))/2)

    pmax=pmax(freqs)
    pmin=pmin(freqs)

    pmax_fs.append(pmax)
    pmin_fs.append(pmin)
    peaksmax.append(max_p)
    peaksmin.append(min_p)

    ## find aL and aR using upper and lower envelopes
    aL=(pmax+pmin)/2
    aR=(pmax-pmin)/2

    unitfact=1/(muas_to_rad * 1e9)
    ## functional form of the visibility with aL and aR as functions of u using the upper and lower envelopes
    def visamp_func(u,dphi):
        return np.sqrt(aL**2+aR**2+2*aL*aR*np.sin(2*np.pi*dphi*u/unitfact))


    ## finding the best fit d_\varphi with prior that d\in[30, 50]
    params, pcov_v = curve_fit(visamp_func, freqs, visamp,p0 = [40], bounds=([30],[50]), maxfev=2000)
    
    return aL, aR, params[0]

def g_fit_GLM(aL, aR, d, x, y):
    deviation= np.sum((visamp_func_GLM(x, aL, aR, d)-np.abs(y))**2)
    avg_v_fit = np.sum(visamp_func_GLM(x, aL, aR, d))
    return np.exp(-np.sqrt(deviation/len(x))/(avg_v_fit/len(x)))

## FIT USING ORIGINAL METHOD ##
def visamp_func_sqrt(u, aL, aR, dphi):
    return np.sqrt(aL**2+aR**2+2*aL*aR*np.sin(2*np.pi*dphi*u/unitfact))/np.sqrt(u*1e9)

def g_fit_1(aL, aR, d, x, y):
    deviation= np.sum((visamp_func_sqrt(x, aL, aR, d)-np.abs(y))**2)
    avg_v_fit = np.sum(visamp_func_sqrt(x, aL, aR, d))
    return np.exp(-np.sqrt(deviation/len(x))/(avg_v_fit/len(x)))

def compute_visamp_fit_sqrt(freqs, visamp, p0_ratio):
    ## approximate bounds for aL and aR
    vmax=np.max(visamp)
    umax=freqs[np.argmax(visamp)]
    vmin=np.min(visamp)
    umin=freqs[np.argmin(visamp)]

    aL_max=(1/2)*(vmax*np.sqrt(1e9*umax)+vmin*np.sqrt(1e9*umin))
    aR_max=(1/2)*(vmax*np.sqrt(1e9*umax)-vmin*np.sqrt(1e9*umin))


    ## find best fit params
    bounds = ([0,0,35], [aL_max, aR_max, 45]) 
    p0 = [aL_max*p0_ratio, aR_max*p0_ratio, 40]
    params, pcov_v = curve_fit(visamp_func_sqrt, freqs, visamp,p0=p0, bounds=bounds, maxfev=2000)
    return params  

# Define the power law function with exponential decay
def power_law_2(x, a, b):
    return a * np.exp(b * x)

def power_law_linear(x, a, b):
    return b * x + a

## functional form of the visibility with aL and aR as functions of u using the upper and lower envelopes
def visamp_func_2(u, aL, aR, dphi, exponent):
    return np.sqrt(power_law_2(u, aL, exponent)**2+power_law_2(u, aR, exponent)**2+2*power_law_2(u, aL, exponent)*power_law_2(u, aR, exponent)*np.sin(2*np.pi*dphi*u/unitfact))

## goodness of fit
def g_fit_2(aL, aR, d, exponent, x, y):
    deviation= np.sum((visamp_func_2(x, aL, aR, d, exponent)-np.abs(y))**2)
    avg_v_fit = np.sum(visamp_func_2(x, aL, aR, d, exponent))
    return np.exp(-np.sqrt(deviation/len(x))/(avg_v_fit/len(x)))

def compute_visamp_fit_2(freqs, visamp):
    # Perform curve fitting for power law behavior
    bounds = ([-np.inf, -1], [0, -0.000005]) 
    log_visamp = np.log(visamp)
    p0 = [np.mean(log_visamp), -0.0005]
    params, params_covariance = curve_fit(power_law_linear, freqs, log_visamp, p0=p0, bounds=bounds, maxfev=5000)
    aL = np.exp(params[0])
    exponent = params[1]
    
    def visamp_func_22(u, aR, dphi):
        return np.sqrt(power_law_2(u, aL, exponent)**2+power_law_2(u, aR, exponent)**2+2*power_law_2(u, aL, exponent)*power_law_2(u, aR, exponent)*np.sin(2*np.pi*dphi*(u)/unitfact))

    aR_max = 0.5 * np.max(np.exp(-exponent * freqs)) * (np.max(visamp)-np.min(visamp))
 
    ## finding the best fit d_\varphi with prior that d\in[35, 45]
    params, pcov_v = curve_fit(visamp_func_22, freqs, visamp,p0 = [aR_max/2, 40], bounds=([0, 35],[aR_max, 45]), maxfev=4000)

    return np.array([aL, params[0], params[1]]), exponent

# functional form of the visibility with aL and aR as parameters, and fitting for b
def visamp_exp_func_b(u, a, b, aL, aR, dphi):
    return np.exp(-a * (u ** b)) * np.sqrt(aL**2 + aR**2 + 2*aL*aR*np.sin(2*np.pi*dphi*u*muas_to_rad*1e9)) / np.sqrt(u)

# logarithm of exponential model functional form fitted to log visibility amplitudes
def log_model_b(u, a, b, aL, aR, dphi):
    return -a * (u ** b) + 0.5 * np.log(aL**2 + aR**2 + 2*aL*aR*np.sin(2*np.pi*dphi*u*muas_to_rad*1e9)) - 0.5 * np.log(u)

## goodness of fit
def g_fit_exp_b(a, b, aL, aR, d, x, y):
    deviation= np.sum((visamp_exp_func_b(x, a, b, aL, aR, d)-np.abs(y))**2)
    avg_v_fit = np.sum(visamp_exp_func_b(x, a, b, aL, aR, d))
    return np.exp(-np.sqrt(deviation/len(x))/(avg_v_fit/len(x)))

def compute_visamp_fit_exp_b(freqs, visamp, log_fit = False, a_max=20, b_max=3):
    vmax=np.max(visamp)
    umax=freqs[np.argmax(visamp)]
    vmin=np.min(visamp)
    umin=freqs[np.argmin(visamp)]

    # aL_max=(1/2)*(vmax*np.sqrt(umax) * np.exp(a_max * (umax ** b_max)) + vmin*np.sqrt(umin) * np.exp(a_max * (umin ** b_max)))
    aL_max=(1/2)*(vmax*np.sqrt(1e9 * umax)+vmin*np.sqrt(1e9 * umin))    
    aR_max=(1/2)*(vmax*np.sqrt(1e9 * umax)-vmin*np.sqrt(1e9 * umin))
    
    b0 = b_max/2
    
    # a0 = np.abs((np.log(vmax) - np.log(vmin)) / (umin ** b0 - umax ** b0) / 50)   # after tests, 10 is a good factor to divide by for the solver to converge
    a0 = 0.0001
    
    # print(aL_max, aR_max, a0)
    bounds = ([0, 0, 0, 0, 35], [a_max, b_max, aL_max, aR_max, 45]) 
    p0 = [a0, b0, aL_max/2, aR_max/2, 40]
        
    # finding the best fit d_\varphi with prior that d\in[35, 45]
    if log_fit:
        params, pcov_v = curve_fit(log_model_b, freqs, np.log(visamp), p0 = p0, bounds=bounds, maxfev=2000)
    else:
        params, pcov_v = curve_fit(visamp_exp_func, freqs, visamp, p0 = p0, bounds=bounds, maxfev=2000)

    if np.allclose(params, p0):
        print("Warning: Fit parameters equal to initial guess")
    return params

# functional form of the visibility with aL and aR as parameters, and setting b=2
def visamp_exp_func(u, a, aL, aR, dphi):
    return np.exp(-a * (u ** 2)) * np.sqrt(aL**2 + aR**2 + 2*aL*aR*np.sin(2*np.pi*dphi*u*muas_to_rad*1e9)) / np.sqrt(u)

# logarithm of exponential model functional form fitted to log visibility amplitudes
def log_model(u, a, aL, aR, dphi):
    return -a * (u ** 2) + 0.5 * np.log(aL**2 + aR**2 + 2*aL*aR*np.sin(2*np.pi*dphi*u*muas_to_rad*1e9)) - 0.5 * np.log(u)

## goodness of fit
def g_fit_exp(a, aL, aR, d, x, y):
    deviation= np.sum((visamp_exp_func(x, a, aL, aR, d)-np.abs(y))**2)
    avg_v_fit = np.sum(visamp_exp_func(x, a, aL, aR, d))
    return np.exp(-np.sqrt(deviation/len(x))/(avg_v_fit/len(x)))

def compute_visamp_fit_exp(freqs, visamp, log_fit = False, a_max=20):
    vmax=np.max(visamp)
    umax=freqs[np.argmax(visamp)]
    vmin=np.min(visamp)
    umin=freqs[np.argmin(visamp)]

    # aL_max=(1/2)*(vmax*np.sqrt(umax) * np.exp(a_max * (umax ** b_max)) + vmin*np.sqrt(umin) * np.exp(a_max * (umin ** b_max)))
    aL_max=(1/2)*(vmax*np.sqrt(1e9 * umax)+vmin*np.sqrt(1e9 * umin))    
    aR_max=(1/2)*(vmax*np.sqrt(1e9 * umax)-vmin*np.sqrt(1e9 * umin))
    
    if aR_max < 0:
        aR_max = aL_max

    
    # a0 = np.abs((np.log(vmax) - np.log(vmin)) / (umin ** b0 - umax ** b0) / 50)   # after tests, 10 is a good factor to divide by for the solver to converge
    a0 = 0.0001
    
    # print(aL_max, aR_max, a0)
    bounds = ([0, 0, 0, 35], [a_max, aL_max, aR_max, 45]) 
    p0 = [a0, aL_max/2, aR_max/2, 40]
        
    # finding the best fit d_\varphi with prior that d\in[35, 45]
    if log_fit:
        params, pcov_v = curve_fit(log_model, freqs, np.log(visamp), p0 = p0, bounds=bounds, maxfev=2000)
    else:
        params, pcov_v = curve_fit(visamp_exp_func, freqs, visamp, p0 = p0, bounds=bounds, maxfev=2000)

    if np.allclose(params, p0):
        print("Warning: Fit parameters equal to initial guess")
    return params

## given a visibility profile across specified baseline angles (=radonangles), stores its radial profile in directory 'path'
def radialfit(visamps, freq, radonangles, mu_n, s_n, ulim1_fit, ulim2_fit, gfit_min, path, p0_ratio, method):
    """
    :param visamps: 2d array of visibility amplitdues values for different radonangles
    :param freq: array of baseline frequencies over which each visibility amplitude is recorded. 
    :param radonangles: iterable object containing the projection angles for the radon transformation
    :param mu_n: mean of the gaussian noise added to visamps
    :param s_n: standard deviation of the gaussian noise added to visamps
    :param ulim1_fit: beginning of the baseline window for fits
    :param ulim2_fit: end of the baseline window for fits
    :param gfit_min: minimum goodness of fit for projected diameter in fits
    :param path: path for saving the output
    :param p0_ratio: parameter in (0,1) used in intial guess p0=[aL_max*p0_ratio, aR_max*p0_ratio, 40] for curve_fit 
    """

    mask=np.where((freq>=ulim1_fit) & (freq<=ulim2_fit))[0]
    freqfit=freq[mask]
    datas=[]
    power=np.array([])
    upower=(ulim2_fit+ulim1_fit)/2
    datas=np.array([gaussian_noise(visamps[i], mu_n, s_n) for i in range (len(radonangles))])
    d_vals=[]
    g_vals=[]
    drange = np.arange(8*M_to_muas, 12*M_to_muas, 1/100)
    
    try:
        for i in range(len(radonangles)):
            data=datas[i][mask]

            if method=="GLM":
                aL, aR, dphi = compute_visamp_GLM_fit(freqfit, data, ulim1_fit, ulim2_fit)

                ## corresponding goodness of fit for each d \in drange
                gvals = [g_fit_GLM(aL, aR, d, freqfit, data) for d in drange]
                
            elif method=="Sqrt":
                params = compute_visamp_fit_sqrt(freqfit, data, p0_ratio)
                aL = params[0]
                aR = params[1]
                dphi = params[2]
                
                ## corresponding goodness of fit for each d \in drange
                gvals = [g_fit_1(aL, aR, d, freqfit, data) for d in drange]
                
            # elif method=="Exponential 1":
            #     params, exponent = compute_visamp_fit_2(freqfit, data)
            #     aL = params[0]
            #     aR = params[1]
            #     dphi = params[2]          
                     
            #     ## corresponding goodness of fit for each d \in drange
            #     gvals = [g_fit_2(aL, aR, d, exponent, freqfit, data) for d in drange]
                
            elif method=="Exponential":
                params = compute_visamp_fit_exp(freqfit, data)
                a = params[0]
                aL = params[1]
                aR = params[2]
                dphi = params[3]       
                     
                ## corresponding goodness of fit for each d \in drange
                gvals = [g_fit_exp(a, aL, aR, d, freqfit, data) for d in drange]
                
            elif method=="Log-Exponential":
                params = compute_visamp_fit_exp(freqfit, data, log_fit = True)
                a = params[0]
                aL = params[1]
                aR = params[2]
                dphi = params[3]       
                        
                ## corresponding goodness of fit for each d \in drange
                gvals = [g_fit_exp(a, aL, aR, d, freqfit, data) for d in drange]


            ## keep values of d with g(d) above gfit_min
            d_maxima, g_maxima = filter_maxima(drange, gvals, gfit_min)            
            d_vals.append(np.array(d_maxima))
            g_vals.append(np.array(g_maxima))

        # d_vals=np.array(d_vals)
        # g_vals=np.array(g_vals)
        # print(d_vals)
        # construct circlipses  
        circlipses, g_circlipses = generate_curves(d_vals, g_vals) ## generate various circlipses
        g_circlipses = [np.prod(g) for g in g_circlipses]  ## joint goodness of fit for each circlipse

        best_circlipse = circlipses[np.array(g_circlipses).argmax()]


        params, pcov_v = curve_fit(circlipse, np.array(radonangles)*np.pi/180, best_circlipse,bounds=([0,0,0,-np.pi/2],[50,50,50,np.pi/2]),maxfev=2000)
        
        RMSD_a=np.sqrt(np.average((best_circlipse-circlipse(np.array(radonangles)*np.pi/180,*params))**2))/np.average(circlipse(np.array(radonangles)*np.pi/180,*params))

        RMSD_b=np.sqrt(np.average((best_circlipse-circlipse(np.array(radonangles)*np.pi/180,*params))**2))/np.ptp(circlipse(np.array(radonangles)*np.pi/180,*params))

        
        R_0 = params[0]
        R_1 = params[1]
        R_2 = params[2]
        phi0 = params[3]
        
        # see if fit is good
        ## check 1: enforce d_para > d_perp
        if np.abs(phi0)<70*np.pi/180:
            if best_circlipse[0]>best_circlipse[18]:
                print("failed requirement d_para > d_perp")
                raise ValueError('Fit not possible')
        else:
            if best_circlipse[0]<best_circlipse[18]: 
                print("failed requirement d_para > d_perp")
                raise ValueError('Fit not possible')
                
        ## check 2: preclude jumping between circlipses- max gap between consecutive points is 0.02M
        if np.max(np.abs(np.diff(best_circlipse)))>0.1*M_to_muas: 
            print("failed due to jumping between circlipses")
            raise ValueError('Fit not possible')
        

        d_1=2*(R_0+R_2)/M_to_muas
        d_2=2*(R_0+R_1)/M_to_muas
        d_perp=min(d_1, d_2)  ## d_perp <= d_para
        d_para=max(d_1, d_2)
        # fractional asymmetry
        f_a = 1-d_perp/d_para

        observables=[d_perp, d_para, f_a]


    except Exception as error:
        print("Fit not possible. The following exception occurred:")
        PrintException()
        best_circlipse=[np.nan]
        circlipses=[np.nan]
        g_circlipses=[np.nan]
        d_vals=[np.nan]
        g_vals=[np.nan]
        RMSD_a=np.nan
        RMSD_b=np.nan
        params=[np.nan, np.nan, np.nan, np.nan]
        observables=[np.nan, np.nan, np.nan]
        

    param_dict={
        "mu":best_circlipse,
        "circlipses":circlipses,
        "g_circlipses":g_circlipses,
        "d_vals":d_vals,
        "g_vals":g_vals,
        "rmsda":RMSD_a,
        "rmsdb":RMSD_b,
        "fit":params,
        "observables":observables,
        "power":power
    }
    
        # Create a directory for the results
    isExist = os.path.exists(path)
    if not isExist:
        os.makedirs(path)
        
    np.save(path+"Visamp_fit_%s_%s_gfit_%s_mun_%s_sn_%s.npy"%(ulim1_fit,ulim2_fit, gfit_min, mu_n, s_n), param_dict)
 
def load_visamp_radialfit(mu_n, s_n, ulim1_fit, ulim2_fit, gfit_min, path):
    return np.load(path+"Visamp_fit_%s_%s_gfit_%s_mun_%s_sn_%s.npy"%(ulim1_fit,ulim2_fit, gfit_min, mu_n, s_n), allow_pickle='TRUE').item()
    
def radialfit_visibility(c_vis, freq, radonangles, mu_n, s_n, ulim1_fit, ulim2_fit, gfit_min, path, p0_ratio, method):
    """
    :param c_vis: 2d array of complex visibility values for different radonangles
    :param freq: array of baseline frequencies over which each visibility amplitude is recorded. 
    :param radonangles: iterable object containing the projection angles for the radon transformation
    :param mu_n: mean of the gaussian noise added to complex visibility
    :param s_n: standard deviation of the gaussian noise added to complex visibility
    :param ulim1_fit: beginning of the baseline window for fits
    :param ulim2_fit: end of the baseline window for fits
    :param gfit_min: minimum goodness of fit for projected diameter in fits
    :param path: path for saving the output
    :param p0_ratio: parameter in (0,1) used in intial guess p0=[aL_max*p0_ratio, aR_max*p0_ratio, 40] for curve_fit 
    :param radial_params: circlipse parameters for noiseless fits
    """

    mask=np.where((freq>=ulim1_fit) & (freq<=ulim2_fit))[0]
    freqfit=freq[mask]
    datas=[]
    power=np.array([])
    upower=(ulim2_fit+ulim1_fit)/2
    datas=np.array([np.abs(gaussian_complex_noise(c_vis[i], mu_n, s_n)) for i in range (len(radonangles))])
    d_vals=[]
    g_vals=[]
    drange = np.arange(8*M_to_muas, 12*M_to_muas, 1/100)

    try:
        for i in range(len(radonangles)):
            data=datas[i][mask]

            if method=="GLM":
                aL, aR, dphi = compute_visamp_GLM_fit(freqfit, data, ulim1_fit, ulim2_fit)

                ## corresponding goodness of fit for each d \in drange
                gvals = [g_fit_GLM(aL, aR, d, freqfit, data) for d in drange]
                
            elif method=="Sqrt":
                params = compute_visamp_fit_sqrt(freqfit, data, p0_ratio)
                aL = params[0]
                aR = params[1]
                dphi = params[2]
                
                ## corresponding goodness of fit for each d \in drange
                gvals = [g_fit_1(aL, aR, d, freqfit, data) for d in drange]
                
            # elif method=="Exponential 1":
            #     params, exponent = compute_visamp_fit_2(freqfit, data)
            #     aL = params[0]
            #     aR = params[1]
            #     dphi = params[2]          
                     
            #     ## corresponding goodness of fit for each d \in drange
            #     gvals = [g_fit_2(aL, aR, d, exponent, freqfit, data) for d in drange]
                
            elif method=="Exponential":
                params = compute_visamp_fit_exp(freqfit, data)
                a = params[0]
                aL = params[1]
                aR = params[2]
                dphi = params[3]       
                     
                ## corresponding goodness of fit for each d \in drange
                gvals = [g_fit_exp(a, aL, aR, d, freqfit, data) for d in drange]
                
            elif method=="Log-Exponential":
                params = compute_visamp_fit_exp(freqfit, data, log_fit = True)
                a = params[0]
                aL = params[1]
                aR = params[2]
                dphi = params[3]       
                        
                ## corresponding goodness of fit for each d \in drange
                gvals = [g_fit_exp(a, aL, aR, d, freqfit, data) for d in drange]

            ## keep values of d with g(d) above gfit_min
            d_maxima, g_maxima = filter_maxima(drange, gvals, gfit_min)
            
            d_vals.append(np.array(d_maxima))
            g_vals.append(np.array(g_maxima))

        # d_vals=np.array(d_vals)
        # g_vals=np.array(g_vals)
        
        # construct circlipses  
        circlipses, g_circlipses = generate_curves(d_vals, g_vals) ## generate various circlipses
        g_circlipses = [np.prod(g) for g in g_circlipses]  ## joint goodness of fit for each circlipse

        best_circlipse = circlipses[np.array(g_circlipses).argmax()]


        params, pcov_v = curve_fit(circlipse, np.array(radonangles)*np.pi/180, best_circlipse,bounds=([0,0,0,-np.pi/2],[50,50,50,np.pi/2]),maxfev=2000)
        

        RMSD_a=np.sqrt(np.average((best_circlipse-circlipse(np.array(radonangles)*np.pi/180,*params))**2))/np.average(circlipse(np.array(radonangles)*np.pi/180,*params))
        RMSD_b=np.sqrt(np.average((best_circlipse-circlipse(np.array(radonangles)*np.pi/180,*params))**2))/np.ptp(circlipse(np.array(radonangles)*np.pi/180,*params))

        
        R_0 = params[0]
        R_1 = params[1]
        R_2 = params[2]
        phi0 = params[3]
        
        # see if fit is good
        ## check 1: enforce d_para > d_perp
        if np.abs(phi0)<70*np.pi/180:
            if best_circlipse[0]>best_circlipse[18]:
                print("failed requirement d_para > d_perp")
                raise ValueError('Fit not possible')
        else:
            if best_circlipse[0]<best_circlipse[18]: 
                print("failed requirement d_para > d_perp")
                raise ValueError('Fit not possible')
                
        ## check 2: preclude jumping between circlipses- max gap between consecutive points is 0.02M
        if np.max(np.abs(np.diff(best_circlipse)))>0.1*M_to_muas: 
            print("failed due to jumping between circlipses")
            raise ValueError('Fit not possible')
        

        d_1=2*(R_0+R_2)/M_to_muas
        d_2=2*(R_0+R_1)/M_to_muas
        d_perp=min(d_1, d_2)  ## d_perp <= d_para
        d_para=max(d_1, d_2)
        # fractional asymmetry
        f_a = 1-d_perp/d_para

        observables=[d_perp, d_para, f_a]


    except Exception as error:
        print("Fit not possible. The following exception occurred:")
        PrintException()
        best_circlipse=[np.nan]
        circlipses=[np.nan]
        g_circlipses=[np.nan]
        d_vals=[np.nan]
        g_vals=[np.nan]
        RMSD_a=np.nan
        RMSD_b=np.nan
        params=[np.nan, np.nan, np.nan, np.nan]
        observables=[np.nan, np.nan, np.nan]
        

    param_dict={
        "mu":best_circlipse,
        "circlipses":circlipses,
        "g_circlipses":g_circlipses,
        "d_vals":d_vals,
        "g_vals":g_vals,
        "rmsda":RMSD_a,
        "rmsdb":RMSD_b,
        "fit":params,
        "observables":observables,
        "power":power
    }

        # Create a directory for the results
    isExist = os.path.exists(path)
    if not isExist:
        os.makedirs(path)
    np.save(path+"Visibility_fit_%s_%s_gfit_%s_mun_%s_sn_%s.npy"%(ulim1_fit,ulim2_fit, gfit_min, mu_n, s_n), param_dict)

def load_visibility_radialfit(mu_n, s_n, ulim1_fit, ulim2_fit, gfit_min, path):
    return np.load(path+"Visibility_fit_%s_%s_gfit_%s_mun_%s_sn_%s.npy"%(ulim1_fit,ulim2_fit, gfit_min, mu_n, s_n), allow_pickle='TRUE').item()