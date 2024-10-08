if __name__ == '__main__':

       import pandas as pd
       import numpy as np
       import sys
       import glob,os
       import shutil
       sys.path.append(os.path.join(os.path.dirname(__file__), 'code'))
       from flowmodel import PlasticSD
       from visualizer import compare_results
       from lifecycleanalysis import Pylca
       from tea import Tea
       from mcda import mcda
       from circularity import circ
       from circularity_statewise import circ_statewise

       import yaml

       scenario_from_yaml = {}
       with open('./input/options_files/' + 'singleyearanalysis' + '.yaml') as file:
              scenario_from_yaml = yaml.safe_load(file)

       # read input parameters file, and define mrf_equipment_efficiency from that
       parameters = pd.read_csv('./input/scenario_files/'+'mechanical_recycling'+'.csv')
       mrf_equipment_efficiency = parameters[['year','discreen1 cardboard', 'discreen1 paper', 'discreen2 cardboard',
              'discreen2 film', 'discreen2 paper', 'eddy aluminum', 'eddy glass',
              'glass_breaker glass', 'magnet film', 'magnet iron', 'magnet other',
              'nir_hdpe aluminum', 'nir_hdpe cardboard', 'nir_hdpe film',
              'nir_hdpe glass', 'nir_hdpe hdpe', 'nir_hdpe other', 'nir_hdpe paper',
              'nir_hdpe pet', 'nir_pet aluminum', 'nir_pet cardboard', 'nir_pet film',
              'nir_pet glass', 'nir_pet hdpe', 'nir_pet other', 'nir_pet paper',
              'nir_pet pet', 'vacuum cardboard', 'vacuum film', 'vacuum paper']]
       mrf_equipment_efficiency = mrf_equipment_efficiency.melt(
              id_vars=['year'],
              value_vars=mrf_equipment_efficiency.columns[1:],
              var_name='year-source-targetmaterial',
              value_name='efficiency')
       mrf_equipment_efficiency['year-source-targetmaterial'] = mrf_equipment_efficiency['year'].astype('str') + ' ' + mrf_equipment_efficiency['year-source-targetmaterial'].astype('str')
       mrf_equipment_efficiency = mrf_equipment_efficiency[['year-source-targetmaterial','efficiency']]
       mrf_equipment_efficiency = mrf_equipment_efficiency.set_index('year-source-targetmaterial')
       parameters = parameters.set_index('year')

       # parsing csv and xlsx files from scenario yaml
       for varname in scenario_from_yaml['input_filenames']['parse_csv'].keys():
              exec(varname + " = pd.read_csv('" + scenario_from_yaml['input_filenames']['parse_csv'][varname] + "')")

       for varname in scenario_from_yaml['input_filenames']['parse_xlsx'].keys():
              exec(varname + " = pd.read_excel('" + scenario_from_yaml['input_filenames']['parse_xlsx'][varname] + "')")

       sys.path.insert(1, './ABM')
       import TPB_ABM_BatchRun

       ###JDS: if we're using abm, but not the shortcut, do the abm batchrun
       if not scenario_from_yaml['flags']['use_shortcut_ABM'] and scenario_from_yaml['parameters']['collection_rate_method'] == "ABM":
              year_period = (scenario_from_yaml['parameters']['final_year'] + 1) - scenario_from_yaml['parameters']['initial_year']
              TPB_ABM_BatchRun.run_func(
                     year_period, reps=1,
                     intervention_scenario=scenario_from_yaml['parameters']['intervention_scenario'])
              
              if not scenario_from_yaml['flags']['bypass_SD_model']:
                     pass
              else:
                     exit()

       #Creating the time array for simulation
       year = list(range(scenario_from_yaml['parameters']['initial_year'], scenario_from_yaml['parameters']['final_year'] + 1))

       #Cleaning the output directory
       r = glob.glob('./output/*')
       for i in r:
              os.remove(i)

       ###JDS: calculate all flows, costs, circularity indicators, and
       def __run__():

              #Loading parameters from the parameters files.
              scenario = str(pd.unique(parameters['scenario'])[0])


              #Creating the flow model object
              psd = PlasticSD(flow = {},
                              material = "pet",
                              recycled_material = "rpet",
                              statewise_composition_filename = "./input/core_files/waste_composition.csv",
                              region_composition_filename = scenario_from_yaml['input_filenames']['no_parse']['region_composition_filename'],
                              demand_model = "linear",
                              year = year,
                              initial_recycled_mat = 0,
                              initial_year = scenario_from_yaml['parameters']['initial_year'],
                              final_year = scenario_from_yaml['parameters']['final_year'],
                              parameters = parameters,
                              collection_rate_method = scenario_from_yaml['parameters']['collection_rate_method'],
                              mrf_equipment_efficiency = mrf_equipment_efficiency,
                              verbose = 0
                             )

              #Calculates all flows
              psd.main()

              #Saving the final flow results and removing the starting year because it has some anomalies.
              flow_results = psd.final_results[psd.final_results['year'] > scenario_from_yaml['parameters']['initial_year']]
              #Removing Hawaii because electricity grid information is currently missing
              for st in scenario_from_yaml['parameters']['states_to_drop']:
                  flow_results = flow_results[flow_results['region'] != st]

              flow_results.to_csv('chk.csv')

              '''
              #Creating the cost object
              cost = Tea(year = year,
                         flow_df = flow_results,
                         virgin_resin_production_df = virgin_resin_production_df,
                         mrf_df = mrf_df,
                         mech_reclaiming_df = mech_reclaiming_df,
                         chem_reclaiming_glyc_df = chem_reclaiming_glyc_df,
                         upcycling_pyro_df = upcycling_pyro_df,
                         fiber_resin_upcycling_df = fiber_resin_upcycling_df,
                         waste_to_incineration_df = waste_to_incineration_df,
                         parameters = parameters,
                         verbose = 0
                        )
              #Calculates the cost information
              cost.main()

              #Adding a column to the cost results with the name of the scenario
              cost.cost_flow_df['scenario'] = scenario
              #Saving cost results
              cost_data_statewise = cost.cost_flow_df.groupby(['year','region'])['vmanuf_cost_of_production', 'collection_cost_waste_plastic',
                     'landfill_transportation_cost_waste_plastic',
                     'wte_transportation_cost_waste_plastic',
                     'mrf_transportation_cost_waste_plastic', 'mrf_sorting_cost_plastic',
                     'transportation_cost_mrf_to_reclaimer', 'mechanical_reclaiming_cost',
                     'chemical_reclaiming_cost', 'pyrolysis_upcycling_cost', 'fiber_resin_upcycling_cost',
                     'incineration_cost', 'landfill_costs'].agg('sum').reset_index()
              cost_data_statewise['scenario'] = scenario
              cost_data_statewise.to_csv(scenario_from_yaml['output_filenames']['cost_results'], index = False)

              #Creating an aggregated cost results database.
              cost_data = cost.cost_flow_df.groupby(['year'])['vmanuf_cost_of_production', 'collection_cost_waste_plastic',
                     'landfill_transportation_cost_waste_plastic',
                     'wte_transportation_cost_waste_plastic',
                     'mrf_transportation_cost_waste_plastic', 'mrf_sorting_cost_plastic',
                     'transportation_cost_mrf_to_reclaimer', 'mechanical_reclaiming_cost',
                     'chemical_reclaiming_cost', 'pyrolysis_upcycling_cost', 'fiber_resin_upcycling_cost',
                     'incineration_cost', 'landfill_costs'].agg('sum').reset_index()
              cost_data['scenario'] = scenario
              cost_data.to_csv(scenario_from_yaml['output_filenames']['aggregated_cost_results'], index = False)

              #Calculating all circularity indicators.
              circ_df = circ(
                     psd,
                     flow_results,
                     scenario,
                     scenario_from_yaml['output_filenames']['total_flow_results'],
                     scenario_from_yaml['output_filenames']['weighted_circ_results'],
                     scenario_from_yaml['output_filenames']['diversion_circ_results'],
                     scenario_from_yaml['output_filenames']['inflow_outflow_circ_results'],
                     scenario_from_yaml['output_filenames']['total_circ_results'],
                     scenario_from_yaml['parameters']['utility']
                     )
              circ_df_statewise = circ_statewise(
                     psd,
                     flow_results,
                     scenario,
                     scenario_from_yaml['output_filenames']['total_flow_results_statewise'],
                     scenario_from_yaml['output_filenames']['weighted_circ_results'],
                     scenario_from_yaml['output_filenames']['diversion_circ_results'],
                     scenario_from_yaml['output_filenames']['inflow_outflow_circ_results'],
                     scenario_from_yaml['output_filenames']['total_circ_results'],
                     scenario_from_yaml['parameters']['utility']
                     )

              #Creating object for LCA calculations
              for st in scenario_from_yaml['parameters']['states_to_drop']:
                     lca_demand = psd.lca_demand_df[(psd.lca_demand_df['year']  > scenario_from_yaml['parameters']['initial_year']) & (psd.lca_demand_df['region'] != st)]
                     displaced_lca_demand = psd.system_displaced_lca_df[(psd.system_displaced_lca_df['year']  > scenario_from_yaml['parameters']['initial_year']) & (psd.system_displaced_lca_df['region'] != st)]

              #Parallelizing for shortcut
              if scenario_from_yaml['flags']['parallelization_flag']:
                     lca_demand = lca_demand[lca_demand['region'] == sys.argv[1]]
                     displaced_lca_demand = displaced_lca_demand[displaced_lca_demand['region'] == sys.argv[1]]

              lca_demand.to_csv('./output/lca_demand_from_flow_model.csv', mode = "a")
              displaced_lca_demand.to_csv('./output/displaced_lca_demand_from_flow_model.csv', mode = "a")

              lca = Pylca(lca_results = scenario_from_yaml['output_filenames']['lca_results'],
                          shortcutlca = scenario_from_yaml['input_filenames']['no_parse']['shortcutlca'],
                          foreground_data = foreground_data,
                          intermediate_demand = scenario_from_yaml['output_filenames']['intermediate_demand'],
                          dynamic_lci = scenario_from_yaml['input_filenames']['no_parse']['dynamic_lci'],
                          electricity_grid_spatial_level = scenario_from_yaml['parameters']['electricity_grid_spatial_level'],
                          static_lci = scenario_from_yaml['input_filenames']['no_parse']['static_lci'],
                          ###JDS: These lci references needed to be removed after we removed them from the options files
                     #      emissions_lci = scenario_from_yaml['input_filenames']['no_parse']['emissions_lci'],
                          traci_lci = scenario_from_yaml['input_filenames']['no_parse']['traci_lci'],
                          lca_locations = scenario_from_yaml['input_filenames']['no_parse']['lca_locations'],
                          lcia_name_bridge = scenario_from_yaml['input_filenames']['no_parse']['lcia_name_bridge'],
                          use_shortcut_lca_calculations = scenario_from_yaml['flags']['use_shortcut_lca_calculations'],
                          scenario = scenario,
                          verbose = 0)
              #Performing LCA calculations
              lca.pylca_run_main(lca_demand)

              system_displaced_lca = Pylca(lca_results = scenario_from_yaml['output_filenames']['displaced_lca_results'],
                          shortcutlca = scenario_from_yaml['input_filenames']['no_parse']['shortcutlca_displaced'],
                          foreground_data = foreground_data,
                          intermediate_demand = scenario_from_yaml['output_filenames']['intermediate_demand_displaced'],
                          dynamic_lci = scenario_from_yaml['input_filenames']['no_parse']['dynamic_lci'],
                          electricity_grid_spatial_level = scenario_from_yaml['parameters']['electricity_grid_spatial_level'],
                          static_lci = scenario_from_yaml['input_filenames']['no_parse']['static_lci'],
                          ###JDS: These lci references needed to be removed after we removed them from the options files
                     #      emissions_lci = scenario_from_yaml['input_filenames']['no_parse']['emissions_lci'],
                          traci_lci = scenario_from_yaml['input_filenames']['no_parse']['traci_lci'],
                          lca_locations = scenario_from_yaml['input_filenames']['no_parse']['lca_locations'],
                          lcia_name_bridge = scenario_from_yaml['input_filenames']['no_parse']['lcia_name_bridge'],
                          use_shortcut_lca_calculations = scenario_from_yaml['flags']['use_shortcut_lca_calculations'],
                          scenario = scenario,
                          verbose = 0)
              #Performing LCA calculations
              system_displaced_lca.pylca_run_main(displaced_lca_demand)


              #Combine lca results and displaced lca results into one.
              print('Combining LCA and displaced LCA results')
              df1 = pd.read_csv(scenario_from_yaml['output_filenames']['lca_results'])
              df2 = pd.read_csv(scenario_from_yaml['output_filenames']['displaced_lca_results'])
              #Making the impacts negative for displacement credits
              df2['impact'] = df2['impact']*-1
              combined_df = pd.concat([df1,df2])
              ###JDS: if this is uncommented, it needs to be scenario_from_yaml['output_filenames']['combined_lca_results']
              #combined_df.to_csv(combined_lca_results, index = False)
              national_lca_df = combined_df.groupby(['year', 'process', 'impacts', 'name',
              'corrected_name', 'scenario'])['impact'].agg('sum').reset_index()
              regional_lca_df = combined_df.groupby(['year','region', 'process', 'impacts', 'name',
              'corrected_name', 'scenario'])['impact'].agg('sum').reset_index()
              national_lca_df.to_csv(scenario_from_yaml['output_filenames']['national_lca_results'], index = False)
              regional_lca_df.to_csv(scenario_from_yaml['output_filenames']['regional_lca_results'], index = False)

              mcda_indicator = mcda(
                                   lca_results = national_lca_df,
                                   cost_results = cost_data,
                                   pci_results = circ_df,
                                   lci_indicator = "Global Warming",
                                   mcda_weights = scenario_from_yaml['parameters']['mcda_weights'],
                                   mcda_results = scenario_from_yaml['output_filenames']['mcda_results']
                                   )

              mcda_indicator.mcda_calc()

              #Creating plots
              ###JDS: if this is uncommented, it needs to be scenario_from_yaml['output_filenames']['total_circ_results'], etc.
              #compare_results(total_circ_results,total_flow_results, combined_lca_results, aggregated_cost_results)
       '''


       if scenario_from_yaml['flags']['local_sensitivity_analysis']:

              orig1 = mrf_equipment_efficiency.copy()
              orig2 = parameters.copy()
              orig3 = scenario_from_yaml['parameters']['utility'].copy()
              sensitivity_parameters_input = sensitivity_parameters_input[sensitivity_parameters_input['switch'] == 'on']

              sensitivity_parameters_input_mrf = sensitivity_parameters_input[sensitivity_parameters_input['type'] == 'mrf']
              for parameter_under_analysis in list(sensitivity_parameters_input_mrf['parameters']):
                     mrf_equipment_efficiency = orig1.copy()
                     for i in year:
                            #Changing to extreme value
                            mrf_equipment_efficiency['efficiency'][str(i)+ " "+parameter_under_analysis] = 0

                     __run__()
                     mrf_equipment_efficiency.to_csv(scenario_from_yaml['output_filenames']['changed_parameter'])
                     folder_name = "result_"+parameter_under_analysis
                     try:
                       shutil.rmtree(folder_name)
                     except FileNotFoundError:
                       print('Folder does not exist: ' + folder_name)
                       pass
                     shutil.copytree("./output",folder_name)


              sensitivity_parameters_input_prm = sensitivity_parameters_input[sensitivity_parameters_input['type'] == 'other']
              for parameter_under_analysis in list(sensitivity_parameters_input_prm['parameters']):
                     parameters = orig2.copy()
                     for i in year:
                            #Changing to extreme value
                            parameters[parameter_under_analysis][i] = 0

                     __run__()
                     parameters.to_csv(scenario_from_yaml['output_filenames']['changed_parameter'])
                     folder_name = "result_"+parameter_under_analysis

                     try:
                       shutil.rmtree(folder_name)
                     except FileNotFoundError:
                       print('Folder does not exist: ' + folder_name)
                       pass
                     shutil.copytree("./output",folder_name)



              sensitivity_parameters_input_utility = sensitivity_parameters_input[sensitivity_parameters_input['type'] == 'utility']
              for parameter_under_analysis in list(sensitivity_parameters_input_utility['parameters']):
                     scenario_from_yaml['parameters']['utility'] = orig3.copy()
                     for i in year:
                            #Changing to extreme low value
                            scenario_from_yaml['parameters']['utility'][parameter_under_analysis] = 0.0001

                     __run__()
                     pd.DataFrame.from_dict(scenario_from_yaml['parameters']['utility'],orient = 'index').to_csv(scenario_from_yaml['output_filenames']['changed_parameter'])
                     folder_name = "result_"+parameter_under_analysis
                     try:
                       shutil.rmtree(folder_name)
                     except FileNotFoundError:
                       print('Folder does not exist: ' + folder_name)
                       pass
                     shutil.copytree("./output",folder_name)


       elif scenario_from_yaml['flags']['range_sensitivity_analysis']:

              orig1 = mrf_equipment_efficiency.copy()
              orig2 = parameters.copy()
              orig3 = scenario_from_yaml['parameters']['utility'].copy()

              sensitivity_parameters_input = sensitivity_parameters_input[sensitivity_parameters_input['switch'] == 'on']

              sensitivity_parameters_input_mrf = sensitivity_parameters_input[sensitivity_parameters_input['type'] == 'mrf']
              for range_value_sensitivity_analysis in scenario_from_yaml['flags']['range_value_sensitivity_analysis_list']:
                     for parameter_under_analysis in list(sensitivity_parameters_input_mrf['parameters']):
                            index= list(sensitivity_parameters_input_mrf['parameters']).index(parameter_under_analysis)
                            limit_flag = list(sensitivity_parameters_input_mrf['limit'])[index]
                            mrf_equipment_efficiency = orig1.copy()
                            for i in year:
                                   old_param = mrf_equipment_efficiency['efficiency'][str(i)+ " "+parameter_under_analysis]
                                   #Changing to a certain percentage value
                                   mrf_equipment_efficiency['efficiency'][str(i)+ " "+parameter_under_analysis] = (mrf_equipment_efficiency['efficiency'][str(i)+ " "+parameter_under_analysis])*(1+range_value_sensitivity_analysis/100)

                                   if limit_flag:
                                          if mrf_equipment_efficiency['efficiency'][str(i)+ " "+parameter_under_analysis] < 0 :
                                                    mrf_equipment_efficiency['efficiency'][str(i)+ " "+parameter_under_analysis] = 0
                                          elif  mrf_equipment_efficiency['efficiency'][str(i)+ " "+parameter_under_analysis] > 1 :
                                                    mrf_equipment_efficiency['efficiency'][str(i)+ " "+parameter_under_analysis] = 1
                                   print("Old parameter value "+str(old_param)+" changed to  "+str(mrf_equipment_efficiency['efficiency'][str(i)+ " "+parameter_under_analysis]) + " "+str(i)+ " "+parameter_under_analysis,flush = True)
                            __run__()
                            mrf_equipment_efficiency.to_csv(scenario_from_yaml['output_filenames']['changed_parameter'])
                            folder_name = "result_"+parameter_under_analysis+str(range_value_sensitivity_analysis)
                            try:
                              shutil.rmtree(folder_name)
                            except FileNotFoundError:
                              print('Folder does not exist: ' + folder_name)
                              pass
                            shutil.copytree("./output",folder_name)


                     sensitivity_parameters_input_prm = sensitivity_parameters_input[sensitivity_parameters_input['type'] == 'other']
                     for parameter_under_analysis in list(sensitivity_parameters_input_prm['parameters']):
                            parameters = orig2.copy()
                            index= list(sensitivity_parameters_input_prm['parameters']).index(parameter_under_analysis)
                            limit_flag = list(sensitivity_parameters_input_prm['limit'])[index]
                            old_param = parameters[parameter_under_analysis][i]
                            for i in year:
                                   #Changing to a certain percentage value
                                   parameters[parameter_under_analysis][i] = parameters[parameter_under_analysis][i]*(1+range_value_sensitivity_analysis/100)
                                   if limit_flag:
                                          if parameters[parameter_under_analysis][i] < 0 :
                                                    parameters[parameter_under_analysis][i] = 0
                                          elif parameters[parameter_under_analysis][i] > 1 :
                                                    parameters[parameter_under_analysis][i] = 1
                                   print("Old parameter value "+str(old_param)+" changed to  "+str(parameters[parameter_under_analysis][i]) + parameter_under_analysis + str(i),flush = True)
                            __run__()
                            parameters.to_csv(scenario_from_yaml['output_filenames']['changed_parameter'])
                            folder_name = "result_"+parameter_under_analysis+str(range_value_sensitivity_analysis)

                            try:
                              shutil.rmtree(folder_name)
                            except FileNotFoundError:
                              print('Folder does not exist: ' + folder_name)
                              pass
                            shutil.copytree("./output",folder_name)

                     sensitivity_parameters_input_utility = sensitivity_parameters_input[sensitivity_parameters_input['type'] == 'utility']
                     for parameter_under_analysis in list(sensitivity_parameters_input_utility['parameters']):
                            scenario_from_yaml['parameters']['utility'] = orig3.copy()
                            index= list(sensitivity_parameters_input_utility['parameters']).index(parameter_under_analysis)
                            limit_flag = list(sensitivity_parameters_input_utility['limit'])[index]
                            for i in year:
                                   old_param = scenario_from_yaml['parameters']['utility'][parameter_under_analysis]
                                   #Changing to a certain percentage value
                                   scenario_from_yaml['parameters']['utility'][parameter_under_analysis] = scenario_from_yaml['parameters']['utility'][parameter_under_analysis]*(1+range_value_sensitivity_analysis/100)

                                   if limit_flag:
                                          if scenario_from_yaml['parameters']['utility'][parameter_under_analysis] < 0 :
                                                    scenario_from_yaml['parameters']['utility'][parameter_under_analysis] = 0
                                          elif scenario_from_yaml['parameters']['utility'][parameter_under_analysis] > 1 :
                                                    scenario_from_yaml['parameters']['utility'][parameter_under_analysis] = 1
                                   print("Old parameter value "+str(old_param)+" changed to  "+str(scenario_from_yaml['parameters']['utility'][parameter_under_analysis]) + " "+parameter_under_analysis + " "+ str(i),flush = True)

                            __run__()
                            pd.DataFrame.from_dict(scenario_from_yaml['parameters']['utility'],orient = 'index').to_csv(scenario_from_yaml['output_filenames']['changed_parameter'])
                            folder_name = "result_"+parameter_under_analysis+str(range_value_sensitivity_analysis)

                            try:
                              shutil.rmtree(folder_name)
                            except FileNotFoundError:
                              print('Folder does not exist: ' + folder_name)
                              pass
                            shutil.copytree("./output",folder_name)



       elif scenario_from_yaml['flags']['uncertainty_analysis_flag']:
              print("Uncertainty analysis")
              orig2 = parameters.copy()
              for run in range(0,scenario_from_yaml['parameters']['uncertainty_runs']):
                     print("This is run "+str(run))
                     np.random.seed(run)
                     for variables_under_analysis in list(uncertainty_df['variables']):

                            index= list(uncertainty_df['variables']).index(variables_under_analysis)
                            limit_flag = list(uncertainty_df['limit'])[index]
                            dis = list(uncertainty_df['distribution'])[index]
                            d_param1 = list(uncertainty_df['dparam1'])[index]
                            d_param2 = list(uncertainty_df['dparam2'])[index]
                            d_param3 = list(uncertainty_df['dparam3'])[index]
                            #print(variables_under_analysis)
                            for i in year:
                                   if limit_flag and i  > scenario_from_yaml['parameters']['initial_year']: #Not including the starting year so that it is same across all runs
                                          if dis == 'triangular':
                                                 parameters[variables_under_analysis][i] = np.random.triangular(d_param2,d_param1,d_param3,1)
                                          elif dis == 'uniform':
                                                 parameters[variables_under_analysis][i] = np.random.randint(d_param2,d_param3*10)/10

                     #Adjusting Mass Ratios so that they add up to 1
                     #Decision Split Point 1

                     sum_decision_point_1 = parameters['mass_ratio_mechanical_recycling'][i] + parameters['mass_ratio_chemical_recycling'][i] + parameters['mass_ratio_ppo'][i] + parameters['mass_ratio_fiber_reinforced_resin'][i]
                     parameters['mass_ratio_mechanical_recycling'][i] = parameters['mass_ratio_mechanical_recycling'][i]/sum_decision_point_1
                     parameters['mass_ratio_chemical_recycling'][i] = parameters['mass_ratio_chemical_recycling'][i]/sum_decision_point_1
                     parameters['mass_ratio_ppo'][i] = parameters['mass_ratio_ppo'][i]/sum_decision_point_1
                     parameters['mass_ratio_fiber_reinforced_resin'][i] = parameters['mass_ratio_fiber_reinforced_resin'][i]/sum_decision_point_1

                     if parameters['mass_ratio_fiber_reinforced_resin'][i] > 0.3:
                            print('Numbers chosen were not within boundary limits')
                            print('run '+str(run)+" is dropped from the analysis")

                     else:
                            #Printing the changed values
                            old_param_list = []
                            new_param_list = []
                            param_name_list = []
                            year_list = []
                            changed_parameter_df = pd.DataFrame()
                            for variables_under_analysis in list(uncertainty_df['variables']):
                                   for i in year:
                                          if limit_flag and i  > scenario_from_yaml['parameters']['initial_year']: #Not including the starting year so that it is same across all runs
                                                 old_param = orig2[variables_under_analysis][i]
                                                 print("Old parameter value "+str(old_param)+" changed to  "+str(parameters[variables_under_analysis][i]) +" " +variables_under_analysis + str(i),flush = True)
                                                 old_param_list.append(old_param)
                                                 new_param_list.append(parameters[variables_under_analysis][i])
                                                 param_name_list.append(variables_under_analysis)
                                                 year_list.append(i)

                            changed_parameter_df['parameter'] = param_name_list
                            changed_parameter_df['old_param_value'] = old_param_list
                            changed_parameter_df['new_param_value'] = new_param_list
                            changed_parameter_df['year'] = year_list
                            changed_parameter_df.to_csv(scenario_from_yaml['output_filenames']['changed_parameter'])
                            __run__()


                            folder_name = "result_uncertainty_analysis_"+str(run)

                            try:
                              shutil.rmtree(folder_name)
                            except FileNotFoundError:
                              print('Folder does not exist: ' + folder_name)
                              pass
                            shutil.copytree("./output",folder_name)
                            dir = "./output"
                            for f in os.listdir(dir):
                                   os.remove(os.path.join(dir, f))





       else:
              __run__()
              folder_name = "result_"+"mechanical_recycling"
              try:
                shutil.rmtree(folder_name)
              except FileNotFoundError:
                print('Folder does not exist: ' + folder_name)
                pass
              shutil.copytree("./output",folder_name)


