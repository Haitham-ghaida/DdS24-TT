# -*- coding:utf-8 -*-
"""
Created on April 12 2022

@author Julien Walzberg - Julien.Walzberg@nrel.gov

BatchRun - TPB_ABM (Theory of Planned Behavior Agent Based Modeling).
This module run batch runs of the model according to user inputs.
"""

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)

from mesa.batchrunner import batch_run
import time
import pandas as pd
from typing import Type
import numpy as np
from copy import deepcopy 

input_data = pd.read_csv('./ABM/InputDataAllStates.csv')
scenarios = input_data['scenario'].unique().tolist()

t0 = time.time()

# noinspection PyShadowingNames
# The variable parameters will be invoke along with the fixed parameters
# allowing for either or both to be honored.
def run_batch(variable_params: dict, number_steps: int,
              num_core: int) -> Type[pd.DataFrame]:
    """
    Set up the batch run.
    :param variable_params: variable parameters from which the batch run
    needs to iterate through.
    :param number_steps: number of steps for each simulation.
    :param num_core: number of core to use in parallel (1 core = 1 run of
    the batch run) to speed up the batch run.
    :return: a panda data frame containing outputs of all simulations.
    """
    # Model is imported here to avoid errors due to a circular import
    from TPB_ABM import TheoryPlannedBehaviorABM
    tot_run = 1
    
    
    for var_p in variable_params.values():
        if type(var_p) is list:
            tot_run *= len(var_p)
        else:
            pass
    print("Total number of run:", tot_run)
    run_data = batch_run(
        TheoryPlannedBehaviorABM,
        parameters=variable_params,
        iterations=1,
        max_steps=number_steps,
        number_processes=num_core,
        data_collection_period=4)
    run_data_df = pd.DataFrame(run_data)
    return run_data_df

def run_func(years: int, reps = 1, sobol: bool = False, 
             intervention_scenario: str = 'baseline') -> None:
    """
    Runs the run batch --> run the ABM
    :param years: the number of years in the simulation period.
    :param reps: number of replicates for a given experiment or scenario.
    :param intervention_scenario: scenario of intervention(s) to run.
    :return: none
    """
    
    year_period = years
    replicates = reps
    behavioral_factors_update = 12
    steps = year_period * behavioral_factors_update
        
    if not sobol:
        
        variable_params = {
            "seed": list(range(replicates)),
            "sobol": sobol,
            "scenario": scenarios, 
            "intervention_scenario": [intervention_scenario]}
        run_data_df = run_batch(
            variable_params=variable_params,
            number_steps=steps,
            num_core=6)

        run_data_df = pd.concat(
            [run_data_df.drop(['Adoption rates'], axis=1),
            run_data_df['Adoption rates'].apply(pd.Series)], axis=1)
        list_gb = ['Year']
        for key in variable_params.keys():
            list_gb.append(key)
        run_data_df = run_data_df.groupby(list_gb).mean()
        
        run_data_df.to_csv('../PCEM/input/ResultsBatchRun.csv')
        
        #run_data_df.to_csv("ResultsBatchRun.csv")
        
    else:
        from SALib.sample import saltelli 
        print("Sobol Sampling")
        
        list_variables = ["sn","pbc","kn","ds", "att", "bin"]
        
        problem = {'num_vars': 6,'names': [
            "sn","pbc","kn","ds", "att", "bin"],
            'bounds': [[0, 1], [0, 1], [0,1], [-1,0], [0,1], [0,1]]}

        x = saltelli.sample(problem, 75)

        lower_bound_row = np.array([0, 0, 0, -1, 0, 0])
        x = np.vstack((x, lower_bound_row))
        upper_bound_row = np.array([1, 1, 1, 0, 1, 1])
        x = np.vstack((x, upper_bound_row))
        baseline_row = np.array([0.5, 0.5, 0.5, -0.5, 0.5, 0.5])
        x = np.vstack((x, baseline_row))

        for x_i in range(x.shape[1]):
            lower_bound = deepcopy(baseline_row)
            bounds = problem['bounds'][x_i]
            if lower_bound[x_i] != bounds[0]:
                lower_bound[x_i] = bounds[0]
                x = np.vstack((x, lower_bound))
                upper_bound = deepcopy(baseline_row)
            if upper_bound[x_i] != bounds[1]:
                upper_bound[x_i] = bounds[1]
                x = np.vstack((x, upper_bound))
            
                    
        appended_data = []
        for i in range(x.shape[0]):
            print("Sobol matrix line: ", i, " out of ", x.shape[0])
            calib_param = x[i][0] 
            calib_param_2 = x[i][1] 
            calib_param_3 = x[i][2] 
            calib_param_4 = x[i][3] 
            calib_param_5 = x[i][4]
            calib_param_6 = x[i][5]
            # calib_param_7 = x[i][6]
        
            
            variable_params = {
                "seed": list(range(replicates)),
                "sobol": sobol,
                "scenario": scenarios,
                "calib_param": [calib_param],
                "calib_param_2": [calib_param_2],
                "calib_param_3": [calib_param_3],
                "calib_param_4": [calib_param_4],
                "calib_param_5": [calib_param_5],
                "calib_param_6": [calib_param_6],
                "calib_param_7": 0}

            run_data_df = run_batch(variable_params = variable_params,
                                    number_steps = steps, num_core = 6)
            
            run_data_df = pd.concat(
            [run_data_df.drop(['Adoption rates'], axis=1),
            run_data_df['Adoption rates'].apply(pd.Series)], axis=1)
            list_gb = ['Year']
            for key in variable_params.keys():
                list_gb.append(key)
            run_data_df = run_data_df.groupby(list_gb).mean()
        
            for k in range(x.shape[1]):
                run_data_df["x_%s" % k] = x[i][k]
            appended_data.append(run_data_df)
        appended_data = pd.concat(appended_data)
        appended_data.to_csv("SobolBatchRun_1013.csv")
            
            
    t1 = time.time()
    print(t1 - t0)
    print("Done!")
