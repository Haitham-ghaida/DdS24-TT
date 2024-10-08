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
                 reg_df,
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

        self.reg_df = reg_df
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
                self.flow[(i,m,'vacuum','disc_screen1')] = float(self.flow[(i,m,'consumer','vacuum')] * (1-self.mrf_equipment_efficiency['efficiency'][str(i)+' vacuum '+m]))
                self.flow[(i,m,'vacuum','film_bale')] = float(self.flow[(i,m,'consumer','vacuum')] * (self.mrf_equipment_efficiency['efficiency'][str(i)+' vacuum '+m]))
            elif m == 'paper':
                self.flow[(i,m,'vacuum','disc_screen1')] = float(self.flow[(i,m,'consumer','vacuum')] * (1-self.mrf_equipment_efficiency['efficiency'][str(i)+' vacuum '+m]))
                self.flow[(i,m,'vacuum','film_bale')]= float(self.flow[(i,m,'consumer','vacuum')] * (self.mrf_equipment_efficiency['efficiency'][str(i)+' vacuum '+m]))
            elif m == 'film':
                self.flow[(i,m,'vacuum','disc_screen1')] = float(self.flow[(i,m,'consumer','vacuum')] * (1-self.mrf_equipment_efficiency['efficiency'][str(i)+' vacuum '+m]))
                self.flow[(i,m,'vacuum','film_bale')] = float(self.flow[(i,m,'consumer','vacuum')] * (self.mrf_equipment_efficiency['efficiency'][str(i)+' vacuum '+m]))
            else:
                self.flow[(i,m,'vacuum','disc_screen1')] = float(self.flow[(i,m,'consumer','vacuum')])
                self.flow[(i,m,'vacuum','film_bale')] = float(0)

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



    def mrf_sorting(self,i):

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

        print(i)
        #Put 0 for no quality control. Otherwise enter the efficiency of the Quality Control.
        qc = self.parameters['quality_control_mrf'][i]

    
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
        #self.flow[(i,self.material,'mrf','landfill')] = self.flow[(i,self.material,'disposal','mrf_tipping')] - self.flow[(i,self.material,'bale','reclaimer')]


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


        self.final_results = pd.DataFrame()
        self.circ_results_wtd = pd.DataFrame()
        self.circ_results_div = pd.DataFrame()
        self.circ_results_inflow_outflow = pd.DataFrame()
        self.cost_results = pd.DataFrame()
        self.lca_demand_df = pd.DataFrame()
        self.system_displaced_lca_df = pd.DataFrame()
        self.cost_df = pd.DataFrame()




        for region in self.reg_df:

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
                print(region)
            for i in self.year:
                
                  

                  self.mrf_sorting(i)
                  
            return self.flow



    