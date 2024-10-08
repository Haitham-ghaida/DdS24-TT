import pandas as pd
import numpy as np


mat = ['Rigids__3_to_7',
       'PET_Other_Rigid',
       'Paper',
       'Aluminum',
       'Cardboard_Boxboard',
       'Glass',
       'HDPE_Bottles', 
       'PP',
       'Steel_Cans',
       'PET_Bottles',
       'Rigids__3_to_7',
       'PP',
       'PET_Other_Rigid',
       'Textiles']


group_df = pd.read_csv('grouping.csv')

for index,row in group_df.iterrows():
    
    df = pd.read_csv('./projected_by_population/'+row['EPA_model']+'projected_amounts_to_relog.csv')
    

    #The fraction files are paper/pet from the waste_composition.csv file. 
    #The missing states are filled up with averages of all states
    if row['MRF_model'] == "film":  
        
        #average = .62931
        save_pet_df = pd.read_csv('./projected_by_population/PET_Bottles_recycled_projected_amounts_to_relog.csv')
        fraction = pd.read_csv('film_fraction.csv')
        fraction = fraction[fraction['fraction']!=0]
        avg = np.mean(fraction['fraction'])
        df2 = save_pet_df[['State','name']]
        df3 = df2.merge(fraction,on = 'State', how = 'outer')
        df3 = df3.fillna(avg)
        df4 = save_pet_df.merge(df3,on=['State','name'])
        df4[['2004.0','2005.0', '2006.0', '2007.0', '2008.0', '2009.0', '2010.0', '2011.0','2012.0', '2013.0', '2014.0', '2015.0', '2016.0', '2017.0', '2018.0','2019.0', '2020.0', '2021.0', '2022.0', '2023.0', '2024.0', '2025.0','2026.0', '2027.0', '2028.0', '2029.0', '2030.0']] = df4[['2004.0','2005.0', '2006.0', '2007.0', '2008.0', '2009.0', '2010.0', '2011.0','2012.0', '2013.0', '2014.0', '2015.0', '2016.0', '2017.0', '2018.0','2019.0', '2020.0', '2021.0', '2022.0', '2023.0', '2024.0', '2025.0','2026.0', '2027.0', '2028.0', '2029.0', '2030.0']].multiply(df4['fraction'], axis = "index")
        df = df4

        
    elif row['MRF_model'] == "paper":
        
        #average = 19.814
        
        save_pet_df = pd.read_csv('./projected_by_population/PET_Bottles_recycled_projected_amounts_to_relog.csv')
        fraction = pd.read_csv('paper_fraction.csv')
        fraction = fraction[fraction['fraction']!=0]
        avg = np.mean(fraction['fraction'])
        df2 = save_pet_df[['State','name']]
        df3 = df2.merge(fraction,on = 'State', how = 'outer')
        df3 = df3.fillna(avg)
        df4 = save_pet_df.merge(df3,on=['State','name'])
        df4[['2004.0','2005.0', '2006.0', '2007.0', '2008.0', '2009.0', '2010.0', '2011.0','2012.0', '2013.0', '2014.0', '2015.0', '2016.0', '2017.0', '2018.0','2019.0', '2020.0', '2021.0', '2022.0', '2023.0', '2024.0', '2025.0','2026.0', '2027.0', '2028.0', '2029.0', '2030.0']] = df4[['2004.0','2005.0', '2006.0', '2007.0', '2008.0', '2009.0', '2010.0', '2011.0','2012.0', '2013.0', '2014.0', '2015.0', '2016.0', '2017.0', '2018.0','2019.0', '2020.0', '2021.0', '2022.0', '2023.0', '2024.0', '2025.0','2026.0', '2027.0', '2028.0', '2029.0', '2030.0']].multiply(df4['fraction'], axis = "index")
        df = df4
        


        
    df['State_County'] = df['State'] + "_" +df['name']
    df = df[['name', 'State','State_County','latitude (deg)', 'longitude (deg)', '2004.0',
           '2005.0', '2006.0', '2007.0', '2008.0', '2009.0', '2010.0', '2011.0',
           '2012.0', '2013.0', '2014.0', '2015.0', '2016.0', '2017.0', '2018.0',
           '2019.0', '2020.0', '2021.0', '2022.0', '2023.0', '2024.0', '2025.0',
           '2026.0', '2027.0', '2028.0', '2029.0', '2030.0',]]
    df.to_csv('./grouped_name_paper_film_correction/'+row['MRF_model'] + 'projected_amounts_to_relog_grouped.csv') 

#%%
#Other
o_df = pd.DataFrame()
for i in range(1,5):
    df = pd.read_csv('./grouped_name_paper_film_correction/'+'other'+str(i)+'projected_amounts_to_relog_grouped.csv')
    o_df = pd.concat([o_df,df])
    
    
o_df2 = o_df.groupby(['name', 'State', 'State_County', 'latitude (deg)',
        'longitude (deg)'])[['2004.0', '2005.0', '2006.0', '2007.0', '2008.0',
'2009.0', '2010.0', '2011.0', '2012.0', '2013.0', '2014.0', '2015.0',
'2016.0', '2017.0', '2018.0', '2019.0', '2020.0', '2021.0', '2022.0',
'2023.0', '2024.0', '2025.0', '2026.0', '2027.0', '2028.0', '2029.0',
'2030.0']].agg('sum').reset_index()
 
o_df2.to_csv('./grouped_name_paper_film_correction/'+'other_projected_amounts_to_relog_grouped.csv')
    
    
    