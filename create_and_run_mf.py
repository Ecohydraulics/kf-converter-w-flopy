# -*- coding: utf-8 -*-
"""
Created on Wed Apr 24 10:42:26 2019
Module for creating and running one individual modow model

@author: alki
"""
import os
import flopy.modflow as fpm
import numpy as np


def create_and_run_mf(mfName='',
                      exeFN='',
                      ws_model='',
                      l_x=None,
                      thck_pm=None,
                      top=None,
                      bot=None,
                      well_lay=None,
                      hk_pm=None,
                      vka_pm=None,
                      hk_wsp=None,
                      vka_wsp=None,
                      hk_well=None,
                      vka_well=None,
                      ibound=1,
                      strt=None,
                      delr=None,
                      delc=None,
                      nlay=None,
                      nrow=None,
                      ncol=None,
                      conv_crit=None,
                      b_div_a=None,
                      print_mf_output=True):
    mfObj = fpm.Modflow(modelname=mfName, exe_name=exeFN, model_ws=ws_model)

    # l_y = l_x
    #    print('Diskretisierungslänge dx = {:f}, dy = {:f}'.format(delr,delc))
    #    print('ncol = {:d}, nrow = {:d}, nlay = {:d}'.format(ncol,nrow,nlay))
    #    print('l_x = {:f}, l_y = {:f}, l_z = {:f}'.format(l_x,l_y))
    #    print('Cell Midpoints z: {}'.format(z))

    # create dis file
    nper = 1
    nstp = 1
    perlen = 1.

    # create the dis object (discretization object)
    dis = fpm.ModflowDis(mfObj, nlay=nlay, nrow=nrow, ncol=ncol, nper=nper, nstp=nstp, perlen=perlen, steady=True,
                         delr=delr, delc=delc, top=top, botm=bot, itmuni=1, lenuni=2)

    bas = fpm.ModflowBas(mfObj, ibound=ibound, strt=strt)

    # create pcg packagae
    pcg = fpm.ModflowPcg(mfObj, mxiter=200, iter1=100, npcond=1, hclose=1e-07, rclose=1e-07,
                         relax=0.97, nbpol=0, iprpcg=0, mutpcg=3, damp=1.0, dampt=1.0, ihcofadd=0,
                         extension='pcg', unitnumber=None, filenames=None)

    # create oc package
    stress_period_data = {}
    for per in range(0, nper):
        for stp in range(0, nstp):
            stress_period_data[per, stp] = ['save head', 'PRINT BUDGET', 'SAVE BUDGET']
    oc = fpm.ModflowOc(mfObj, ihedfm=0, iddnfm=0, chedfm='(1000f10.4)', cddnfm=None, cboufm=None,
                       compact=False,
                       stress_period_data=stress_period_data,
                       extension=['oc', 'hds', 'ddn', 'cbc', 'ibo'], unitnumber=[14, 52, 53, 54, 0], filenames=None, )

    # In[3]:

    # lpf package
    # create lpf object
    #    laytyp = 0
    #    laywet = 0
    #    hk = np.full(np.shape(ibound),hk_pm)
    #    hk[well_lay,0,0] = hk_well
    #    hk[bot>=thck_pm] = hk_wsp
    #    vka = np.full(np.shape(ibound),vka_pm)
    #    vka[bot>=thck_pm] = vka_wsp
    #    vka[well_lay,0,0] = vka_well
    #
    #    # Add LPF package to the MODFLOW model
    #    lpf = fpm.ModflowLpf(mfObj, laytyp=laytyp, layavg=0, chani=1.0, layvka=0, laywet=laywet, ipakcb=53,
    #                   hdry=-888, iwdflg=0, wetfct=1, iwetit=1100, ihdwet=1, hk=hk, hani=1.0, vka=vka,
    #                   ss=3.3e-6, sy=0.3, vkcb=0, wetdry=-1, storagecoefficient=False,
    #                   constantcv=False, thickstrt=False, nocvcorrection=False, novfc=False,
    #                   extension='lpf', unitnumber=None, filenames=None)

    # In[4]:
    kf = np.full(np.shape(ibound), hk_pm)
    kf[well_lay, 0, 0] = hk_well
    kf[bot >= thck_pm] = hk_wsp
    vka = np.full(np.shape(ibound), vka_pm)
    vka[bot >= thck_pm] = vka_wsp
    vka[well_lay, 0, 0] = vka_well

    thk = np.empty((nlay, nrow, ncol))
    vcont = np.empty((nlay - 1, nrow, ncol))
    for il in range(0, nlay - 1):
        if il == 0:
            thk[il, :, :] = top - bot[il]
        else:
            thk[il, :, :] = bot[il] - bot[il + 1]
        # print(np.amax( thk[il,:,:]))
        # print(np.amax(kf[il,:,:])*np.amax(thk[il,:,:]))

        vcont[il, :, :] = vka[il, :, :] / (thk[il, :, :] / 2 + thk[il + 1, :, :] / 2)

    trans = kf * thk

    bcf = fpm.ModflowBcf(mfObj, ipakcb=53, intercellt=0, laycon=0, trpy=1.0, hdry=-1e+30,
                         iwdflg=0, wetfct=0.1, iwetit=1, ihdwet=0, tran=trans, hy=1.0, vcont=vcont,
                         sf1=1e-05, sf2=0.15, wetdry=-0.01, extension='bcf', unitnumber=None, filenames=None)
    # Add LPF package to the MODFLOW model
    #    lpf = fpm.ModflowLpf(mfObj, laytyp=laytyp, layavg=0, chani=1.0, layvka=0, laywet=laywet, ipakcb=53,
    #                   hdry=-888, iwdflg=0, wetfct=1, iwetit=1100, ihdwet=1, hk=hk, hani=1.0, vka=vka,
    #                   ss=3.3e-6, sy=0.3, vkcb=0, wetdry=-1, storagecoefficient=False,
    #                   constantcv=False, thickstrt=False, nocvcorrection=False, novfc=False,
    #                   extension='lpf', unitnumber=None, filenames=None)

    # In[4]:

    # hfb package

    #    hfb_data = []
    #    # loop over hfb
    #    for hfbIdx in range(0,numHFB):
    #        # loop over x
    #        for ic in range(0,ncol-1):
    #            if (x[ic] <= hfbX[hfbIdx]) and (x[ic+1] > hfbX[hfbIdx]):
    #                hfbcol1 = ic
    #                hfbcol2 = ic+1
    #                break
    #        # loop over y and z
    #        for ir in range(0,nrow):
    #            for il in range(0,nlay):
    #                if y[ir] <= window_width/2:
    #                    hfbRatio = hfbRatioWindow
    #                else:
    #                    hfbRatio = hfbRatioClosed
    #                if (top - z[il] < hfbRatio[hfbIdx]*m):
    #                    hfb_data.append([il,ir,hfbcol1,ir,hfbcol2,hydchr[hfbIdx]])
    #                else:
    #                    break
    # print(hfb_data)
    # with open(os.path.join(ws_model,'{}.hfb'.format(mfName)),'w') as outObj:
    #    outObj.write('{:10d}{:10d}{:10d}\n'.format(0,0,len(hfb_data)))
    #    for idx,hfb in enumerate(hfb_data):
    #        outObj.write('{:10d}{:10d}{:10d}{:10d}{:10d}{:10.3e}\n'.format(hfb[0]+1,hfb[1]+1,hfb[2]+1,hfb[3]+1,hfb[4]+1,hfb[5]))
    # print(m)

    #    hfb = fpm.ModflowHfb(mfObj, nphfb=0, mxfb=0, nhfbnp=0, hfb_data=hfb_data, nacthfb=0, no_print=False, options=None, extension='hfb', unitnumber=None, filenames=None)

    # In[5]:
    # write forheimer input file
    fn = os.path.join(ws_model, '{}.nlfp'.format(mfName))
    with open(fn, 'w') as in_obj:
        in_obj.write('#bla\n')
        in_obj.write('{:f}\n'.format(conv_crit))
        for il in range(0, nlay):
            in_obj.write('CONSTANT    {:f}\n'.format(b_div_a))
    # In[5]:

    # write input files
    mfObj.write_input()

    # append  package to name file
    namFN = os.path.join(ws_model, '{}.nam'.format(mfName))
    unit = 87
    pack_str = 'NLFP'
    with open(namFN, 'a') as namFile:
        namFile.write('{}{:16d}  {}\n'.format(pack_str, unit, '{}.nlfp'.format(mfName)))

    # In[6]:

    # run modflow
    if print_mf_output:
        success = mfObj.run_model()
    else:
        success = mfObj.run_model(silent=True)
    # write last budget of FM flow to budget logfil
    if print_mf_output:
        listFN = os.path.join(ws_model, '{}.list'.format(mfName))
        if os.path.exists(listFN):
            with open(listFN, "r") as inf:
                inf.seek(0, 2)  # Seek @ EOF
                fsize = inf.tell()  # Get Size
                inf.seek(max(fsize - 1500, 0), 0)  # Set pos @ last n chars
                lines = inf.readlines()  # Read to end
                print('\n')
                print('***************************************************\n')
                print('Flow model output for last stress period\n')
                print('\n')
                # print(lines)
                for line in lines:
                    print(line)
    return success, dis

