# libs
import os
import math
import numpy as np
import flopy.utils.binaryfile as bf
from create_and_run_mf import create_and_run_mf
import pandas as pd

#######################################################################
# Input Parameter
#######################################################################
# create modflow object

mfName = 'ex'
exeFN = 'mf2005_graz/CFP_NLFP_final_version.exe'
ws_model = '002_kf_wert_bestimmung'  # Ordner (Workspace für jeweilige Rechnung)


def compute_kf(q_meas, l_z, thck_pm, b_div_a, kf_start=1e-5, eps=1e-5):
    constant_head_well_q = np.nan

    while math.isnan(constant_head_well_q):
        # wirkliche gemessene Rate (wird intern noch aus Symetriegründen durch 4 geteilt)
        # q_meas = 3.632e-5  # m³/s

        # Abbruch Kriterium, eps = 1e-4 heißt auf 4 Nachkommastellen genau

        # Gebiet Geometrie
        l_x = 1.  # Gebietslänge x in m
        l_y = l_x  # Gebietslänge y in m
        # l_z = 0.10  # Gebietslänge z in m
        top = l_z
        bot = 0.0
        # thck_pm = 0.02
        thck_wsp = l_z - thck_pm
        well_width = 0.0025  # Messzellenlänge in m
        well_height = 0.005  # Messzellenhöhe in m
        well_z = 0.01  # Position Brunnen in z (0 = Boden)

        # forchheimer
        conv_crit = 1e-4  # [-] Konvergenz Kriterium
        # b_div_a = 0.000335712  # b/a aus Paper Mayaud et al

        #########################################################################
        # ab hier musst du nichts mehr ändern
        #########################################################################

        hk_wsp = 1.0  # kf horizontal im Freiwasserbereich m/s
        vka_wsp = 1.0  # kf vertikal im Freiwasserbereich m/s
        hk_pm = kf_start  # kf horizontal im Sediment in m/s
        aniso_vertical = 1.0  # kf vertical anisotropy factor
        hk_well = 0.5
        vka_well = 0.5

        # discretization
        # exponetiell wachsende Zellen in y und x Richtung mit logspace
        array_sum = np.logspace(np.log10(well_width), np.log10(l_x), 30)
        array_diff = []
        for i in range(len(array_sum)):
            if i == 0:
                array_diff.append(array_sum[i])
            else:
                # print(array_sum[i ]- array_sum[i-1])
                array_diff.append(array_sum[i] - array_sum[i - 1])
        delr = array_diff
        delc = array_diff
        bot = np.linspace(0.0, thck_pm, int(thck_pm / well_height))
        bot = np.append(bot, np.linspace(thck_pm + thck_wsp / 5, thck_wsp + thck_pm, 5))
        bot = np.flip(bot, 0)

        # dz = np.append(dz,np.linspace(thck_wsp + thck_pm/well_height/2,thck_wsp + thck_pm - thck_pm/well_height/2,thck_pm/well_height))
        ncol = len(delc)
        nrow = len(delr)
        nlay = len(bot) - 1

        # print('Anzahl Zellen: {}'.format(nrow * ncol * nlay))

        # Brunnenlayer
        for il, value in enumerate(bot):
            if (value > well_z) and (bot[il + 1] <= well_z):
                well_lay = il
                # print(well_lay)
                break

        # ibound
        ibound = np.full((nlay, nrow, ncol), 1, dtype=int)
        ibound[0:, 0:, 0] = 0  # not active at well
        ibound[well_lay, 0, 0] = -1  # Messzelle Dirichlet
        ibound[0, :, :] = -1  # WSP Top Dirichlet

        # starting heads
        strt = np.full((nlay, nrow, ncol), l_z)
        strt[well_lay, 0, 0] = well_z

        q_meas_quarter = q_meas / 4.

        eps_cur = 1e10
        counter = 1

        while eps_cur > eps:
            # print('Iter {:d}'.format(counter))
            # print('kf: {}'.format(hk_pm))
            counter = counter + 1
            #######################################################################
            # Aufruf Funktion create_and_run_mf
            #######################################################################
            succsess, dis = create_and_run_mf(mfName=mfName,
                                              exeFN=exeFN,
                                              ws_model=ws_model,
                                              l_x=l_x,
                                              thck_pm=thck_pm,
                                              top=bot[0],
                                              bot=bot[1:],
                                              well_lay=well_lay,
                                              hk_pm=hk_pm,
                                              vka_pm=hk_pm * aniso_vertical,
                                              hk_wsp=hk_wsp,
                                              vka_wsp=vka_wsp,
                                              hk_well=hk_well,
                                              vka_well=vka_well,
                                              ibound=ibound,
                                              strt=strt,
                                              delr=delr,
                                              delc=delc,
                                              nlay=nlay,
                                              nrow=nrow,
                                              ncol=ncol,
                                              conv_crit=conv_crit,
                                              b_div_a=b_div_a,
                                              print_mf_output=False)

            cbc_obj = bf.CellBudgetFile(os.path.join(ws_model, '{}.cbc'.format(mfName)), precision='single')
            # print(cbc_obj.list_records())
            constant_head = cbc_obj.get_data(kstpkper=(0, 0), text='CONSTANT HEAD')[0]
            constant_head_well_q = np.abs(constant_head[well_lay, 0, 0])  # m³/s
            # print('Rate calc: {}, Rate meas: {}'.format(constant_head_well_q * 4, q_meas_quarter * 4))
            kf_factor = q_meas_quarter / constant_head_well_q
            # print(kf_factor)
            hk_pm = hk_pm * kf_factor  # kf horizontal im Sediment in m/s
            eps_last = eps_cur
            eps_cur = np.abs(q_meas_quarter - constant_head_well_q) / q_meas_quarter
        # print('Rate calc: {}, Rate meas: {}'.format(constant_head_well_q * 4, q_meas_quarter * 4))
    return hk_pm


if __name__ == '__main__':
    slurping_rate = 3.632e-5
    l_z = 0.10
    thck_pm = 0.02
    b_div_a = 0.000335712
    df_inputs = pd.read_excel(io='input-data.xlsx', engine='openpyxl', skiprows=[1])
    df_inputs['th_pm'] = df_inputs['depth'] + df_inputs['wl']
    KC_w_different_porosities = ['Carling and Reader (1982) [Estimated kf]',
                                 'Wu and Wang (2006) [Estimated kf]',
                                 'Wooster et al. (2008) [Estimated kf]',
                                 'Frings et al. (2011)  [Estimated kf]'
                                 ]
    df_inputs['b_forchheimer'] = 10.44 / (9.81 * df_inputs['Mean Grain Size dm [mm]'] / 1000)

    df_outputs = pd.DataFrame([])
    df_outputs['sample'] = df_inputs['sample']
    for kc in KC_w_different_porosities:
        df_inputs['a_forchheimer'] = 1 / df_inputs[kc]
        kf_array = np.array([])
        for meas in range(0, df_inputs.shape[0]):
            slurp_rate = df_inputs['slurp_rate1'].iloc[meas] * 1e-6  # in m³/s
            lz = df_inputs['lz'].iloc[meas]
            th_pm = df_inputs['depth'].iloc[meas]
            b_div_a = df_inputs['b_forchheimer'].iloc[meas] / df_inputs['a_forchheimer'].iloc[meas]
            kf = compute_kf(slurp_rate, lz, th_pm, b_div_a)
            kf_array = np.append(kf_array, kf)
            print(kf_array)
        df_outputs[kc] = kf_array
        df_outputs.to_csv('computed_kfs.csv')  # write results within the loop
