import requests
import pandas as pd

def get_counties_in_batches(username):
    url = 'http://api.geonames.org/searchJSON'
    max_rows = 1000  # maximum
    start_row = 0
    total_results = 3144 # number of counties in USA
    all_counties = []

    while start_row < total_results:
        # Define the parameters for this batch
        params = {
            'formatted': 'true',
            'country': 'US',
            'featureCode': 'ADM2',
            'maxRows': max_rows,
            'startRow': start_row,
            'username': username
        }

        # Make the API request
        response = requests.get(url, params=params)
        data = response.json()

        # Append counties from this batch to the list
        all_counties.extend(data.get('geonames', []))

        # Update the total number of results
        total_results = data.get('totalResultsCount', 0)

        # Move to the next batch
        start_row += max_rows

    return all_counties


if __name__ == "__main__":

    username = 'tarblaster'
    counties = get_counties_in_batches(username)

    # reorganise the data to create a csv with the uris of each pair state - 
    county_dict = {}
    for county in counties:
        
        uri = f"https://www.geonames.org/{county['geonameId']}"
        county_dict[(county['adminName1'],county['toponymName'])]= uri
        
    county_s = pd.Series(county_dict)
    county_s.index.names = ['adminName1','toponymName']
    county_s.rename('uri').to_csv('counties_uris.csv')