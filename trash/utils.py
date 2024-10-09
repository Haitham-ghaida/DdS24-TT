import requests

def ask_geonames(params):

    url = 'http://api.geonames.org/searchJSON'

    response = requests.get(url, params=params)
    data = response.json()

    return data