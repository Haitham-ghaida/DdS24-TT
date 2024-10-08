import pandas as pd
import numpy as np

mat =  ['pet',
        'film',
        'cardboard',
        'glass',
        'paper',
        'hdpe',
        'iron',
        'aluminum',
        'other']

years = ['2004.0', '2005.0', '2006.0', '2007.0', '2008.0',
'2009.0', '2010.0', '2011.0', '2012.0', '2013.0', '2014.0', '2015.0',
'2016.0', '2017.0', '2018.0', '2019.0', '2020.0', '2021.0', '2022.0',
'2023.0', '2024.0', '2025.0', '2026.0', '2027.0', '2028.0', '2029.0',
'2030.0']

years2 = [float(x) for x in years]

years3 = []
for y1 in range(2031,2051):
    years3.append(y1)
    
    
from sklearn import linear_model    
import numpy as np


for m in mat:
    df = pd.read_csv('./grouped_name_paper_film_correction/'+m+'projected_amounts_to_relog_grouped.csv')
    df = df.fillna(0)
    projected_df = pd.DataFrame()
    
    for index,row in df.iterrows():
        one_row = []
        for y in years:
            try:
                one_row.append(row[y])
            except:
                one_row.append(row[str(int(float(y)))])
            
        Y = np.array(one_row)
        X = np.array(years2).reshape((-1, 1))
        
        regr = linear_model.LinearRegression()
        regr.fit(X,Y)
        
        predicted_data = regr.predict(np.array(years3).reshape((-1, 1)))
    
        tdf = pd.DataFrame([predicted_data],columns = years3)
        projected_df = pd.concat([projected_df,tdf])
    
        
        #projected = regr.predict(2031)
    projected_df = projected_df.reset_index()    
    final_df = pd.concat([df,projected_df],axis = 1)
    try:
        del final_df['Unnamed: 0']
    except:
        pass
    final_df.to_csv('./projected_by_linear_model_to_2050/'+m+'projected_amounts_to_relog_grouped_2050.csv')


