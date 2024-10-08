import pandas as pd 

df = pd.read_csv("./input/efficiency.csv")
df2 = df['year-source-targetmaterial'].str.split(' ', n = 1, expand = True)
df['year'] = df2[0]
df['source_target'] = df2[1]
df2 = pd.pivot_table(df, values=['efficiency'], index=['year'], columns=['source_target']).reset_index()
df2.columns = df2.columns.droplevel(0)
df2 = df2.rename(columns={"":"year"})
df2.to_csv("eff_pivoted.csv")


df3 = df2.melt(id_vars=['year'],value_vars=['discreen1 cardboard', 'discreen1 paper', 'discreen2 cardboard',
       'discreen2 film', 'discreen2 paper', 'eddy aluminum', 'eddy glass',
       'glass_breaker glass', 'magnet film', 'magnet iron', 'magnet other',
       'nir_hdpe aluminum', 'nir_hdpe cardboard', 'nir_hdpe film',
       'nir_hdpe glass', 'nir_hdpe hdpe', 'nir_hdpe other', 'nir_hdpe paper',
       'nir_hdpe pet', 'nir_pet aluminum', 'nir_pet cardboard', 'nir_pet film',
       'nir_pet glass', 'nir_pet hdpe', 'nir_pet other', 'nir_pet paper',
       'nir_pet pet', 'vacuum cardboard', 'vacuum film', 'vacuum paper'],var_name='year-source-targetmaterial',value_name='efficiency')

df3['year-source-targetmaterial'] = df3['year'] + ' ' + df3['year-source-targetmaterial']
df3 = df3[['year-source-targetmaterial','efficiency']]
df3.to_csv('efficiency_updated.csv',index = False)




