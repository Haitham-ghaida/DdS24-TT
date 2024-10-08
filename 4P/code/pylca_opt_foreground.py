import warnings
import pandas as pd
import numpy as np
import sys
import multiprocessing
import time
import os

#Reading in static and dynamics lca databases
#We are integrating static lca with dynamics lca over here. 
def preprocessing(year,state,df_static,dynamic_lci_filename,electricity_grid_spatial_level):

    """
    This function preprocesses the process inventory before the LCA calculation. It joins the dynamic LCA
    inventory with the static LCA inventory. Removes dummy processes with no output from the inventory. 

    Parameters
    ----------
    year : str
         year of LCA calculation
    state : str
         state of Facility
    df_static : pd.DataFrame
         lca inventory static 
    dynamic_lci_filename: str
         filename for the dynamic inventory   
    
    Returns
    -------
    pd.DataFrame
        cleaned process inventory merged with dynamic data
    pd.DataFrame    
        inventory with no product flows

    """
    
    #Reading in dynamics LCA databases
    df_dynamic = pd.read_csv(dynamic_lci_filename) 
    if electricity_grid_spatial_level == 'state':
        df_dynamic_year = df_dynamic[(df_dynamic['year'] == year) & (df_dynamic['state'] == state)]
        df_dynamic_year = df_dynamic_year.drop('state',axis = 1)
    else:
        df_dynamic_year = df_dynamic[(df_dynamic['year'] == year)]
    
    frames = [df_static,df_dynamic_year]
    df = pd.concat(frames)
    df_input = df[df['input'] == True]
    df_output = df[df['input'] == False]
    df_input.loc[:,'value'] = df_input.loc[:,'value']  * (-1)
    #process_df = df_output
    df = pd.concat([df_input,df_output])
    process_input_with_process  =  pd.unique(df_output['product'])
    df['indicator'] = df['product'].isin(process_input_with_process)   
    process_df = df[df['indicator'] == True] 
    df_with_all_other_flows = df[df['indicator'] == False]    
    del process_df['indicator']
    del df_with_all_other_flows['indicator']   
    #df_with_all_other_flows = df_input
    process_df.loc[:,'value'] = process_df.loc[:,'value'].astype(np.float64)
    return process_df,df_with_all_other_flows


def solver(tech_matrix,F,process, df_with_all_other_flows):

    """
    This function houses the optimizer for solve Xs = F. 
    Solves the Xs=F equation. 
    Solves the scaling vector.  

    Parameters
    ----------
    tech_matrix : numpy matrix
         technology matrix from the process inventory
    F : vector
         Final demand vector 
    process: str
         filename for the dynamic inventory   
    df_with_all_other_flows: pd.DataFrame
         lca inventory with no product flows

    
    Returns
    -------
    pd.DataFrame
        LCA results
    """

    tm= tech_matrix.to_numpy()
    det = np.linalg.det(tm)
    scv = np.linalg.solve(tm, F)

    scaling_vector = pd.DataFrame()
    scaling_vector['process'] = process
    scaling_vector['scaling_factor'] = scv

    results_df = df_with_all_other_flows.merge(scaling_vector, on=['process'], how='left')

    results_df['value'] = abs(results_df['value']) * results_df['scaling_factor']
    results_df = results_df[results_df['value'] > 0]
    results_df = results_df.fillna(0)
    results_total = results_df.groupby(by=['product', 'unit'])['value'].agg(sum).reset_index()

    return results_total


def electricity_corrector_before20(df):
    """
    This function is used to replace pre 2020 electricity flows with the base electricity mix flow
    in the USLCI inventory Electricity, at Grid, US, 2010'    

    Parameters
    ----------
    df: pd.DataFrame
        process inventory

    Returns
    -------
    pd.DataFrame
        process inventory with electricity flows before 2020 converted to the base electricity
        mix flow in USLCI. 
    """
    df = df.replace(to_replace='electricity', value='Electricity, at Grid, US, 2010')
    return df


def runner(tech_matrix,F,yr,j,final_demand_scaler,process,df_with_all_other_flows,intermediate_demand_filename):
    
    """
    Calls the optimization function and arranges and stores the results into a proper pandas dataframe. 
    
    Parameters
    ----------
    tech matrix: pd.Dataframe
         technology matrix built from the process inventory. 
    F: final demand series vector
         final demand of the LCA problem
    yr: int
         year of analysis
    i: int
         facility ID
    j: str
        stage
    k: str
        material
    final_demand_scaler: int
        scaling variable number to ease optimization
    process: list
        list of processes included in the technology matrix
    df_with_all_other_flows: pd.DataFrame
        Dataframe with flows in the inventory which do not have a production process. 

    Returns
    -------
    pd.DataFrame
        Returns the final LCA reults in a properly arranged dataframe with all supplemental information

    """

    res = pd.DataFrame()
    res = solver(tech_matrix, F, process, df_with_all_other_flows)        
    res['value'] = res['value'] * final_demand_scaler
    if not res.empty:

       res.loc[:, 'year'] = yr
       res.loc[:, 'stage'] = j
       res = electricity_corrector_before20(res)
       # Intermediate demand is not required by the framewwork, but it is useful
       # for debugging.    
       return res
    
    else:        
       print(f"Calculation failed  for {j} in {yr}")





def model_lci(f_d,yr,stage,region,df_static,dynamic_lci_filename,electricity_grid_spatial_level,intermediate_demand_filename):

    """
    Main function of this module which received information from DES interface and runs the suppoeting optimization functions. 
    Creates the technology matrix and the final demand vector based on input data. 
    Performs necessary checks before and after the LCA optimization calculation. 
    
    Parameters
    ----------
    f_d: pd.Dataframe
      Dataframe from DES interface containing material flow information
    yr: int
      year of analysis
    fac_id: int
      facility id
    stage: str
      stage of analysis
    material: str
      material of LCA analysis
    df_static: pd.Dataframe
      static foreground LCA inventory
    dynamic_lci_filename: str
      filename for the dynamic LCA inventory
    
    Returns
    -------
    pd.DataFrame
        Final LCA results in the form of a dataframe after performing after calculation checks

    """

    f_d = f_d.drop_duplicates()
    f_d = f_d.dropna()
    # Running LCA for all years as obtained from CELAVI
    #Incorporating dynamics lci database
    process_df,df_with_all_other_flows = preprocessing(int(yr),region,df_static,dynamic_lci_filename,electricity_grid_spatial_level)
    #Creating the technoology matrix for performing LCA caluclations
    tech_matrix = process_df.pivot_table(index = 'product', columns = 'process', values = 'value' )
    tech_matrix = tech_matrix.fillna(0)
    # This list of products and processes essentially help to determine the indexes and the products and processes
    # to which they belong.
    products = list(tech_matrix.index)
    process = list(tech_matrix.columns)
    product_df = pd.DataFrame(products)
    final_dem = product_df.merge(f_d, left_on=0, right_on='flow name', how='left')
    final_dem = final_dem.fillna(0)
    chksum = np.sum(final_dem['flow quantity'])
    if chksum == 0:
        print('LCA inventory does not exist for %s %s %s' % (str(yr), stage, region))
        return pd.DataFrame()
    
    else:
        #To make the optimization easier
        if chksum > 100000:
            final_demand_scaler = 10000
        elif chksum > 10000:
            final_demand_scaler = 1000
        elif chksum > 100:
            final_demand_scaler = 10
        else:
            final_demand_scaler = 1
            
        F = final_dem['flow quantity']
        # Dividing by scaling value to solve scaling issues
        F = F / final_demand_scaler
    
        res = runner(tech_matrix, F, yr, stage, final_demand_scaler , process, df_with_all_other_flows,intermediate_demand_filename)
        
        if len(res.columns) != 5:
            
            print(f'model_celavi_lci: res has {len(res.columns)}; needs 5 columns',
                  flush=True)
            return pd.DataFrame(
                columns=['flow name', 'unit', 'flow quantity',
                         'year', 'stage']
            )
        else:
            res.columns = ['flow name', 'unit', 'flow quantity', 'year', 'stage']

            if not res.empty:
                if res.isnull().values.any():
                    print('Process or product information missing in the process adder',flush=True)
                    sys.exit(1)
                else:
                    #No issues
                    pass
            else:
                print('Dataframe empty. Something went wrong. Please check',flush=True)
                sys.exit(1)

            res.to_csv("./output/intermediate_demand_of_foreground.csv", mode = 'a', index = False)
            return res
