import pandas as pd
from pylca_opt_foreground import model_lci
from insitu_emission import model_lci_insitu
import os
import time
from pylca_opt_background import model_celavi_lci_background
# Background LCA runs on the USLCI after the foreground process
from pylca_background_postprocess import postprocessing, impact_calculations

class Pylca:
    """    
    The Pylca class 
    - Provides an object which stores the files names required for performing LCA calculations
    - Calls the main functions required for performing LCIA calculations

    Parameters
    ----------
    lca_results: str
        final_lcia_results.csv Stores final results. 
    
    shortcutlca: str
        lca_db.csv Stores emission factors for short cut calculations
    
    dynamic_lci: str
        elec_gen_dynamic_final.csv Inventory for dynamic electricity grid mix
    
    static_lci: str
        foreground_process_inventory.csv Process inventory for foreground activities
    
    stock: str
        stock.p Stock file to store GFRP at cement co processing plant for one year
    
    emissions_lci: str
        emissions_inventory.csv Emissions LCI inventory file. 
    
    traci_lci: str
        traci21.csv TRACI2.1 characterization factor file.
    """
    def __init__(self,
                 lca_results,
                 shortcutlca,
                 foreground_data,
                 intermediate_demand,
                 dynamic_lci,
                 electricity_grid_spatial_level,
                 static_lci,
                #  emissions_lci,
                 traci_lci,
                 lca_locations,
                 lcia_name_bridge,
                 use_shortcut_lca_calculations,
                 scenario,
                 verbose
                 ):
        
        """
        This function stores the filenames required for LCIA calculations as properties of an object. 
        
        Parameters
        ----------
        lca_results: str
            filename for the lca results file

        lcia_des : str
            Path to file that stores impact results for passing back to the
            discrete event simulation.

        shortcutlca: str
            filename for the shortcut file for improving LCA calculations

        intermediate_demand : str
            Path to file that stores final demands by year. For debugging
            purposes only.

        dynamic_lci: str
            filename for the lca inventory dependent upon time
            
        electricity_grid_spatial_level: str
            grid spatial level used for lca calculations - region or national

        static_lci: str
            filename for the lca fixed inventory 

        lci_activity_locations
            Path to file that provides a correspondence between location
            identifiers in the US LCI.

        stock: str
            filename for storage pickle variable

        emissions_lci: str
            filename for emissions inventory

        traci_lci: str
            filename for traci CF file

        use_shortcut_lca_calculations: str
            boolean flag for using lca shortcut performance improvement method
            
        substitution_rate: Dict
            Dictionary of material: sub rates for materials displaced by the
            circular component
        """
        # filepaths for files used in the pylca calculations
        self.lca_results = lca_results
        self.shortcutlca = shortcutlca
        self.foreground_data = foreground_data
        self.intermediate_demand = intermediate_demand
        self.dynamic_lci = dynamic_lci
        self.electricity_grid_spatial_level = electricity_grid_spatial_level
        self.static_lci = static_lci
        # self.emissions_lci = emissions_lci
        self.traci_lci = traci_lci
        self.lca_locations = lca_locations
        self.lcia_name_bridge = lcia_name_bridge
        self.use_shortcut_lca_calculations = use_shortcut_lca_calculations
        self.scenario = scenario
        self.verbose = verbose
        
        #This is the final LCIA results file. Its created using the append function as CELAVI runs. 
        #Thus if there is a chance it exists we need to delete it
        try:
            os.remove(self.lca_results)
            print('old lcia results file deleted')
        except FileNotFoundError:
            print('No existing results file:'+self.lca_results)

    def lca_performance_improvement(self, df, region):
        """
        This function is used to bypass optimization based pylca celavi calculations
        It reads emission factor data from previous runs stored in a file
        and performs lca rapidly

        Needs to be reset after any significant update to data

        Parameters
        ----------
        df
            shortcut lca db filename
        
        Returns
        -------

        pd.DataFrame
            DataFrame with lca calculations performed along with missing activities and processes not performed
        
        pd.DataFrame
            DataFrame without any results if file doesn't exist
        """
        try:
            db = pd.read_csv(self.shortcutlca+"_"+region+".csv")
            db = db.drop_duplicates()
            db.columns = ['year', 'process','region', 'flow name', 'emission factor kg/kg']
            df2 = df.merge(db, on = ['year','process','region'], how = 'outer',indicator = True)
            df_with_lca_entry = df2[df2['_merge'] == 'both'].drop_duplicates()
            
            
            df_with_no_lca_entry =  df2[df2['_merge'] == 'left_only']
            df_with_no_lca_entry = df_with_no_lca_entry.drop(labels = ['flow name','emission factor kg/kg','_merge'], axis = 1)
            df_with_no_lca_entry = df_with_no_lca_entry.drop_duplicates()
            

            
            df_with_lca_entry['flow quantity'] = df_with_lca_entry['p.flow.quantity'] * df_with_lca_entry['emission factor kg/kg']
            df_with_lca_entry = df_with_lca_entry[['flow name', 'flow quantity', 'year', 'process','region']]
            df_with_lca_entry2 = df_with_lca_entry[df_with_lca_entry['process'] == "PET, electricity displaced"]
            result_shortcut = impact_calculations(df_with_lca_entry,self.traci_lci)
            return df_with_no_lca_entry, result_shortcut
        
        except FileNotFoundError:
            
            print('Shortcut file not found:'+self.shortcutlca+"_"+region+".csv")        
            return df,pd.DataFrame()

    def pylca_run_main(self, df):
        """
        This function runs the individual pylca celavi functions for performing various calculations
        
        Parameters
        ----------
        df: pd.DataFrame
             Material flows from DES
        
        Returns
        -------
        pd.DataFrame
            LCIA results (also appends to csv file)
        """
        df = df[df['flow_quantity'] != 0]        
        res_df = pd.DataFrame()
        lcia_mass_flow = pd.DataFrame()
        
        df_static = pd.read_csv(self.static_lci)

        
        #The LCA needs to be done for every region separately. Thus separating the regions in the dataframe.
        regions = list(pd.unique(df['region']))
        for region in regions:

            df1 = df[df['region'] == region]
            if self.use_shortcut_lca_calculations:
                 #Calling the lca performance improvement function to do shortcut calculations. 
                 df1,result_shortcut = self.lca_performance_improvement(df1,region)

            else:                    
                 df1 = df1
                 result_shortcut = pd.DataFrame()
            if not df1.empty:

                years = list(pd.unique(df1['year']))            
                for year in years:
                    df2 = df1[df1['year'] == year]
                    processes = list(pd.unique(df2['process']))
                    for process in processes:
                        df3 = df2[df2['process'] == process]

                        time0 = time.time()
                        if self.use_shortcut_lca_calculations:
                                 #Calling the lca performance improvement function to do shortcut calculations. 
                                 df4,result_shortcut = self.lca_performance_improvement(df3,region)

                        else:                    
                                 df4 = df3
                                 result_shortcut = pd.DataFrame()
                        time0 = time.time()
                        if not df4.empty:

                            if not df_static.empty:

                                df5 = df4.merge(self.foreground_data, left_on = ['process'],right_on = ['process'])
                                df5['flow quantity'] = df5['flow quantity']*df5['p.flow.quantity']
                                df5['unit'] = df5['unit_y']
                                df6 = df5.drop(labels = ['unit_x','unit_y','flow_quantity','p.flow.quantity'], axis = 1)
                                df_without_em = df6[df6['type'] != 'emission']  
                                df_emission = df6[df6['type'] == 'emission']                    
                                df_emission['flow unit'] = df_emission['unit']
                                df_emission_a = df_emission[['flow name','flow unit','flow quantity','year','process','region']]
                                df_emission_a.to_csv("./output/insitu_emissions_intermediate_file.csv", mode = 'a')                    
                                df7= df_without_em[['flow name','flow quantity']]
                                
                                if sum(df7['flow quantity']) != 0:

                                    # model_celavi_lci() is calculating foreground processes and dynamics of electricity mix.
                                    # It calculates the LCI flows of the foreground process.
                                    res = model_lci(df7,year,process,region,df_static,self.dynamic_lci,self.electricity_grid_spatial_level,self.intermediate_demand)
                                    # model_celavi_lci_insitu() calculating direct emissions from foreground
                                    # processes.
                                    #emission = model_lci_insitu(working_df,year,process,df_emissions)
                                    
                                    if not res.empty:
                                        res = model_celavi_lci_background(res,year,process,self.lca_locations)
                                        res['region'] = region
                                        lci = postprocessing(res,df_emission_a)
                                        res = impact_calculations(lci,self.traci_lci)
                                        res_df = pd.concat([res_df,res])
                                        res_df.to_csv('./output/intermediate_results_file_lcia.csv', index = False) 
                                                                         
                                        lca_db = df2.merge(lci,on = ['year','process','region'])
                                        lca_db['emission factor kg/kg'] = lca_db['flow quantity']/lca_db['p.flow.quantity']   
                                        lca_db = lca_db[['year','process','region','flow name','emission factor kg/kg']]
                                        lca_db['year'] = lca_db['year'].astype(int)
                                        lca_db = lca_db.drop_duplicates()
                                        lca_db.to_csv(self.shortcutlca+"_"+region+".csv",
                                                      mode = 'a',
                                                      index = False,
                                                      header = False)
                                        #print('LCA shortcut added '+str(region) + " " + str(year) + " " + str(process))
                                        res_df.drop_duplicates()
                                        if self.verbose == 1:
                                            print('LCA done for '+region+" "+str(year)+" "+process)
                                    else:                                
                                        print(f'Empty dataframe returned from pylcia foreground for {year} {process}')
                        
                                else:                              
                                    print('Final demand for %s %s is zero' % (str(year), process))
                        
                        
                        else:
                            if self.verbose == 1:
                                print('Only shortcut calculations done', flush = True)            

                        if not result_shortcut.empty:
                            res_df = pd.concat([res_df,result_shortcut]) 
                            if self.verbose == 1:               
                                print(region + ' - ' + str(year) + ' - ' + process + ' - ' + ' shortcut calculations done',flush = True)
                        if self.verbose == 1: 
                            print('One set of calculations took '+str(time.time() - time0) + ' seconds', flush = True)
            
            if not result_shortcut.empty:
                res_df = pd.concat([res_df,result_shortcut]) 
                if self.verbose == 1:                
                    print(region + ' - ' + ' regional shortcut calculations done',flush = True)

        if self.verbose == 1: 
            print('Cleaning up database', flush = True)
        res_df  = res_df.drop_duplicates()
        res_df = res_df[['year','region','process','impacts','impact']]


        lcia_df = pd.read_csv(self.lcia_name_bridge)
        res_df2 = res_df.merge(lcia_df, left_on = ['impacts'], right_on = ['name'])
        res_df2['impacts'] = res_df2['corrected_name']
        res_df2['scenario'] = self.scenario
        res_df2.to_csv(self.lca_results)



        

    
           
