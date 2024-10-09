import requests
import pandas as pd
import os

def get_counties_in_batches(username:str)->list:
    """returns a list of all counties in US from the geonames platform, uncluding
    a unique uri.

    Args:
        username (str): valid username for the geonames api

    Returns:
        list: list of counties in US with the associated metadata
    """

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


def main():
    """returns a csv with the uri of each county in USA. It assumes that you've
    a valid username to use the geonames api and that the value is stored as an
    environment variable as GEONAMES_USERNAME
    """

    username = os.getenv('GEONAMES_USERNAME')
    counties = get_counties_in_batches(username)

    # reorganise the data to create a csv with the uris of each pair state - 
    county_dict = {}
    for county in counties:
        
        uri = f"https://www.geonames.org/{county['geonameId']}"
        county_dict[(county['adminName1'],county['toponymName'])]= uri
        
    county_s = pd.Series(county_dict)
    county_s.index.names = ['adminName1','toponymName']
    county_s.rename('uri').to_csv('counties_uris.csv')

if __name__ == "__main__":

    main()
