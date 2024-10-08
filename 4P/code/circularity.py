import pandas as pd

def circ(psd,final_results,scenario,total_flow_results,weighted_circ_results,diversion_circ_results,inflow_outflow_circ_results,total_circ_results,utility):

    #Numerous circularity metrics are available for calculation. 
    #Handling all the circularity results. 
    circ_results_wtd = psd.circ_results_wtd[psd.circ_results_wtd['year'] != 2019]
    circ_results_div = psd.circ_results_div[psd.circ_results_div['year'] != 2019]
    circ_results_inflow_outflow = psd.circ_results_inflow_outflow[psd.circ_results_inflow_outflow['year'] != 2019]
    
    us_results = final_results.groupby(['year'])[['vmanuf_to_use', 'use_to_dispose', 'dispose_to_landfill','dispose_to_collection',
           'dispose_to_mrf', 'dispose_to_wte_uncollected','dispose_to_wte_collected','mrf_to_m_reclaimer', 'mrf_to_c_reclaimer',
           'mrf_to_c_upcycler','mrf_to_ppo_reclaimer','mrf_to_frp_reclaimer','mrf_to_landfill', 'm_reclaimer_to_manuf',
           'm_reclaimer_to_landfill', 'c_reclaimer_to_manuf',
           'c_reclaimer_to_landfill', 'rmanuf_to_use', 'rmanuf_to_landfill', 'cl_recycled', 'downcycled',
           'wte_energy','pyrolysis_fuel_oil','fiber_reinforced_resin','plastic_demand_data','total_bale_quantity',
           'total_bale_quantity_mechanical_reclaimer',
           'total_bale_quantity_chemical_reclaimer',
           'total_bale_quantity_upcycling_reclaimer',
           'total_bale_quantity_pyrolysis_reclaimer',
           'total_bale_quantity_fiber_reinforced_resin_reclaimer',
           'landfill']].agg('sum').reset_index()
    
    #Calculating different circularity metrics
    X_recycling = utility['L_recycling']/utility['L_average']*utility['U_recycling']/utility['U_average']
    X_downcycling = utility['L_downcycling']/utility['L_average']*utility['U_downcycling']/utility['U_average']
    X_pyrolysis = utility['L_pyrolysis']/utility['L_average']*utility['U_pyrolysis']/utility['U_average']
    X_fiber_reinforced_resin = utility['L_fiber_resin']/utility['L_average']*utility['U_fiber_resin']/utility['U_average']
    X_incineration = utility['L_incineration']/utility['L_average']*utility['U_incineration']/utility['U_average']

    us_results['cl_circularity'] = us_results['cl_recycled']/us_results['use_to_dispose']
    us_results['ol_circularity'] = us_results['downcycled']/us_results['use_to_dispose']
    us_results['u_circularity_ppo'] = us_results['total_bale_quantity_pyrolysis_reclaimer']/us_results['use_to_dispose']
    us_results['u_circularity_frp'] = us_results['total_bale_quantity_fiber_reinforced_resin_reclaimer']/us_results['use_to_dispose']
    us_results['u_circularity'] = us_results['mrf_to_c_upcycler']/us_results['use_to_dispose']
    us_results['wte_circularity'] = (us_results['dispose_to_wte_collected'] + us_results['dispose_to_wte_uncollected'])/us_results['use_to_dispose']
    us_results['linear_flow_index'] = us_results['vmanuf_to_use']*us_results['landfill']/((us_results['vmanuf_to_use']+us_results['rmanuf_to_use'])*(us_results['vmanuf_to_use']+us_results['rmanuf_to_use']))
    
    def mci_negative_converter(df):
       df[df<0] = 0
       return df

    us_results['material_circularity_index_recycling'] = mci_negative_converter(1 - us_results['linear_flow_index']*0.9/X_recycling)
    us_results['material_circularity_index_downcycling'] = mci_negative_converter(1 - us_results['linear_flow_index']*0.9/X_downcycling)
    us_results['material_circularity_index_pyrolysis'] = mci_negative_converter(1 - us_results['linear_flow_index']*0.9/X_pyrolysis)
    us_results['material_circularity_index_fiber_reinforced_resin'] = mci_negative_converter(1 - us_results['linear_flow_index']*0.9/X_fiber_reinforced_resin)
    us_results['material_circularity_index_incineration'] = mci_negative_converter(1 - us_results['linear_flow_index']*0.9/X_incineration)



    us_results['utility_factor_incineration'] = X_incineration
    us_results['utility_factor_recycling'] =  X_recycling
    us_results['utility_factor_downcycling'] = X_downcycling
    us_results['utility_factor_pyrolysis'] = X_pyrolysis
    us_results['utility_fiber_reinforced_resin'] = X_fiber_reinforced_resin

    us_results['material_circularity_index'] = us_results['material_circularity_index_recycling'] * us_results['cl_circularity'] + us_results['material_circularity_index_downcycling'] * us_results['ol_circularity'] + us_results['material_circularity_index_pyrolysis']*us_results['u_circularity_ppo'] + us_results['material_circularity_index_fiber_reinforced_resin'] * us_results['u_circularity_frp'] + us_results['material_circularity_index_incineration'] * us_results['wte_circularity']




    us_results['scenario'] = scenario
    us_results.to_csv(total_flow_results,index = False)




    circ_results_wtd_us = circ_results_wtd.groupby(['year'])[['rec_mass', 'total_disposal']].agg('sum').reset_index()
    circ_results_wtd_us['wtd_circularity'] = round(circ_results_wtd_us['rec_mass']/circ_results_wtd_us['total_disposal'],3)
    circ_results_wtd_us['scenario'] = scenario
    circ_results_wtd_us.to_csv(weighted_circ_results, index = False)
    
    circ_results_div_us = circ_results_div.groupby(['year'])[['vpet_manuf','total_disposal','total_landfill']].agg('sum').reset_index()
    circ_results_div_us['div_circularity'] = round((circ_results_div_us['total_disposal'] - circ_results_div_us['total_landfill'])/circ_results_div_us['total_disposal'],3)
    circ_results_div_us['scenario'] = scenario
    circ_results_div_us.to_csv(diversion_circ_results, index = False)
    
    circ_results_inflow_outflow_us = circ_results_inflow_outflow.groupby(['year'])[['vmat_inflow', 'cmat_inflow', 'wmat_outflow', 'cmat_outflow']].agg('sum').reset_index()
    circ_results_inflow_outflow_us['inflow_circularity'] = circ_results_inflow_outflow_us['cmat_inflow']/(circ_results_inflow_outflow_us['cmat_inflow'] + circ_results_inflow_outflow_us['vmat_inflow'])
    circ_results_inflow_outflow_us['outflow_circularity'] = circ_results_inflow_outflow_us['cmat_outflow']/(circ_results_inflow_outflow_us['cmat_outflow'] + circ_results_inflow_outflow_us['wmat_outflow'])
    circ_results_inflow_outflow_us['avg_inflow_outflow_circularity'] = (circ_results_inflow_outflow_us['inflow_circularity'] + circ_results_inflow_outflow_us['outflow_circularity'])/2
    circ_results_inflow_outflow_us['scenario'] = scenario
    circ_results_inflow_outflow_us.to_csv(inflow_outflow_circ_results, index = False)
    
    
    totlc = pd.DataFrame()
    totlc['year'] = pd.Series(us_results['year'])
    totlc['closedloop_circularity'] = pd.Series(us_results['cl_circularity'])
    totlc['openloop_circularity'] = pd.Series(us_results['ol_circularity'])
    totlc['upcycling_circularity'] = pd.Series(us_results['u_circularity'])
    totlc['incineration_circularity'] = pd.Series(us_results['wte_circularity'])
    totlc['material_circularity_index'] = pd.Series(us_results['material_circularity_index'])
    totlc['avg_inflow_outflow_circularity'] = pd.Series(circ_results_inflow_outflow_us['avg_inflow_outflow_circularity'])
    totlc['landfill_diversion_circularity'] = pd.Series(circ_results_div_us['div_circularity'])
    totlc['Weighted_circularity'] = pd.Series(circ_results_wtd_us['wtd_circularity'])
    
    
    cols = ['closedloop_circularity', 'openloop_circularity',
           'upcycling_circularity', 'incineration_circularity',
           'avg_inflow_outflow_circularity', 'landfill_diversion_circularity',
           'Weighted_circularity','material_circularity_index']
    
    totlc_m = totlc.melt(id_vars=['year'], value_vars=cols, var_name='circularity', value_name='cvalue', col_level=None, ignore_index=True)
    totlc_m['scenario'] = scenario
    totlc_m.to_csv(total_circ_results,index = False)

    return totlc