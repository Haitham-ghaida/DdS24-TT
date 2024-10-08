# -*- coding:utf-8 -*-
"""
Created on October 28 2021
@author Julien Walzberg - Julien.Walzberg@nrel.gov
TPB_ABM (Theory of Planned Behavior Agent Based Modeling)
This module contains the model class that creates and activates agents. It also
contains the agent class and code lines to run the model. The module also
defines inputs (default values can be changed by user) and collects outputs
(i.e., results).
"""

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)

from typing import Any, Callable, Tuple, Type
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import NetworkGrid
from mesa.datacollection import DataCollector
import networkx as nx
import random
from scipy.stats import truncnorm
import numpy as np
import pandas as pd
from copy import deepcopy
from functools import reduce
import operator
from TPB_ABM_BatchRun import input_data


class TheoryPlannedBehaviorABM(Model):
    def __init__(self,
                 seed: int = 0,
                 sobol: bool = False,
                 calib_param: float = 1,
                 calib_param_2: float = 1,
                 calib_param_3: float = 1, 
                 calib_param_4: float = 1, 
                 calib_param_5: float = 1, 
                 calib_param_6: float = 1, 
                 calib_param_7: float = 1, 
                 input_data: Type[pd.DataFrame] = input_data,
                 scenario: str = 'baseline',
                 intervention_scenario: str = 'baseline',
                 intervention_period: int = 10,
                 social_network_parameters: dict = {
                     "average_degree": 10, "rewiring_probability": 0.1},
                 year_period: int = 30,
                 behavioral_factors_update: int = 12,
                 decision_frequency: int = 365,
                 habit_formation: dict = {"threshold": {
                     "mean": 69, 'standard_deviation': 47, 'min': 18,
                     'max': 254}, "high_prob_habit": (0.7, 0.9),
                     "gap_requirement_fraction": 0.3},
                 tpb_weights: dict = {
                     'err': {'mode': 1, 'min': 0.99, 'max': 1.01},
                     'att': {'mode': 0.34, 'min': 0.29, 'max': 0.39},
                     'sn': {'mode': 0.33, 'min': 0.23, 'max': 0.42},
                     'pbc': {'mode': 0.39, 'min': 0.32, 'max': 0.44},
                     'kn': {'mode': 0.20, 'min': 0.14, 'max': 0.26},
                     'pr': {'mode': 0.41, 'min': 0.25, 'max': 0.54},
                     'ht': {'mode': 0.12, 'min': 0.06, 'max': 0.17},
                     'bin': {'mode': 0.24, 'min': 0.16, 'max': 0.32},
                     'ds': {'mode': -0.11, 'min': -0.17, 'max': -0.05},
                     'ns': {'mode': -0.17, 'min': -0.35, 'max': 0.02}},
                 agent_outputs: bool = False
                 ) -> None:
        """
        Initiates model from input data.
        :param seed: number used to initialize the random generator.
        :param sobol: switch Sobol analysis on or off.
        :param calib_param: parameter used to calibrate the model.
        :param calib_param_2: parameter used to calibrate the model.
        :param input_data: file containing input data related to agents'
        behaviors.
        :param scenario: scenario of "input_data" to run.
        :param intervention_scenario: scenario of intervention(s) to run.
        :param intervention_period: period (in years) for which the
        intervention is applied.
        :param social_network_parameters: characteristics of the social
        network (in real social network, the average degree is often [5, 10];
        if rewiring prob: 0 it yields a regular lattice, 1 it yields a random
        network, [0.01, 0.1] it yields a small world network).
        :param year_period: number of years in the simulation period.
        :param behavioral_factors_update: frequency (per year) that behavioral
        factors get updated.
        :param decision_frequency = frequency (per year) that a decision
        regarding plastic waste is made in the household.
        :param behavior_parameters: parameters characterizing the different
        behaviors (i.e., choices).
        :param habit_formation: repetition threshold for a new behavior to
        become habitual.
        :param tpb_weights: weights of variables in the TPB model.
        :param agent_outputs: if True, the model provides simulation outputs at
        the agent level.
        """
        # Assign inputs to instance variables
        self.seed = seed
        self.sobol = sobol
        self.calib_param = calib_param
        self.calib_param_2 = calib_param_2
        self.calib_param_3 = calib_param_3
        self.calib_param_4 = calib_param_4
        self.calib_param_5 = calib_param_5
        self.calib_param_6 = calib_param_6
        self.calib_param_7 = calib_param_7
        
        if sobol:
            tpb_weights: dict = {
                        'err': {'mode': 1, 'min': 0.99, 'max': 1.01},
                        'att': {'mode': self.calib_param_5,
                                'min': self.calib_param_5-1E-6,
                                'max': self.calib_param_5+1E-6},
                        'sn': {'mode': self.calib_param,
                               'min': self.calib_param-1E-6,
                               'max': self.calib_param+1E-6},
                        'pbc': {'mode': self.calib_param_2,
                                'min': self.calib_param_2-1E-6,
                                'max': self.calib_param_2+1E-6},
                        'kn': {'mode': self.calib_param_3,
                               'min': self.calib_param_3-1E-6,
                               'max': self.calib_param_3+1E-6},
                        'pr': {'mode': 0.41, 'min': 0.25, 'max': 0.54},
                        'ht': {'mode': 0.12, 'min': 0.06, 'max': 0.17},
                        'bin': {'mode': self.calib_param_6,
                                'min': self.calib_param_6-1E-6,
                                'max': self.calib_param_6+1E-6},
                        'ds': {'mode': self.calib_param_4,
                               'min': self.calib_param_4-1E-6,
                               'max':self.calib_param_4+1E-6},
                        'ns': {'mode': -0.17, 'min': -0.35, 'max': 0.02}}
            
            habit_formation: dict = {"threshold": {
                        "mean": 69, 'standard_deviation': 75, 'min': 18,
                        'max': 254}, "high_prob_habit": (
                            self.calib_param_7, self.calib_param_7 + 1E-6),
                        "gap_requirement_fraction": 0.3}
                
            list_states: list = ['Alabama', 'Arizona', 'Arkansas', 
                                'California', 'Colorado', 'Connecticut', 
                                'Delaware', 'Florida', 'Georgia', 'Hawaii',
                                'Idaho', 'Illinois', 'Indiana', 'Iowa',
                                'Kansas', 'Kentucky', 'Louisiana', 'Maine',
                                'Maryland', 'Massachusetts', 'Michigan', 
                                'Minnesota', 'Mississippi', 'Missouri',
                                'Montana', 'Nebraska', 'Nevada',
                                'New Hampshire', 'New Jersey', 'New Mexico', 
                                'New York', 'North Carolina', 'North Dakota',
                                'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania',
                                'Rhode Island', 'South Carolina',
                                'South Dakota', 'Tennessee', 'Texas', 'Utah',
                                'Vermont', 'Virginia', 'Washington',
                                'West Virginia','Wisconsin', 'Wyoming']
        
            social_network_parameters = {"average_degree": 10,
                                         "rewiring_probability": 0.1}
        
        self.scenario = scenario

        self.intervention_scenario = intervention_scenario
        self.intervention_period = intervention_period

        self.input_data = deepcopy(input_data)
        
        self.input_data = input_data[
            input_data['scenario'] == self.scenario].drop('scenario', 1)

        
        # self.input_data = input_data[(input_data['scenario'] == 'Arizona') |
        # (input_data['scenario'] == 'Connecticut') |
        # (input_data['scenario'] == 'Iowa') |
        # (input_data['scenario'] == 'Oregon') |
        # (input_data['scenario'] == 'Alabama')]
    
        self.input_data.to_csv("checkingInput.csv")
        

        self.social_network_parameters = social_network_parameters
        self.year_period = year_period
        self.behavioral_factors_update = behavioral_factors_update
        self.decision_frequency = decision_frequency
        self.habit_formation = deepcopy(habit_formation)
        self.tpb_weights = deepcopy(tpb_weights)
        self.agent_outputs = agent_outputs

        # Initialize random seed
        random.seed(self.seed)
        # noinspection PyTypeChecker
        np.random.seed(self.seed)
        self.reset_randomizer(self.seed)

        # Yearly changes from intervention scenario
        self.intervention_scenario_targets = \
            self.intervention_scenario_targets_setup(
                self.intervention_scenario)

        # creates model variables
        self.running = True  # required for batch runs
        self.clock = 0
        self.year = 0
        # A subset of the input_data data frame is converted to a dictionary
        # and taken as a **kwarg argument to draw the number of agents from a
        # truncated normal distribution (it only uses the mean, median, min
        # and max from the input data dictionary)
        self.num_agents = int(self.trunc_normal_distrib_draw(
            1, **self.subset_dic_from_dataframe(
                self.input_data, True, [('behavior', 'trash')],
                ['mean', 'standard_deviation', 'min', 'max'],
                'characteristics')['households']))
        self.number_steps = self.year_period * self.behavioral_factors_update
        self.decisions_per_step = round(
            self.decision_frequency / self.behavioral_factors_update)
        self.behavior_parameters = [self.subset_dic_from_dataframe(
            self.input_data, True, [('behavior', x)], [], 'characteristics')
                for x in list(self.input_data['behavior'].unique())]
        
        self.tpb_weights = {k: np.random.triangular(
            v['min'], v['mode'], v['max'], None) for k, v in
            self.tpb_weights.items()}
        
        self.bhvr_charac_distrib = \
            self.distribute_agent_characteristics_in_pop(
                list(self.tpb_weights.keys()), self.trunc_normal_distrib_draw,
                self.dic_cumulative_frequencies, self.roulette_wheel_choice,
                self.behavior_parameters, self.num_agents, self.tpb_weights)
        # Initialize dictionaries containing zeros as variables for the
        # collection of outputs
        self.behavior_adoption = dict.fromkeys(
            [x['name']['strings'] for x in self.behavior_parameters], 0)
        self.cum_behavior_adoption = dict.fromkeys(
            [x['name']['strings'] for x in self.behavior_parameters], 0)
        self.yearly_adoption_rates = dict.fromkeys(
            [x['name']['strings'] for x in self.behavior_parameters], 0)

        # Create agents, the social network, and the schedule; to avoid errors,
        # when building the social network, the minimum between the number of
        # agents and the average degree of the graph
        
        self.social_network = nx.watts_strogatz_graph(
            self.num_agents,
            min(self.num_agents,
                self.social_network_parameters['average_degree']),
                self.social_network_parameters['rewiring_probability'],
            seed=random.seed(self.seed))
        
        self.grid = NetworkGrid(self.social_network)
        self.schedule = RandomActivation(self)
        for node in self.social_network.nodes():
            a = DecisionMakingAgent(node, self)
            self.schedule.add(a)
            self.grid.place_agent(a, node)

        # Create data collectors
        self.model_reporters = {
            "Seed": "seed",
            "Year": "year",
            "Behavior adoption": "behavior_adoption",
            "Adoption rates": "yearly_adoption_rates"}
        self.agent_reporters = {"Behavior adoption": "adopted_behavior"}
        if agent_outputs:
            self.datacollector = DataCollector(
                model_reporters=self.model_reporters,
                agent_reporters=self.agent_reporters)
        else:
            self.datacollector = DataCollector(
                model_reporters=self.model_reporters)

    # Init methods
    # ------
    def distribute_agent_characteristics_in_pop(
        self, factor_names: list, distribution: Type[classmethod],
        dic_cumulative_frequencies: Type[classmethod],
        roulette_wheel_choice: Type[classmethod], behavior_parameters: dict,
            num_choices: int, tpb_weights: dict) -> dict:
        """
        Distributes agents' characteristics within the population.
        :param factor_names: the names of the characteristics of which values
        need to be distributed within the agent population.
        :param distribution: the distribution method chosen for the
        characteristic.
        :param distribution: the distribution to use to assign the
        characteristic within th agents population.
        :param dic_cumulative_frequencies: a function to set up a dictionary
        containing cumulative frequencies of its keys (as values).
        :param roulette_wheel_choice: a function to randomly (or not) draw
        values according to their frequencies.
        :param behavior_parameters: parameters used in the distribution for the
        characteristic "factor_name".
        :param num_choice: number of draws from the roulette wheel (typically
        num_choice would be the size of the agent population).
        :param tpb_weights: dictionary containing weights of the decision
        model.
        :return: a dictionary containing lists of characteristics to distribute
        to the agents.
        """
        bhvr_charac_distrib = {}
        for factor_name in factor_names:
            characteristic_distribution = {}
            agent_proportions = {}
            for behavior in behavior_parameters:
                # Distribution parameters of the characteristic presence (e.g.,
                # "1", "recycling" or a value) needs to be given (and not the
                # distribution parameters for the characteristic absence
                # (e.g., "0", "trash" or a value))
                charac_distrib = distribution(1, **behavior[factor_name])
                value_absence, value_presence, f_based_distrib = \
                    self.charac_value_computation(behavior, factor_name,
                                                  tpb_weights)
                # Distribution treatment is different depending on input data
                if f_based_distrib is None:
                    if behavior[factor_name]['independent_charac']:
                        # The lines below build a list of value_absence and
                        # value_presence (e.g., 0 and 1) with their frequencies
                        # determined from the input data (e.g., 84% and 16%)
                        agent_proportions = {value_absence: 1 - charac_distrib,
                                             value_presence: charac_distrib}
                        cum_prop = dic_cumulative_frequencies(
                            agent_proportions)
                        list_charac = roulette_wheel_choice(
                            cum_prop, num_choices, False)
                        characteristic_distribution[behavior['name'][
                            'strings']] = list_charac
                    else:
                        agent_proportions[value_presence] = charac_distrib
                elif f_based_distrib == 'truncnorm':
                    characteristic_distribution[
                        behavior['name']['strings']] = value_presence
                else:
                    pass  # placeholder for other functions
            if not behavior[factor_name]['independent_charac']:
                cum_prop = dic_cumulative_frequencies(agent_proportions)
                list_charac = roulette_wheel_choice(cum_prop, num_choices,
                                                    False)
                for behavior in behavior_parameters:
                    characteristic_distribution[behavior['name'][
                        'strings']] = list_charac
            bhvr_charac_distrib[factor_name] = characteristic_distribution
        return bhvr_charac_distrib

    def charac_value_computation(self, behavior: dict,
                                 factor_name: str,
                                 tpb_weights: dict) -> Tuple[Any, Any, Any]:
        """
        Determines values to distribute within the population.
        :param behavior: dictionary of characteristics for the behavior.
        :param factor_name: characteristic from which values need to be be
        distributed within the population.
        :param tpb_weights: dictionary containing weights of the decision
        model.
        return: values to distribute.
        """
        f_based_distrib = None
        try:
            value_absence = float(behavior[factor_name]['value_absence'])
            value_presence = float(behavior[factor_name]['value_presence'])
        except ValueError:
            value_absence = behavior[factor_name]['value_absence']
            value_presence = behavior[factor_name]['value_presence']
            # If values are determined with a function, this code handles it
            function_based_value = ['function_based_']
            if any(x in value_absence or x in value_presence for x in
                   function_based_value):
                if value_presence.replace(function_based_value[0], '') == \
                    'truncnorm' or value_absence.replace(
                        function_based_value[0], '') == 'truncnorm':
                    if tpb_weights[factor_name] < 0:
                        behavior[factor_name]['mean'] = behavior[
                            factor_name]['max'] - behavior[factor_name]['mean']
                    value_presence = value_absence = \
                        self.trunc_normal_distrib_draw(
                            self.num_agents, **behavior[factor_name])
                    f_based_distrib = 'truncnorm'
                else:
                    raise Exception('Function does not exist')
        if tpb_weights[factor_name] < 0:
            temp_value = deepcopy(value_presence)
            value_presence = value_absence
            value_absence = temp_value
        if not behavior[factor_name]['independent_charac']:
            value_absence = None
        # If f_based_distrib is not None, the subsequent treatment of
        # value_absence and value_presence will be different
        return value_absence, value_presence, f_based_distrib

    def intervention_scenario_targets_setup(
            self, intervention_scenario: str) -> dict:
        """
        Initialize different intervention scenarios targets to model's inputs,
        i.e., define targeted values for behavioral factors according to a
        given scenario.
        :param intervention_scenario: a dictionary containing initial values
        for parameters characterizing the intervention scenario.
        """
        intervention_scenario_targets = {'recycling': {}, 'trash': {},
                                         'wishcycling': {}}
        if intervention_scenario == 'scn1_ds&bin':
            intervention_scenario_targets['recycling']['ds'] = 0
            intervention_scenario_targets['wishcycling']['ds'] = 0
        elif intervention_scenario == 'scn2_kn_r':
            intervention_scenario_targets['recycling']['kn'] = 1
            intervention_scenario_targets['recycling']['att'] = 1
        elif intervention_scenario == 'scn3_kn_w':
            intervention_scenario_targets['wishcycling']['bin'] = 0
        elif intervention_scenario == 'scn4_pbc':
            intervention_scenario_targets['recycling']['ds'] = 0
            intervention_scenario_targets['recycling']['pbc'] = 1
            intervention_scenario_targets['recycling']['bin'] = 1
            intervention_scenario_targets['recycling']['att'] = 1
            intervention_scenario_targets['wishcycling']['bin'] = 0
            for var in ['err', 'sn', 'kn', 'pr', 'ht', 'ns']:
                self.tpb_weights[var]['mode'] *= 1E-6
                self.tpb_weights[var]['min'] *= 1E-6
                self.tpb_weights[var]['max'] *= 1E-6
        else:
            pass
        return intervention_scenario_targets
    # ------

    # Basic methods
    # ------
    @staticmethod
    def trunc_normal_distrib_draw(n_draw: int, **kwargs) -> float:
        """
        Draws a value from a truncated normal distribution. The truncated
        normal is used because many "natural" phenomena have a distribution
        close to a normal distribution and the truncated normal enables
        avoiding extreme values (Burkardt, 2014).
        :param n_draw: number of draw from the distribution.
        :param min: minimum of the range from where to draw.
        :param max: maximum of the range from where to draw.
        :param mean: mean of the distribution.
        :param standard_deviation: standard deviation of the distribution.
        :return: drawn value.
        """
        mean, standard_deviation, min, max = kwargs['mean'], \
            kwargs['standard_deviation'], kwargs['min'], kwargs['max']
        a = (min - mean) / standard_deviation
        b = (max - mean) / standard_deviation
        loc = mean
        scale = standard_deviation
        distribution = truncnorm(a, b, loc, scale)
        draw = distribution.rvs(n_draw)
        if n_draw > 1:
            draw = list(draw)
        else:
            draw = float(draw)
        return draw

    @staticmethod
    def subset_dic_from_dataframe(
            input_df: Type[pd.DataFrame], transpose: bool,
            columns_to_drop_if_condition: list, filters: list,
            index_rows: str) -> dict:
        """
        Transforms a subset of a pandas data frame into a dictionary.
        :param input_df: input data frame.
        :param transpose: transpose rows and columns if necessary.
        :param columns_to_drop_if_condition: list of tuples of the form:
        ('column_name', 'condition_on_column_values') used to reduce the data
        frame to rows of interest (i.e., select rows).
        :param filters: reduce the dictionary to certain columns of the data
        frame (i.e., select columns).
        :param index_rows: used to replace number index into values of rows of
        interest (will be used as the dictionary first keys).
        :return: dictionary.
        """
        if columns_to_drop_if_condition:
            for element in columns_to_drop_if_condition:
                input_df = input_df[input_df[element[0]] == element[1]]
                input_df = input_df.drop(element[0], 1)
        input_df = input_df.set_index(index_rows)
        if filters:
            input_df = input_df.filter(filters)
        if transpose:
            input_df = input_df.T
        output_dict = input_df.to_dict()
        return output_dict

    @staticmethod
    def dic_cumulative_frequencies(dic: dict) -> dict:
        """
        From a dictionary containing keys and their frequencies, outputs a
        dictionary with their cumulative frequencies.
        :param dic: the input dictionary with frequencies of keys.
        :return: an output dictionary with cumulative frequencies.
        """
        list_cumprob = np.cumsum(list(dic.values()))
        dic_cumprob = dict(zip(dic.keys(), list_cumprob))
        return dic_cumprob

    @staticmethod
    def roulette_wheel_choice(cum_dict_frequencies: dict, num_choices: int,
                              deterministic: bool) -> list:
        """
        Makes a choice according to a roulette wheel process.
        :param cum_dict_frequencies: a dictionary containing cumulative
        frequencies (determines the size of the wedges in the roulette wheel).
        :param num_choices: number of choices (number of roulette draws).
        :param deterministic: if False randomly select the pick (where the ball
        falls on the wheel), otherwise choose the pick as to distribute values
        to exactly respect the dictionary's frequencies.
        :return: a shuffled list of num_choices choices and where the
        occurrence of each choice depends on its frequency.
        """
        list_choice = []
        max_cum_freq = max(cum_dict_frequencies.values())
        for c in range(num_choices):
            if deterministic:
                pick = c / num_choices * max_cum_freq
            else:
                pick = random.uniform(0, max_cum_freq)
            current = 0
            for key, value in cum_dict_frequencies.items():
                current += value
                if value > pick:
                    choice = key
                    list_choice.append(choice)
                    break
        random.shuffle(list_choice)
        return list_choice

    @staticmethod
    def min_max_normalization(dic: dict) -> dict:
        """
        Performs a min-max normalization of value in a dictionary.
        :param dic: input dictionary.
        :return: output dictionary where each value is between 0 and 1.
        """
        min_v = min(dic.values())
        max_v = max(dic.values())
        if (max_v - min_v) != 0:
            dic = {k: (v - min_v) / (max_v - min_v) for k, v in dic.items()}
        return dic

    @staticmethod
    def divide_dic_values_by_sum(dic: dict) -> dict:
        """
        Divides each value of a dictionary by the sum of the dictionary's
        values. Values must all be positive.
        :param dic: dictionary of scores.
        :return: a dictionary of values between 0 and 1 that sums to 1.
        """
        if [v for v in dic.values() if v < 0]:
            error = ValueError('Dictionary values should all be a positive.')
            raise error
        tot = np.nansum([element for element in list(dic.values())])
        dic = {k: v / tot for k, v in dic.items()}
        return dic

    @staticmethod
    def assign_elements_from_list(list_elements: list,
                                  exclusive_assignment: bool) -> Any:
        """
        Chooses an element from a list, either randomly or the last element of
        the list (and, if so, removes it from the list).
        :param list_elements: list of elements to choose from.
        :param exclusive_assignment: if True the last element is returned and
        removed from the list, if False the element is randomly chosen from the
        list and the list is left intact.
        :return: the chosen element
        """
        if exclusive_assignment:
            element = list_elements.pop()
        else:
            element = random.choice(list_elements)
        return element

    @staticmethod
    def list_without_last_element(list_elements: list) -> list:
        """
        Return a list without its last element.
        :param list_elements: list of elements from which last element needs to
        be removed
        :return: the modified list
        """
        return list_elements[:-1]

    def apply_f_to_last_value_nested_dic(
        self, nested_dictionary: dict,
            function_to_apply: Callable,
            f_input_name_for_v: str, **kwargs) -> dict:
        """
        Iterates through a nested dictionary until a value that is not a
        dictionary is found. Then applies a function to that value.
        :param nested_dictionary: the dictionary to iterate through.
        :param function_to_apply: the function to apply to the last value in
        the nested dictionary.
        :param f_input_name_for_v: name of the function input for the value.
        :param **kwargs: function's inputs.
        return: nested dictionary with f(final_value).
        """
        kwargs[f_input_name_for_v] = None
        addresses_final_values = list(
            self.all_keys(nested_dictionary))
        for address in addresses_final_values:
            address = [x for x in address if x is not None]
            value = self.nested_dic_get_from_key_list(
                nested_dictionary, address)
            kwargs[f_input_name_for_v] = value
            new_value = function_to_apply(**kwargs)
            self.nested_dic_get_from_key_list(
                nested_dictionary, address[:-1])[address[-1]] = new_value
        return nested_dictionary

    def all_keys(self, nested_dictionary: dict) -> Tuple:
        """
        Iterates through a nested dictionary until a value that is not a
        dictionary is found.
        :param nested_dictionary: the dictionary to iterate through.
        yield: all keys in an ordered fashion (i.e., addresses) as a tuple.
        """
        for key, value in nested_dictionary.items():
            if isinstance(value, dict):
                for pair in self.all_keys(value):
                    yield (key, *pair)
            else:
                yield (key, None)

    @staticmethod
    def nested_dic_get_from_key_list(
            input_dic: dict, nested_keys: list) -> Any:
        """
        Returns the value in a nested dictionary given its "address" (list of
        the nested dictionary keys accessing that value).
        :param input_dic: nested dictionary from which value has to be
        retrieved.
        :param nested_keys: list of keys composing the "address" of the value
        to access.
        return: the accessed value.
        """
        value = reduce(operator.getitem, nested_keys, input_dic)
        return value
    # ------

    # Step methods
    # ------
    def update_yearly_adoption_rates(self):
        """
        Updates yearly adoption rates.
        """
        for k, v in self.behavior_adoption.items():
            self.cum_behavior_adoption[k] += v
        if self.clock % self.behavioral_factors_update == 0:
            self.yearly_adoption_rates = self.divide_dic_values_by_sum(
                self.cum_behavior_adoption)
            self.cum_behavior_adoption = dict.fromkeys(
                [x['name']['strings'] for x in self.behavior_parameters], 0)

    def variable_reinitialization(self) -> None:
        """
        Re-initializes model variables.
        """
        self.behavior_adoption = dict.fromkeys(
            [x['name']['strings'] for x in self.behavior_parameters], 0)
    # ------

    def step(self) -> None:
        """
        Advances the model by one step and collects output data.
        """
        self.schedule.step()
        self.update_yearly_adoption_rates()
        self.variable_reinitialization()
        self.datacollector.collect(self)
        self.clock += 1
        self.year = int(self.clock / self.behavioral_factors_update)


class DecisionMakingAgent(Agent):
    def __init__(self, unique_id: int, model) -> None:
        super().__init__(unique_id, model)
        """
        Creation of new agent.
        """
        self.init = True
        # One method for each behavioral factor must exist
        self.behavioral_factors = self.assign_characteristics_with_list_pop()
        for k in self.model.tpb_weights.keys():
            self.behavioral_factors[k] = getattr(self, k)(
                self.behavioral_factors, k)
        self.current_habits = dict.fromkeys(
            [x['name']['strings'] for x in self.model.behavior_parameters], 0)
        self.memory_past_habits = dict.fromkeys(
            [x['name']['strings'] for x in self.model.behavior_parameters], 0)
        self.habit_formation_threshold = round(
            self.model.trunc_normal_distrib_draw(
                1, min=self.model.habit_formation['threshold']['min'],
                max=self.model.habit_formation['threshold']['max'],
                mean=self.model.habit_formation['threshold']['mean'],
                standard_deviation=self.model.habit_formation[
                    'threshold']['standard_deviation']))
        self.current_habits[self.adopted_behavior] += \
            self.habit_formation_threshold
        self.habitual_decision = False
        self.break_habitual_decision = 0
        self.init = False

    def assign_characteristics_with_list_pop(self) -> dict:
        """
        Assign individual characteristics to agent based on their distribution
        within the population.
        :return: a modified dictionary of characteristic distributions.
        """
        # From a dictionary of list of values, obtains the same dictionary with
        # single values (using list.pop())
        behavioral_factors = self.model.apply_f_to_last_value_nested_dic(
            deepcopy(self.model.bhvr_charac_distrib),
            self.model.assign_elements_from_list, 'list_elements',
            list_elements=None, exclusive_assignment=True)
        # Apply same function to update dict by removing popped value
        self.model.bhvr_charac_distrib = \
            self.model.apply_f_to_last_value_nested_dic(
                self.model.bhvr_charac_distrib,
                self.model.list_without_last_element, 'list_elements',
                list_elements=None)
        return behavioral_factors

    def err(self, behavioral_factors: dict, factor_name: str,
            **kwargs) -> dict:
        """
        Updates the TPB error scores.
        :param behavioral_factor: factors affecting choice selection.
        :param factor_name: characteristic from which values need to be be
        distributed within the population.
        return: dictionary containing the factor's scores for each behavior.
        """
        _ = kwargs
        if not self.init:
            behavioral_factors = self.apply_intervention_scenario(
                behavioral_factors, factor_name,
                self.model.intervention_scenario_targets,
                self.model.intervention_period)
        scores = behavioral_factors[factor_name]
        return scores

    def att(self, behavioral_factors: dict, factor_name: str,
            **kwargs) -> dict:
        """
        Updates the TPB attitude scores.
        :param behavioral_factor: factors affecting choice selection.
        :param factor_name: characteristic from which values need to be be
        distributed within the population.
        return: dictionary containing the factor's scores for each behavior.
        """
        _ = kwargs
        if not self.init:
            behavioral_factors = self.apply_intervention_scenario(
                behavioral_factors, factor_name,
                self.model.intervention_scenario_targets,
                self.model.intervention_period)
        scores = behavioral_factors[factor_name]
        return scores

    def pbc(self, behavioral_factors: dict, factor_name: str,
            **kwargs) -> dict:
        """
        Updates the TPB attitude scores.
        :param behavioral_factor: factors affecting choice selection.
        :param factor_name: characteristic from which values need to be be
        distributed within the population.
        return: dictionary containing the factor's scores for each behavior.
        """
        _ = kwargs
        if not self.init:
            behavioral_factors = self.apply_intervention_scenario(
                behavioral_factors, factor_name,
                self.model.intervention_scenario_targets,
                self.model.intervention_period)
        scores = behavioral_factors[factor_name]
        return scores

    def sn(self, behavioral_factors: dict, factor_name: str,
            **kwargs) -> dict:
        """
        Updates the TPB subjective norms scores for each choice as measured
        by the proportion of agents that have already adopted a given choice.
        :return: the subjective norms scores for each choice.
        """
        _ = kwargs
        if self.init:
            self.adopted_behavior = list(
                behavioral_factors[factor_name].values()).pop()
        scores = {}
        neighbors_nodes = self.model.grid.get_neighbors(
            self.unique_id, include_center=False)
        # noinspection PyCallByClass,PyArgumentList
        neighbors_nodes = [x for x in neighbors_nodes
                           if not self.model.grid.is_cell_empty(x)]
        choices = [x['name']['strings'] for
                   x in self.model.behavior_parameters]
        for choice in choices:
            # noinspection PyCallByClass,PyArgumentList
            list_agent_w_choice = [
                agent for agent in
                self.model.grid.get_cell_list_contents(neighbors_nodes) if
                getattr(agent, 'adopted_behavior') == choice]
            if len(neighbors_nodes) != 0:
                score_key = len(list_agent_w_choice) / len(neighbors_nodes)
            else:
                score_key = 0
            scores[choice] = score_key
        return scores

    def kn(self, behavioral_factors: dict, factor_name: str,
            **kwargs) -> dict:
        """
        Updates the TPB attitude scores.
        :param behavioral_factor: factors affecting choice selection.
        :param factor_name: characteristic from which values need to be be
        distributed within the population.
        return: dictionary containing the factor's scores for each behavior.
        """
        _ = kwargs
        if not self.init:
            behavioral_factors = self.apply_intervention_scenario(
                behavioral_factors, factor_name,
                self.model.intervention_scenario_targets,
                self.model.intervention_period)
        scores = behavioral_factors[factor_name]
        return scores

    def pr(self, behavioral_factors: dict, factor_name: str,
            **kwargs) -> dict:
        """
        Updates the TPB attitude scores.
        :param behavioral_factor: factors affecting choice selection.
        :param factor_name: characteristic from which values need to be be
        distributed within the population.
        return: dictionary containing the factor's scores for each behavior.
        """
        if self.init:
            _ = kwargs
            scores = behavioral_factors[factor_name]
            return scores
        else:
            scores = self.current_habits
            return scores

    def ht(self, behavioral_factors: dict, factor_name: str,
            **kwargs) -> dict:
        """
        Updates the TPB attitude scores.
        :param behavioral_factor: factors affecting choice selection.
        :param factor_name: characteristic from which values need to be be
        distributed within the population.
        return: dictionary containing the factor's scores for each behavior.
        """
        _ = kwargs
        if not self.init:
            behavioral_factors = self.apply_intervention_scenario(
                behavioral_factors, factor_name,
                self.model.intervention_scenario_targets,
                self.model.intervention_period)
        scores = behavioral_factors[factor_name]
        return scores

    def bin(self, behavioral_factors: dict, factor_name: str,
            **kwargs) -> dict:
        """
        Updates the TPB attitude scores.
        :param behavioral_factor: factors affecting choice selection.
        :param factor_name: characteristic from which values need to be be
        distributed within the population.
        return: dictionary containing the factor's scores for each behavior.
        """
        _ = kwargs
        if not self.init:
            behavioral_factors = self.apply_intervention_scenario(
                behavioral_factors, factor_name,
                self.model.intervention_scenario_targets,
                self.model.intervention_period)
        scores = behavioral_factors[factor_name]
        return scores

    def ds(self, behavioral_factors: dict, factor_name: str,
            **kwargs) -> dict:
        """
        Updates the TPB attitude scores.
        :param behavioral_factor: factors affecting choice selection.
        :param factor_name: characteristic from which values need to be be
        distributed within the population.
        return: dictionary containing the factor's scores for each behavior.
        """
        _ = kwargs
        if not self.init:
            behavioral_factors = self.apply_intervention_scenario(
                behavioral_factors, factor_name,
                self.model.intervention_scenario_targets,
                self.model.intervention_period)
        scores = behavioral_factors[factor_name]
        return scores

    def ns(self, behavioral_factors: dict, factor_name: str,
            **kwargs) -> dict:
        """
        Updates the TPB attitude scores.
        :param behavioral_factor: factors affecting choice selection.
        :param factor_name: characteristic from which values need to be be
        distributed within the population.
        return: dictionary containing the factor's scores for each behavior.
        """
        _ = kwargs
        if not self.init:
            behavioral_factors = self.apply_intervention_scenario(
                behavioral_factors, factor_name,
                self.model.intervention_scenario_targets,
                self.model.intervention_period)
        scores = behavioral_factors[factor_name]
        return scores

    def apply_intervention_scenario(
        self, behavioral_factors: dict, factor_name: str,
        intervention_scenario_targets: dict,
            intervention_period: int) -> dict:
        """
        Apply intervention scenario: linearly increase the probability that the
        intervention reach its target throughout the intervention period.
        Modify the behavioral_factor variable accordingly.
        :param behavioral_factor: factors affecting choice selection.
        :param factor_name: characteristic from which values need to be be
        distributed within the population.
        :param intervention_scenario_targets: dictionary containing value to be
        reached by the end of the intervention period (e.g., 100% of agents
        possess a given characteristics at the end of the intervention period).
        :param intervention_period: period during which a given intervention is
        applied.
        """
        for bhvr, factor_dic in \
                intervention_scenario_targets.items():
            if factor_dic and factor_name in factor_dic:
                if behavioral_factors[factor_name][bhvr] != \
                        factor_dic[factor_name]:
                    prob_intervention_effect = 1 / (
                        intervention_period - self.model.year)
                    dice = random.random()
                    if self.break_habitual_decision != 0:
                        behavioral_factors[factor_name][bhvr] = factor_dic[
                            factor_name]
                    elif dice < prob_intervention_effect and \
                        self.model.intervention_scenario != 'baseline' \
                        and self.model.year < intervention_period and \
                        self.model.clock % \
                            self.model.behavioral_factors_update == 0:
                        behavioral_factors[factor_name][bhvr] = factor_dic[
                            factor_name]
                        # Assumes old habits are broken for three times the
                        # maximum time it can takes to form a new habit
                        self.break_habitual_decision = \
                            int(self.model.habit_formation[
                                'threshold']['max'] * 1.5 *
                                self.model.behavioral_factors_update /
                                self.model.decision_frequency)
        return behavioral_factors

    def decision_model(
            self, behavior_parameters: list, tpb_weights: dict,
            behavioral_factors: dict, min_max_normalization: Callable,
            habitual_decision: bool) -> None:
        """
        Computes the behavior scores for each choice depending on the elements
        of the TPB: attitude, subjective norms, perceived behavioral control
        as well as other variables. The method follows discrete choice analysis
        principles (the function used is essentially akin to a utility
        function). A process similar to Hicks & Theis 2014 is followed except
        that probability is defined simply dividing values by their sum. As
        all "utility" scores are positive, it provides for a better
        probabilistic representation and fundamentals than using a softmax
        function. Indeed it represents how much each choice contributes to an
        overall utility and thus has a chance to be selected. On the other hand
        a softmax function is more direct and can accept negative inputs but is
        heavily influenced by the choice of the base (e.g., e or 10) which
        makes the resulting probabilities more difficult to justify.
        :param behavior_parameters: parameters characterizing the different
        behaviors (i.e., choices).
        :param tpb_weights: weights of the different factors in the TPB.
        :param behavioral_factors: factors affecting choice selection.
        :param min_max_normalization: min max normalization method.
        :param habitual_decision: determine if decision is habitual or comes
        from an intention to perform the behavior.
        """
        for k, v in tpb_weights.items():
            new_scores = getattr(self, k)(self.behavioral_factors, k)
            if new_scores:
                behavioral_factors[k] = new_scores
            behavioral_factors[k] = min_max_normalization(
                behavioral_factors[k])
        choices = {x['name']['strings']: x['availability'] for
                   x in behavior_parameters}
        scores_behaviors = dict.fromkeys(choices.keys(), 0)
        for key, value in choices.items():
            for k, v in tpb_weights.items():
                scores_behaviors[key] += abs(v) * behavioral_factors[k][key]
            if not value:
                scores_behaviors.pop(key)
        scores_behaviors = self.model.divide_dic_values_by_sum(
            scores_behaviors)
        cum_scores_behaviors = self.model.dic_cumulative_frequencies(
            scores_behaviors)
        selected_choices = []
        if habitual_decision:
            # choices within the period are habitual, they correspond to the
            # most adopted behavior in the previous period
            selected_choices = [self.adopted_behavior] * \
                self.model.decisions_per_step
            self.current_habits[self.adopted_behavior] += \
                self.model.decisions_per_step
            self.model.behavior_adoption[self.adopted_behavior] += \
                self.model.decisions_per_step
        else:
            for _ in range(self.model.decisions_per_step):
                # roulette wheel process to select choice to account for the
                # decision model's uncertainty and agent's bounded rationality
                choice = self.model.roulette_wheel_choice(
                    cum_scores_behaviors, 1, False)[0]
                selected_choices.append(choice)
                self.current_habits[choice] += 1
                self.model.behavior_adoption[choice] += 1
        self.adopted_behavior = max(set(selected_choices),
                                    key=selected_choices.count)

    def compute_habitual_decision(
            self, habit_formation_threshold: int, habit_formation_gap: float,
            high_prob_habit: tuple) -> bool:
        """
        Computes the probability that a decision is habitual if conditions are
        met, and if so, following a pseudo-random event, decision is habitual.
        :param habit_formation_threshold: necessary number of behavior
        occurrence before it becomes habitual.
        :param habit_formation_gap: occurrence gap between behaviors necessary
        for a new behavior to become habitual (expressed as a ratio).
        :param high_prob_habit: probability parameters that a behavior becomes
        habitual.
        :return: boolean defining if a behavior is habitual.
        """
        max_habit = max(self.current_habits, key=self.current_habits.get)
        habit_wo_max = {k: v for k, v in self.current_habits.items() if
                        k != max_habit}
        scd_max_habit = max(habit_wo_max, key=habit_wo_max.get)
        if self.current_habits[max_habit] >= habit_formation_threshold and \
                self.current_habits[scd_max_habit] < habit_formation_gap * \
                self.current_habits[max_habit]:
            habit_prob = random.uniform(high_prob_habit[0], high_prob_habit[1])
            # model assumes that an intervention break up trash habits during
            # a period long enough for recycling to become habitual (defined
            # from the habit_formation_threshold maximum value)
            if self.model.intervention_scenario != 'baseline' \
                and max_habit == 'trash' and \
                    self.break_habitual_decision != 0:
                habit_prob *= 0
                self.break_habitual_decision -= 1
            dice = random.random()
            if dice < habit_prob:
                self.adopted_behavior = max_habit
                return True
            else:
                return False
        else:
            return False

    def update_past_and_current_habits(self):
        """
        Update the two dictionaries containing past (habits from previous year)
        and current (habits for the current year [affecting the next year's
        decisions]).
        """
        if self.model.clock % self.model.behavioral_factors_update == 0:
            for k in self.current_habits.keys():
                self.current_habits[k] = self.current_habits[k] - \
                    self.memory_past_habits[k]
            self.memory_past_habits = deepcopy(self.current_habits)

    def update_agent_variables(self) -> None:
        """
        Updates instance (agent) variables.
        """
        self.habitual_decision = self.compute_habitual_decision(
            self.habit_formation_threshold,
            self.model.habit_formation['gap_requirement_fraction'],
            self.model.habit_formation['high_prob_habit'])
        self.decision_model(
            self.model.behavior_parameters, self.model.tpb_weights,
            self.behavioral_factors, self.model.min_max_normalization,
            self.habitual_decision)
        self.update_past_and_current_habits()

    def step(self) -> None:
        """
        Evolution of agent at each step.
        """
        self.update_agent_variables()