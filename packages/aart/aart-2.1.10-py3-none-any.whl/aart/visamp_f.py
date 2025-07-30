from aart import *

#Eq. 32 in 2206.02781
def smooth_connection(x):
    '''Infinitely smooth function, =0 for x<=0'''
    if x<=0:
        return 0
    else:
        return np.exp(-1.0/x**2)

#Eq. 32 in 2206.02781`
def smooth_plateau(x):
    '''Infinitely smooth function, =0 for x<=0, =1 for x>=1'''
    return smooth_connection(x)/(smooth_connection(x)+smooth_connection(1-x)) 

def imagetreat(image,radonangle,limsn,lims0, limits, psi, dBH):
    
    Gc=6.67e-11 # G constant [m^3 kg^-1 s^-2]
    cc= 2.99792458e8 # c constant [m/s]
    Msc=1.988435e30 # Solar Mass [Kg]

    MMkg= 6.2e9*psi*Msc # [Kg]
    MM=MMkg *Gc/cc**2 # Mass of the BH in meters, i.e., for M87(psi*6.2*10^9) psi ("Best fit") Solar Masses 

    # Size of the real image in meters
    sizeim_Real=(limits)*MM 
    #1 microarcsec in radians
    muas_to_rad = np.pi/648000 *1e-6 
    
    fov_Real=np.arctan(sizeim_Real/(dBH))/muas_to_rad #muas
    
    # Computes the radon cut of an image and scales it
    NN = image.shape[0]
    fov=fov_Real*(limsn/lims0)
    fov_rad=fov*1e-6*1./3600.*np.pi/180.
    dfovreal=fov_rad/NN
    radon_scaled = radon(image, theta=[radonangle]).flatten()    
    xaxis=np.linspace(-limsn,limsn,num=NN)
    return dfovreal*radon_scaled, xaxis

def radon_cut(I0,I1,I2,supergrid0,supergrid1,supergrid2, spin_case, i_case, mask, **params):
    
    radonangles=params.get('radonangles')
    path=params.get('path')
    radonfile=params.get('radonfile')
    dx0=params.get('dx0')
    dx1=params.get('dx1')
    dx2=params.get('dx2')
    limits=params.get('limits')
    psi=params.get('psi')
    dBH=params.get('dBH')
    maxbaseline=params.get('maxbaseline')
    Ncut=params.get('Ncut')    
    gfactor=params.get('gfactor')
    bvapp=params.get('bvapp')
    fudge=params.get('fudge')[mask]
    betaphi=params.get('betaphi')[mask]
    betar=params.get('betar')[mask]
    gammap=params.get('gammap')[mask]
    sigmap=params.get('sigmap')[mask]
    mup=params.get('mup')[mask]
    sub_kep=params.get('sub_kep')[mask]
    
    Gc=6.67e-11 # G constant [m^3 kg^-1 s^-2]
    cc= 2.99792458e8 # c constant [m/s]
    Msc=1.988435e30 # Solar Mass [Kg]

    MMkg= 6.2e9*psi*Msc # [Kg]
    MM=MMkg *Gc/cc**2 # Mass of the BH in meters, i.e., for M87(psi*6.2*10^9) psi ("Best fit") Solar Masses 

    # Size of the real image in meters
    sizeim_Real=(limits)*MM 
    #1 microarcsec in radians
    muas_to_rad = np.pi/648000 *1e-6 
    
    fov_Real=np.arctan(sizeim_Real/(dBH))/muas_to_rad #muas

    for i in range(len(radonangles)):

        radonangle = radonangles[i]
        radon0=imagetreat(I0,radonangle,supergrid0[-1,0],supergrid0[-1,0], limits, psi, dBH)
        radon1=imagetreat(I1,radonangle,supergrid1[-1,0],supergrid0[-1,0], limits, psi, dBH)
        radon2=imagetreat(I2,radonangle,supergrid2[-1,0],supergrid0[-1,0], limits, psi, dBH)

        R0 = interpolate.interp1d(radon0[1],radon0[0],fill_value=0, bounds_error=False,kind="linear")
        R1 = interpolate.interp1d(radon1[1],radon1[0],fill_value=0, bounds_error=False,kind="linear")
        R2 = interpolate.interp1d(radon2[1],radon2[0],fill_value=0, bounds_error=False,kind="linear")

        dx=np.min([dx0,dx1,dx2])
        xvalues =np.round(np.arange(-limits,limits+dx, dx),4)

        R=R0(xvalues)+R1(xvalues)+R2(xvalues)
        
        
        xaxis1=np.linspace(-fov_Real,fov_Real,num=xvalues.shape[0]) # in muas
        deltax1=xaxis1[1]-xaxis1[0]
        
        # apply window function to get rid of spurious oscillations from discontinuities in the FFT         
        alpha = 0.5  # alpha=0 means rectangular window, alpha=1 means Hann window
        window = tukey(len(R), alpha)

        R*=window

        # Compute 1D FFT of the projection, shift and take modulus
        padding=16
        radonff = fft(R,padding*xvalues.shape[0]) #1D FFT of the projection
        radonshift=fftshift(radonff) # recenter FFT
        radonvisamp=np.abs(radonshift) # this is the visamp

        xfourier1=fftshift(fftfreq(padding*xvalues.shape[0],d=deltax1)) #re centered frequencies in muas^-1
        xfourier1/= 1e-6 * 1./3600. * np.pi/180. # in rad^-1
        xfourier1 /= 1e9 # in Glambda

        indice1=np.where((xfourier1>=0.) & (xfourier1<maxbaseline))[0] # select only the positive freqs the FFT is symmetrical anyway
        visamp=radonvisamp[indice1[0]:(indice1[-1]+1)] # select FFT for these positive freqs
    
        
        # Create a directory for the results
        isExist = os.path.exists(path)
        if not isExist:
            os.makedirs(path)
            print("A directory (Results) was created to store the results")
        
        filename=path+"Visamp_%s_a_%s_i_%s_dx0_%s_dx1_%s_dx2_%s_sk_%s_bphi_%s_br_%s_bvapp_%s_gfact_%s_mup_%s_gp_%s_sp_%s_fudge_%s_Ncut_%s.h5"%(radonangle,spin_case,i_case, dx0, dx1, dx2, sub_kep, betaphi, betar,  bvapp, gfactor, np.round(mup, 3), gammap, sigmap, fudge, int(Ncut))
        
        h5f = h5py.File(filename, 'w')

        h5f.create_dataset('visamp', data=visamp)

        if radonfile==1:
            h5f.create_dataset('radon', data=R)

        if Ncut==0:
            h5f.create_dataset('freqs', data=xfourier1[indice1])
            if radonfile==1:
                h5f.create_dataset('x_radon', data=xvalues)

        h5f.close()

        print("File ",filename," created.")


def radon_cut_visibility(I0,I1,I2,supergrid0,supergrid1,supergrid2, spin_case, i_case, mask, **params):
    
    radonangles=params.get('radonangles')
    path=params.get('path')
    radonfile=params.get('radonfile')
    dx0=params.get('dx0')
    dx1=params.get('dx1')
    dx2=params.get('dx2')
    limits=params.get('limits')
    psi=params.get('psi')
    dBH=params.get('dBH')
    maxbaseline=params.get('maxbaseline')
    Ncut=params.get('Ncut')    
    gfactor=params.get('gfactor')
    bvapp=params.get('bvapp')
    fudge=params.get('fudge')[mask]
    betaphi=params.get('betaphi')[mask]
    betar=params.get('betar')[mask]
    gammap=params.get('gammap')[mask]
    sigmap=params.get('sigmap')[mask]
    mup=params.get('mup')[mask]
    sub_kep=params.get('sub_kep')[mask]
    
    Gc=6.67e-11 # G constant [m^3 kg^-1 s^-2]
    cc= 2.99792458e8 # c constant [m/s]
    Msc=1.988435e30 # Solar Mass [Kg]

    MMkg= 6.2e9*psi*Msc # [Kg]
    MM=MMkg *Gc/cc**2 # Mass of the BH in meters, i.e., for M87(psi*6.2*10^9) psi ("Best fit") Solar Masses 

    # Size of the real image in meters
    sizeim_Real=(limits)*MM 
    #1 microarcsec in radians
    muas_to_rad = np.pi/648000 *1e-6 
    
    fov_Real=np.arctan(sizeim_Real/(dBH))/muas_to_rad #muas

    for i in range(len(radonangles)):

        radonangle = radonangles[i]
        radon0=imagetreat(I0,radonangle,supergrid0[-1,0],supergrid0[-1,0], limits, psi, dBH)
        radon1=imagetreat(I1,radonangle,supergrid1[-1,0],supergrid0[-1,0], limits, psi, dBH)
        radon2=imagetreat(I2,radonangle,supergrid2[-1,0],supergrid0[-1,0], limits, psi, dBH)

        R0 = interpolate.interp1d(radon0[1],radon0[0],fill_value=0, bounds_error=False,kind="linear")
        R1 = interpolate.interp1d(radon1[1],radon1[0],fill_value=0, bounds_error=False,kind="linear")
        R2 = interpolate.interp1d(radon2[1],radon2[0],fill_value=0, bounds_error=False,kind="linear")

        dx=np.min([dx0,dx1,dx2])
        xvalues =np.round(np.arange(-limits,limits+dx, dx),4)

        R=R0(xvalues)+R1(xvalues)+R2(xvalues)
        
        
        xaxis1=np.linspace(-fov_Real,fov_Real,num=xvalues.shape[0]) # in muas
        deltax1=xaxis1[1]-xaxis1[0]

        # apply window function to get rid of spurious oscillations from discontinuities in the FFT         
        alpha = 0.5  # alpha=0 means rectangular window, alpha=1 means Hann window
        window = tukey(len(R), alpha)

        R*=window

        # Compute 1D FFT of the projection, shift and take modulus
        padding=16
        radonff = fft(R,padding*xvalues.shape[0]) #1D FFT of the projection
        radonshift=fftshift(radonff) # recenter FFT
        radonvisibility=radonshift # this is the complex visibility

        xfourier1=fftshift(fftfreq(padding*xvalues.shape[0],d=deltax1)) #re centered frequencies in muas^-1
        xfourier1/= 1e-6 * 1./3600. * np.pi/180. # in rad^-1
        xfourier1 /= 1e9 # in Glambda

        indice1=np.where((xfourier1>=0.) & (xfourier1<maxbaseline))[0] # select only the positive freqs the FFT is symmetrical anyway
        visibility=radonvisibility[indice1[0]:(indice1[-1]+1)] # select FFT for these positive freqs
    
        
        # Create a directory for the results
        isExist = os.path.exists(path)
        if not isExist:
            os.makedirs(path)
            print("A directory (Results) was created to store the results")
        
        filename=path+"Visibility_%s_a_%s_i_%s_dx0_%s_dx1_%s_dx2_%s_sk_%s_bphi_%s_br_%s_bvapp_%s_gfact_%s_mup_%s_gp_%s_sp_%s_fudge_%s_Ncut_%s.h5"%(radonangle,spin_case,i_case, dx0, dx1, dx2, sub_kep, betaphi, betar,  bvapp, gfactor, np.round(mup, 3), gammap, sigmap, fudge, int(Ncut))
        
        h5f = h5py.File(filename, 'w')

        h5f.create_dataset('visibility', data=visibility)

        if radonfile==1:
            h5f.create_dataset('radon', data=R)

        if Ncut==0:
            h5f.create_dataset('freqs', data=xfourier1[indice1])
            if radonfile==1:
                h5f.create_dataset('x_radon', data=xvalues)

        h5f.close()

        print("File ",filename," created.")