import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import matplotlib
matplotlib.rcParams.update(matplotlib.rcParamsDefault)
sns.set_style("ticks")
sns.color_palette('bright')
sns.set_context('paper')



def bar_compare_graphs_without_manuf(df,sc,ind,lab):


        
        df_s = df[df['scenario'] == sc]
        df_s[ind] = df_s[ind].astype('float')

        
        #df1 = df_s[df_s['stage'] == 'Chem. Recycling']
        #df2 = df_s[df_s['stage'] == 'MRF' ]
        #df3 = df_s[df_s['stage'] == 'Manufacturing costs virgin PET' ]
        #df4 = df_s[df_s['stage'] == 'Mech. Recycling']
        #df5 = df_s[df_s['stage'] == 'waste_collection']
        
        if sc != 'Norecycling':
          df_s = df_s[df_s['stage'] != 'Virgin polymer manufacturing cost']


        if sc != 'Norecycling':
          df_s = df_s[df_s['stage'] != 'Resin manufacturing']

        
        df1_1 = df_s.groupby(['year', 'stage'])[ind].sum().unstack().fillna(0)
        
        
        ax1 = df1_1.plot(figsize = (20,10),kind='bar', stacked=True,width=0.5)
        #ax1.set_ylim([0, 10e9])
        plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)
        ax1.set_ylabel(lab, fontsize = 16)
        ax1.set_xlabel('year', fontsize = 16)
        plt.legend(fontsize=16)
        #plt.show()    
       
        fig = ax1.get_figure()
        fig.savefig('./output/'+sc+ind+lab+'_compare.png',bbox_inches='tight')



def bar_compare_graphs_without_manuf2(df,sc,ind,lab):

        df = df[(df['year'] == 2020) | (df['year'] == 2035) | (df['year'] == 2049)]        
        df_s = df[df['scenario'] == sc]
        df_s[ind] = df_s[ind].astype('float')

        
        if sc != 'Norecycling':
          df_s = df_s[df_s['stage'] != 'Virgin polymer manufacturing cost']


        if sc != 'Norecycling':
          df_s = df_s[df_s['stage'] != 'Resin manufacturing']

        
        df1_1 = df_s.groupby(['year', 'stage'])[ind].sum().unstack().fillna(0)
        
        
        ax1 = df1_1.plot(figsize = (20,10),kind='bar', stacked=True,width=0.5)
        plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)
        ax1.set_ylabel(lab, fontsize = 16)
        ax1.set_xlabel('year', fontsize = 16)
        
        #ax1.set_ylim([0, 3e9])
        
        plt.legend(fontsize=14)
        #plt.show()    
       
        fig = ax1.get_figure()
        fig.savefig('./output/'+sc+ind+lab+'_compare_3_years.png',bbox_inches='tight')


def bar_compare_graphs_with_manuf(df,sc,ind,lab):
        
        df_s = df[df['scenario'] == sc]
        df_s[ind] = df_s[ind].astype('float')

        
        #df1 = df_s[df_s['stage'] == 'Chem. Recycling']
        #df2 = df_s[df_s['stage'] == 'MRF' ]
        #df3 = df_s[df_s['stage'] == 'Manufacturing costs virgin PET' ]
        #df4 = df_s[df_s['stage'] == 'Mech. Recycling']
        #df5 = df_s[df_s['stage'] == 'waste_collection']
        
       
        df1_1 = df_s.groupby(['year', 'stage'])[ind].sum().unstack().fillna(0)
        
        
        ax1 = df1_1.plot(figsize = (20,10),kind='bar', stacked=True,width=0.5)
        plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)
        ax1.set_ylabel(lab, fontsize = 16)
        ax1.set_xlabel('year', fontsize = 16)
        plt.legend(fontsize=16)
        #plt.show()    

        fig = ax1.get_figure()
        fig.savefig('./output/'+sc+lab+'_compare_with_manuf.png',bbox_inches='tight')


def bar_circularity(df,sc,ind,lab):
    
        df_s = df[df['scenario'] == sc]
        df_s[ind] = df_s[ind].astype('float')

        
        #df1 = df_s[df_s['stage'] == 'Chem. Recycling']
        #df2 = df_s[df_s['stage'] == 'MRF' ]
        #df3 = df_s[df_s['stage'] == 'Manufacturing costs virgin PET' ]
        #df4 = df_s[df_s['stage'] == 'Mech. Recycling']
        #df5 = df_s[df_s['stage'] == 'waste_collection']

        
        ax1 = df_s.plot(x = 'year', y = ind, figsize = (20,10),kind='bar',width=0.5)
        plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)
        ax1.set_ylabel(lab, fontsize = 16)
        ax1.set_xlabel('year', fontsize = 16)
        plt.legend(fontsize=16)
        #plt.show()    
        
        



        fig = ax1.get_figure()
        fig.savefig('./output/'+sc+lab+'_compare.png',bbox_inches='tight')
    
    


def compare_results(totlc,us_results, us_lcia_results,totl_cost):
            
        totlc = pd.read_csv(totlc)
        us_results = pd.read_csv(us_results)   
        us_lcia_results = pd.read_csv(us_lcia_results)  
        totl_cost2 = pd.read_csv(totl_cost)

        

        cols = ['vmanuf_cost_of_production','collection_cost_waste_plastic','landfill_transportation_cost_waste_plastic','wte_transportation_cost_waste_plastic','mrf_transportation_cost_waste_plastic','mrf_sorting_cost_plastic','transportation_cost_mrf_to_reclaimer','mechanical_reclaiming_cost','chemical_reclaiming_cost','pyrolysis_upcycling_cost','fiber_resin_upcycling_cost','landfill_costs','incineration_cost']
        totl_cost = totl_cost2.melt(id_vars=['year','scenario'],value_vars=cols,var_name='stage',value_name='costs')

        circ_bridge = pd.read_csv('./input/core_files/circularity_name_bridge.csv')
        totlc = totlc.merge(circ_bridge, on = ['circularity'])
        totlc['circularity'] = totlc['circularity_n']

        stage_bridge = pd.read_csv('./input/core_files/stage_name_bridge.csv')
        totl_cost = totl_cost.merge(stage_bridge, on = ['stage'])
        totl_cost['stage'] = totl_cost['stage_n']
        
        process_bridge = pd.read_csv('./input/core_files/process_name_bridge.csv')
        us_lcia_results['stage'] = us_lcia_results['process']
        us_lcia_results = us_lcia_results.merge(process_bridge, on = ['stage'])
        us_lcia_results['stage'] = us_lcia_results['stage_n']


        df = totl_cost
        df['costs'] = df['costs'].astype('float')
        df['year'] = df['year'].astype('int')
        
        
        scenarios = list(pd.unique(df['scenario']))
        for sc in scenarios:
            print(sc)
            bar_compare_graphs_without_manuf(df,sc,'costs','cost ($)')
            bar_compare_graphs_with_manuf(df,sc,'costs','cost ($)')
            bar_compare_graphs_without_manuf2(df,sc,'costs','cost ($)')

        df = us_lcia_results
        

        scenarios = list(pd.unique(df['scenario']))
        
        for sc in scenarios:
            print(sc)
            bar_compare_graphs_without_manuf(df,sc,'impact','Global Warming kgCo2eq.')
            bar_compare_graphs_with_manuf(df,sc,'impact','Global Warming kgCo2eq.')
            bar_compare_graphs_without_manuf2(df,sc,'impact','Global Warming kgCo2eq.')


        scenarios = list(pd.unique(totlc['scenario']))
        
        
        for sc in scenarios:
            print(sc)
            df = totlc[totlc['scenario'] == sc]  
            df = df[df['circularity'] == 'Material Circularity Index']       
            fig3, ax3 = plt.subplots(figsize = (20,6))
            ax3 = sns.lineplot(df['year'],df['cvalue'],hue=df['circularity'])
            def change_width(ax3, new_value):
                for patch in ax3.patches :
                    current_width = patch.get_width()
                    diff = current_width - new_value
            
                    # we change the bar width
                    patch.set_width(new_value)
            
                    # we recenter the bar
                    patch.set_x(patch.get_x() + diff * .5)
        
            change_width(ax3, 0.15)
           
            plt.xticks(fontsize=14)
            plt.yticks(fontsize=14)
            ax3.set_ylabel('Circularity Value', fontsize = 16)
            ax3.set_xlabel('year', fontsize = 16)
            plt.legend(fontsize=16)
            fig3.savefig('./output/'+sc+'circularitylineplots.png', bbox_inches = 'tight')   
            
        for sc in scenarios:
            print(sc)
            df = totlc[totlc['scenario'] == sc]   
            df = df[df['circularity'] == 'Material Circularity Index'] 
            df = df[(df['year'] == 2020) | (df['year'] == 2035) | (df['year'] == 2049)]     
            fig3, ax3 = plt.subplots(figsize = (20,6))
            ax3 = sns.barplot(df['year'],df['cvalue'],hue=df['circularity'])
            def change_width(ax3, new_value):
                for patch in ax3.patches :
                    current_width = patch.get_width()
                    diff = current_width - new_value
            
                    # we change the bar width
                    patch.set_width(new_value)
            
                    # we recenter the bar
                    patch.set_x(patch.get_x() + diff * .5)
        
            change_width(ax3, 0.15)
           
            plt.xticks(fontsize=14)
            plt.yticks(fontsize=14)
            plt.legend(fontsize=16)
            ax3.set_ylabel('Circularity Value', fontsize = 16)
            ax3.set_xlabel('year', fontsize = 16)
            fig3.savefig('./output/'+sc+'circularitybarplots_3_years.png', bbox_inches = 'tight') 


'''
def graph1(totlc,us_results,us_lca_results,totl_cost):
    
    fig1, ax1 = plt.subplots()
    fig1.tight_layout(pad=3.0)


    ax1 = sns.scatterplot(ax=ax1, x=us_results['year'], y=us_results['rpet_manuf'], linewidth=2, hue=us_results['grade'], palette='bright', legend=True)
    ax1.set_ylabel(ylabel='mmlbs')
    ax1.set_xlabel(xlabel='year')


    fig1.tight_layout()
    fig1.subplots_adjust(bottom=0.1)
    #plt.legend(handles=h, labels=l,frameon=True,loc='lower center')
    #fig1.legend(['United States','China','Global','United States(rcp)','China(rcp)','Global(rcp)'],loc="lower center", ncol=2, nrow = 3)
    plt.show()
    fig1.savefig('Circularity1.png',dpi=300)
    
                                                                                                                                                                                                                                                                                         
    
    fig3, ax3 = plt.subplots()
    ax3 = sns.scatterplot(totlc['year'],totlc['circularity'])
    #ax3 = sns.lineplot(conventional['year'],conventional['rec_rate'], label = 'Recycling Rate', hue = conventional['grade'],legend = False)
    ax3.legend()
    plt.show()
    fig3.savefig('Circularity2.png',dpi=300)
    
    
    #fig4, ax4 = plt.subplots()
    #ax4 = sns.lineplot(totlc['year'],totlc['landfill'].cumsum())
    #ax3 = sns.lineplot(conventional['year'],conventional['rec_rate'], label = 'Recycling Rate', hue = conventional['grade'],legend = False)
    #ax4.legend()
    #plt.show()
    #fig4.savefig('Circularity3.png',dpi=300)


    fig5, ax5 = plt.subplots()
    ax5 = sns.scatterplot(totlc['year'],totlc['rec_mass'])
    #ax3 = sns.lineplot(conventional['year'],conventional['rec_rate'], label = 'Recycling Rate', hue = conventional['grade'],legend = False)
    ax5.legend()
    plt.show()
    fig5.savefig('Circularity4.png',dpi=300)

    fig6, ax6 = plt.subplots()
    ax6 = sns.scatterplot(totl_cost['year'],totl_cost['costs'], hue = totl_cost['stage'])
    #ax3 = sns.lineplot(conventional['year'],conventional['rec_rate'], label = 'Recycling Rate', hue = conventional['grade'],legend = False)
    ax6.legend()
    plt.show()
    fig6.savefig('Cost.png',dpi=300)

    fig7, ax7 = plt.subplots()
    ax7 = sns.scatterplot(us_lca_results['year'],us_lca_results['value'], hue = us_lca_results['process'])
    ax7.set_ylabel('lcia impact')
    #ax3 = sns.lineplot(conventional['year'],conventional['rec_rate'], label = 'Recycling Rate', hue = conventional['grade'],legend = False)
    ax7.legend()
    plt.show()
    fig7.savefig('lca.png',dpi=300)

    

        



def group(df,col):
    
    df = df[df['year'] != 'year']
    df[col] = df[col].astype('float')
    df = df.groupby(['year','scenario'])[col].agg('sum')
    return df.reset_index()
    

def comparison_graph():
    
        totlc = pd.read_csv('total_circularity_results.csv')
        us_results = pd.read_csv('total_flow_results.csv')   
        us_lcia_results2 = pd.read_csv('final_lcia_results.csv')  
        totl_cost = pd.read_csv('total_cost.csv')
    
        df = group(totl_cost,'costs')
        
        
        fig1, ax1 = plt.subplots(figsize = (20,3))
        ax1 = sns.barplot(x=df['year'], y=df['costs'], hue=df['scenario'])
        ax1.set_ylabel('costs', fontsize = 16)
        ax1.legend()
        plt.show()
        
        
        
        
        df = group(us_lcia_results2,'value')
        
        
        fig7, ax7 = plt.subplots(figsize = (20,3))
        ax7 = sns.barplot(x=df['year'], y=df['value'], hue=df['scenario'])
        ax7.set_ylabel('lcia impact')
        ax7.legend()
        plt.show()
        
        
        
        df = group(totlc,'rec_mass')
        
                      
        fig2, ax2 = plt.subplots(figsize = (20,3))
        ax2 = sns.barplot(x=df['year'], y=df['rec_mass'], hue=df['scenario'])
        ax2.set_ylabel('Recycled PET mass', fontsize = 16)
        ax2.legend()
        plt.show()
        
        
        
        df = group(totlc,'circularity')
        
        
        fig3, ax3 = plt.subplots(figsize = (20,3))
        ax3 = sns.barplot(x=df['year'], y=df['circularity'], hue=df['scenario'])
        ax3.set_ylabel('circularity', fontsize = 16)
        plt.legend(fontsize=16)
        plt.show()

def bar_compare_graphs_without_manuf(df,sc,ind,lab):
        
        df_s = df[df['scenario'] == sc]
        df_s[ind] = df_s[ind].astype('float')

        
        #df1 = df_s[df_s['stage'] == 'Chem. Recycling']
        #df2 = df_s[df_s['stage'] == 'MRF' ]
        #df3 = df_s[df_s['stage'] == 'Manufacturing costs virgin PET' ]
        #df4 = df_s[df_s['stage'] == 'Mech. Recycling']
        #df5 = df_s[df_s['stage'] == 'waste_collection']
        
        if sc != 'Norecycling':
          df_s = df_s[df_s['stage'] != 'Manufacturing costs virgin PET']


        if sc != 'Norecycling':
          df_s = df_s[df_s['stage'] != 'Resin manufacturing']

        
        df1_1 = df_s.groupby(['year', 'stage'])[ind].sum().unstack().fillna(0)
        
        
        ax1 = df1_1.plot(figsize = (20,6),kind='bar', stacked=True,width=0.5)
        plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)
        ax1.set_ylabel(lab, fontsize = 16)
        ax1.set_xlabel('year', fontsize = 16)
        plt.legend(fontsize=16)
        plt.show()    
        
        



        fig = ax1.get_figure()
        fig.savefig(sc+ind+lab+'_compare.png',bbox_inches='tight')


def bar_compare_graphs_with_manuf(df,sc,ind,lab):
        
        df_s = df[df['scenario'] == sc]
        df_s[ind] = df_s[ind].astype('float')

        
        #df1 = df_s[df_s['stage'] == 'Chem. Recycling']
        #df2 = df_s[df_s['stage'] == 'MRF' ]
        #df3 = df_s[df_s['stage'] == 'Manufacturing costs virgin PET' ]
        #df4 = df_s[df_s['stage'] == 'Mech. Recycling']
        #df5 = df_s[df_s['stage'] == 'waste_collection']
        
       
        df1_1 = df_s.groupby(['year', 'stage'])[ind].sum().unstack().fillna(0)
        
        
        ax1 = df1_1.plot(figsize = (20,6),kind='bar', stacked=True,width=0.5)
        plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)
        ax1.set_ylabel(lab, fontsize = 16)
        ax1.set_xlabel('year', fontsize = 16)
        plt.legend(fontsize=16)
        plt.show()    

        



        fig = ax1.get_figure()
        fig.savefig(sc+lab+'_compare_with_manuf.png',bbox_inches='tight')


def bar_circularity(df,sc,ind,lab):
    
        df_s = df[df['scenario'] == sc]
        df_s[ind] = df_s[ind].astype('float')

        
        #df1 = df_s[df_s['stage'] == 'Chem. Recycling']
        #df2 = df_s[df_s['stage'] == 'MRF' ]
        #df3 = df_s[df_s['stage'] == 'Manufacturing costs virgin PET' ]
        #df4 = df_s[df_s['stage'] == 'Mech. Recycling']
        #df5 = df_s[df_s['stage'] == 'waste_collection']

        
        ax1 = df_s.plot(x = 'year', y = ind, figsize = (20,6),kind='bar',width=0.5)
        plt.xticks(fontsize=14)
        plt.yticks(fontsize=14)
        ax1.set_ylabel(lab, fontsize = 16)
        ax1.set_xlabel('year', fontsize = 16)
        plt.legend(fontsize=16)
        plt.show()    
        
        



        fig = ax1.get_figure()
        fig.savefig(sc+lab+'_compare.png',bbox_inches='tight')
    
    


def compare_results():
            
        totlc = pd.read_csv('total_circularity_results.csv')
        us_results = pd.read_csv('total_flow_results.csv')   
        us_lcia_results = pd.read_csv('final_lcia_results.csv')  
        totl_cost = pd.read_csv('total_cost.csv')
        
        circ_bridge = pd.read_csv('circularity_name_bridge.csv')
        totlc = totlc.merge(circ_bridge, on = ['circularity'])
        totlc['circularity'] = totlc['circularity_n']

        stage_bridge = pd.read_csv('stage_name_bridge.csv')
        totl_cost = totl_cost.merge(stage_bridge, on = ['stage'])
        totl_cost['stage'] = totl_cost['stage_n']
        process_bridge = pd.read_csv('process_name_bridge.csv')
        us_lcia_results = us_lcia_results.merge(process_bridge, on = ['stage'])
        us_lcia_results['stage'] = us_lcia_results['stage_n']

        
        df = totl_cost
        df['costs'] = df['costs'].astype('float')
        df['year'] = df['year'].astype('int')
        
        
        scenarios = list(pd.unique(df['scenario']))
        
        for sc in scenarios:
            print(sc)
            bar_compare_graphs_without_manuf(df,sc,'costs','cost ($)')
            bar_compare_graphs_with_manuf(df,sc,'costs','cost ($)')

        

        df = us_lcia_results

        scenarios = list(pd.unique(df['scenario']))
        
        for sc in scenarios:
            print(sc)
            bar_compare_graphs_without_manuf(df,sc,'value','Global Warming kgCo2eq.')
            bar_compare_graphs_with_manuf(df,sc,'value','Global Warming kgCo2eq.')

        

        scenarios = list(pd.unique(totlc['scenario']))
        
        for sc in scenarios:
            print(sc)
            df = totlc[totlc['scenario'] == sc]         
            fig3, ax3 = plt.subplots(figsize = (20,6))
            ax3 = sns.lineplot(df['year'],df['cvalue'],hue=df['circularity'])
            def change_width(ax3, new_value):
                for patch in ax3.patches :
                    current_width = patch.get_width()
                    diff = current_width - new_value
            
                    # we change the bar width
                    patch.set_width(new_value)
            
                    # we recenter the bar
                    patch.set_x(patch.get_x() + diff * .5)
        
            change_width(ax3, 0.15)
           
            plt.xticks(fontsize=14)
            plt.yticks(fontsize=14)
            ax3.set_ylabel('Circularity Value', fontsize = 16)
            ax3.set_xlabel('year', fontsize = 16)
            plt.legend(fontsize=16)
            fig3.savefig(sc+'circularitylineplots.png', bbox_inches = 'tight')   
            
        for sc in scenarios:
            print(sc)
            df = totlc[totlc['scenario'] == sc]         
            fig3, ax3 = plt.subplots(figsize = (20,6))
            ax3 = sns.barplot(df['year'],df['cvalue'],hue=df['circularity'])
            def change_width(ax3, new_value):
                for patch in ax3.patches :
                    current_width = patch.get_width()
                    diff = current_width - new_value
            
                    # we change the bar width
                    patch.set_width(new_value)
            
                    # we recenter the bar
                    patch.set_x(patch.get_x() + diff * .5)
        
            change_width(ax3, 0.15)
           
            plt.xticks(fontsize=14)
            plt.yticks(fontsize=14)
            plt.legend(fontsize=16)
            ax3.set_ylabel('Circularity Value', fontsize = 16)
            ax3.set_xlabel('year', fontsize = 16)
            fig3.savefig(sc+'circularitybarplots.png', bbox_inches = 'tight')               

def comparison_of_scenarios():
    
        totlc = pd.read_csv('total_circularity_results.csv')
        us_results = pd.read_csv('total_flow_results.csv')   
        us_lcia_results = pd.read_csv('final_lcia_results.csv')  
        totl_cost = pd.read_csv('total_cost.csv')
        
        df_circ = totlc[['year','circularity','scenario','cvalue']]
        df_circ = df_circ.sort_values(by = ['year','scenario'])
        circ = list(pd.unique(df_circ['circularity']))
        
        
        for c in circ:
            df_circ2 = df_circ[df_circ['circularity'] == c]
            fig3, ax3 = plt.subplots()
            ax3 = sns.lineplot(df_circ2['year'],df_circ2['cvalue'],linewidth=2, hue=df_circ2['scenario'])
            #ax3 = sns.lineplot(conventional['year'],conventional['rec_rate'], label = 'Recycling Rate', hue = conventional['grade'],legend = False)
            ax3.legend()
            plt.title(c)
            plt.show()
            fig3.savefig(c+'comparisoncircline.png',dpi=300)
        
        
        #fig3, ax3 = plt.subplots(figsize = (20,4))
        #ax3 = sns.barplot(df_circ['year'],df_circ['circularity'],hue=df_circ['scenario'])
        #ax3 = sns.lineplot(conventional['year'],conventional['rec_rate'], label = 'Recycling Rate', hue = conventional['grade'],legend = False)
        #ax3.legend()
        #plt.show()
        #fig3.savefig('comparisoncircbar.png',dpi=300)
        
        
        
        
        
        df_circ = us_lcia_results
        df_circ = df_circ[df_circ['year'] != 2019]
        df_circ = df_circ.groupby(['year','lcia','scenario'])['value'].agg('sum').reset_index()
        df_circ = df_circ.sort_values(by = ['year','scenario'])
        fig3, ax3 = plt.subplots()
        ax3 = sns.lineplot(df_circ['year'],df_circ['value'],linewidth=2, hue=df_circ['scenario'])
        #ax3 = sns.lineplot(conventional['year'],conventional['rec_rate'], label = 'Recycling Rate', hue = conventional['grade'],legend = False)
        ax3.set_ylabel('Global warming kgCO2eq./year')
        ax3.legend()
        plt.show()
        fig3.savefig('comparisonlcialine.png',dpi=300) 
        
        
        
        df_circ = us_lcia_results
        df_circ = df_circ[df_circ['year'] != 2019]
        df_circ = df_circ.groupby(['year','lcia','scenario'])['value'].agg('sum').reset_index()
        df_circ = df_circ.sort_values(by = ['year','scenario'])
        fig3, ax3 = plt.subplots(figsize = (20,4))
        ax3 = sns.barplot(df_circ['year'],df_circ['value'],hue=df_circ['scenario'])
        #ax3 = sns.lineplot(conventional['year'],conventional['rec_rate'], label = 'Recycling Rate', hue = conventional['grade'],legend = False)
        ax3.set_ylabel('Global warming kgCO2eq./year')
        ax3.legend()
        plt.show()
        fig3.savefig('comparisonlciabar.png',dpi=300) 
        
        
        
        
        
        df_circ = totl_cost
        df_circ = df_circ[df_circ['year'] != 2019]
        df_circ = df_circ.groupby(['year','scenario'])['costs'].agg('sum').reset_index()
        df_circ = df_circ.sort_values(by = ['year','scenario'])
        fig3, ax3 = plt.subplots()
        ax3 = sns.lineplot(df_circ['year'],df_circ['costs'],linewidth=2, hue=df_circ['scenario'])
        #ax3 = sns.lineplot(conventional['year'],conventional['rec_rate'], label = 'Recycling Rate', hue = conventional['grade'],legend = False)
        ax3.set_ylabel('Costs ($)/year')
        ax3.legend()
        plt.show()
        fig3.savefig('comparisoncostsline.png',dpi=300) 
        
        
        
        df_circ = totl_cost
        df_circ = df_circ[df_circ['year'] != 2019]
        df_circ = df_circ.groupby(['year','scenario'])['costs'].agg('sum').reset_index()
        df_circ = df_circ.sort_values(by = ['year','scenario'])
        fig3, ax3 = plt.subplots(figsize = (20,4))
        ax3 = sns.barplot(df_circ['year'],df_circ['costs'],hue=df_circ['scenario'])
        #ax3 = sns.lineplot(conventional['year'],conventional['rec_rate'], label = 'Recycling Rate', hue = conventional['grade'],legend = False)
        ax3.legend()
        plt.show()
        fig3.savefig('comparisoncostsbar.png',dpi=300) 



def single_scenario_plots():

    totlc = pd.read_csv('total_circularity_results.csv')
    us_results = pd.read_csv('total_flow_results.csv')   
    us_lcia_results = pd.read_csv('final_lcia_results.csv')  
    totl_cost = pd.read_csv('total_cost.csv')
    
    df_circ = totlc[['year','circularity','scenario']]
    df_circ = df_circ.sort_values(by = ['year','scenario'])
    
    
    df_lcia = us_results.merge(us_lcia_results, on = ['year','scenario'])
    
    df_lcia = df_lcia[['year','scenario','stage', 'lcia', 'value','use_to_dispose']]
    
    df_lcia = df_lcia.groupby(['year','scenario','lcia','use_to_dispose'])['value'].agg(sum).reset_index()
    
    
    df_lcia['value/unit'] = df_lcia['value']/(df_lcia['use_to_dispose']*1000000*0.453)
    
    fig3, ax3 = plt.subplots()
    ax3 = sns.lineplot(df_lcia['year'],df_lcia['value/unit'],linewidth=2, hue=df_lcia['scenario'])
    ax3.legend()
    plt.show()
    fig3.savefig('comparisonlcaiperunitline.png',dpi=300)   
    
    fig3, ax3 = plt.subplots(figsize = (20,4))
    ax3 = sns.barplot(df_lcia['year'],df_lcia['value/unit'],hue=df_lcia['scenario'])
    ax3.legend()
    plt.show()
    fig3.savefig('comparisonlcaiperunitbar.png',dpi=300)   
    
    
    

    fig3, ax3 = plt.subplots()
    ax3 = sns.lineplot(df_circ['year'],df_circ['circularity'],linewidth=2, hue=df_circ['scenario'])
    #ax3 = sns.lineplot(conventional['year'],conventional['rec_rate'], label = 'Recycling Rate', hue = conventional['grade'],legend = False)
    ax3.legend()
    plt.show()
    fig3.savefig('comparisoncircline.png',dpi=300)       
    
    
    
    fig3, ax3 = plt.subplots(figsize = (20,4))
    ax3 = sns.barplot(df_circ['year'],df_circ['circularity'],hue=df_circ['scenario'])
    #ax3 = sns.lineplot(conventional['year'],conventional['rec_rate'], label = 'Recycling Rate', hue = conventional['grade'],legend = False)
    ax3.legend()
    plt.show()
    fig3.savefig('comparisoncircbar.png',dpi=300)

    
      
    df_lcia = us_lcia_results
    df_lcia = df_lcia[df_lcia['year'] != 2019]
    df_lcia = df_lcia.groupby(['year','lcia','scenario'])['value'].agg('sum').reset_index()
    df_lcia = df_lcia.sort_values(by = ['year','scenario'])        
    df_lcia_func = df_lcia.merge(totlc, on = ['year','scenario'])
    df_lcia_func['lcia/lb'] = df_lcia_func['value'] / (df_lcia_func['total_disposal']*1000000)
    
    
    
    fig3, ax3 = plt.subplots()
    ax3 = sns.lineplot(df_lcia_func['year'],df_lcia_func['lcia/lb'],linewidth=2, hue=df_lcia_func['scenario'])
    #ax3 = sns.lineplot(conventional['year'],conventional['rec_rate'], label = 'Recycling Rate', hue = conventional['grade'],legend = False)
    ax3.legend()
    plt.show()
    fig3.savefig('comparisonlcialine.png',dpi=300) 
    
    
    
    df_lcia = us_lcia_results
    df_lcia = df_lcia[df_lcia['year'] != 2019]
    df_lcia = df_lcia.groupby(['year','lcia','scenario'])['value'].agg('sum').reset_index()
    df_lcia = df_lcia.sort_values(by = ['year','scenario'])        
    df_lcia_func = df_lcia.merge(totlc, on = ['year','scenario'])
    df_lcia_func['lcia/lb'] = df_lcia_func['value'] / (df_lcia_func['total_disposal']*1000000)
      
    
    fig3, ax3 = plt.subplots(figsize = (20,4))
    ax3 = sns.barplot(df_lcia_func['year'],df_lcia_func['lcia/lb'],hue=df_lcia_func['scenario'])
    #ax3 = sns.lineplot(conventional['year'],conventional['rec_rate'], label = 'Recycling Rate', hue = conventional['grade'],legend = False)
    plt.ylim(5, 7)
    ax3.legend()
    plt.show()
    fig3.savefig('comparisonlciabar.png',dpi=300) 
    
    
       
    
    df_circ = totl_cost
    df_circ = df_circ[df_circ['year'] != 2019]
    df_circ = df_circ.groupby(['year','scenario'])['costs'].agg('sum').reset_index()
    df_circ = df_circ.sort_values(by = ['year','scenario'])
    fig3, ax3 = plt.subplots()
    ax3 = sns.lineplot(df_circ['year'],df_circ['costs'],linewidth=2, hue=df_circ['scenario'])
    #ax3 = sns.lineplot(conventional['year'],conventional['rec_rate'], label = 'Recycling Rate', hue = conventional['grade'],legend = False)
    ax3.legend()
    plt.show()
    fig3.savefig('comparisoncostsline.png',dpi=300) 
    
    
    
    df_circ = totl_cost
    df_circ = df_circ[df_circ['year'] != 2019]
    df_circ = df_circ.groupby(['year','scenario'])['costs'].agg('sum').reset_index()
    df_circ = df_circ.sort_values(by = ['year','scenario'])
    fig3, ax3 = plt.subplots(figsize = (20,4))
    ax3 = sns.barplot(df_circ['year'],df_circ['costs'],hue=df_circ['scenario'])
    #ax3 = sns.lineplot(conventional['year'],conventional['rec_rate'], label = 'Recycling Rate', hue = conventional['grade'],legend = False)
    ax3.legend()
    plt.show()
    fig3.savefig('comparisoncostsbar.png',dpi=300) 




def graph(**kwargs):
    
    print(kwargs.columns)    
    plt.rcParams["font.weight"] = "bold"
    plt.rcParams["axes.labelweight"] = "bold"
    fig1, ax1 = plt.subplots()
    #graph_df  = graph_df[graph_df['value'] > 0.01]
    #ax1.bar(kwargs['year'],kwargs['plastic_demand'], label = 'Plastic Demand')
    ax1.bar(kwargs['year'],kwargs['pet_manuf'], label = 'vPET Demand')
    ax1.bar(kwargs['year'],kwargs['rpet_manuf'], label = 'rPET availability')
    
    #ax1.plot(time,reclaimed_plastic, label = 'recycled resin \n production')
    #ax1.plot(time,landfill_incineration, label = 'Landfill Incineration')
    
    ax1.legend()
    plt.title('Resin', fontdict=None, loc='center', pad=None)

    
    
    
    
    #fig2, ax2 = plt.subplots()
    #ax2.plot(time,reclaimed_plastic, label = 'recycled resin \n production')
    #ax2.legend()
    #plt.title('Recycled Resin', fontdict=None, loc='center', pad=None)
    #plt.show()
    
  
    fig3, ax3 = plt.subplots()
    ax3.scatter(kwargs['year'],kwargs['rec_rate'], label = 'Recycling rate')
    ax3.scatter(kwargs['year'],kwargs['circularity'], label = 'Circularity')
    ax3.scatter(kwargs['year'],kwargs['selectivity'], label = 'Selectivity')
    ax3.legend()
    plt.show()
    
def graph2():  
    
    sen = pd.read_csv(data['resultsfile']).drop_duplicates()
    sen = sen.sort_values(by = 'sensitivity_values')
    sen.to_csv(data['resultsfile'],index = False)
    plt.rcParams["font.weight"] = "bold"
    plt.rcParams["axes.labelweight"] = "bold"
    fig4, ax4 = plt.subplots()
    for v in list(pd.unique(sen['variable'])):
        temp = sen[sen['variable'] == v]             
        ax4.plot(temp['sensitivity_values'],temp['circularity'], label = v)
        ax4.legend()
    plt.xlabel('Percentage_change')
    plt.ylabel('Circularity')
    plt.title('Sensitivity Variable Value', fontdict=None, loc='center', pad=None)
    plt.show()



def graph3(novel):

    ax = sns.lineplot(x=novel['year'],y=novel['impact'], linewidth = 2,hue = novel['stage'],palette='bright',legend= True)
    ax.set_title(pd.unique(novel['impacts'][0]))  
    plt.show()


def lcia_graph():
    traci = pd.read_csv('./pylca/traci21.csv')
    traci = traci.fillna(0)
    impacts = list(traci.columns)
    valuevars = ['Global Warming Air (kg CO2 eq / kg substance)']
    traci_df = pd.melt(traci, id_vars=['CAS #','Formatted CAS #','Substance Name'], value_vars=valuevars, var_name='impacts', value_name='value')
    traci_df['value'] = traci_df['value'].astype(float)
    final_lci_result = pd.read_csv('./pyLCA/results/lci_results_processed_multi.csv')
    final_lci_result['flow name'] =   final_lci_result['flow name'].str.upper()                                 
                                       
    #impacts = ['Global Warming Air (kg CO2 eq / kg substance)']                                   
    for im in valuevars:
        
        
       df =  traci_df[traci_df['impacts'] == im] 
       graph_df_lcia = final_lci_result.merge(df, left_on = ['flow name'], right_on = ['Substance Name'])
       graph_df_lcia['impact'] = graph_df_lcia['flow quantity'] * graph_df_lcia['value']
       graph_df_lcia = graph_df_lcia.groupby(['year', 'stage',
           'flow unit', 'impacts'])['impact'].agg('sum').reset_index()
       total_lcia = graph_df_lcia.groupby(['year',
           'flow unit', 'impacts'])['impact'].agg('sum').reset_index()
       total_lcia['stage'] = 'Total'   
       graph3(graph_df_lcia)
       graph3(total_lcia)
       
       
       
def comparative_graph():
    
    df_circ = pd.read_excel('comparative_results_lci.xlsx')
    
    df_circ = df_circ[['year','circularity','scenario']]
    df_circ = df_circ.sort_values(by = ['year','scenario'])
    
    fig3, ax3 = plt.subplots()
    ax3 = sns.lineplot(df_circ['year'],df_circ['circularity'],linewidth=2, hue=df_circ['scenario'])
    #ax3 = sns.lineplot(conventional['year'],conventional['rec_rate'], label = 'Recycling Rate', hue = conventional['grade'],legend = False)
    ax3.legend()
    plt.show()
    fig3.savefig('comparisoncirc.png',dpi=300)
    
    df_circ = pd.read_excel('lcia_comparative.xlsx')
    df_circ = df_circ[df_circ['year'] != 2019]
    df_circ = df_circ.groupby(['year','impacts','scenario'])['impact'].agg('sum').reset_index()
    df_circ = df_circ.sort_values(by = ['year','scenario'])
    fig3, ax3 = plt.subplots()
    ax3 = sns.lineplot(df_circ['year'],df_circ['impact'],linewidth=2, hue=df_circ['scenario'])
    #ax3 = sns.lineplot(conventional['year'],conventional['rec_rate'], label = 'Recycling Rate', hue = conventional['grade'],legend = False)
    ax3.legend()
    plt.show()
    fig3.savefig('comparisonlcia.png',dpi=300)  
'''
    
    