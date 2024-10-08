import pandas as pd
import numpy as np

class Tea:
    """    
    The Techno economic analysis class 
    - Provides an object which stores the files names required for Techno economic analysis calculations

    Parameters
    ----------
    
    year: int
        simulation year array
    
    flow_df: pandas dataframe
        Stores information regarding the flow values in the different activities of the system
    
    virgin_resin_production_df: pandas Dataframe
        Stores cost information for virgin resin production
    mrf_df: pandas dataframe
        Stores cost information for MRF
    
    mech_reclaiming_df: pandas dataframe
        Stores cost information for mechanical recycling
    
    chem_reclaiming_glyc_df: pandas dataframe
        Stores cost information for chemical recycling - glycolysis
    
    chem_upcycling_pyro_df: pandas dataframe
        Stores cost information for chemical upycling - pyrolysis
    
    waste_to_incineration_df: pandas dataframe
        Stores cost information for waste incineration to energy
    
    parameters: pandas dataframe
        Stores model input parameters for PCEP

    """
    def __init__(self,
                 year,
                 flow_df,
                 virgin_resin_production_df,
                 mrf_df,
                 mech_reclaiming_df,
                 chem_reclaiming_glyc_df,
                 upcycling_pyro_df,
                 fiber_resin_upcycling_df,
                 waste_to_incineration_df,
                 parameters,
                 verbose):
        
        """
        This function stores the filenames and parameters required for Techno economic analysis as properties of an object. 
        
        Parameters
        ----------
        """
        # filepaths for files used in the pylca calculations
        self.year = year
        self.cost_flow_df = flow_df
        self.virgin_resin_production_df = virgin_resin_production_df
        self.mrf_df = mrf_df
        self.mech_reclaiming_df = mech_reclaiming_df
        self.chem_reclaiming_glyc_df = chem_reclaiming_glyc_df
        self.upcycling_pyro_df = upcycling_pyro_df
        self.fiber_resin_upcycling_df = fiber_resin_upcycling_df
        self.waste_to_incineration_df = waste_to_incineration_df
        self.hours_in_an_year = 8760*0.90
        self.parameters = parameters
        self.verbose = verbose
        


    '''Calculating Costs'''


    def virgin_resin_production_costs(self,mass_flow_pyear,df):
        
        """
        This functions calculates the virgin resin production cost. 
        
        Parameters
        ----------
        mass_flow: float
            Mass quantity of plastic entering the unit operation
        
        df: pandas database
            Database storing economic information for the unit operation
                
        
        Return
        ------        
        None       
        
        """
        
        #Mass flow in Tonnes / year
        df['mass_flow'] = mass_flow_pyear
        df['size_ratio'] = df['mass_flow']/df['Throughput (tonnes/yr)']
    
        
        df['scaled_inv'] = df['Investment (USD)'] * np.power(df['size_ratio'],df['Scaling Exponent'])
    
        #Converting to Levelised cost of sorting
        df['scaled_inv'] = df['scaled_inv']/20 #$/year    
        df['scaled_operating_cost_per_year'] = df['Operating Costs (USD/year)']* df['mass_flow']/ df['Throughput (tonnes/yr)']
        
        #Scaling up costs to an year
        df['total cost'] = df['scaled_operating_cost_per_year'] +  df['scaled_inv']
        
        df['stage'] = 'Virgin Resin Manufacture'
        virgin_resin_production_cost = sum(df['total cost'])
        
        return virgin_resin_production_cost  
    
    def mrf_costs(self,mass_flow,df):
        
        """
        This functions calculates the sorting costs in the Material Recovery Facility
        
        Parameters
        ----------
        mass_flow: float
            Mass quantity of plastic entering the unit operation
        
        df: pandas database
            Database storing economic information for the unit operation
                
        
        Return
        ------        
        None       
        
        """

        #Mass flow in Tons / hour
        '''DIFFERENT EQUIPMENT HAVE DIFFERENT FLOWS'''    
        df['mass_flow'] = mass_flow #Correct later
        df['size_ratio'] = df['mass_flow']/df['Throughput (tons/hr)']
        df['scaled_inv'] = df['Investment (USD)'] * np.power(df['size_ratio'],df['Scaling Exponent']) 
        #Converting to Levelized cost of sorting    
        df['scaled_inv'] = df['scaled_inv']/20 #$/year    
        df['scaled_lab'] = df['mass_flow'] * df['Labor'] / df['Throughput (tons/hr)']
        df['labor_cost'] = df['Labor rate']*df['scaled_lab'] #$/hr
        df['scaled_elec'] = df['mass_flow'] * df['Electricity (kW)'] / df['Throughput (tons/hr)'] #KW
        df['electricity_cost'] = df['scaled_elec'] * df['Electricity cost'] #$/hr taking 6 cents per kwh
        df['stage'] = 'MRF'

        #Scaling up costs to an year        
        #Multiplying by number of hours in an year
        df['total cost'] = (df['labor_cost'] * self.hours_in_an_year) + (df['electricity_cost'] * self.hours_in_an_year) + (df['scaled_inv'])
        mrf_cost = sum(df['total cost'])

        #total cost is coming per year. 
        return mrf_cost
        
     
        
    def reclaiming_mechanical_costs(self,mass_flow,df):
        
        """
        This functions calculates the mechanical recycling cost. 
        
        Parameters
        ----------
        mass_flow: float
            Mass quantity of plastic entering the unit operation
        
        df: pandas database
            Database storing economic information for the unit operation
                
        
        Return
        ------        
        None       
        
        """        
        
        #Mass flow in Tons / hour    
        df['mass_flow'] = mass_flow
        df['size_ratio'] = df['mass_flow']/df['Throughput (tons/hr)']
        df['scaled_inv'] = df['Investment (USD)'] * np.power(df['size_ratio'],df['Scaling Exponent']) 
        #Converting to Levelised cost of sorting
        df['scaled_inv'] = df['scaled_inv']/20 #$/year
        
        df['scaled_lab'] = df['mass_flow'] * df['Labor need'] * df['Setting']/ df['Throughput (tons/hr)']
        df['labor_cost'] = df['Labor rate (USD/hr)']*df['scaled_lab'] #$/hr
        df['scaled_elec'] = df['mass_flow'] * df['Electricity (kW)'] / df['Throughput (tons/hr)']
        df['electricity_cost'] = df['scaled_elec'] * df['Electricity cost']  #$/hr
        df['stage'] = 'Mech. Recycling'

        #Scaling up costs to an year        
        #Multiplying by number of hours in an year
        df['total cost'] = (df['labor_cost'] * self.hours_in_an_year) + (df['electricity_cost'] * self.hours_in_an_year) + (df['scaled_inv'])
        reclaiming_cost = sum(df['total cost'])
        #total cost is coming per year. 
        return reclaiming_cost
    
    
    
    def reclaiming_chemical_costs(self,mass_flow_pyear,df):
        
        """
        This functions calculates the chemical recycling cost. 
        
        Parameters
        ----------
        mass_flow: float
            Mass quantity of plastic entering the unit operation
        
        df: pandas database
            Database storing economic information for the unit operation
                
        
        Return
        ------        
        None       
        
        """
        
        #Mass flow in Tonnes / year
        df['mass_flow'] = mass_flow_pyear
        df['size_ratio'] = df['mass_flow']/df['Throughput (tonnes/yr)']
    
        
        df['scaled_inv'] = df['Investment (USD)'] * np.power(df['size_ratio'],df['Scaling Exponent'])
    
        #Converting to Levelised cost of sorting
        df['scaled_inv'] = df['scaled_inv']/20 #$/year    
        df['scaled_fixed_operating_cost_per_year'] = df['Fixed Operating Costs (USD/year)'] * df['mass_flow']/ df['Throughput (tonnes/yr)']
        df['scaled_variable_operating_cost_per_year'] = df['Variable Operating Costs (USD/year)'] * df['mass_flow']/ df['Throughput (tonnes/yr)']

        #Scaling up costs to an year
        df['total cost'] = df['scaled_fixed_operating_cost_per_year'] + df['scaled_variable_operating_cost_per_year']+ df['scaled_inv']
        
        df['stage'] = 'Chem. Recycling'
        reclaiming_cost = sum(df['total cost'])
        
        return reclaiming_cost
    
    
    def pyrolysis_upcycling_chemical_costs(self,mass_flow,df):
        
        """
        This functions calculates the chemical upcycling cost. 
        
        Parameters
        ----------
        mass_flow: float
            Mass quantity of plastic entering the unit operation
        
        df: pandas database
            Database storing economic information for the unit operation
                
        
        Return
        ------        
        None       
        
        """
        
        #Mass flow in Tonnes / hour
        
        df['mass_flow'] = mass_flow
        df['size_ratio'] = df['mass_flow']/df['Throughput (tonnes/hr)']
       
        df['scaled_inv'] = df['Investment (USD)'] * np.power(df['size_ratio'],df['Scaling Exponent']) 
        #Converting to Levelised cost
        df['scaled_inv'] = df['scaled_inv']/20 #$/year       
        
        
        #everything here is per year
        df['scaled_variable_operating_cost_yr'] = df['mass_flow'] * df['Variable Operating Costs ($/yr)'] / df['Throughput (tonnes/hr)']
        df['scaled_fixed_operating_cost_yr'] = df['mass_flow'] * df['Fixed Operating Costs ($/yr)'] / df['Throughput (tonnes/hr)']    
        
        #Total cost per year. 
        df['total cost'] = df['scaled_variable_operating_cost_yr'] + df['scaled_inv'] + df['scaled_fixed_operating_cost_yr']
        df['stage'] = 'pyrolysis'
        upcycling_cost = sum(df['total cost'])
        
        return upcycling_cost
    
    def fiber_resin_upcycling_costs(self,mass_flow_pyear,df):
        
        """
        This functions calculates the fiber resin upcycling_costs. 
        
        Parameters
        ----------
        mass_flow: float
            Mass quantity of plastic entering the unit operation
        
        df: pandas database
            Database storing economic information for the unit operation
                
        
        Return
        ------        
        None       
        
        """
        
        #Mass flow in Tonnes / year
        df['mass_flow'] = mass_flow_pyear
        df['size_ratio'] = df['mass_flow']/df['Throughput (tonnes/yr)']
    
        
        df['scaled_inv'] = df['Investment (USD)'] * np.power(df['size_ratio'],df['Scaling Exponent'])
    
        #Converting to Levelised cost of sorting
        df['scaled_inv'] = df['scaled_inv']/20 #$/year   
        df['scaled_fixed_operating_cost_per_year'] = df['Fixed operating costs (USD/year)'] * df['mass_flow']/ df['Throughput (tonnes/yr)']
        df['scaled_variable_operating_cost_per_year'] = df['Variable operating costs (USD/year)'] * df['mass_flow']/ df['Throughput (tonnes/yr)']

        #Scaling up costs to an year
        df['total cost'] = df['scaled_fixed_operating_cost_per_year'] + df['scaled_variable_operating_cost_per_year']+ df['scaled_inv']
        
        df['stage'] = 'fiber reinforced resin upcycling'
        fiber_resin_upcycling_cost = sum(df['total cost'])
        
        return fiber_resin_upcycling_cost

    
    def wte_costs(self,mass_flow,df):
        
        """
        This functions calculates the waste incineration cost. 
        
        Parameters
        ----------
        mass_flow: float
            Mass quantity of plastic entering the unit operation
        
        df: pandas database
            Database storing economic information for the unit operation
                
        
        Return
        ------        
        None       
        
        """
        
        #Mass flow in Tons / year
        #Total cost per year. 
        
        df['mass_flow'] = mass_flow
        df['size_ratio'] = df['mass_flow']/df['Throughput (tons/yr)']
    
        
        df['scaled_inv'] = df['Investment (USD)'] * np.power(df['size_ratio'],df['Scaling Exponent'])
    
        #Converting to Levelised cost of sorting
        df['scaled_inv_per_year'] = df['scaled_inv']/20 #$/year    
        df['scaled_operating_cost_per_year'] = df['Total Operating Costs ($/yr)'] * df['mass_flow']/ df['Throughput (tons/yr)']
    
        #Scaling up costs to an year
        df['total cost'] = df['scaled_operating_cost_per_year'] +  df['scaled_inv_per_year']

        df['stage'] = 'waste to incineration'
        incineration_cost = sum(df['total cost'])
        
        return incineration_cost
    
    
    def main(self):
        
            """
            The main function of the flow model that runs all the other supportive functions.
            Calculates all the costs and saves the economic information in the cost object. 
            
            Parameters
            ----------
            None
                    
            
            Return
            ------        
            None       
            
            """
                       
            '''Flows are coming in Million Pounds per Year'''
            '''Need to convert'''
            '''Manufacturing costs'''
            #million pounds per year   

            #Virgin Resin manufacture Costs
            #Mass flow in Tonnes yr  
            mass_in_Tonnes_year_conversion_factor = 0.453 * 1000 #Tonnes/year
            virgin_resin_production = list(self.cost_flow_df['vmanuf_to_use'] * mass_in_Tonnes_year_conversion_factor)            
            virgin_resin_costs_data = []
            for index, val in enumerate(virgin_resin_production):
                 virgin_resin_costs_data.append(self.virgin_resin_production_costs(val,self.virgin_resin_production_df))                     

            self.cost_flow_df['vmanuf_cost_of_production'] = virgin_resin_costs_data
            if self.verbose == 1: 
                print('Manufacturing cost calculated')
            
            #Collection Costs
            #Mass flow in Tons              
            mass_in_Tons_conversion_factor = 0.500 * 1000 #Tons
            self.cost_flow_df = self.parameters.merge(self.cost_flow_df,on = ['year'])
            self.cost_flow_df['collection_cost_waste_plastic'] = mass_in_Tons_conversion_factor * self.cost_flow_df['use_to_dispose']*self.cost_flow_df['collection_cost']
            if self.verbose == 1: 
                print('collection cost calculated')
            
            #Transportation Costs
            self.cost_flow_df['landfill_transportation_cost_waste_plastic'] = mass_in_Tons_conversion_factor * self.cost_flow_df['dispose_to_landfill'] * self.cost_flow_df['distance_for_landfill']  * self.cost_flow_df['transportation_cost'] 
            self.cost_flow_df['wte_transportation_cost_waste_plastic'] = mass_in_Tons_conversion_factor * (self.cost_flow_df['dispose_to_wte_uncollected']+self.cost_flow_df['dispose_to_wte_collected']) * self.cost_flow_df['distance_for_wte']  * self.cost_flow_df['transportation_cost'] 
            self.cost_flow_df['mrf_transportation_cost_waste_plastic'] = mass_in_Tons_conversion_factor * self.cost_flow_df['dispose_to_mrf'] * self.cost_flow_df['distance_for_mrf']  * self.cost_flow_df['transportation_cost'] 
            if self.verbose == 1: 
                print('transportation cost calculated')            

            #MRF Sorting Costs               
            #Mass flow in Tons / hour
            #Choosing only plastics flow
   
            mass_in_Tons_hour_conversion_factor = 0.500 * 1000 / self.hours_in_an_year #Tons/hour
            flow_to_mrf = list(self.cost_flow_df['dispose_to_mrf'] * mass_in_Tons_hour_conversion_factor)
            mrf_cost_data = []
            for mass_f in flow_to_mrf:
                mrf_cost_data.append(self.mrf_costs(mass_f,self.mrf_df))
                
                
            self.cost_flow_df['mrf_sorting_cost_plastic'] = mrf_cost_data
            if self.verbose == 1: 
                print('mrf cost calculated')



            #Transportation from Sorter to Reclaimer Costs            
            #Mass flow in Tonne
            #total material is in mm lbs. Convert to tonne
            mass_in_tonne_conversion_factor = 1000 * 0.453
            trans_cost = self.cost_flow_df['transportation_cost']#0.13 #$/MT-km
            distance = self.cost_flow_df['distance_from_mrf_to_reclaimer']#585.6 #km
            

            bale_to_reclaimer = list(self.cost_flow_df['total_bale_quantity'] * mass_in_tonne_conversion_factor)
            self.cost_flow_df['transportation_cost_mrf_to_reclaimer'] =  bale_to_reclaimer*trans_cost*distance
            if self.verbose == 1: 
                print('transportation cost calculated')
    
            
            #Mechanical Recycling Costs
            #Mass flow in Tons / hour
            mass_in_Tons_hour_conversion_factor =  0.500 * 1000 / self.hours_in_an_year #Tons/hour
            flow_to_mechanical_reclaimer = list(self.cost_flow_df['total_bale_quantity_mechanical_reclaimer'] * mass_in_Tons_hour_conversion_factor)
            grades = list(self.cost_flow_df['grade'])
            mech_reclaiming_cost_data = []
            for index,val in enumerate(flow_to_mechanical_reclaimer):
                grade_choice =grades[index]
                #Choosing the proper grade
                graded_mech_reclaiming_df = self.mech_reclaiming_df[self.mech_reclaiming_df['Grade'] == grade_choice]
                mech_reclaiming_cost_data.append(self.reclaiming_mechanical_costs(val,graded_mech_reclaiming_df))

            self.cost_flow_df['mechanical_reclaiming_cost'] = mech_reclaiming_cost_data
            if self.verbose == 1: 
                print('mechanical recycling cost calculated')
            
    
            #Chemical Recycling Glycolysis Costs
            #Mass flow in Tonnes yr  
            mass_in_Tonnes_year_conversion_factor = 0.453 * 1000 #Tonnes/year
            flow_to_chemical_reclaimer = list(self.cost_flow_df['total_bale_quantity_chemical_reclaimer'] * mass_in_Tonnes_year_conversion_factor)            
            chem_reclaiming_costs_data = []
            for index, val in enumerate(flow_to_chemical_reclaimer):
                 chem_reclaiming_costs_data.append(self.reclaiming_chemical_costs(val,self.chem_reclaiming_glyc_df))                     

            self.cost_flow_df['chemical_reclaiming_cost'] = chem_reclaiming_costs_data
            if self.verbose == 1: 
                print('chemical recycling cost calculated')
    
            #Chemical Upcycling Pyrolysis Costs
            #Mass flow in Tonnes / hour                 
            mass_in_Tonnes_hour_conversion_factor = 0.453 * 1000 / self.hours_in_an_year #Tonnes/hour
            flow_to_pyrolysis_upcycler = list(self.cost_flow_df['total_bale_quantity_pyrolysis_reclaimer'] * mass_in_Tonnes_hour_conversion_factor)    
            pyrolysis_upcycling_costs_data = []
            for index, val in enumerate(flow_to_pyrolysis_upcycler):
                pyrolysis_upcycling_costs_data.append(self.pyrolysis_upcycling_chemical_costs(val,self.upcycling_pyro_df))
            
                
            self.cost_flow_df['pyrolysis_upcycling_cost'] = pyrolysis_upcycling_costs_data
            if self.verbose == 1: 
                print('pyrolysis upcycling cost calculated')
            
            #Chemical Upcycling fiber reinforced resin Costs
            #Mass flow in Tonnes yr  
            mass_in_Tonnes_year_conversion_factor = 0.453 * 1000 #Tonnes/year
            flow_to_fiber_resin_upcycler = list(self.cost_flow_df['total_bale_quantity_fiber_reinforced_resin_reclaimer'] * mass_in_Tonnes_year_conversion_factor)            
            fiber_resin_upcycling_costs_data = []
            for index, val in enumerate(flow_to_fiber_resin_upcycler):
                 fiber_resin_upcycling_costs_data.append(self.fiber_resin_upcycling_costs(val,self.fiber_resin_upcycling_df))                     

            self.cost_flow_df['fiber_resin_upcycling_cost'] = fiber_resin_upcycling_costs_data
            if self.verbose == 1: 
                print('fiber resin upcycling costs calculated')



            #Waste to incineration Costs
            #Mass flow in Tons / year                
            mass_in_Tons_year_conversion_factor = 0.500 * 1000 #Tons/Year
            #Choosing a particular size of plant as basis
            waste_to_incineration_df = self.waste_to_incineration_df[self.waste_to_incineration_df['Throughput (tons/yr)'] == 500000] #Corressponds to 1M population
            flow_to_wte = list((self.cost_flow_df['dispose_to_wte']) * mass_in_Tons_year_conversion_factor)  
            incineration_costs_data = []
            for index,val in enumerate(flow_to_wte):
                incineration_costs_data.append(self.wte_costs(val,waste_to_incineration_df))
            
            self.cost_flow_df['incineration_cost'] = incineration_costs_data
            if self.verbose == 1: 
                print('waste incineration cost calculated')

            #Landfilling Costs
            #Mass flow in Tons / year 
            landfilling_cost = 55.36 #$/ton
            mass_in_Tons_year_conversion_factor = 0.500 * 1000 #Tons/Year
            self.cost_flow_df['landfill_costs'] = self.cost_flow_df['landfill'] * mass_in_Tons_year_conversion_factor * landfilling_cost
            if self.verbose == 1: 
                print('landfilling cost calculated')

  
        
