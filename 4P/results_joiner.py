import pandas as pd

lci_indicator = 'Global Warming'
mcda_weights = {}
mcda_weights['global_warming'] = 0.333
mcda_weights['cost'] = 0.333
mcda_weights['pci'] = 0.333

def single_analysis_comparison():
        
        paths = ['mechanical_recycling',
                 'frp',
                 'ppo',
                 'no_recycling',
                 'waste_to_incineration',
                 'chemical_recycling']

        flow_res = pd.DataFrame()
        lca_res = pd.DataFrame()
        cost_res = pd.DataFrame()

        for p in paths:
            
            df = pd.read_csv(p+'/total_flow_results.csv')
            flow_res = pd.concat([flow_res,df])
            
            df = pd.read_csv(p+'/national_lca_results.csv')
            lca_res = pd.concat([lca_res,df])
            
            df = pd.read_csv(p+'/aggregated cost data.csv')
            cost_res = pd.concat([cost_res,df])    
            
            print(p)


        flow_res.to_csv('flow_res.csv',index = False)
        lca_res.to_csv('lca_res.csv',index = False)
        cost_res.to_csv('cost_res.csv',index = False)


            
        flow_res2020 = flow_res[flow_res['year'] == 2020]
        flow_res2020.to_csv('flowres2020.csv', index = False)

        cost_res2020 = cost_res[cost_res['year'] == 2020]
        cost_res2020.to_csv('costres2020.csv', index = False)

        lca_res2020 = lca_res[lca_res['year'] == 2020]
        lca_res2020.to_csv('lcares2020.csv', index = False)


        if lci_indicator == 'Global Warming':
                     gwp = lca_res2020[lca_res2020['impacts'] == "Global Warming Air (kg CO2 eq )"]
                     gwp_grouped = gwp.groupby(['year', 'scenario','corrected_name'])['impact'].agg('sum').reset_index()

        max_gwp = gwp_grouped['impact'].max()
        
        pci_grouped = flow_res2020
        cst_grouped = cost_res2020

        cst_grouped = cst_grouped.melt(id_vars = ['year','scenario'], value_vars = ['vmanuf_cost_of_production', 'collection_cost_waste_plastic',
       'landfill_transportation_cost_waste_plastic',
       'wte_transportation_cost_waste_plastic',
       'mrf_transportation_cost_waste_plastic', 'mrf_sorting_cost_plastic',
       'transportation_cost_mrf_to_reclaimer', 'mechanical_reclaiming_cost',
       'chemical_reclaiming_cost', 'pyrolysis_upcycling_cost',
       'fiber_resin_upcycling_cost', 'incineration_cost', 'landfill_costs'], var_name = 'stage', value_name = 'costs').reset_index()             
        cst_grouped = cst_grouped.groupby(['year','scenario'])['costs'].agg('sum').reset_index().drop_duplicates()
        max_cst = cst_grouped['costs'].max()
        cst_grouped['normalized_cost'] = 1-(cst_grouped['costs']/max_cst)
      



        mcda_df = pd.DataFrame()
        mcda_df['plastic_circularity_index'] = pci_grouped['material_circularity_index']
        mcda_df[lci_indicator] = gwp_grouped['impact']
        mcda_df['cost'] = cst_grouped['costs']
        mcda_df['scenario'] = gwp_grouped['scenario']
        mcda_df['year'] = gwp_grouped['year']

        mcda_df['MCDA_indicator'] = mcda_df['cost']*mcda_weights['normalized_cost'] + mcda_df['Global Warming']*mcda_weights['global_warming'] + mcda_df['plastic_circularity_index']*mcda_weights['pci']  
        mcda_df.to_csv(mcda_results)



def sensitivity_local():
        paths = ['vacuum cardboard',
        'vacuum paper',
        'vacuum film',
        'discreen1 cardboard',
        'discreen1 paper',
        'glass_breaker glass',
        'discreen2 cardboard',
        'discreen2 paper',
        'discreen2 film',
        'nir_pet aluminum',
        'nir_pet cardboard',
        'nir_pet glass',
        'nir_pet hdpe',
        'nir_pet paper',
        'nir_pet pet',
        'nir_pet film',
        'nir_pet other',
        'recovery_foodgrade',
        'recovery_highgrade',
        'recovery_mediumgrade',
        'recovery_lowgrade',
        'mechanical_recycling_foodgrade_selectivity',
        'mechanical_recycling_highgrade_selectivity',
        'mechanical_recycling_mediumgrade_selectivity',
        'mechanical_recycling_lowgrade_selectivity',
        'distance_for_landfill',
        'distance_for_wte',
        'distance_for_mrf',
        'distance_from_mrf_to_reclaimer',
        'user_defined_collection_rate',
        'L_recycling',
        'U_recycling',
        'L_downcycling',
        'U_downcycling',
        'L_incineration',
        'U_incineration',
        'L_pyrolysis_upcycling',
        'U_pyrolysis_upcycling',
        'L_fiber_resin_upcycling',
        'U_fiber_resin_upcycling',
        'L_average',
        'U_average']

        flow_res = pd.DataFrame()
        lca_res = pd.DataFrame()
        cost_res = pd.DataFrame()


        for p in paths:
            
            df = pd.read_csv('./'+p+'/total_flow_results.csv')
            df['parameter'] = p
            flow_res = pd.concat([flow_res,df])
            
            df = pd.read_csv('./'+p+'/national_lca_results.csv')
            df['parameter'] = p
            lca_res = pd.concat([lca_res,df])
            
            df = pd.read_csv('./'+p+'/aggregated cost data.csv')
            df['parameter'] = p
            cost_res = pd.concat([cost_res,df])    

            print(p)

        flow_res['baseline'] = 0.06624003
        flow_res['difference'] = (flow_res['baseline'] - flow_res['material_circularity_index'])/flow_res['baseline']
        flow_res.to_csv('flow_res.csv',index = False)       
        cost_res.to_csv('cost_res.csv',index = False)
        lca_res = lca_res[lca_res['process'] != "PET, manufacture"]
        lca_res = lca_res.groupby(['year','impacts','corrected_name', 'scenario','parameter'])['impact'].agg('sum').reset_index()
        lca_res = lca_res[lca_res['corrected_name'] == 'Global Warming Air (kg CO2 eq )']
        
        lca_res['baseline'] = -69133190.12
        lca_res['difference'] = (lca_res['baseline'] - lca_res['impact'])/lca_res['baseline']
        lca_res.to_csv('lca_res.csv',index = False)


def sensitivity_range():


        scenarios = ['mechanical_recycling',
                 'frp',
                 'ppo',
                 'no_recycling',
                 'waste_to_incineration',
                 'chemical_recycling']

        flow_res_dic = {}
        flow_res_dic['waste_to_incineration']={}
        flow_res_dic['chemical_recycling']={}
        flow_res_dic['mechanical_recycling']={}
        flow_res_dic['frp']={}
        flow_res_dic['ppo']={}
        flow_res_dic['no_recycling']={}

        flow_res_dic['waste_to_incineration']['circ'] = 0.0
        flow_res_dic['chemical_recycling']['circ'] = 0.0
        flow_res_dic['mechanical_recycling']['circ'] = 0.0
        flow_res_dic['frp']['circ'] = 0.0
        flow_res_dic['ppo']['circ'] = 0.0
        flow_res_dic['no_recycling']['circ'] = 0.0


        lca_res_dic = {}
        lca_res_dic['waste_to_incineration']={}
        lca_res_dic['chemical_recycling']={}
        lca_res_dic['mechanical_recycling']={}
        lca_res_dic['frp']={}
        lca_res_dic['ppo']={}
        lca_res_dic['no_recycling']={}

        lca_res_dic['waste_to_incineration']['lca'] = 0.0
        lca_res_dic['chemical_recycling']['lca'] = 0.0
        lca_res_dic['mechanical_recycling']['lca'] = 0.0
        lca_res_dic['frp']['lca'] = 0.0
        lca_res_dic['ppo']['lca'] = 0.0
        lca_res_dic['no_recycling']['lca'] = 0.0

        paths = ['vacuum cardboard',
        'vacuum paper',
        'vacuum film',
        'discreen1 cardboard',
        'discreen1 paper',
        'glass_breaker glass',
        'discreen2 cardboard',
        'discreen2 paper',
        'discreen2 film',
        'nir_pet aluminum',
        'nir_pet cardboard',
        'nir_pet glass',
        'nir_pet hdpe',
        'nir_pet paper',
        'nir_pet pet',
        'nir_pet film',
        'nir_pet other',
        'recovery_foodgrade',
        'recovery_highgrade',
        'recovery_mediumgrade',
        'recovery_lowgrade',
        'mechanical_recycling_foodgrade_selectivity',
        'mechanical_recycling_highgrade_selectivity',
        'mechanical_recycling_mediumgrade_selectivity',
        'mechanical_recycling_lowgrade_selectivity',
        'distance_for_landfill',
        'distance_for_wte',
        'distance_for_mrf',
        'distance_from_mrf_to_reclaimer',
        'user_defined_collection_rate',
        'L_recycling',
        'U_recycling',
        'L_downcycling',
        'U_downcycling',
        'L_incineration',
        'U_incineration',
        'L_pyrolysis_upcycling',
        'U_pyrolysis_upcycling',
        'L_fiber_resin_upcycling',
        'U_fiber_resin_upcycling',
        'L_average',
        'U_average']

        flow_res = pd.DataFrame()
        lca_res = pd.DataFrame()
        cost_res = pd.DataFrame()

        flder_name = 'resulttest'
        #sensitivity_analysis_range = ["-50","-40","-30","0","10","30","50"]
        sensitivity_analysis_range = ["-50","50"]

        for sc in scenarios:

            for p in paths:

                for s in sensitivity_analysis_range:
                
                    df = pd.read_csv('./'+flder_name+sc+'/'+'result_'+p+s+'/total_flow_results.csv')
                    df['parameter'] = p
                    df['sensitivity range'] = s
                    flow_res = pd.concat([flow_res,df])
                    
                    df = pd.read_csv('./'+flder_name+sc+'/'+'result_'+p+s+'/national_lca_results.csv')
                    df['parameter'] = p
                    df['sensitivity range'] = s
                    lca_res = pd.concat([lca_res,df])
                    
                    df = pd.read_csv('./'+flder_name+sc+'/'+'result_'+p+s+'/aggregated cost data.csv')
                    df['parameter'] = p
                    df['sensitivity range'] = s
                    cost_res = pd.concat([cost_res,df])    

                    print(p)

            flow_res['scenario'] = sc
            flow_res['baseline'] = flow_res_dic[sc]['circ']
            flow_res['difference'] = (flow_res['baseline'] - flow_res['material_circularity_index'])/flow_res['baseline']

            flow_res.to_csv('flow_res.csv',index = False) 
            cost_res['scenario'] = sc      
            cost_res.to_csv('cost_res.csv',index = False)

            #lca_res = lca_res[lca_res['process'] != "PET, manufacture"]
            lca_res = lca_res.groupby(['year','impacts','corrected_name', 'scenario','parameter','sensitivity range'])['impact'].agg('sum').reset_index()
            lca_res = lca_res[lca_res['corrected_name'] == 'Global Warming Air (kg CO2 eq )']
            
            lca_res['scenario'] = sc
            lca_res['baseline'] = lca_res_di[sc]['lca']
            lca_res['difference'] = (lca_res['baseline'] - lca_res['impact'])/lca_res['baseline']
            lca_res.to_csv(sc+'lca_res.csv',index = False)



        
#single_analysis_comparison()
#sensitivity_local()
sensitivity_range()