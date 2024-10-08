import pandas as pd
import numpy as np
import sys
import pickle

class PlasticSD:

    """
    The Pylca class
    - Provides an object which stores the files names required for performing LCA calculations

    Parameters
    ----------
    flow: dict

    material: str

    recycled_material: str

    statewise_composition_filename: str

    region_composition_filename: str

    demand_model: str

    year: list of ints

    initial_recycled_mat: int

    initial_year: int

    final_year: int

    parameters: pandas dataframe

    collection_rate_method : str

    mrf_equipment_efficiency: pandas dataframe


    Returns
    -------

    None

    """

    def __init__(self,
                 flow,
                 material,
                 recycled_material,
                 statewise_composition_filename,
                 region_composition_filename,
                 demand_model,
                 year,
                 initial_recycled_mat,
                 initial_year,
                 final_year,
                 parameters,
                 collection_rate_method,
                 mrf_equipment_efficiency,
                 verbose
                 ):

        self.flow = flow
        self.material = material
        self.recycled_material = recycled_material
        self.statewise_composition_filename = statewise_composition_filename
        self.region_composition_filename = region_composition_filename
        self.demand_model = demand_model
        self.year = year
        self.initial_recycled_mat = initial_recycled_mat
        self.initial_year = initial_year
        self.final_year = final_year
        self.parameters = parameters
        self.collection_rate_method = collection_rate_method
        self.waste_collection_rate = {}
        self.mrf_equipment_efficiency = mrf_equipment_efficiency
        self.verbose = verbose


        #List of material
        self.recycle_stream_material= ['aluminum','cardboard','iron','glass','hdpe','paper','pet','film','other']
        self.state_abrev = {'Alabama': 'AL', 'Arizona': 'AZ', 'Arkansas': 'AR',
                            'California': 'CA', 'Colorado': 'CO', 'Connecticut': 'CT',
                            'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA', 'Hawaii': 'HI', 'Idaho': 'ID',
                            'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA', 'Kansas': 'KS', 'Kentucky': 'KY',
                            'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD', 'Massachusetts': 'MA', 'Michigan': 'MI',
                            'Minnesota': 'MN', 'Mississippi': 'MS', 'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE',
                            'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ', 'New Mexico': 'NM',
                            'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH',
                            'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
                            'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT',
                            'Vermont': 'VT', 'Virginia': 'VA', 'Washington': 'WA', 'West Virginia':
                            'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY'}
        #dictionary used to convert between full state names and their abreviations


    def demand_func(self):

       """
       Demand function calculates the plastic demand for different years

       Parameters
       ----------

       None

       Return
       ------

       None

       """

       #Function for modeling pet demand
       if self.material == 'pet':

           plastic = []
           time = []
           for i in self.year:
                time.append(i)
                '''Using Linear function'''
                if self.demand_model == 'linear':
                    #These are fixed functions and won't change
                    plastic.append(185.51*i - 367515)
                elif self.demand_model == 'log':
                    #These are fixed functions and won't change
                    plastic.append(372028*np.ln(i)-3000000)
       #mm lbs per year
       self.plastic_demand = pd.DataFrame(plastic,time)



    def composition(self):

        """
        Reading and formatting the composition data for recycling stream in the different states


        Parameters
        ----------
        None

        Return
        ----------
        None

        """
        comp_df = pd.read_csv(self.statewise_composition_filename)
        comp_df = comp_df.melt(id_vars = ['states'], var_name = 'mat', value_name = 'value', value_vars = ['pet', 'hdpe', 'other', 'iron', 'film', 'paper', 'cardboard', 'glass', 'aluminum']) 
        composition_dic = {}
        for i,row in comp_df.iterrows():
            composition_dic[(row['states'],'consumer','vacuum',row['mat'])] = row['value']
        self.composition_dic = composition_dic
        self.reg_df = pd.read_csv(self.region_composition_filename)


    #Recycling rate calculation function
    def linear_collection_rate_calc(self,coeff_input,i):

        """
        Calculation of the waste collection rate

        Parameters
        ----------

        coeff_input : array of waste collection model coefficient inputs

        i : year

        Return
        ----------

        Waste collection rate per year : array with waste collection rate numbers

        """

        #Creating a model for waste collection from residences
        #Storing the variables for the collection model. It required socioeconomic variables.
        coll = {}
        coll[(i,'income')] = self.parameters['income'][i]
        coll[(i,'age')] = self.parameters['age'][i]
        coll[(i,'education')] = self.parameters['education'][i]
        coll[(i,'popdensity')] = self.parameters['pop_density'][i]
        coll[(i,'varP')] = self.parameters['varP'][i]
        coll[(i,'ordin')] = self.parameters['ordin'][i]
        coll[(i,'educationexp')] = self.parameters['educationexp'][i]
        coll[(i,'curb')] = self.parameters['curb'][i]
        coll[(i,'drop')] = self.parameters['drop'][i]


        #Storing coefficiencts
        pool_coeff = {}
        pool_coeff[(i,'income')] = -0.0002 #inversely propotional. Income increases recycling rate decreases
        pool_coeff[(i,'age')] = 0.38
        pool_coeff[(i,'education')] = 0.151
        pool_coeff[(i,'popdensity')] = -0.001 #inversely propotional. Pop density increases recycling rate decreases
        pool_coeff[(i,'varP')] = 0.315
        pool_coeff[(i,'ordin')] = 4.151
        pool_coeff[(i,'educationexp')] = 0.534 #This number does not make sense
        pool_coeff[(i,'curb')] = 0.037
        pool_coeff[(i,'drop')] = 1.274
        pool_coeff[(i,'const')] = 0.262
        pool_coeff[(i,'curbdrop')] = 0.001

        #Random effect coefficients
        rand_coeff = {}
        rand_coeff[(i,'income')] = -0.0001 #inversely propotional. Income increases recycling rate decreases
        rand_coeff[(i,'age')] = 0.229
        rand_coeff[(i,'education')] = 0.136
        rand_coeff[(i,'popdensity')] = -0.001 #inversely propotional. Income increases recycling rate decreases
        rand_coeff[(i,'varP')] = 1.623
        rand_coeff[(i,'ordin')] = 2.969
        rand_coeff[(i,'educationexp')] = 0.747
        rand_coeff[(i,'curb')] = -0.011 #inversely propotional. Curbside increases recycling rate decreases?? Does not make sense
        rand_coeff[(i,'drop')] = 0.934
        rand_coeff[(i,'const')] = 4.956
        rand_coeff[(i,'curbdrop')] = 0.026


        if coeff_input == 'random coefficient':
           coeff = rand_coeff
        else:
           coeff = pool_coeff
        current_year = i
        #Recycling rate calculation
        #Value is in fraction
        self.waste_collection_rate[current_year] =  (coll[(current_year,'income')] * coeff[(current_year,'income')]+coll[(current_year,'age')] * coeff[(current_year,'age')]+coll[(current_year,'education')] * coeff[(current_year,'education')]+coll[(current_year,'popdensity')] * coeff[(current_year,'popdensity')]+coll[(current_year,'varP')] * coeff[(current_year,'varP')]+coll[(current_year,'ordin')] * coeff[(current_year,'ordin')]+coll[(current_year,'educationexp')] * coeff[(current_year,'educationexp')]+coll[(current_year,'curb')] * coeff[(current_year,'curb')]+coll[(current_year,'drop')] * coeff[(current_year,'drop')]+coll[(current_year,'curb')]*coll[(current_year,'drop')]*coeff[(current_year,'curbdrop')]+coeff[(current_year,'const')])/100


    #New function tat utilzes the ABM to calculate the recycling rate.
    def new_collection_rate(self, i: int, region) -> float:

        """
        New function that utilizes the ABM to calculate the recycling rate
        :param self: takes in the model, non-static method
        :param i: corresponds to the current year used in the modelling period
        :param region: string corresponding to the state (region) of modelling
        :return: a float containing the recycling rate
        """

        df = pd.read_csv("./input/core_files/ResultsBatchRun.csv") #should be ResultsBatchRun when we run the ABM, this is a fixed file that doens't change
        #print("This is the dataframe", df['scenario'].unique().tolist())
        df = df.replace({'scenario': self.state_abrev})
        #print("This is the dataframe", df['scenario'].unique().tolist())
        df = df.groupby(['Year', 'scenario'], as_index = False).mean()
        df = df[df['Year'] == i]
        df = df[df['scenario'] == region]
        #print("This is the dataframe", df.head())

        trash = float(df['trash'])

        recycling =  1-trash
        current_year = i + self.initial_year
        self.waste_collection_rate[current_year] = recycling

    def splitter_disposal(self,i):

        """
        Calculates splitting of waste between landfill,

        Parameters
        ----------

        i : int
            year

        Return
        ----------

        None

        """

        not_collected_waste_incinerated_fraction = self.parameters['not_collected_waste_incinerated_fraction']
        not_collected_waste_landfilled_fraction = self.parameters['not_collected_waste_landfilled_fraction']
        self.flow[(i,self.material,'disposal','waste_collection')] = self.waste_collection_rate[i] * self.flow[(i,self.material,'use','disposal')]
        self.flow[(i,self.material,'waste_collection','waste_incineration')] = self.flow[(i,self.material,'disposal','waste_collection')] * self.parameters['mass_ratio_waste_incineration'][i]
        not_collected_waste = self.flow[(i,self.material,'use','disposal')] - self.flow[(i,self.material,'disposal','waste_collection')]

        #Subtracting the amount that was sent to waste incineration after being collected
        self.flow[(i,self.material,'disposal','mrf_tipping')] = self.flow[(i,self.material,'disposal','waste_collection')] - self.flow[(i,self.material,'waste_collection','waste_incineration')]


        self.flow[(i,self.material,'disposal','waste_incineration')] = not_collected_waste_incinerated_fraction[i] * not_collected_waste
        self.flow[(i,self.material,'disposal','landfill')] = not_collected_waste_landfilled_fraction[i] * not_collected_waste
        #LANDFILL FLOW 1


    def waste_incineration_to_electricity(self,i):

        """
        Calculates production of electricity from waste incineration process

        Parameters
        ----------

        i : int
            year

        Return
        ----------

        None

        """

        waste_incineration_to_electricity_conversion_rate = self.parameters['waste_incineration_to_electricity_conversion_rate_short_tons to_kwh'][i]
        conversion_million_pounds_to_short_tons = 0.5*1000
        self.flow[(i,'electricity','waste_incineration','grid')] = (self.flow[(i,self.material,'disposal','waste_incineration')] + self.flow[(i,self.material,'waste_collection','waste_incineration')]) * conversion_million_pounds_to_short_tons * waste_incineration_to_electricity_conversion_rate#tons * 550kwh

    def vacuum(self,i):

        """
        Calculates flow of material in the vacuum unit of mrf

        Parameters
        ----------

        i : int
            year

        Return
        ----------

        None

        """

        for m in  self.recycle_stream_material:
            if m == 'cardboard':
                self.flow[(i,m,'vacuum','disc_screen1')] = self.flow[(i,m,'consumer','vacuum')] * (1-self.mrf_equipment_efficiency['efficiency'][str(i)+' vacuum '+m])
            elif m == 'paper':
                self.flow[(i,m,'vacuum','disc_screen1')] = self.flow[(i,m,'consumer','vacuum')] * (1-self.mrf_equipment_efficiency['efficiency'][str(i)+' vacuum '+m])
            elif m == 'film':
                self.flow[(i,m,'vacuum','disc_screen1')] = self.flow[(i,m,'consumer','vacuum')] * (1-self.mrf_equipment_efficiency['efficiency'][str(i)+' vacuum '+m])
            else:
                self.flow[(i,m,'vacuum','disc_screen1')] = self.flow[(i,m,'consumer','vacuum')]

    def disc_screen(self,i):

        """
        Calculates flow of material in the disc screen unit of mrf

        Parameters
        ----------

        i : int
            year

        Return
        ----------

        None

        """

        for m in self.recycle_stream_material:
            if m == 'cardboard':
                self.flow[(i,m,'disc_screen1','glass_breaker')] = self.flow[(i,m,'vacuum','disc_screen1')] * (1-self.mrf_equipment_efficiency['efficiency'][str(i)+' discreen1 '+m])
            elif m == 'paper':
                self.flow[(i,m,'disc_screen1','glass_breaker')] = self.flow[(i,m,'vacuum','disc_screen1')] * (1-self.mrf_equipment_efficiency['efficiency'][str(i)+' discreen1 '+m])
            else:
                self.flow[(i,m,'disc_screen1','glass_breaker')] = self.flow[(i,m,'vacuum','disc_screen1')]


    def glass_breaker(self,i):

        """
        Calculates flow of material in the glass breaker unit of mrf

        Parameters
        ----------

        i : int
            year

        Return
        ----------

        None

        """

        for m in self.recycle_stream_material:
            if m == 'glass':
                 self.flow[(i,m,'glass_breaker','disc_screen2')] = self.flow[(i,m,'disc_screen1','glass_breaker')] * (1-self.mrf_equipment_efficiency['efficiency'][str(i)+' glass_breaker '+m])
            else:
                 self.flow[(i,m,'glass_breaker','disc_screen2')] = self.flow[(i,m,'disc_screen1','glass_breaker')]





    def disc_screen2(self,i):

        """
        Calculates flow of material in the disc screen 2 unit of mrf

        Parameters
        ----------

        i : int
            year

        Return
        ----------

        None

        """

        for m in self.recycle_stream_material:
            if m == 'cardboard':
                 self.flow[(i,m,'disc_screen2','nir_pet')] = self.flow[(i,m,'glass_breaker','disc_screen2')] * (1-self.mrf_equipment_efficiency['efficiency'][(str(i)+' discreen2 '+m)])
            elif m == 'paper':
                 self.flow[(i,m,'disc_screen2','nir_pet')] = self.flow[(i,m,'glass_breaker','disc_screen2')] * (1-self.mrf_equipment_efficiency['efficiency'][(str(i)+' discreen2 '+m)])
            elif m == 'film':
                 self.flow[(i,m,'disc_screen2','nir_pet')] = self.flow[(i,m,'glass_breaker','disc_screen2')] * (1-self.mrf_equipment_efficiency['efficiency'][(str(i)+' discreen2 '+m)])
            else:
                 self.flow[(i,m,'disc_screen2','nir_pet')] = self.flow[(i,m,'glass_breaker','disc_screen2')]



    def nir_pet(self,i):

        """
        Calculates flow of material in the NIR PET unit of mrf

        Parameters
        ----------

        i : int
            year

        Return
        ----------

        None

        """

        for m in self.recycle_stream_material:
            if m != 'iron':
                 self.flow[(i,m,'nir_pet','nir_hdpe')] = self.flow[(i,m,'disc_screen2','nir_pet')] * (1-self.mrf_equipment_efficiency['efficiency'][(str(i)+' nir_pet '+m)])
            else:
                 self.flow[(i,m,'nir_pet','nir_hdpe')] = self.flow[(i,m,'disc_screen2','nir_pet')]



    def nir_hdpe(self,i):

        """
        Calculates flow of material in the NIR HDPE unit of mrf

        Parameters
        ----------

        i : int
            year

        Return
        ----------

        None

        """

        for m in self.recycle_stream_material:
            if m != 'iron':
                 self.flow[(i,m,'nir_hdpe','magnet')] = self.flow[(i,m,'nir_pet','nir_hdpe')] * (1-self.mrf_equipment_efficiency['efficiency'][(str(i)+' nir_hdpe '+m)])
            else:
                 self.flow[(i,m,'nir_hdpe','magnet')] = self.flow[(i,m,'nir_pet','nir_hdpe')]




    def pet_bale(self,i,qc):

        """
        Calculates flow of material in the PET BALE of mrf

        Parameters
        ----------

        qc: int
            quality control

        i : int
            year

        Return
        ----------

        None

        """

        for m in self.recycle_stream_material:
            self.flow[(i,m,'nir_pet','bale')] = self.flow[(i,m,'disc_screen2','nir_pet')] - self.flow[(i,m,'nir_pet','nir_hdpe')]
            if m != 'pet':
               self.flow[(i,m,'nir_pet','bale')] = self.flow[(i,m,'nir_pet','bale')] * (1-qc)




    def hdpe_bale(self,i,qc):

        """
        Calculates flow of material in the HDPE bale of mrf

        Parameters
        ----------

        qc: int
            quality control

        i : int
            year

        Return
        ----------

        None

        """

        for m in self.recycle_stream_material:
                self.flow[(i,m,'nir_hdpe','bale')] = self.flow[(i,m,'nir_pet','nir_hdpe')] - self.flow[(i,m,'nir_hdpe','magnet')]
                if m != 'hdpe':
                   self.flow[(i,m,'nir_hdpe','bale')] = self.flow[(i,m,'nir_hdpe','bale')] * (1-qc)



    def mrf_sorting(self,i,region):

        """
        Calculates flows withing the mrf unit operation model

        Parameters
        ----------
        region: str
            state

        i : int
            year

        Return
        ----------

        None

        """

        #List of material
        recycle_stream_material = ['aluminum','cardboard','iron','glass','hdpe','paper','pet','film','other']


        #Put 0 for no quality control. Otherwise enter the efficiency of the Quality Control.
        qc = self.parameters['quality_control_mrf'][i]

        composition_reg = {}



        for mat in self.recycle_stream_material:

            composition_reg[(i,'consumer','vacuum',mat)] = self.composition_dic[(region,'consumer','vacuum',mat)]


        #Mutliplying the total national plastic material flow with the respective composition so as to get the quantity of flow in a particular region. That flow is used for analysis in the region rather than total flow for the nation.
        total_recycle_flow = self.flow[(i,self.material,'disposal','mrf_tipping')]/composition_reg[(i,'consumer','vacuum',self.material)]
        for mat in recycle_stream_material:
            self.flow[(i,mat,'consumer','vacuum')] = total_recycle_flow * composition_reg[(i,'consumer','vacuum',mat)]

        self.vacuum(i)
        self.disc_screen(i)
        self.glass_breaker(i)
        self.disc_screen2(i)
        self.nir_pet(i)
        self.nir_hdpe(i)
        self.pet_bale(i,qc)

        if self.material == 'pet':
            for mat in self.recycle_stream_material:
                self.flow[(i,mat,'bale','reclaimer')] = self.flow[(i,mat,'nir_pet','bale')]

        #LANDFILL 2
        self.flow[(i,self.material,'mrf','landfill')] = self.flow[(i,self.material,'disposal','mrf_tipping')] - self.flow[(i,self.material,'bale','reclaimer')]


    def splitter_sorter(self,i):

        """
        Calculates split fractions between recycling pathways -
            1. Mechanical Recycling Pathway
            2. Chemical Recycling Pathway
            3. Chemical Upcycling pathways


        Parameters
        ----------


        i : int
            year

        Return
        ----------

        None

        """

        '''At this point, the material can choose between recycling pathways'''

        self.flow[(i,self.material,'bale','mech_reclaimer')] = self.flow[(i,self.material,'bale','reclaimer')] * self.parameters['mass_ratio_mechanical_recycling'][i]
        self.flow[(i,self.material,'bale','chem_reclaimer')] = self.flow[(i,self.material,'bale','reclaimer')] * self.parameters['mass_ratio_chemical_recycling'][i]





    def mechanical_recycling_grade_model(self,i):

        """
        Models mechanical recycling of plastics and subsequent recovery.

        Parameters
        ----------

        i : int
            year

        Return
        ----------

        None

        """


        total = 0
        for mat in self.recycle_stream_material:
           total = total + self.flow[(i,mat,'bale','reclaimer')]

        try:
            pet = self.flow[(i,self.material,'bale','reclaimer')]/total
        except:
            pet = 0

        if pet >= self.parameters['grade_foodgrade'][i]:
            self.grade_choice = 'food'
        elif pet >= self.parameters['grade_highgrade'][i]:
            self.grade_choice = 'high'
        elif pet >= self.parameters['grade_mediumgrade'][i]:
            self.grade_choice = 'medium'
        else:
            self.grade_choice = 'low'

        #Grade is determined by the purity of the bale: 'food', 'high', 'medium', and 'low'
        self.recovery_choice = self.parameters['recovery_' + self.grade_choice + 'grade'][i]
        self.mech_selectivity = self.parameters['mechanical_recycling_' + self.grade_choice + 'grade_selectivity'][i]

        self.flow[(i,self.material,'mech_reclaimer','manuf')] = self.flow[(i,self.material,'bale','mech_reclaimer')] * self.recovery_choice
        self.flow[(i,self.material,'mech_reclaimer','landfill')] = self.flow[(i,self.material,'bale','mech_reclaimer')] - self.flow[(i,self.material,'mech_reclaimer','manuf')]

        #LANDFILL 3
    def chemical_recycling_model(self,i):

        """
        Models chemical recycling of plastics and subsequent recovery.

        Parameters
        ---------

        i : int
            year

        Return
        ------

        None

        """

        self.chemical_selectivity = self.parameters['chemical_recycling_selectivity'][i]

        self.flow[(i,self.material,'chem_reclaimer','manuf')] = self.flow[(i,self.material,'bale','chem_reclaimer')] * self.parameters['recovery_chemical_recycling'][i]
        self.flow[(i,self.material,'chem_reclaimer','landfill')] = self.flow[(i,self.material,'bale','chem_reclaimer')] - self.flow[(i,self.material,'chem_reclaimer','manuf')]

        #LANDFILL 4
    def chemical_upcycling_model(self,i):
        """
        Models chemical upcycling of plastics and subsequent recovery.

        Parameters
        ----------

        i : int
            year

        Return
        ------

        None

        """

        #Conversion rate = 0.709
        #I am not aware of the the loss here.
        #Upcycling can be divided into two different pathways. We have two pyrolysis pathways.
        #One creates pyrolysis oil and one creates fiber.
        self.flow[(i,self.material,'bale','frp_upcycler')] = self.flow[(i,self.material,'bale','reclaimer')] * self.parameters['mass_ratio_fiber_reinforced_resin'][i]
        self.flow[(i,self.material,'bale','ppo_upcycler')] = self.flow[(i,self.material,'bale','reclaimer')] * self.parameters['mass_ratio_ppo'][i]
        self.flow[(i,self.material,'bale','chem_upcycler')] = self.flow[(i,self.material,'bale','frp_upcycler')] + self.flow[(i,self.material,'bale','ppo_upcycler')]
        self.flow[(i,'pyrolysis_oil','chem_upcycler','manuf')] = self.flow[(i,self.material,'bale','ppo_upcycler')] * self.parameters['pet_to_ppo_conversion_factor'][i]
        self.flow[(i,'fiber_reinforced_resin','chem_upcycler','manuf')] = self.flow[(i,self.material,'bale','frp_upcycler')] * self.parameters['pet_to_polyester_conversion_factor'][i] * self.parameters['polyester_to_fiber_reinforced_resin_conversion_factor'][i]
        #self.flow[(i,'pyrolysis_oil','chem_upcycler','landfill')] = self.flow[(i,self.material,'bale','chem_upcycler')] - self.flow[(i,'pyrolysis_oil','chem_upcycler','manuf')]
        #self.flow[(i,'polyester','chem_upcycler','landfill')] = self.flow[(i,self.material,'bale','chem_upcycler')] - self.flow[(i,'polyester','chem_upcycler','manuf')]
        #self.flow[(i,self.material,'chem_upcycler','landfill')] = self.flow[(i,'pyrolysis_oil','chem_upcycler','landfill')] + self.flow[(i,'polyester','chem_upcycler','landfill')]
        self.flow[(i,self.material,'chem_upcycler','landfill')] = 0

    def grade_model_pathway_selector(self,i):
        """
        Models substitution of plastics based on selectivity of different processes and pathways.

        Parameters
        ----------


        i : int
            year

        Return
        ------

        None

        """
        if self.grade_choice == 'food':
            self.flow[(i,self.recycled_material,'manuf','recycling')] = self.flow[(i,self.material,'mech_reclaimer','manuf')] * self.mech_selectivity + self.flow[(i,self.material,'chem_reclaimer','manuf')] * self.chemical_selectivity
            self.flow[(i,self.material,'manuf','landfill')] = self.flow[(i,self.material,'mech_reclaimer','manuf')]  + self.flow[(i,self.material,'chem_reclaimer','manuf')] - self.flow[(i,self.recycled_material,'manuf','recycling')]
            #LANDFILL 5
        else:
            self.flow[(i,self.recycled_material,'manuf','recycling')] = self.flow[(i,self.material,'chem_reclaimer','manuf')] * self.chemical_selectivity
            self.flow[(i,self.recycled_material,'manuf','downcycling')] = self.flow[(i,self.material,'mech_reclaimer','manuf')] * self.mech_selectivity
            self.flow[(i,self.material,'manuf','landfill')] = self.flow[(i,self.material,'chem_reclaimer','manuf')] + self.flow[(i,self.material,'mech_reclaimer','manuf')] - self.flow[(i,self.recycled_material,'manuf','recycling')] -  self.flow[(i,self.recycled_material,'manuf','downcycling')]
            #LANDFILL 6

    def total_landfill_flow_calculator(self,i):
        """
        Calculates total landfill flow

        Parameters
        ----------


        i : int
            year

        Return
        ----------

        None

        """

        self.flow[(i,self.material,'system','landfill')] = 0
        for source in ['manuf', 'mrf', 'mech_reclaimer', 'chem_reclaimer', 'chem_upcycler', 'disposal']:
            self.flow[(i,self.material,'system','landfill')] += self.flow[(i,self.material,source,'landfill')]

    def circ_tracker_wtd_based(self):

        """
        Calculates the weight based circularity which requires dynamic information.
        This circularity requires historical information of flows. So this indicator is calculated within the flow model


        Parameters
        ----------
        None


        Return
        ----------
        None

        """


        circularity = {}
        total_disposal = []
        for i in self.year:

            vpet_manuf = self.flow[(i,self.material,'use','disposal')] - self.flow[(i,self.recycled_material,'manuf','recycling')]
            circularity[i] = {}
            life = []
            rate_of_recovery = []
            recycled_mass = []
            circ = []
            total_disposal.append(self.flow[(i,self.material,'use','disposal')])
            for j in range(i,self.final_year+1):

                rate_of_recovery.append(self.flow[(i,self.recycled_material,'manuf','recycling')]/self.flow[(j,self.material,'use','disposal')])
                if j == i:
                    recycled_mass.append(vpet_manuf*rate_of_recovery[j-i])
                elif j > i:
                    recycled_mass.append(recycled_mass[j-1-i]*rate_of_recovery[j-i])

                life.append(j-i+1)
                circ.append((recycled_mass[j-i] * (j-i+1)))

            circularity[i]['life'] = life
            circularity[i]['recycled_mass'] = recycled_mass
            circularity[i]['rate'] = rate_of_recovery
            circularity[i]['circularity'] = circ

        time = []
        rec_mass = []
        for y in reversed(self.year):
            total_circ = 0
            for y1 in range(y,2018,-1):
                     k = y-y1
                     val = circularity[y1]['circularity'][k]
                     total_circ = total_circ + val



            time.append(y)
            rec_mass.append(total_circ)


        df = pd.DataFrame()
        df['year'] = list(reversed(time))
        df['rec_mass'] = list(reversed(rec_mass))
        df['total_disposal'] = total_disposal


        return df


    def circ_tracker_inflow_outflow(self):

        """
        Calculates the Inflow- Outflow circularity which requires dynamic information.
        This circularity requires historical information of flows. So this indicator is calculated within the flow model


        Parameters
        ----------
        None


        Return
        ----------
        None

        """

        vmat_inflow = []
        cmat_inflow = []
        wmat_outflow = []
        cmat_outflow = []
        time = []

        for i in self.year:
            vmat_inflow.append(self.flow[(i,self.material,'manuf','use')])
            cmat_inflow.append(self.flow[(i,self.recycled_material,'manuf','recycling')])
            wmat_outflow.append(self.flow[(i,self.material,'system','landfill')])
            #This is debatable.
            cmat_outflow.append(self.flow[(i,self.recycled_material,'manuf','recycling')] + self.flow[(i,self.recycled_material,'manuf','downcycling')] + self.flow[(i,self.material,'bale','chem_upcycler')] + self.flow[(i,self.material,'disposal','waste_incineration')])
            time.append(i)

        df = pd.DataFrame()
        df['year'] = time
        df['vmat_inflow'] = vmat_inflow
        df['cmat_inflow'] = cmat_inflow
        df['wmat_outflow'] = wmat_outflow
        df['cmat_outflow'] = cmat_outflow

        return df


    def circ_tracker_landfill_diversion(self):

        """
        Calculates the Landfill diversion circularity which requires dynamic information.
        This circularity requires historical information of flows. So this indicator is calculated within the flow model


        Parameters
        ----------
        None


        Return
        ----------
        None

        """

        vpet_manuf = []
        total_disposal = []
        total_landfill = []
        time = []

        for i in self.year:
            vpet_manuf.append(self.flow[(i,self.material,'manuf','use')])
            total_disposal.append(self.flow[(i,self.material,'use','disposal')])
            total_landfill.append(self.flow[(i,self.material,'system','landfill')])
            time.append(i)

        df = pd.DataFrame()
        df['year'] = time
        df['vpet_manuf'] = vpet_manuf
        df['total_disposal'] = total_disposal
        df['total_landfill'] = total_landfill

        return df

    def lca_df_creator(self,i):

        """
        Life cycle assessment database creator function. This database is used for lca calculations further in the code.


        Parameters
        ----------
        i : year
            str


        Return
        ----------
        None

        """

        waste_collected = self.flow[(i,self.material,'disposal','waste_collection')] #Amount collected
        baled_plastic = self.flow[(i,self.material,'bale','reclaimer')] #PET in the bale
        mech_reclaimed_plastic = self.flow[(i,self.material,'mech_reclaimer','manuf')] #PET from recycler to manuf
        chem_reclaimed_plastic = self.flow[(i,self.material,'chem_reclaimer','manuf')] #PET from recycler to manuf
        pyrolyis_oil = self.flow[(i,'pyrolysis_oil','chem_upcycler','manuf')] #PPO produced
        pyrolysis_oil_combusted = self.flow[(i,'pyrolysis_oil','chem_upcycler','manuf')] #PPO Combusted
        residual_oil_displaced = self.flow[(i,'pyrolysis_oil','chem_upcycler','manuf')] #PPO produced
        #polyester = self.flow[(i,'polyester','chem_upcycler','manuf')] #Polyester produced
        #polyester_displaced = self.flow[(i,'polyester','chem_upcycler','manuf')] #Polyester displaced by production
        fiber_reinforced_resin = self.flow[(i,'fiber_reinforced_resin','chem_upcycler','manuf')] #Fiber reinforced resin produced
        fiber_reinforced_resin_displaced = self.flow[(i,'fiber_reinforced_resin','chem_upcycler','manuf')] #Fiber reinforced resin  displaced by production
        waste_to_incineration = self.flow[(i,self.material,'disposal','waste_incineration')] + self.flow[(i,self.material,'waste_collection','waste_incineration')] #Input to the waste incineration process
        transportation_pet_bale_reclaimer = self.flow[(i,self.material,'bale','mech_reclaimer')] + self.flow[(i,self.material,'bale','chem_reclaimer')] + self.flow[(i,self.material,'bale','chem_upcycler')] #tonne km of PET transported
        virgin_pet = self.flow[(i,self.material,'manuf','use')] #PET Virgin production
        landfill = self.flow[(i,self.material,'system','landfill')] #Total PET landfill amount

        flow_value = [waste_collected,
                      baled_plastic,
                      mech_reclaimed_plastic,
                      chem_reclaimed_plastic,
                      pyrolyis_oil,
                      pyrolysis_oil_combusted,
                      fiber_reinforced_resin,
                      waste_to_incineration,
                      transportation_pet_bale_reclaimer,
                      virgin_pet,
                      landfill]
        year = [i] * len(flow_value)
        #flow_name = ['PET, tipping floor','postconsumer PET','mechancial RPET,'+' '+ self.grade_mechanical+' grade','chemical RPET','pyrolyis_oil','waste to incineration PET','sorted PET','virgin PET','landfilling' ]
        unit = ['kg'] * len(flow_value)
        unit[8] = 'tonne-km'
        
        process = ['PET, collection',
                   'PET, at MRF',
                   'PET, mechanical reclamation, '+ self.grade_choice +' grade',
                   'PET, chemical reclamation',
                   'PET, pyrolysis',
                   'PET, pyrolysis combustion',
                   'PET, fiber',
                   'PET, waste to incineration',
                   'PET, transportation to reclaimer',
                   'PET, manufacture',
                   'PET, landfill']
        #Direction means the model has final demand of these materials
        #direction = ['input','input','input','input','input','input','input','input','input']

        lst = list(zip(process,flow_value,year,unit))
        self.lca_flow_quantities = pd.DataFrame(lst, columns =['process','flow_quantity','year','unit'])

        #Converting mmlbs / year to kgs because all LCA calculations are in kgs.
        self.lca_flow_quantities.loc[self.lca_flow_quantities['unit'] == 'kg','p.flow.quantity'] = self.lca_flow_quantities['flow_quantity']* 453592.37
        self.lca_flow_quantities.loc[self.lca_flow_quantities['unit'] == 'kWh','p.flow.quantity'] = self.lca_flow_quantities['flow_quantity']
        distance_transportation = 366 #miles 585.6 km
        distance_transportation = 585.6 #km
        #converting tonne km / year
        self.lca_flow_quantities.loc[self.lca_flow_quantities['unit'] == 'tonne-km', 'p.flow.quantity'] = self.lca_flow_quantities['flow_quantity'] * 453592.37/1000*distance_transportation

    def system_displaced_lca_df_creator(self,i):

        """
        Life cycle assessment database creator function. This database is used for lca calculations further in the code.


        Parameters
        ----------
        i : year
            str


        Return
        ----------
        None

        """


        residual_oil_displaced = self.flow[(i,'pyrolysis_oil','chem_upcycler','manuf')]
        fiber_reinforced_resin_displaced = self.flow[(i,'fiber_reinforced_resin','chem_upcycler','manuf')]
        electricity_displaced = self.flow[(i,'electricity','waste_incineration','grid')]
        pet_displaced_downcycling = self.flow[(i,self.recycled_material,'manuf','downcycling')]

        flow_value = [residual_oil_displaced,
                      fiber_reinforced_resin_displaced,
                      electricity_displaced,
                      pet_displaced_downcycling]



        year = [i] * len(flow_value)
        #flow_name = ['PET, tipping floor','postconsumer PET','mechancial RPET,'+' '+ self.grade_mechanical+' grade','chemical RPET','pyrolyis_oil','waste to incineration PET','sorted PET','virgin PET','landfilling' ]
        unit = ['kg',
                'kg',
                'kWh',
                'kg']
        process = ['PET, residual oil displaced',
                   'PET, fiber, displacement',
                   'PET, electricity displaced',
                   'PET, resin displaced by downcycling']
        #Direction means the model has final demand of these materials
        #direction = ['input','input','input','input','input','input','input','input','input']

        lst = list(zip(process,flow_value,year,unit))
        self.displaced_lca_flow_quantities = pd.DataFrame(lst, columns =['process','flow_quantity','year','unit'])

        #Converting mmlbs / year to kgs because all LCA calculations are in kgs.

        self.displaced_lca_flow_quantities.loc[self.displaced_lca_flow_quantities['unit'] == 'kg','p.flow.quantity'] = self.displaced_lca_flow_quantities['flow_quantity'] * 453592.37
        self.displaced_lca_flow_quantities.loc[self.displaced_lca_flow_quantities['unit'] == 'kWh','p.flow.quantity'] = self.displaced_lca_flow_quantities['flow_quantity']
        distance_transportation = 366 #miles 585.6 km
        distance_transportation = 585.6 #km
        #converting tonne km / year
        self.displaced_lca_flow_quantities.loc[self.displaced_lca_flow_quantities['unit'] == 'tonne-km', 'p.flow.quantity'] = self.displaced_lca_flow_quantities['flow_quantity'] * 453592.37/1000*distance_transportation

    def main(self):

        """
        The main function of the flow model that runs all the other supportive functions.
        Calculates all the flows and saves the flow information in the flow object.

        Parameters
        ----------
        None


        Return
        ------
        None

        """

        self.demand_func()
        self.composition()
        self.final_results = pd.DataFrame()
        self.circ_results_wtd = pd.DataFrame()
        self.circ_results_div = pd.DataFrame()
        self.circ_results_inflow_outflow = pd.DataFrame()
        self.cost_results = pd.DataFrame()
        self.lca_demand_df = pd.DataFrame()
        self.system_displaced_lca_df = pd.DataFrame()
        self.cost_df = pd.DataFrame()



        for index,row in self.reg_df.iterrows():

            #Saving the flow information

            #graph variables
            vmanuf_use = []
            use_to_dispose = []
            dispose_to_landfill = []
            dispose_to_collection = []
            dispose_to_wte_uncollected = []
            dispose_to_wte_collected = []
            dispose_to_wte = []
            dispose_to_mrf = []
            total_bale_quantity = []
            total_bale_quantity_mechanical_reclaimer = []
            total_bale_quantity_chemical_reclaimer = []
            total_bale_quantity_upcycling_reclaimer = []
            total_bale_quantity_pyrolysis_reclaimer = []
            total_bale_quantity_fiber_reinforced_resin_reclaimer = []

            mrf_to_m_reclaimer = []
            mrf_to_c_reclaimer = []
            mrf_to_c_upcycler = []
            mrf_to_ppo = []
            mrf_to_frp = []
            mrf_to_landfill = []

            m_reclaimer_to_manuf = []
            m_reclaimer_to_landfill = []
            c_reclaimer_to_manuf = []
            c_reclaimer_to_landfill = []
            downcycled = []
            recycled = []

            rmanuf_to_use = []
            rmanuf_to_landfill = []
            wte_energy = []
            pyrolysis_fuel_oil = []
            fiber_reinforced_resin = []
            plastic_demand_data = []
            landfill = []

            years = []
            grade_array = []
            lca_df = pd.DataFrame()
            system_displaced_lca_df = pd.DataFrame()


            if self.verbose == 1:
                print(row['regions'])
            for i in self.year:

                  region = row['regions']
                  pl_dem = self.plastic_demand.loc[i,0] * row['ratio']#mm lbs per year
                  if i == self.initial_year:
                      self.flow[(self.initial_year,self.recycled_material,'recycling','use')] = pl_dem * self.initial_recycled_mat/100
                  else:
                      pass

                  self.flow[(i,self.material,'manuf','use')] = pl_dem/0.99 - self.flow[(i,self.recycled_material,'recycling','use')]
                  self.flow[(i,self.material,'use','disposal')] = pl_dem

                  if self.collection_rate_method == "ABM":
                        self.new_collection_rate(i-self.initial_year, region)
                  elif self.collection_rate_method == "user defined":
                        self.waste_collection_rate[i] = self.parameters['user_defined_collection_rate'][i]
                  else:
                        self.linear_collection_rate_calc('pool coefficient', i)
                  self.splitter_disposal(i)
                  self.waste_incineration_to_electricity(i)
                  self.mrf_sorting(i,region)
                  self.splitter_sorter(i)
                  self.mechanical_recycling_grade_model(i)
                  self.chemical_recycling_model(i)
                  self.chemical_upcycling_model(i)
                  self.grade_model_pathway_selector(i)
                  self.flow[(i+1,self.recycled_material,'recycling','use')] =  self.flow[(i,self.recycled_material,'manuf','recycling')]
                  self.total_landfill_flow_calculator(i)
                  self.lca_df_creator(i)
                  self.system_displaced_lca_df_creator(i)


                  lca_df = pd.concat([lca_df,self.lca_flow_quantities])
                  system_displaced_lca_df = pd.concat([system_displaced_lca_df,self.displaced_lca_flow_quantities])
                  vmanuf_use.append(self.flow[(i,self.material,'manuf','use')])
                  use_to_dispose.append(self.flow[(i,self.material,'use','disposal')])
                  dispose_to_landfill.append(self.flow[(i,self.material,'disposal','landfill')])
                  dispose_to_collection.append(self.flow[(i,self.material,'disposal','waste_collection')])
                  dispose_to_wte_uncollected.append(self.flow[(i,self.material,'disposal','waste_incineration')])
                  dispose_to_wte_collected.append(self.flow[(i,self.material,'waste_collection','waste_incineration')])
                  dispose_to_wte.append(self.flow[(i,self.material,'waste_collection','waste_incineration')]+self.flow[(i,self.material,'disposal','waste_incineration')])
                  dispose_to_mrf.append(self.flow[(i,self.material,'disposal','mrf_tipping')])

                  total_material = 0
                  for mat in self.recycle_stream_material:
                     total_material = total_material + self.flow[(i,mat,'bale','reclaimer')]
                  total_bale_quantity.append(total_material)

                  mrf_to_m_reclaimer.append(self.flow[(i,self.material,'bale','mech_reclaimer')])
                  mrf_to_c_reclaimer.append(self.flow[(i,self.material,'bale','chem_reclaimer')])
                  mrf_to_ppo.append(self.flow[(i,self.material,'bale','ppo_upcycler')])
                  mrf_to_frp.append(self.flow[(i,self.material,'bale','frp_upcycler')])
                  mrf_to_c_upcycler.append(self.flow[(i,self.material,'bale','chem_upcycler')])
                  mrf_to_landfill.append(self.flow[(i,self.material,'mrf','landfill')])

                  total_bale_quantity_mechanical_reclaimer.append(total_material*self.parameters['mass_ratio_mechanical_recycling'][i])
                  total_bale_quantity_chemical_reclaimer.append(total_material*self.parameters['mass_ratio_chemical_recycling'][i])
                  total_bale_quantity_upcycling_reclaimer.append(total_material*(self.parameters['mass_ratio_ppo'][i]+self.parameters['mass_ratio_fiber_reinforced_resin'][i]))
                  total_bale_quantity_pyrolysis_reclaimer.append(total_material*self.parameters['mass_ratio_ppo'][i])
                  total_bale_quantity_fiber_reinforced_resin_reclaimer.append(total_material*self.parameters['mass_ratio_fiber_reinforced_resin'][i])

                  m_reclaimer_to_manuf.append(self.flow[(i,self.material,'mech_reclaimer','manuf')])
                  m_reclaimer_to_landfill.append(self.flow[(i,self.material,'mech_reclaimer','landfill')])
                  c_reclaimer_to_manuf.append(self.flow[(i,self.material,'chem_reclaimer','manuf')])
                  c_reclaimer_to_landfill.append(self.flow[(i,self.material,'chem_reclaimer','landfill')]  )

                  recycled.append(self.flow[(i,self.recycled_material,'manuf','recycling')])
                  downcycled.append(self.flow[(i,self.recycled_material,'manuf','downcycling')])

                  rmanuf_to_use.append(self.flow[(i,self.recycled_material,'manuf','recycling')])
                  rmanuf_to_landfill.append(self.flow[(i,self.material,'manuf','landfill')])
                  wte_energy.append(self.flow[(i,'electricity','waste_incineration','grid')])
                  pyrolysis_fuel_oil.append(self.flow[(i,'pyrolysis_oil','chem_upcycler','manuf')])
                  fiber_reinforced_resin.append(self.flow[(i,'fiber_reinforced_resin','chem_upcycler','manuf')])
                  plastic_demand_data.append(self.plastic_demand.loc[i,0])
                  landfill.append(self.flow[(i,self.material,'system','landfill')])
                  years.append(i)
                  grade_array.append(self.grade_choice)


            df =  pd.DataFrame({'year':pd.Series(years),
                                'vmanuf_to_use':pd.Series(vmanuf_use),
                                'use_to_dispose':pd.Series(use_to_dispose),
                                'dispose_to_landfill':pd.Series(dispose_to_landfill),
                                'dispose_to_collection':pd.Series(dispose_to_collection),
                                'dispose_to_wte_uncollected':pd.Series(dispose_to_wte_uncollected),
                                'dispose_to_wte_collected':pd.Series(dispose_to_wte_collected),
                                'dispose_to_wte':pd.Series(dispose_to_wte),
                                'dispose_to_mrf':pd.Series(dispose_to_mrf),
                                'mrf_to_m_reclaimer':pd.Series(mrf_to_m_reclaimer),
                                'mrf_to_c_reclaimer':pd.Series(mrf_to_c_reclaimer),
                                'mrf_to_c_upcycler':pd.Series(mrf_to_c_upcycler),
                                'mrf_to_ppo_reclaimer':pd.Series(mrf_to_ppo),
                                'mrf_to_frp_reclaimer':pd.Series(mrf_to_frp),
                                'mrf_to_landfill':pd.Series(mrf_to_landfill),
                                'm_reclaimer_to_manuf':pd.Series(m_reclaimer_to_manuf),
                                'm_reclaimer_to_landfill':pd.Series(m_reclaimer_to_landfill),
                                'c_reclaimer_to_manuf':pd.Series(c_reclaimer_to_manuf),
                                'c_reclaimer_to_landfill':pd.Series(c_reclaimer_to_landfill),
                                'rmanuf_to_use':pd.Series(rmanuf_to_use),
                                'rmanuf_to_landfill':pd.Series(rmanuf_to_landfill),
                                'cl_recycled':pd.Series(recycled),
                                'downcycled':pd.Series(downcycled),
                                'wte_energy':pd.Series(wte_energy),
                                'pyrolysis_fuel_oil':pd.Series(pyrolysis_fuel_oil),
                                'fiber_reinforced_resin':pd.Series(fiber_reinforced_resin),
                                'plastic_demand_data':pd.Series(plastic_demand_data),
                                'landfill':pd.Series(landfill),
                                'grade':pd.Series(grade_array),
                                'total_bale_quantity':pd.Series(total_bale_quantity),
                                'total_bale_quantity_mechanical_reclaimer':pd.Series(total_bale_quantity_mechanical_reclaimer),
                                'total_bale_quantity_chemical_reclaimer':pd.Series(total_bale_quantity_chemical_reclaimer),
                                'total_bale_quantity_upcycling_reclaimer':pd.Series(total_bale_quantity_upcycling_reclaimer),
                                'total_bale_quantity_pyrolysis_reclaimer':pd.Series(total_bale_quantity_pyrolysis_reclaimer),
                                'total_bale_quantity_fiber_reinforced_resin_reclaimer':pd.Series(total_bale_quantity_fiber_reinforced_resin_reclaimer)
                                })

            circ_df_wt_bsd_df = self.circ_tracker_wtd_based()
            circ_df_diversion_df = self.circ_tracker_landfill_diversion()
            circ_df_inflow_outflow_df  = self.circ_tracker_inflow_outflow()

            #Adding Region
            df['region'] = region
            circ_df_wt_bsd_df['region'] = region
            circ_df_diversion_df['region'] = region
            circ_df_inflow_outflow_df['region'] = region
            lca_df['region'] = region
            system_displaced_lca_df['region'] = region


            self.final_results = pd.concat([self.final_results,df])
            self.circ_results_wtd = pd.concat([self.circ_results_wtd,circ_df_wt_bsd_df])
            self.circ_results_div = pd.concat([self.circ_results_div,circ_df_diversion_df])
            self.circ_results_inflow_outflow = pd.concat([self.circ_results_inflow_outflow,circ_df_inflow_outflow_df])
            self.lca_demand_df = pd.concat([self.lca_demand_df,lca_df])
            self.system_displaced_lca_df = pd.concat([self.system_displaced_lca_df,system_displaced_lca_df])



    