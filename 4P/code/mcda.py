import pandas as pd

class mcda:
       """
       The MCDA class
              - Combines the LCA, Circularity (PCI) and Cost into one indicator for a final indicator. 
              - Uses just one LCA Indicator for now. 

       Parameters
       ----------
       lca_results: pandas DataFrame
              LCA results data table
       cost_results: pandas DataFrame
              cost results data table
       pci_results: pandas DataFrame
              pci results data table
       lci_indicator: str
              Life cycle indicator chose from inclusion in MCDA analysis
       mcda_weights: dictionary
              Weights value for MCDA calculations
       mcda_results: str
              filename and path to save the MCDA results

       """

       def __init__(self,
                    lca_results,
                    cost_results,
                    pci_results,
                    lci_indicator,
                    mcda_weights,
                    mcda_results
                    ):

              """
              This function stores the variables for lca, PCI and Cost results for combining into the MCDA
              Parameters
              ----------
              lca_results: pandas DataFrame
                     LCA results data table
              cost_results: pandas DataFrame
                     cost results data table
              pci_results: pandas DataFrame
                     pci results data table
              lci_indicator: str
                     Life cycle indicator chose from inclusion in MCDA analysis
              mcda_weights: dictionary
                     Weights value for MCDA calculations
              mcda_results: str
                     filename and path to save the MCDA results
              """

              self.lca_results = lca_results
              self.cost_results = cost_results
              self.pci_results = pci_results
              self.lci_indicator = lci_indicator
              self.mcda_weights = mcda_weights
              self.mcda_results = mcda_results

       def mcda_calc(self):

              """
              


              
              print(self.lca_results.columns)
              print(self.cost_results.columns)
              print(self.pci_results.columns)

              if self.lci_indicator == 'Global Warming':
                     gwp = self.lca_results[self.lca_results['impacts'] == "Global Warming Air (kg CO2 eq )"]
                     gwp_grouped = gwp.groupby(['year', 'scenario','corrected_name'])['impact'].agg('sum').reset_index()

              max_gwp = gwp_grouped['impact'].max()
              cst_grouped['normalized_cost'] = 1-(cst_grouped['cost']/max_cst)

              pci_grouped = self.pci_results
              cst_grouped = self.cost_results



              cst_grouped = cst_grouped.melt(id_vars = ['year','scenario'], value_vars = ['vmanuf_cost_of_production', 'collection_cost_waste_plastic',
              'landfill_transportation_cost_waste_plastic',
              'wte_transportation_cost_waste_plastic',
              'mrf_transportation_cost_waste_plastic', 'mrf_sorting_cost_plastic',
              'transportation_cost_mrf_to_reclaimer', 'mechanical_reclaiming_cost',
              'chemical_reclaiming_cost', 'pyrolysis_upcycling_cost',
              'fiber_resin_upcycling_cost', 'incineration_cost', 'landfill_costs'], var_name = 'stage', value_name = 'costs').reset_index()             
              cst_grouped = cst_grouped.groupby(['year','scenario'])['costs'].agg('sum').reset_index().drop_duplicates()
              max_cst = cst_grouped['cost'].max()
              cst_grouped['normalized_cost'] = 1-(cst_grouped['cost']/max_cst)
              



              mcda_df = pd.DataFrame()
              mcda_df['plastic_circularity_index'] = pci_grouped['material_circularity_index']
              mcda_df[self.lci_indicator] = gwp_grouped['impact']
              mcda_df['cost'] = cst_grouped['costs']
              mcda_df['scenario'] = gwp_grouped['scenario']
              mcda_df['year'] = gwp_grouped['year']

              mcda_df['MCDA_indicator'] = mcda_df['cost']*self.mcda_weights['normalized_cost'] + mcda_df['Global Warming']*self.mcda_weights['global_warming'] + mcda_df['plastic_circularity_index']*self.mcda_weights['pci']  
              mcda_df.to_csv(self.mcda_results)

              """

              return 0












