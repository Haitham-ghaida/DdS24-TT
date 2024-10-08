import pandas as pd
lci_indicator = 'Global Warming'



mcda_weights = {}
mcda_weights['global_warming'] = 0.333
mcda_weights['cost'] = 0.333
mcda_weights['pci'] = 0.333

verbose_print = False

def mcda(flow_res,lca_res,cost_res,analysis):

        if lci_indicator == 'Global Warming':
                     gwp_grouped = lca_res[lca_res['impacts'] == "Global Warming Air (kg CO2 eq )"]
                     gwp_grouped = gwp_grouped.rename(columns = {'impact':lci_indicator})

        
        pci_grouped = flow_res
        cst_grouped = cost_res



        if analysis == "single_analysis_comparison":


            pci_grouped = pci_grouped[['material_circularity_index','year','scenario']]
            cst_grouped = cst_grouped[['costs','year','scenario']]
            gwp_grouped = gwp_grouped[[lci_indicator,'year','scenario']]

            merge1 = pci_grouped.merge(cst_grouped, on = ['year','scenario'])
            merge2 = merge1.merge(gwp_grouped, on = ['year','scenario'])
            mcda_df = merge2

        elif analysis == "uncertainty_analysis_comparison":


            pci_grouped = pci_grouped[['material_circularity_index','year','scenario','seed']]
            cst_grouped = cst_grouped[['costs','year','scenario','seed']]
            gwp_grouped = gwp_grouped[[lci_indicator,'year','scenario','seed']]

            merge1 = pci_grouped.merge(cst_grouped, on = ['year','scenario','seed'])
            merge2 = merge1.merge(gwp_grouped, on = ['year','scenario','seed'])
            mcda_df = merge2



        elif analysis == "local_sensitivity_analysis_without_difference":
            pci_grouped = pci_grouped[['material_circularity_index','year','scenario','parameter']]
            cst_grouped = cst_grouped[['costs','year','scenario','parameter']]
            gwp_grouped = gwp_grouped[[lci_indicator,'year','scenario','parameter']]  

            merge1 = pci_grouped.merge(cst_grouped, on = ['year','scenario','parameter'])
            merge2 = merge1.merge(gwp_grouped, on = ['year','scenario','parameter'])
            mcda_df = merge2 

        else:
            pci_grouped = pci_grouped[['material_circularity_index','year','scenario','parameter','sensitivity range']]
            cst_grouped = cst_grouped[['costs','year','scenario','parameter','sensitivity range']]
            gwp_grouped = gwp_grouped[[lci_indicator,'year','scenario','parameter','sensitivity range']]  

            merge1 = pci_grouped.merge(cst_grouped, on = ['year','scenario','parameter','sensitivity range'])
            merge2 = merge1.merge(gwp_grouped, on = ['year','scenario','parameter','sensitivity range'])
            mcda_df = merge2                  


        mcda_fin = pd.DataFrame()
        years = list(pd.unique(mcda_df['year']))
        for y in years:
            df = mcda_df[mcda_df['year'] == y]
            max_cst = df['costs'].max()
            max_gwp = df[lci_indicator].max()
            df['normalized_cost'] = 1-(df['costs']/max_cst)
            df['normalized_'+lci_indicator] = 1-(df[lci_indicator]/max_gwp)

            
            if analysis == "single_analysis_comparison":
                df = df[['normalized_cost','normalized_'+lci_indicator,'material_circularity_index','year','scenario']]
                mcda_fin = pd.concat([mcda_fin,df])

            elif analysis == "uncertainty_analysis_comparison":
                df = df[['normalized_cost','normalized_'+lci_indicator,'material_circularity_index','year','scenario','seed']]
                mcda_fin = pd.concat([mcda_fin,df])

            elif analysis == "local_sensitivity_analysis_without_difference":
                df = df[['normalized_cost','normalized_'+lci_indicator,'material_circularity_index','year','scenario','parameter']]
                mcda_fin = pd.concat([mcda_fin,df]) 
            else:
                df = df[['normalized_cost','normalized_'+lci_indicator,'material_circularity_index','year','scenario','parameter','sensitivity range']]
                mcda_fin = pd.concat([mcda_fin,df])                            

        mcda_fin['plastic_circularity_index'] = mcda_fin['material_circularity_index']
        mcda_df = mcda_fin
        mcda_df['MCDA_indicator'] = mcda_df['normalized_cost']*mcda_weights['cost'] + mcda_df['normalized_'+lci_indicator]*mcda_weights['global_warming'] + mcda_df['plastic_circularity_index']*mcda_weights['pci']  
        return mcda_df

def single_analysis_comparison():

        flder_name = './resultdebugtest'
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
            
            df = pd.read_csv(flder_name+p+'/result_'+p+'/total_flow_results.csv')
            flow_res = pd.concat([flow_res,df])
            
            df = pd.read_csv(flder_name+p+'/result_'+p+'/national_lca_results.csv')
            lca_res = pd.concat([lca_res,df])
            
            df = pd.read_csv(flder_name+p+'/result_'+p+'/aggregated cost data.csv')
            cost_res = pd.concat([cost_res,df])  
            
            print(p)

        cost_res= cost_res.melt(id_vars = ['year','scenario'], value_vars = ['vmanuf_cost_of_production', 'collection_cost_waste_plastic',
           'landfill_transportation_cost_waste_plastic',
           'wte_transportation_cost_waste_plastic',
           'mrf_transportation_cost_waste_plastic', 'mrf_sorting_cost_plastic',
           'transportation_cost_mrf_to_reclaimer', 'mechanical_reclaiming_cost',
           'chemical_reclaiming_cost', 'pyrolysis_upcycling_cost',
           'fiber_resin_upcycling_cost', 'incineration_cost', 'landfill_costs'], var_name = 'stage', value_name = 'costs').reset_index() 

        if verbose_print:
            flow_res.to_csv('./result/flow_res.csv',index = False)
            lca_res.to_csv('./result/lca_res.csv',index = False)
            cost_res.to_csv('./result/cost_res.csv',index = False)


       
        flow_res2020 = flow_res[flow_res['year'] == 2020]
        flow_res2020.to_csv('./result/flowres2020.csv', index = False)

        cost_res2020 = cost_res[cost_res['year'] == 2020]
        cost_res2020.to_csv('./result/costres2020.csv', index = False)

        lca_res2020 = lca_res[lca_res['year'] == 2020]
        lca_res2020.to_csv('./result/lcares2020.csv', index = False)

        lca_res2020 = lca_res2020.groupby(['year','impacts','name','corrected_name','scenario'])['impact'].agg('sum').reset_index()

        lca_res2020.to_csv('./result/lcares2020grouped.csv', index = False)  

        cost_res2020 = cost_res2020.groupby(['year','scenario'])['costs'].agg('sum').reset_index().drop_duplicates()

        cost_res2020.to_csv('./result/costres2020grouped.csv', index = False)          

        mcda(flow_res2020,lca_res2020,cost_res2020,'single_analysis_comparison')



def compound_effect(added_scenario):



        flder_name = './resultdebugtest'
        paths = ['mechanical_recycling',
                 'frp',
                 'ppo',
                 'waste_to_incineration',
                 'chemical_recycling']

        flow_res = pd.DataFrame()
        lca_res = pd.DataFrame()
        cost_res = pd.DataFrame()

        for p in paths:
            
            df = pd.read_csv(flder_name+p+added_scenario+'/result_'+p+added_scenario+'/total_flow_results.csv')
            flow_res = pd.concat([flow_res,df])
            
            df = pd.read_csv(flder_name+p+added_scenario+'/result_'+p+added_scenario+'/national_lca_results.csv')
            lca_res = pd.concat([lca_res,df])
            
            df = pd.read_csv(flder_name+p+added_scenario+'/result_'+p+added_scenario+'/aggregated cost data.csv')
            cost_res = pd.concat([cost_res,df])  
            
            print(p)

        cost_res= cost_res.melt(id_vars = ['year','scenario'], value_vars = ['vmanuf_cost_of_production', 'collection_cost_waste_plastic',
           'landfill_transportation_cost_waste_plastic',
           'wte_transportation_cost_waste_plastic',
           'mrf_transportation_cost_waste_plastic', 'mrf_sorting_cost_plastic',
           'transportation_cost_mrf_to_reclaimer', 'mechanical_reclaiming_cost',
           'chemical_reclaiming_cost', 'pyrolysis_upcycling_cost',
           'fiber_resin_upcycling_cost', 'incineration_cost', 'landfill_costs'], var_name = 'stage', value_name = 'costs').reset_index() 


        flow_res.to_csv('./result/flow_res'+added_scenario+'.csv',index = False)
        lca_res.to_csv('./result/lca_res'+added_scenario+'.csv',index = False)
        cost_res.to_csv('./result/cost_res'+added_scenario+'.csv',index = False)


        lca_res = lca_res.groupby(['year','impacts','name','corrected_name','scenario'])['impact'].agg('sum').reset_index()

        lca_res.to_csv('./result/lcaresgrouped'+added_scenario+'.csv', index = False)  

        cost_res = cost_res.groupby(['year','scenario'])['costs'].agg('sum').reset_index().drop_duplicates()

        cost_res.to_csv('./result/costresgrouped'+added_scenario+'.csv', index = False)          

        mcda_df = mcda(flow_res,lca_res,cost_res,'single_analysis_comparison')

        mcda_df.to_csv('./result/mcda_results'+added_scenario+'.csv', index = False) 

#compound_effect("_increase_nir_pet_eff")
#compound_effect("_with_increasing_collection")
#compound_effect("_inc_coll_nirpet_eff")

def sensitivity_local():

        scenarios = ['mechanical_recycling',
                 'frp',
                 'ppo',
                 'no_recycling',
                 'waste_to_incineration',
                 'chemical_recycling']

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
        'chemical_recycling_selectivity',
        'polyester_to_fiber_reinforced_resin_conversion_factor',
        'pet_to_polyester_conversion_factor',
        'pet_to_ppo_conversion_factor',
        'recovery_chemical_recycling',
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

        flow_res_t = pd.DataFrame()
        lca_res_t = pd.DataFrame()
        cost_res_t = pd.DataFrame()
        typ = 'local'

        for sc in scenarios:

                flow_res = pd.DataFrame()
                lca_res = pd.DataFrame()
                cost_res = pd.DataFrame()

                print(sc)

                for p in paths:
                    
                    df = pd.read_csv('./resultshortlocalsens'+sc+'/result_'+p+'/total_flow_results.csv')
                    df['parameter'] = p
                    flow_res = pd.concat([flow_res,df])
                    
                    df = pd.read_csv('./resultshortlocalsens'+sc+'/result_'+p+'/national_lca_results.csv')
                    df['parameter'] = p
                    lca_res = pd.concat([lca_res,df])
                    
                    df = pd.read_csv('./resultshortlocalsens'+sc+'/result_'+p+'/aggregated cost data.csv')
                    df['parameter'] = p
                    cost_res = pd.concat([cost_res,df])    

                    print(p)

                #flow_res['baseline'] = flow_res_dic[sc]['circ']
                #flow_res['difference'] = (flow_res['baseline'] - flow_res['material_circularity_index'])/flow_res['baseline']
                
                if verbose_print:
                    flow_res.to_csv('./result/'+sc+typ+'flow_res.csv',index = False)       
                    cost_res.to_csv('./result/'+sc+typ+'cost_res.csv',index = False)



                #lca_res = lca_res[lca_res['process'] != "PET, manufacture"]
                #lca_res = lca_res.groupby(['year','impacts','corrected_name', 'scenario','parameter'])['impact'].agg('sum').reset_index()
                #lca_res = lca_res[lca_res['corrected_name'] == 'Global Warming Air (kg CO2 eq )']
                
                #lca_res['baseline'] = lca_res_dic[sc]['lca']
                #lca_res['difference'] = (lca_res['baseline'] - lca_res['impact'])/lca_res['baseline']
                


                flow_res_t = pd.concat([flow_res_t,flow_res])
                lca_res_t = pd.concat([lca_res_t,lca_res])
                cost_res_t = pd.concat([cost_res_t,cost_res])


        lca_res_t = lca_res_t.groupby(['year','impacts','name','corrected_name', 'scenario','parameter'])['impact'].agg('sum').reset_index()          
        lca_base = pd.read_csv('./result/'+'lcares2020grouped.csv')
        lca_base = lca_base.rename(columns={'impact':'baseline'})
        lca_df = lca_res_t.merge(lca_base,on = ['year','impacts','name','corrected_name','scenario'])
        lca_df['difference'] = (lca_df['impact'] - lca_df['baseline'])/lca_df['baseline']
        lca_df.to_csv("./result/lca_local_sensitivity_analysis_with_difference.csv",index = False)


        flow_base = pd.read_csv('./result/'+'flowres2020.csv')
        flow_base = flow_base[['year','scenario','material_circularity_index']]
        flow_base = flow_base.rename(columns={'material_circularity_index':'mci_baseline'})
        flow_df = flow_res_t.merge(flow_base, on = ['year','scenario'])
        flow_df['difference'] = (flow_df['material_circularity_index'] - flow_df['mci_baseline'])/flow_df['mci_baseline']
        flow_df.to_csv("./result/flow_local_sensitivity_analysis_with_difference.csv",index = False)


        
        cost_res_t= cost_res_t.melt(id_vars = ['year','scenario','parameter'], value_vars = ['vmanuf_cost_of_production', 'collection_cost_waste_plastic',
       'landfill_transportation_cost_waste_plastic',
       'wte_transportation_cost_waste_plastic',
       'mrf_transportation_cost_waste_plastic', 'mrf_sorting_cost_plastic',
       'transportation_cost_mrf_to_reclaimer', 'mechanical_reclaiming_cost',
       'chemical_reclaiming_cost', 'pyrolysis_upcycling_cost',
       'fiber_resin_upcycling_cost', 'incineration_cost', 'landfill_costs'], var_name = 'stage', value_name = 'costs').reset_index()      

        cost_res_t = cost_res_t.groupby(['year','scenario','parameter'])['costs'].agg('sum').reset_index().drop_duplicates()
        cost_base = pd.read_csv('./result/'+'costres2020grouped.csv')
        cost_base = cost_base[['year','scenario','costs']]
        cost_base = cost_base.rename(columns={'costs':'cost_baseline'})
        cost_df = cost_res_t.merge(cost_base, on = ['year','scenario'])
        cost_df['difference'] = (cost_df['costs'] - cost_df['cost_baseline'])/cost_df['cost_baseline']
        cost_df.to_csv("./result/cost_local_sensitivity_analysis_with_difference.csv",index = False)


        mcda_df = mcda(flow_res_t,lca_res_t,cost_res_t,'local_sensitivity_analysis_without_difference')
        mcda_base = pd.read_csv('./result/'+'single_analysis_comparison'+'mcda_results.csv')
        mcda_base = mcda_base[['year','scenario','MCDA_indicator']]
        mcda_base = mcda_base.rename(columns={'MCDA_indicator':'MCDA_baseline'})
        mcda_df = mcda_df.merge(mcda_base,on = ['scenario','year'])
        mcda_df['difference'] = (mcda_df['MCDA_indicator'] - mcda_df['MCDA_baseline'])/mcda_df['MCDA_baseline']
        mcda_df.to_csv("./result/mcda_local_sensitivity_analysis_with_difference.csv",index = False)


def sensitivity_range():


        scenarios = ['mechanical_recycling',
                 'frp',
                 'ppo',
                 'no_recycling',
                 'waste_to_incineration',
                 'chemical_recycling']

        typ = "range"

        flow_res_dic = {}
        flow_res_dic['waste_to_incineration']={}
        flow_res_dic['chemical_recycling']={}
        flow_res_dic['mechanical_recycling']={}
        flow_res_dic['frp']={}
        flow_res_dic['ppo']={}
        flow_res_dic['no_recycling']={}

        flow_res_dic['waste_to_incineration']['circ'] = 0.0238465
        flow_res_dic['chemical_recycling']['circ'] = 0.112315506
        flow_res_dic['mechanical_recycling']['circ'] = 0.026422912
        flow_res_dic['frp']['circ'] = 0.357612956
        flow_res_dic['ppo']['circ'] = 0.038150499 
        flow_res_dic['no_recycling']['circ'] = 0


        lca_res_dic = {}
        lca_res_dic['waste_to_incineration']={}
        lca_res_dic['chemical_recycling']={}
        lca_res_dic['mechanical_recycling']={}
        lca_res_dic['frp']={}
        lca_res_dic['ppo']={}
        lca_res_dic['no_recycling']={}

        lca_res_dic['waste_to_incineration']['lca'] = 7484740125
        lca_res_dic['chemical_recycling']['lca'] = 6446617186
        lca_res_dic['mechanical_recycling']['lca'] = 6579097506
        lca_res_dic['frp']['lca'] = 2122865118
        lca_res_dic['ppo']['lca'] = 10152531042
        lca_res_dic['no_recycling']['lca'] = 7357516592

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




        flder_name = './sens_results/resultshortsensitivity'
        #sensitivity_analysis_range = ["-50","-40","-30","0","10","30","50"]
        sensitivity_analysis_range = ["-50","50"]

        flow_res = pd.DataFrame()
        lca_res = pd.DataFrame()
        cost_res = pd.DataFrame()


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


        lca_res = lca_res.groupby(['year','impacts','name','corrected_name', 'scenario','parameter','sensitivity range'])['impact'].agg('sum').reset_index()          
        lca_base = pd.read_csv('./result/'+'lcares2020grouped.csv')
        lca_base = lca_base.rename(columns={'impact':'baseline'})
        lca_df = lca_res.merge(lca_base,on = ['year','impacts','name','corrected_name','scenario'])
        lca_df['difference'] = (lca_df['impact'] - lca_df['baseline'])/lca_df['baseline']
        lca_df.to_csv("./result/lca_range_sensitivity_analysis_with_difference.csv",index = False)


        flow_base = pd.read_csv('./result/'+'flowres2020.csv')
        flow_base = flow_base[['year','scenario','material_circularity_index']]
        flow_base = flow_base.rename(columns={'material_circularity_index':'mci_baseline'})
        flow_df = flow_res.merge(flow_base, on = ['year','scenario'])
        flow_df['difference'] = (flow_df['material_circularity_index'] - flow_df['mci_baseline'])/flow_df['mci_baseline']
        flow_df.to_csv("./result/flow_range_sensitivity_analysis_with_difference.csv",index = False)


        
        cost_res= cost_res.melt(id_vars = ['year','scenario','parameter','sensitivity range'], value_vars = ['vmanuf_cost_of_production', 'collection_cost_waste_plastic',
       'landfill_transportation_cost_waste_plastic',
       'wte_transportation_cost_waste_plastic',
       'mrf_transportation_cost_waste_plastic', 'mrf_sorting_cost_plastic',
       'transportation_cost_mrf_to_reclaimer', 'mechanical_reclaiming_cost',
       'chemical_reclaiming_cost', 'pyrolysis_upcycling_cost',
       'fiber_resin_upcycling_cost', 'incineration_cost', 'landfill_costs'], var_name = 'stage', value_name = 'costs').reset_index()      

        cost_res = cost_res.groupby(['year','scenario','parameter','sensitivity range'])['costs'].agg('sum').reset_index().drop_duplicates()
        cost_base = pd.read_csv('./result/'+'costres2020grouped.csv')
        cost_base = cost_base[['year','scenario','costs']]
        cost_base = cost_base.rename(columns={'costs':'cost_baseline'})
        cost_df = cost_res.merge(cost_base, on = ['year','scenario'])
        cost_df['difference'] = (cost_df['costs'] - cost_df['cost_baseline'])/cost_df['cost_baseline']
        cost_df.to_csv("./result/cost_range_sensitivity_analysis_with_difference.csv",index = False)

        mcda_df = mcda(flow_res,lca_res,cost_res,'range_sensitivity_analysis_without_difference')
        mcda_base = pd.read_csv('./result/'+'single_analysis_comparison'+'mcda_results.csv')
        mcda_base = mcda_base[['year','scenario','MCDA_indicator']]
        mcda_base = mcda_base.rename(columns={'MCDA_indicator':'MCDA_baseline'})
        mcda_df = mcda_df.merge(mcda_base,on = ['scenario','year'])
        mcda_df['difference'] = (mcda_df['MCDA_indicator'] - mcda_df['MCDA_baseline'])/mcda_df['MCDA_baseline']
        mcda_df.to_csv("./result/mcda_range_sensitivity_analysis_with_difference.csv",index = False)


def uncertainty_analysis_statewise(added_scenario):



        flder_name = './resultdebugtest'
        p = 'uncertainty_analysis_'
        runs = range(0,1)

        flow_res = pd.DataFrame()
        lca_res = pd.DataFrame()
        cost_res = pd.DataFrame()

        for r in runs:
            r = str(r)  

            df = pd.read_csv(flder_name+added_scenario+'/result_'+p+r+'/total_flow_results_statewise.csv')
            df['seed'] = r
            flow_res = pd.concat([flow_res,df])
            
            df = pd.read_csv(flder_name+added_scenario+'/result_'+p+r+'/regional_lca_results.csv')
            df['seed'] = r
            lca_res = pd.concat([lca_res,df])
                        
            df = pd.read_csv(flder_name+added_scenario+'/result_'+p+r+'/costs_results_by_region_year.csv')
            df['seed'] = r
            cost_res = pd.concat([cost_res,df])
              
        cost_res = cost_res.melt(id_vars = ['year','scenario','seed','region'], value_vars = ['vmanuf_cost_of_production', 'collection_cost_waste_plastic',
           'landfill_transportation_cost_waste_plastic',
           'wte_transportation_cost_waste_plastic',
           'mrf_transportation_cost_waste_plastic', 'mrf_sorting_cost_plastic',
           'transportation_cost_mrf_to_reclaimer', 'mechanical_reclaiming_cost',
           'chemical_reclaiming_cost', 'pyrolysis_upcycling_cost',
           'fiber_resin_upcycling_cost', 'incineration_cost', 'landfill_costs'], var_name = 'stage', value_name = 'costs').reset_index() 


        flow_res.to_csv('./result/flow_res'+added_scenario+'.csv',index = False)
        lca_res.to_csv('./result/lca_res'+added_scenario+'.csv',index = False)
        cost_res.to_csv('./result/cost_res'+added_scenario+'.csv',index = False)


        lca_res = lca_res.groupby(['year','region','impacts','name','corrected_name','scenario','seed'])['impact'].agg('sum').reset_index()

        lca_res.to_csv('./result/lcaresgrouped'+added_scenario+'.csv', index = False)  

        cost_res = cost_res.groupby(['year','region','scenario','seed'])['costs'].agg('sum').reset_index().drop_duplicates()

        cost_res.to_csv('./result/costresgrouped'+added_scenario+'.csv', index = False)          

        #mcda_df = mcda(flow_res,lca_res,cost_res,'uncertainty_analysis_comparison')

        #mcda_df.to_csv('./result/mcda_results'+added_scenario+'.csv', index = False) 

#uncertainty_analysis('uncertainty_scenario')
uncertainty_analysis_statewise('uncertainty_scenario')
#single_analysis_comparison()
#sensitivity_local()
#sensitivity_range()