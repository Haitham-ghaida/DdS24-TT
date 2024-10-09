from utils import ask_geonames
import os
import pandas as pd

def main():

    username = os.getenv('GEONAMES_USERNAME')
    params = {
        'formatted': 'true',
        'country': 'US',
        'featureCode': 'ADM1',
        # 'maxRows': max_rows,
        # 'startRow': start_row,
        'username': username
        }
    
    data = ask_geonames(params)

    state_dict = {state['name']:f"https://www.geonames.org/{state['geonameId']}" 
    for state in data['geonames']}

    states_s = pd.Series(state_dict,name='uri')
    states_s.index.name = 'states'
    states_s.to_csv('states_uris.csv')

if __name__ == "__main__":
    main()