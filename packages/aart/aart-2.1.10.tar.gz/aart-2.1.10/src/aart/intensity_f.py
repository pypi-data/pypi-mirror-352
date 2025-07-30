from aart import *

def Delta(r,a):
    """
    Calculates the Kerr metric function \Delta(t)
    :param r: radius of the source
    :param a: spin of the black hole
    """
    return r**2-2*r+a**2

def PIF(r,a):
    """
    Calculates PI(r) (Eq. B6 P1)
    :param r: radius of the source
    :param a: spin of the black hole
    """
    return (r**2+a**2)**2-a**2*Delta(r,a)

def urbar(r,a):
    """
    Calculates the r (contravariant) component of the four velocity for radial infall
    (Eq. B34b P1)
    :param r: radius of the source
    :param a: spin of the black hole
    """
    return -np.sqrt(2*r*(r**2+a**2))/(r**2)

def Omegabar(r,a):
    """
    Calculates the angular velocity of the radial infall
    (Eq. B32a P1)
    :param r: radius of the source
    :param a: spin of the black hole
    """
    return (2*a*r)/PIF(r,a)

def Omegahat(r,a,laux):
    """
    Calculates the angular velocity of the sub-Keplerian orbit
    (Eq. B39 P1)
    :param r: radius of the source
    :param a: spin of the black hole
    """
    return (a+(1-2/r)*(laux-a))/(PIF(r,a)/(r**2)-(2*a*laux)/r)

def uttilde(r, a,urT,OT):
    """
    Calculates the t (contravariant) component of the general four velocity
    (Eq. B52 P1)
    :param r: radius of the source
    :param a: spin of the black hole
    :param urT: r (contravariant) component of the general four velocity
    :param OT: Angular velocity of the general four velocity
    """
    return np.sqrt((1 + urT**2*r**2/Delta(r,a))/(1-(r**2+a**2)*OT**2-(2/r)*(1-a*OT)**2))

def Ehat(r,a,laux):
    """
    Calculates the orbital energy of the sub-Keplerian flow
    (Eq. B44a P1)
    :param r: radius of the source
    :param a: spin of the black hole
    :param laux: sub-Keplerian specific angular momentum
    """
    return np.sqrt(Delta(r,a)/(PIF(r,a)/(r**2)-(4*a*laux)/r-(1-2/r)*laux**2))

def nuhat(r,a,laux,Ehataux):
    """
    Calculates the radial velocity of the sub-Keplerian flow
    (Eq. B45 P1)
    :param r: radius of the source
    :param a: spin of the black hole
    :param laux: sub-Keplerian specific angular momentum
    :param Ehataux: sub-Keplerian orbital energy
    """
    return r/Delta(r,a)*np.sqrt(np.abs(PIF(r,a)/(r**2)-(4*a*laux)/r-(1-2/r)*laux**2-Delta(r,a)/(Ehataux**2)))

def lhat(r,a, sub_kep):
    """
    Calculates the rspecific angular momentum of the sub-Keplerian flow
    (Eq. B44b P1)
    :param r: radius of the source
    :param a: spin of the black hole
    """
    return sub_kep*(r**2+a**2-2*a*np.sqrt(r))/(np.sqrt(r)*(r-2)+a)

def Rint(r,a,lamb,eta):
    """
    Evaluates the "radial potential", for calculating the redshift factor for infalling material
    :param r: radius of the source
    :param a: spin of the black hole
    :param lamb: angular momentum
    :param eta: carter constant

    :return: radial potential evaluated at the source
    """
    #Eqns (P2 5)
    return (r**2 + a**2 - a*lamb)**2 - (r**2 - 2*r + a**2)*(eta + (lamb - a)**2)

def gDisk(r,a,b,lamb,eta, betaphi, betar, sub_kep):
    """
    Calculates the redshift factor for a photon outside the inner-most stable circular orbit(isco) (assume circular orbit)
    (Eq. B13 P1)
    :param r: radius of the source
    :param a: spin of the black hole
    :param lamb: angular momentum
    :param eta: Carter constant

    :return: the redshift factor associated with the ray
    """

    OH=Omegahat(r,a,lhat(r,a,sub_kep))
    OT=OH+(1-betaphi)*(Omegabar(r,a)-OH)
    ur=(1-betar)*urbar(r,a)
    ut=uttilde(r,a,ur,OT)
    uphi=ut*OT
    
    return 1/(ut*(1-b*np.sign(ur)*sqrt(np.abs(Rint(r,a,lamb,eta)*ur**2))/Delta(r,a)/ut-lamb*uphi/ut))

def gGas(r,a,b,lamb,eta, betaphi, betar, sub_kep):
    """
    Calculates the redshift factor for a photon inside the isco (assume infalling orbit)
    (Eq. B13 P1)
    :param r: radius of the source
    :param a: spin of the black hole
    :param b: sign for the redshift
    :param lamb: angular momentum
    :param eta: carter constant

    :return: the redshift factor associated with the ray
    """
    #Calculate radius of the inner-most stable circular orbit
    isco=rms(a)

    lms=lhat(isco,a, sub_kep)
    OH=Omegahat(r,a,lms)
    OT=OH+(1-betaphi)*(Omegabar(r,a)-OH)

    Ems=Ehat(isco,a,lms)
    urhat=-Delta(r,a)/(r**2)*nuhat(r, a, lms ,Ems)*Ems
    ur=urhat+(1-betar)*(urbar(r,a)-urhat)
    ut=uttilde(r,a,ur,OT)
    uphi=OT*ut

    return 1/(ut*(1-b*np.sign(ur)*sqrt(np.abs(Rint(r,a,lamb,eta)*ur**2))/Delta(r,a)/ut-lamb*uphi/ut))

#calculate the observed brightness for a purely radial profile
def bright_radial(grid,mask,redshift_sign,a,rs,isco,thetao, betaphi, betar, gfactor, gammap, mup, sigmap, sub_kep):
    """
    Calculate the brightness of a rotationally symmetric disk
    (Eq. 50 P1)
    :param grid: alpha and beta grid on the observer plane on which we evaluate the observables
    :param mask: mask out the lensing band, see lb_f.py for detail
    :param redshift_sign: sign of the redshift
    :param a: black hole spin
    :param rs: source radius
    :param isco: radius of the inner-most stable circular orbit
    :param thetao: observer inclination

    :return: image of a lensed equitorial source with only radial dependence. 
    """
    alpha = grid[:,0][mask]
    beta = grid[:,1][mask]

    rs = rs[mask]

    lamb,eta = rt.conserved_quantities(alpha,beta,thetao,a)

    brightness = np.zeros(rs.shape[0])
    redshift_sign = redshift_sign[mask]

    brightness[rs>=isco]= gDisk(rs[rs>=isco],a,redshift_sign[rs>=isco],lamb[rs>=isco],eta[rs>=isco], betaphi, betar, sub_kep)**gfactor*ilp.profile(rs[rs>=isco],a,gammap,mup,sigmap)
    brightness[rs<isco]= gGas(rs[rs<isco],a,redshift_sign[rs<isco],lamb[rs<isco],eta[rs<isco], betaphi, betar, sub_kep)**gfactor*ilp.profile(rs[rs<isco],a,gammap,mup,sigmap)
    
    r_p = 1+np.sqrt(1-a**2)
    brightness[rs<=r_p] = 0
    
    I = np.zeros(mask.shape)
    I[mask] = brightness
    
    return(I)


#calculate the observed brightness for an arbitrary profile, passed in as the interpolation object
#but ignoring the time delay due to lensing
def fast_light(grid,mask,redshift_sign,a,isco,rs,th,interpolation,thetao, betaphi, betar, gfactor, sub_kep):
    """
    Calculate the black hole image ignoring the time delay due to lensing or geometric effect
    (Eq. 116 P1)
    :param grid: alpha and beta grid on the observer plane on which we evaluate the observables
    :param mask: mask out the lensing band, see lb_f.py for detail
    :param redshift_sign: sign of the redshift
    :param a: black hole spin
    :param isco: radius of the inner-most stable circular orbit
    :param rs: source radius
    :param th: source angle, polar coordinate
    :param interpolation: 2 dimensional brightness function of the source, interpolation object
    :param thetao: observer inclination

    :return: image of a lensed equitorial source with only radial dependence. 
    """
    alpha = grid[:,0][mask]
    beta = grid[:,1][mask]
    rs = rs[mask]
    th = th[mask]
    lamb,eta = rt.conserved_quantities(alpha,beta,thetao,a)
    brightness = np.zeros(rs.shape[0])
    redshift_sign = redshift_sign[mask]

    x_aux=rs*np.cos(th)
    y_aux=rs*np.sin(th)
 
    brightness[rs>=isco]= gDisk(rs[rs>=isco],a,redshift_sign[rs>=isco],lamb[rs>=isco],eta[rs>=isco], betaphi, betar,sub_kep)**gfactor*interpolation(np.vstack([x_aux[rs>=isco],y_aux[rs>=isco]]).T)
    brightness[rs<isco]= gGas(rs[rs<isco],a,redshift_sign[rs<isco],lamb[rs<isco],eta[rs<isco], betaphi, betar, sub_kep)**gfactor*interpolation(np.vstack([x_aux[rs<isco],y_aux[rs<isco]]).T)
    
    r_p = 1+np.sqrt(1-a**2)
    brightness[rs<=r_p] = 0
    
    I = np.zeros(mask.shape)
    I[mask] = brightness
    return(I)

#calculate the observed brightness for an arbitrary, evolving profile, passed in as the interpolation object
def slow_light(grid,mask,redshift_sign,a,isco,rs,th,ts,interpolation,thetao, betaphi, betar, gfactor, sub_kep):
    """
    Calculate the black hole image including the time delay due to lensing and geometric effect
    (Eq. 50 P1)

    :param grid: alpha and beta grid on the observer plane on which we evaluate the observables
    :param mask: mask out the lensing band, see lb_f.py for detail
    :param redshift_sign: sign of the redshift
    :param a: black hole spin
    :param isco: radius of the inner-most stable circular orbit
    :param rs: source radius
    :param th: source angle, polar coordinate
    :param ts: time of emission at the source
    :param interpolation: a time series of 2 dimensional brightness function of the source, 3d interpolation object
    :param thetao: observer inclination

    :return: image of a lensed equitorial source with only radial dependence. 
    """
    alpha = grid[:,0][mask]
    beta = grid[:,1][mask]
    rs = rs[mask]
    th = th[mask]
    ts = ts[mask]
    lamb,eta = rt.conserved_quantities(alpha,beta,thetao,a)
    brightness = np.zeros(rs.shape[0])
    redshift_sign = redshift_sign[mask]
    
    x_aux=rs*np.cos(th)
    y_aux=rs*np.sin(th)

    brightness[rs>=isco]= gDisk(rs[rs>=isco],a,redshift_sign[rs>=isco],lamb[rs>=isco],eta[rs>=isco], betaphi, betar, sub_kep)**gfactor*interpolation(np.vstack([ts[rs>=isco],x_aux[rs>=isco],y_aux[rs>=isco]]).T)
    brightness[rs<isco]= gGas(rs[rs<isco],a,redshift_sign[rs<isco],lamb[rs<isco],eta[rs<isco], betaphi, betar, sub_kep)**gfactor*interpolation(np.vstack([ts[rs<isco],x_aux[rs<isco],y_aux[rs<isco]]).T)

    r_p = 1+np.sqrt(1-a**2)
    brightness[rs<=r_p] = 0
    
    I = np.zeros(mask.shape)
    I[mask] = brightness
    return(I)

def br(supergrid0,mask0,N0,rs0,sign0,supergrid1,mask1,N1,rs1,sign1,supergrid2,mask2,N2,rs2,sign2, spin_case, i_case, isco, thetao, mask3, **params):
    """
    Calculate and save the radial brightness profile
    """
    bvapp=params.get('bvapp')
    betaphi=params.get('betaphi')[mask3]
    betar=params.get('betar')[mask3]
    gfactor=params.get('gfactor')
    gammap=params.get('gammap')[mask3]
    sigmap=params.get('sigmap')[mask3]
    path=params.get('path')
    mup=params['mup'][mask3]
    sub_kep=params.get('sub_kep')[mask3]
    fudge=params.get('fudge')[mask3]
    
    bghts0 = bright_radial(supergrid0,mask0,sign0,spin_case,rs0,isco,thetao, betaphi, betar, gfactor, gammap, mup, sigmap, sub_kep)
    bghts1 = bright_radial(supergrid1,mask1,sign1,spin_case,rs1,isco,thetao, betaphi, betar, gfactor, gammap, mup, sigmap, sub_kep)
    bghts2 = bright_radial(supergrid2,mask2,sign2,spin_case,rs2,isco,thetao, betaphi, betar, gfactor, gammap, mup, sigmap, sub_kep)

    I0 = bghts0.reshape(N0,N0).T
    I1 = fudge*bghts1.reshape(N1,N1).T
    I2 = fudge*bghts2.reshape(N2,N2).T
    
    # Create a directory for the results
    isExist = os.path.exists(path)
    if not isExist:
        os.makedirs(path)
        print("A directory (Results) was created to store the results")

    filename=path+"Intensity_a_%s_i_%s_sk_%s_bphi_%s_br_%s_bvapp_%s_gfact_%s_mp_%s_gp_%s_sp_%s.h5"%(spin_case,i_case, sub_kep, betaphi, betar,  bvapp, gfactor, np.round(mup, 3), gammap, sigmap)
    h5f = h5py.File(filename, 'w')

    h5f.create_dataset('bghts0', data=I0)
    h5f.create_dataset('bghts1', data=I1)
    h5f.create_dataset('bghts2', data=I2)

    h5f.close()

    print("File ",filename," created.")

def br_bv(supergrid0,mask0,N0,rs0,sign0, spin_case, i_case, isco, thetao, mask3, **params):
    """
    Calculate and save the radial brightness profile
    """
    bvapp=params.get('bvapp')
    sub_kep=params.get('sub_kep')[mask3]
    betaphi=params.get('betaphi')[mask3]
    betar=params.get('betar')[mask3]
    gfactor=params.get('gfactor')
    gammap=params.get('gammap')[mask3]
    sigmap=params.get('sigmap')[mask3]
    path=params.get('path')
    mup=params['mup'][mask3]
                      
    bghts0 = bright_radial(supergrid0,mask0,sign0,spin_case,rs0,isco,thetao, betaphi, betar, gfactor, gammap, mup, sigmap, sub_kep)

    I0 = bghts0.reshape(N0,N0).T
    
    # Create a directory for the results
    isExist = os.path.exists(path)
    if not isExist:
        os.makedirs(path)
        print("A directory (Results) was created to store the results")

    filename=path+"Intensity_a_%s_i_%s_sk_%s_bphi_%s_br_%s_bvapp_%s_gfact_%s_mp_%s_gp_%s_sp_%s.h5"%(spin_case,i_case, sub_kep, betaphi, betar,  bvapp, gfactor, np.round(mup, 3), gammap, sigmap)
    h5f = h5py.File(filename, 'w')

    h5f.create_dataset('bghts0', data=I0)

    h5f.close()

    print("File ",filename," created.")

def gfactorf(grid,mask,redshift_sign,a,isco,rs,th,thetao, betaphi, betar, sub_kep):
    """
    Calculate the redshift factor
    :param grid: alpha and beta grid on the observer plane on which we evaluate the observables
    :param mask: mask out the lensing band, see lb_f.py for detail
    :param redshift_sign: sign of the redshift
    :param a: black hole spin
    :param isco: radius of the inner-most stable circular orbit
    :param rs: source radius
    :param th: source angle, polar coordinate
    :param thetao: observer inclination

    :return: redshift factor at each point.

    """
    
    alpha = grid[:,0][mask]
    beta = grid[:,1][mask]
    rs = rs[mask]
    th = th[mask]
    lamb,eta = rt.conserved_quantities(alpha,beta,thetao,a)
    gfact = np.zeros(rs.shape[0])
    redshift_sign = redshift_sign[mask]
    
    x_aux=rs*np.cos(th)
    y_aux=rs*np.sin(th)

    gfact[rs>=isco]= gDisk(rs[rs>=isco],a,redshift_sign[rs>=isco],lamb[rs>=isco],eta[rs>=isco], betaphi, betar, sub_kep)
    gfact[rs<isco]= gGas(rs[rs<isco],a,redshift_sign[rs<isco],lamb[rs<isco],eta[rs<isco], betaphi, betar, sub_kep)
    
    r_p = 1+np.sqrt(1-a**2)
    gfact[rs<=r_p] = 0
    
    gs = np.zeros(mask.shape)
    gs[mask] = gfact
    return(gs)