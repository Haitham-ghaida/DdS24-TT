#Using population projected data to project waste production data for every country

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

pop_projection_df = pd.read_csv('county_population_projected_data.csv')
county_centroid = pd.read_csv('county_centroid_information.csv')
state_abbv = pd.read_csv('state-abbreviation.csv')
county_centroid = county_centroid[['State_code','Latitude', 'Longitude','county']].astype('str')
county_centroid = county_centroid.merge(state_abbv, on = ['State_code'])


collection_rate = pd.read_csv('state-collection-rate.csv')
collection_rate = collection_rate[collection_rate['Year'] == 0]
collection_rate = collection_rate.groupby(['Year', 'scenario'], as_index = False).mean()
collection_rate['State'] = collection_rate['scenario']


for m in mat:
    
    data3 = pd.read_csv('../grouped_data_files/'+m+'_data_grouped.csv')
    del data3['Population']
    data3 = data3.merge(pop_projection_df,on=['State','county'])
    data3[m+'_Tons_Generated_total'] = data3[m+'_Tons_Generated_Per_Capita'] * data3['Population']
    data3[m+'_Generated_total_metrictonnes'] = data3[m+'_Tons_Generated_total'] * 907.185/1000
    data3[m+'_Tons_Recycled_total'] = data3[m+'_Tons_Recycled_Per_Capita'] * data3['Population']
    data3[m+'_Recycled_total_metrictonnes'] = data3[m+'_Tons_Recycled_total'] * 907.185/1000 
    
    #data3.to_csv(m+'_data_grouped_projected_data.csv',index=False)
    
    df2 = data3.merge(county_centroid, on = ['county','State'],how='left')
    #df2 = df2.merge(collection_rate,on=['State'])
    #Fix this part to use collection rate for PET bottles.
    df2['latitude (deg)'] = df2['Latitude'].str.replace("°","")
    df2['longitude (deg)'] = df2['Longitude'].str.replace("°","")
    df2['latitude (deg)'] = df2['Latitude'].str.replace("°","")
    df2['longitude (deg)'] = df2['Longitude'].str.replace("°","")
    
    df2['name'] = df2['county']
    
    #ASK THIS STRANGE ISSUE
    #df2['amount 1'] = df2[m+'_Tons_Recycled_total_kg']/1000
    #df2['amount1'] = df2['amount1'] * (1-df2['trash'])
    #Fix this part to use collection rate for PET bottles.
    df2 = df2[['name','State','latitude (deg)','longitude (deg)','Year',m+'_Generated_total_metrictonnes',m+'_Recycled_total_metrictonnes']].dropna()
    df2 = df2.sort_values(by=['name'])
    #print(df2['amount 1'].sum(),m)
    
    #Dont do this. Argonne will multiply collection rate 
    if m == 'PET_Bottles' or m == 'HDPE_Bottles':
       df3 = df2.pivot_table(index=['name','State','latitude (deg)','longitude (deg)'],columns=['Year'],values=[m+'_Generated_total_metrictonnes']).reset_index()
       df4 = df2.pivot_table(index=['name','State','latitude (deg)','longitude (deg)'],columns=['Year'],values=[m+'_Recycled_total_metrictonnes']).reset_index()
    

    else:
       df3 = df2.pivot_table(index=['name','State','latitude (deg)','longitude (deg)'],columns=['Year'],values=[m+'_Recycled_total_metrictonnes']).reset_index()
    
    cols = ['name','State','latitude (deg)','longitude (deg)',2004.0, 2005.0, 2006.0, 2007.0, 2008.0, 2009.0,
           2010.0, 2011.0, 2012.0, 2013.0, 2014.0, 2015.0, 2016.0, 2017.0, 2018.0,
           2019.0, 2020.0, 2021.0, 2022.0, 2023.0, 2024.0, 2025.0, 2026.0, 2027.0,
           2028.0, 2029.0, 2030.0]
    
    df3.columns = df3.columns.droplevel()
    df3.columns = cols
    #df3 = df3.replace(0,np.nan).dropna()
    
    df3.to_csv(m+'projected_amounts_to_relog.csv',index=False)
    
    if m == 'PET_Bottles' or m == 'HDPE_Bottles':
        df4.columns = df4.columns.droplevel()
        df4.columns = cols
        df4.to_csv(m+'_recycled_projected_amounts_to_relog.csv',index=False) 


