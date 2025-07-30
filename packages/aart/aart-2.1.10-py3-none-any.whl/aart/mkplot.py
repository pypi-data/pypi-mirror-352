#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from aart import *

def lb(mask1, mask2, fig_size=[5,5], res=400, save_path='./Results/', **params):  
    
    """
    Plots the boundaries of the lensing bands and the grid points of the n=1 lensing band, and saves the it. Requires the 'clb' function in the 'lensingbands' module to have already been called for the correspondsing spin and inclination angle.
    :param mask1: identifies the appropriate profile according to the indexing of the 'spins' array in params 
    :param mask2: identifies the appropriate profile according to the indexing of the 'i_angles' array in params
    :param fig_size: dimensions of figure
    :param res: dots per inch of figure
    :param save_path: path for saving the plot
    """
    spin_case=params.get('spins')[mask1]
    i_case=params.get('i_angles')[mask2]
    load_path=params.get('path')
    dx0=params.get('dx0')
    dx1=params.get('dx1')
    dx2=params.get('dx2')
    
    fnbands=load_path+"LensingBands_a_%s_i_%s_dx0_%s_dx1_%s_dx2_%s.h5"%(spin_case,i_case, dx0, dx1, dx2)

    h5f = h5py.File(fnbands,'r')

    #Points for the boundary of the BH shadow
    alpha_critc=h5f['alpha'][:]
    beta_critc=h5f['beta'][:]

    #The concave hulls for the lensing bands
    hull_0i=h5f['hull_0i'][:]
    hull_0e=h5f['hull_0e'][:]
    hull_1i=h5f['hull_1i'][:]
    hull_1e=h5f['hull_1e'][:]
    hull_2i=h5f['hull_2i'][:]
    hull_2e=h5f['hull_2e'][:]

    #The grid points for each lensing band
    supergrid0=h5f['grid0'][:]
    N0=int(h5f["N0"][0])
    mask0=h5f['mask0'][:]
    lim0=int(h5f["lim0"][0])
    supergrid1=h5f['grid1'][:]
    N1=int(h5f["N1"][0])
    mask1=h5f['mask1'][:]
    lim1=int(h5f["lim1"][0])
    supergrid2=h5f['grid2'][:]
    N2=int(h5f["N2"][0])
    mask2=h5f['mask2'][:]
    lim2=int(h5f["lim2"][0])

    h5f.close()
    
    fig, ax = plt.subplots(figsize=fig_size,dpi=res)

    ax.axvline(0,color="k",linewidth=0.2)
    ax.axhline(0,color="k",linewidth=0.2)

    ax.plot(alpha_critc,beta_critc,color="k",linewidth=0.3,linestyle="--")
    ax.plot(alpha_critc,-beta_critc,color="k",linewidth=0.3,linestyle="--")

    ax.fill(hull_0i[:,0],hull_0i[:,1],color="k")
    ax.plot(hull_1i[:,0],hull_1i[:,1],'r',linewidth=0.2)
    ax.plot(hull_1e[:,0],hull_1e[:,1],'r',linewidth=0.2)
    ax.plot(hull_2i[:,0],hull_2i[:,1],'b',linewidth=0.2)
    ax.plot(hull_2e[:,0],hull_2e[:,1],'b',linewidth=0.2)

    #Plotting the grid points of the n=1 lensing band
    ax.scatter(supergrid1[:,0][mask1],supergrid1[:,1][mask1],color="r",marker=".",s=.00001,alpha=0.5)

    ax.set_xlim(-12,12)
    ax.set_ylim(-12,12)

    ax.set_xlabel(r"$\alpha$"+" "+"(M)")
    ax.set_ylabel(r"$\beta$"+" "+"(M)")
    
    # Create a directory for the results
    isExist = os.path.exists(save_path)
    if not isExist:
        os.makedirs(save_path)

    plt.savefig(save_path+'LB_a_%s_i_%s_dx0_%s_dx1_%s_dx2_%s.png'%(spin_case,i_case, dx0, dx1, dx2),dpi=res,bbox_inches='tight')

    plt.show()
    
def directimage(mask1, mask2, contours=[3,6,9,12,15,20], fig_size=[5,5], res=400, save_path='./Results/', **params):
    
    """
    Plots the coordinates of the direct image of the n=0 band on the observers' screen and saves the figure. The contours of the polar coordinate are plotted at 45 degree intervals in the background, and contours of constant Boyer-Lindquist radius are also plotted. Requires 'raytracing' and 'clb' from the 'raytracing' and 'lensingbands' modules, respectively, to have been called for the corresponding spin and inclination angle.
    :param mask1: identifies the appropriate profile according to the indexing of the 'spins' array in params 
    :param mask2: identifies the appropriate profile according to the indexing of the 'i_angles' array in params
    :param contours: iterable object containing constant Boyer-Lindquist radii to be plotted as contours
    :param fig_size: dimensions of figure
    :param res: dots per inch of figure
    :param save_path: path for saving the plot
    """
    spin_case=params.get('spins')[mask1]
    i_case=params.get('i_angles')[mask2]
    load_path=params.get('path')
    dx0=params.get('dx0')
    dx1=params.get('dx1')
    dx2=params.get('dx2')
    bvapp=params.get('bvapp')
    
    fnbands=load_path+"LensingBands_a_%s_i_%s_dx0_%s_dx1_%s_dx2_%s.h5"%(spin_case,i_case, dx0, dx1, dx2)

    h5f = h5py.File(fnbands,'r')

    #Points for the boundary of the BH shadow
    alpha_critc=h5f['alpha'][:]
    beta_critc=h5f['beta'][:]

    #The concave hulls for the lensing bands
    hull_0i=h5f['hull_0i'][:]
    hull_0e=h5f['hull_0e'][:]
    hull_1i=h5f['hull_1i'][:]
    hull_1e=h5f['hull_1e'][:]
    hull_2i=h5f['hull_2i'][:]
    hull_2e=h5f['hull_2e'][:]

    #The grid points for each lensing band
    supergrid0=h5f['grid0'][:]
    N0=int(h5f["N0"][0])
    mask0=h5f['mask0'][:]
    lim0=int(h5f["lim0"][0])
    supergrid1=h5f['grid1'][:]
    N1=int(h5f["N1"][0])
    mask1=h5f['mask1'][:]
    lim1=int(h5f["lim1"][0])
    supergrid2=h5f['grid2'][:]
    N2=int(h5f["N2"][0])
    mask2=h5f['mask2'][:]
    lim2=int(h5f["lim2"][0])

    h5f.close()
    
    fnrays=load_path+"Rays_a_%s_i_%s_bv_%s_dx0_%s_dx1_%s_dx2_%s.h5"%(spin_case,i_case, bvapp, dx0, dx1, dx2)

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

    fig, ax = plt.subplots(figsize=fig_size,dpi=res)

    ax.fill(hull_0i[:,0],hull_0i[:,1],color="k",linewidth=1,zorder=0)

    CSphi=ax.contourf(phi0.reshape(N0,N0).T%(2*np.pi),cmap="Greys",levels=np.linspace(0,2*np.pi,9),extent=[-lim0,lim0,-lim0,lim0],origin="lower")
    CSr=ax.contour(rs0.reshape(N0,N0).T,levels=contours,extent=[-lim0,lim0,-lim0,lim0],origin="lower",linewidths=0.5,colors='k')

    ax.set_xlim(-lim0,lim0)
    ax.set_ylim(-lim0,lim0)

    ax.set_xlabel(r"$\alpha$"+" "+"(M)")
    ax.set_ylabel(r"$\beta$"+" "+"(M)")
    
    isExist = os.path.exists(save_path)
    if not isExist:
        os.makedirs(save_path)
    
    plt.savefig(save_path+'Rays_a_%s_i_%s_bv_%s.png'%(spin_case,i_case, bvapp),dpi=res,bbox_inches='tight')
    
    plt.show()
    
def bhimage(mask1, mask2, fig_size=[5,5], res=400, save_path='./Results/', **params):
    
    """
    Produces and saves an image of the BH by plotting its radial intensity. Requires 'cintensity', 'raytracing' and 'clb' from the 'radialintensity', 'raytracing' and 'lensingbands' modules, respectively, to have been called for the corresponding spin and inclination angle.
    :param mask1: identifies the appropriate profile according to the indexing of the 'spins' array in params 
    :param mask2: identifies the appropriate profile according to the indexing of the 'i_angles' array in params
    :param fig_size: dimensions of figure
    :param res: dots per inch of figure
    :param save_path: path for saving the plot  
    """
    spin_case=params.get('spins')[mask1]
    i_case=params.get('i_angles')[mask2]
    load_path=params.get('path')
    dx0=params.get('dx0')
    dx1=params.get('dx1')
    dx2=params.get('dx2')
    bvapp=params.get('bvapp')
    betaphi=params.get('betaphi')[mask1]
    betar=params.get('betar')[mask1]
    gfactor=params.get('gfactor')
    gammap=params.get('gammap')[mask1]
    sigmap=params.get('sigmap')[mask1]
    path=params.get('path')
    mup=params.get('mup')[mask1]
    sub_kep=params.get('sub_kep')[mask1]
    
    fnbands=load_path+"LensingBands_a_%s_i_%s_dx0_%s_dx1_%s_dx2_%s.h5"%(spin_case,i_case, dx0, dx1, dx2)
    h5f = h5py.File(fnbands,'r')
    lim0=int(h5f["lim0"][0])
    h5f.close()
    
    fint=load_path+"Intensity_a_%s_i_%s_sk_%s_bphi_%s_br_%s_bvapp_%s_gfact_%s_mp_%s_gp_%s_sp_%s.h5"%(spin_case,i_case, sub_kep, betaphi, betar,  bvapp, gfactor, np.round(mup, 3), gammap, sigmap)

    h5f = h5py.File(fint,'r')

    I0=h5f['bghts0'][:]
    I1=h5f['bghts1'][:]
    I2=h5f['bghts2'][:]

    h5f.close()
    
    fig, ax = plt.subplots(figsize=fig_size,dpi=res)

    ax.imshow(I0+I1+I2,vmax=np.max(I0+I1+I2)*1.2,origin="lower",cmap="afmhot",extent=[-lim0,lim0,-lim0,lim0])

    ax.set_xlim(-10,10)
    ax.set_ylim(-10,10)

    ax.set_xlabel(r"$\alpha$"+" "+"(M)")
    ax.set_ylabel(r"$\beta$"+" "+"(M)")
    
    isExist = os.path.exists(save_path)
    if not isExist:
        os.makedirs(save_path)

    plt.savefig(save_path+'BHImage_a_%s_i_%s_sk_%s_bphi_%s_br_%s_bvapp_%s_gfact_%s_mp_%s_gp_%s_sp_%s.png'%(spin_case,i_case, sub_kep, betaphi, betar,  bvapp, gfactor, np.round(mup, 3), gammap, sigmap),dpi=res,bbox_inches='tight')

    plt.show()
    
def visplot(mask1, mask2, norm, rangles=[0,90], fig_size=[5,5], res=400, save_path='./Results/', **params):
    """
    Plots the the visibility profile for specified baesline angles. Requires 'cvisamp', 'cintensity', 'raytracing' and'clb' from the 'visamp', 'radialintensity', 'raytracing' and 'lensingbands' modules, respectively, to have been called for the corresponding spin and inclination angle.
    :param mask1: identifies the appropriate profile according to the indexing of the 'spins' array in params 
    :param mask2: identifies the appropriate profile according to the indexing of the 'i_angles' array in params
    :param rangles: iterable object containing radon angles along which the visibility will be plotted
    :param fig_size: dimensions of figure
    :param res: dots per inch of figure
    :param save_path: path for saving the plot
    """
    spin_case=params.get('spins')[mask1]
    i_case=params.get('i_angles')[mask2]
    maxbaseline=params.get('maxbaseline')
    Ncut=params.get('Ncut')
    load_path=params.get('path')
    radonfile=params.get('radonfile')
    dx0=params.get('dx0')
    dx1=params.get('dx1')
    dx2=params.get('dx2')
    maxbaseline=params.get('maxbaseline')
    Ncut=params.get('Ncut')
    gfactor=params.get('gfactor')
    fudge=params.get('fudge')[mask1]
    betaphi=params.get('betaphi')[mask1]
    betar=params.get('betar')[mask1]
    gammap=params.get('gammap')[mask1]
    sigmap=params.get('sigmap')[mask1]
    mup=params.get('mup')[mask1]
    sub_kep=params.get('sub_kep')[mask1]
    bvapp=params.get('bvapp')
    
    freqss = []
    visamps = []
    radial_norm = 0
    for i in range(len(rangles)):
        fnrays=load_path+"Visamp_%s_a_%s_i_%s_dx0_%s_dx1_%s_dx2_%s_sk_%s_bphi_%s_br_%s_bvapp_%s_gfact_%s_mup_%s_gp_%s_sp_%s_fudge_%s_Ncut_%s.h5"%(rangles[i],spin_case,i_case, dx0, dx1, dx2, sub_kep, betaphi, betar,  bvapp, gfactor, np.round(mup, 3), gammap, sigmap, fudge, int(Ncut))
                                 
        h5f = h5py.File(fnrays,'r')

        freqs=h5f['freqs'][:]
        visamp=h5f['visamp'][:]

        maxvis = np.max(visamp)    # max norm for some baseline angle
        if maxvis > radial_norm:
            radial_norm = maxvis

        h5f.close()
        freqss.append(freqs)
        visamps.append(visamp)
    freqss=np.array(freqss)

    # normalize visibility
    visamps = norm * np.array(visamps) / radial_norm
    
    fig, ax = plt.subplots(figsize=fig_size,dpi=res)

    for i in range(len(rangles)):
        ax.plot(freqss[0],visamps[i],linewidth=0.5,label=r"$\varphi=$"+"%s"%rangles[i])

    plt.yscale("log")
    plt.ylabel("Visibility Amplitude (Jy)",size=14)
    plt.xlabel("Baseline Length $u$ (G$\\lambda$)",size=14)
    plt.legend(loc="best",frameon=False)
    plt.xlim(0.,maxbaseline)
    plt.ylim(1e-6,1)
    
    isExist = os.path.exists(save_path)
    if not isExist:
        os.makedirs(save_path)
    plt.savefig(save_path+"Visplot_rangles_%s_%s_a_%s_i_%s_dx0_%s_dx1_%s_dx2_%s_sk_%s_bphi_%s_br_%s_bvapp_%s_gfact_%s_mp_%s_gp_%s_sp_%s_fudge_%s_Ncut_%s.png"%(rangles[0], rangles[-1] ,spin_case,i_case, dx0, dx1, dx2, sub_kep, betaphi, betar,  bvapp, gfactor, np.round(mup, 3), gammap, sigmap, fudge, int(Ncut)),dpi=res,bbox_inches='tight')
    
    plt.show()
    
def sourceprofile(i_fname):
    """
    Plots the given equatorial source profile. Currently, this function is limited to the use of inoisy files as source profiles (see https://github.com/AFD-Illinois/inoisy). The inoisy file should be saved in the same directory as the file calling this funciton.
    :param i_fname: sample equatorial profile
    """
    sourcefile = h5py.File(i_fname, 'r')
    
    # The inoisy files contain lots of useful information. Here we will just extract what we need for this example. 
    data = np.array(sourcefile['data/data_env'])

    #Limits of the figure
    xystart = np.array(sourcefile['params/x1start'])[0]

    print("There are %s snapshots in this inoisy data set"%data.shape[0])
    print("Each one has a %s x %s size"%(data.shape[1],data.shape[2]))
    
    fig, ax = plt.subplots(figsize=[5,5],dpi=400)

    #You can select different snapshots by changing the slicing 
    ax.imshow(np.log(data[0,:,:]),cmap="plasma",origin="lower",extent=[-xystart,xystart,-xystart,xystart])

    ax.set_facecolor('xkcd:black')
    ax.set_xlabel(r"$X$"+" "+"(M)")
    ax.set_ylabel(r"$Y$"+" "+"(M)")

    plt.show()

def dynamicalimage(mask1, mask2, fig_size=[5,5], res=400, save_path='./Results/', **params):
    """
    Plots single dynamical image produced by 'image' function in 'iImages' module.
    :param mask1: identifies the appropriate profile according to the indexing of the 'spins' array in params 
    :param mask2: identifies the appropriate profile according to the indexing of the 'i_angles' array in params
    :param fig_size: dimensions of figure
    :param res: dots per inch of figure
    :param save_path: path for saving the plot
    """
    spin_case=params.get('spins')[mask1]
    i_case=params.get('i_angles')[mask2]
    load_path=params.get('path')
    bvapp=params.get('bvapp')
    betaphi=params.get('betaphi')[mask1]
    betar=params.get('betar')[mask1]
    gfactor=params.get('gfactor')
    sub_kep=params.get('sub_kep')[mask1]
    i_tM=params.get('i_tM')
    dx0=params.get('dx0')
    dx1=params.get('dx1')
    dx2=params.get('dx2')
    
    fnbands=load_path+"LensingBands_a_%s_i_%s_dx0_%s_dx1_%s_dx2_%s.h5"%(spin_case,i_case, dx0, dx1, dx2)
    h5f = h5py.File(fnbands,'r')
    lim0=int(h5f["lim0"][0])
    h5f.close()
    
    fimages=load_path+"Dynamical_Image_a_%s_i_%s_bv_%s_bphi_%s_br_%s_gfact_%s_sk_%s_itM_%s.h5"%(spin_case,i_case, bvapp, betaphi, betar, gfactor, sub_kep, i_tM)
    #fimages="Images_a_%s_i_%s.h5"%(0.94,17)

    print("Reading file: ",fimages)

    h5f = h5py.File(fimages,'r')

    I0=h5f['bghts0'][:]
    I1=h5f['bghts1'][:]
    I2=h5f['bghts2'][:]

    h5f.close()
    
    fig, ax = plt.subplots(figsize=fig_size,dpi=res)

    ax.imshow(I0+I1+I2,vmax=np.max(I0+I1+I2)*1.2,origin="lower",cmap="plasma",extent=[-lim0,lim0,-lim0,lim0])

    ax.set_xlim(-10,10)
    ax.set_ylim(-10,10)

    ax.set_xlabel(r"$\alpha$"+" "+"(M)")
    ax.set_ylabel(r"$\beta$"+" "+"(M)")

    plt.show()
    
    isExist = os.path.exists(save_path)
    if not isExist:
        os.makedirs(save_path)
    
    plt.savefig(save_path+"Dynamical_Image_a_%s_i_%s_bv_%s_bphi_%s_br_%s_gfact_%s_sk_%s_itM_%s.png"%(spin_case,i_case, bvapp, betaphi, betar, gfactor, sub_kep, i_tM),dpi=res,bbox_inches='tight')
    
def movie(mask1, mask2, res=400, save_path='./Results/', **params):
    """
    Produces various images of the BH at different times and compiles this into a gif which is saved (but not displayed).
    :param mask1: identifies the appropriate profile according to the indexing of the 'spins' array in params 
    :param mask2: identifies the appropriate profile according to the indexing of the 'i_angles' array in params
    :param res: dots per inch of each composite figure
    :param save_path: path for saving the plot
    """    
    spin_case=params.get('spins')[mask1]
    i_case=params.get('i_angles')[mask2]
    load_path=params.get('path')
    betaphi=params.get('betaphi')[mask1]
    betar=params.get('betar')[mask1]
    gfactor=params.get('gfactor')
    sub_kep=params.get('sub_kep')[mask1]
    i_tM=params.get('i_tM')
    f_tM=params.get('f_tM')
    snapshots=params.get('snapshots')
    bvapp=params.get('bvapp')
    dx0=params.get('dx0')
    dx1=params.get('dx1')
    dx2=params.get('dx2')
    
    fnbands=load_path+"LensingBands_a_%s_i_%s_dx0_%s_dx1_%s_dx2_%s.h5"%(spin_case,i_case, dx0, dx1, dx2)
    h5f = h5py.File(fnbands,'r')
    lim0=int(h5f["lim0"][0])
    h5f.close()
    
    fimages=load_path+"Images_a_%s_i_%s_bv_%s_bphi_%s_br_%s_gfact_%s_sk_%s_itM_%s_ftM_%s_shots_%s.h5"%(spin_case,i_case, bvapp, betaphi, betar, gfactor, sub_kep, i_tM, f_tM, snapshots)


    print("Reading file: ",fimages)

    h5f = h5py.File(fimages,'r')

    Is0=h5f['bghts0'][:]
    Is1=h5f['bghts1'][:]
    Is2=h5f['bghts2'][:]

    h5f.close()
    
    fignames=[]
    VMAX=np.max(Is0+Is1+Is2)
    for tsnap in np.arange(i_tM, f_tM,int((f_tM-i_tM)/snapshots)):
        fig, ax = plt.subplots()

        ax.imshow(Is0[tsnap,:,:]+Is1[tsnap,:,:]+Is2[tsnap,:,:],vmax=VMAX,origin="lower",cmap="plasma",extent=[-lim0,lim0,-lim0,lim0])
        ax.set_xlim(-10,10)
        ax.set_ylim(-10,10)

        ax.set_xlabel(r"$\alpha$"+" "+"(M)")
        ax.set_ylabel(r"$\beta$"+" "+"(M)")

        fignames.append(save_path+'Fig_a_%s_i_%s_bphi_%s_br_%s_sk_%s_gfact_%s_tsnap_%s.png'%(spin_case, i_case, betaphi, betar, sub_kep, gfactor, tsnap))
        
        isExist = os.path.exists(save_path)
        if not isExist:
            os.makedirs(save_path)
        plt.savefig(save_path+'Fig_a_%s_i_%s_bphi_%s_br_%s_sk_%s_gfact_%s_tsnap_%s.png'%(spin_case, i_case, betaphi, betar, sub_kep, gfactor, tsnap),dpi=res,bbox_inches='tight')
        plt.close(fig)

    with imageio.get_writer('BHMovie_a_%s_i_%s_bphi_%s_br_%s_sk_%s_gfact_%s.gif'%(spin_case, i_case, betaphi, betar, sub_kep, gfactor), mode='I') as writer:
        for filename in fignames:
            image = imageio.imread(filename)
            writer.append_data(image)

    # We delete the created images and just keep the GIF
    for filename in set(fignames):
        os.remove(filename)