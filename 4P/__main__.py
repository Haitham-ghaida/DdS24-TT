if __name__ == '__main__':

       import pandas as pd
       import numpy as np
       import sys
       import glob,os
       import shutil
       sys.path.append(os.path.join(os.path.dirname(__file__), 'code'))
       from flow_model import PlasticSD
       import logging
       import yaml

    



       scenario_from_yaml = {}
       with open('./input/options_files/' + 'singleyearanalysis' + '.yaml') as file:
              scenario_from_yaml = yaml.safe_load(file)

       #Creating the time array for simulation
       year = list(range(scenario_from_yaml['parameters']['initial_year'], scenario_from_yaml['parameters']['final_year'] + 1))
       year = [2020]   

       # read input parameters file, and define mrf_equipment_efficiency from that
       parameters = pd.read_csv('./input/scenario_files/'+'mrf_equipment_efficiency'+'.csv')
       mrf_equipment_efficiency = parameters[['year','disc_screen1 cardboard', 'disc_screen1 paper', 'disc_screen2 cardboard',
              'disc_screen2 film', 'disc_screen2 paper', 'eddy aluminum', 'eddy glass',
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


       mrf_equipment_efficiency_dic = {}
       mrf_equipment_efficiency = mrf_equipment_efficiency.reset_index().drop_duplicates()
       for index,row in mrf_equipment_efficiency.iterrows():
            mrf_equipment_efficiency_dic[row['year-source-targetmaterial']] = row['efficiency']

       recycle_stream_material= ['aluminum','cardboard','iron','glass','hdpe','paper','pet','film','other']
       unit_ops = ['vacuum','disc_screen1','glass_breaker','disc_screen2','nir_pet','nir_hdpe','magnet','eddy']
       for y in year:
           for r in recycle_stream_material:
            for u in unit_ops:
                try:
                    ck = mrf_equipment_efficiency_dic[str(y)+' '+u+' '+r]
                except:
                    mrf_equipment_efficiency_dic[str(y)+' '+u+' '+r] = 0
                
       mrf_equipment_efficiency = pd.DataFrame.from_dict(mrf_equipment_efficiency_dic,orient='index')
       mrf_equipment_efficiency['efficiency'] = mrf_equipment_efficiency[0]

       
       parameters = parameters.set_index('year')


       #Cleaning the output directory
       r = glob.glob('./output/*')
       for i in r:
              os.remove(i)


       recycle_stream_material= ['aluminum','cardboard','iron','glass','hdpe','paper','pet','film','other']
           
       outputs = ['vacuum','film_bale','cardboard_bale','glass_bale','pet_bale','hdpe_bale','iron_bale','aluminum_bale']
       
       unit_ops = ['vacuum','disc_screen1','glass_breaker','disc_screen2','nir_pet','nir_hdpe','magnet','eddy']
           
       flow = {}
       
       reg_df_data = pd.read_csv('./input/core_data_files/State_County.csv')
       #reg_df_data = reg_df_data.sample(20)
       reg_df_data = reg_df_data[reg_df_data['State_County'] == 'Maryland_Dorchester']

              
       # Film Bale
       yr_list = []
       mat_list = []
       value_list = []
       loc_list = []
       bale_list = []
       df = pd.DataFrame()

       electricity_df_result = pd.DataFrame()
       for index,row in reg_df_data.iterrows():

           for mat in recycle_stream_material:
               
               data_df = pd.read_csv('./input/core_data_files/projected_by_linear_model_to_2050/'+mat+'projected_amounts_to_relog_grouped_2050.csv')
               data_df = data_df[data_df['State_County'] == row['State_County'] ]
               for y in year:
                   if len(data_df) > 1:
                       logging.warning('Issue with dataframe size')
                   else:
                       data_df = data_df.reset_index() 
                   
                   flow[(y,mat,'consumer','vacuum')] = float(data_df.loc[0,str(float(y))])
                   
                   
                   
           scenario = str(pd.unique(parameters['scenario'])[0])
    
           reg_df = [row['State_County']]
           #logging.info(reg_df)
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
       


           for o_bales in outputs:
               for key in flow_result:
                   if key[3] == o_bales:
                       yr_list.append(key[0])
                       mat_list.append(key[1])
                       value_list.append(flow_result[key])
                       bale_list.append(o_bales)
                       loc_list.append(row['State_County'])
                       
                       
           df_energy = pd.read_csv('./input/core_data_files/mrf_electricity.csv') 
           
           ops_list = []
           value_list_elec = []
           for u in unit_ops:
               total = 0
               for key in flow_result:
                   
                   if key[3] == u:
                       total = total + flow_result[key]
               print(total,u)    
               ops_list.append(u)
               value_list_elec.append(total)




           total_mrf_flow = 0
           for key in flow_result:
            
            if key[3] == 'vacuum':
                total_mrf_flow = total_mrf_flow + flow_result[key]

           time = total_mrf_flow/30
           electricty_df = pd.DataFrame()
           electricty_df['ops_list'] = ops_list
           electricty_df['total_flow'] = value_list_elec
           electricty_df['time'] = time 
           
           df_energy = df_energy.merge(electricty_df,left_on=['Equipment'],right_on = ['ops_list'])
           df_energy['electricity kwh'] = df_energy['Rated motor capacity (kW)']/df_energy['Fraction of equipment capacity utilized ']*df_energy['time']
           df_energy['diesel_l'] = 10*total_mrf_flow
           df_energy['region'] = row['State_County']
           electricity_df_result = pd.concat([electricity_df_result,df_energy])
           
         
               
       df['location'] = loc_list
       df['year'] = yr_list
       df['bale'] = bale_list
       df['material'] = mat_list
       df['value'] = value_list
       
       
       df.to_csv('./output/bale_output.csv')
       electricity_df_result.to_csv('./output/electricity_output.csv')
       

import pandas as pd


