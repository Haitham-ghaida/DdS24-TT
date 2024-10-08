if __name__ == '__main__':

       import pandas as pd
       import numpy as np
       import sys
       import glob,os
       import shutil
       sys.path.append(os.path.join(os.path.dirname(__file__), 'code'))
       from flow_model_new import PlasticSD
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
       year = [2020]
       #Cleaning the output directory
       r = glob.glob('./output/*')
       for i in r:
              os.remove(i)


       recycle_stream_material= ['aluminum','cardboard','iron','glass','hdpe','paper','pet','film','other']

       flow = {}
       loc = "South Carolina_Abbeville"
       for mat in recycle_stream_material:
           
           df = pd.read_csv('./input/projected_by_linear_model_to_2050/'+mat+'projected_amounts_to_relog_grouped_2050.csv')
           df = df[df['State_County'] == loc ]
           for y in year:
           
               flow[(y,mat,'consumer','vacuum')] = float(df.loc[0,str(float(y))])
               
               
               
       scenario = str(pd.unique(parameters['scenario'])[0])

       reg_df = [loc]
       #Creating the flow model object
       psd =  PlasticSD(reg_df = reg_df,
                        flow = flow,
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
       flow_result = psd.main()
       
       
       # Film Bale
       yr_list = []
       mat_list = []
       value_list = []
       loc_list = []
       df = pd.DataFrame()
       
       outputs = ['film_bale']
       
       for o_bales in outputs:
           for key in flow_result:
               if key[3] == o_bales:
                   print(key)
                   yr_list.append(key[0])
                   mat_list.append(key[1])
                   value_list.append(flow_result[key])
                   loc_list.append(loc)
               
               
       df['location'] = loc_list
       df['year'] = yr_list
       df['bale'] = o_bales
       df['material'] = mat_list
       df['value'] = value_list
       
       
       df.to_csv('bale_output.csv')
       
       sys.exit(0)
           




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

       __run__()
       folder_name = "result_"+"mechanical_recycling"
       try:
         shutil.rmtree(folder_name)
       except FileNotFoundError:
         print('Folder does not exist: ' + folder_name)
         pass
       shutil.copytree("./output",folder_name)


