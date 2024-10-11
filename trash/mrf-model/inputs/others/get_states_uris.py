from utils import ask_geonames,verify_uris
import os
import pandas as pd

def main():
    
    username = os.getenv('GEONAMES_USERNAME','ups!')
    if username == 'ups!':
        raise ValueError('the username of geonames could not be found as env variable')


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
    csv_name = 'states_uris.csv'
    states_s.to_csv(csv_name)

    verify_uris(csv_name)


if __name__ == "__main__":
    main()