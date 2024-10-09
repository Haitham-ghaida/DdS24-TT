import requests
from tqdm import tqdm
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

def ask_geonames(params):

    url = 'http://api.geonames.org/searchJSON'

    response = requests.get(url, params=params)
    data = response.json()

    return data

def check_url(url):
    try:
        response = requests.head(url, timeout=10)
        return url, response.status_code
    except requests.RequestException:
        return url, 'Error'

def verify_uris(csv_file, uri_column='uri'):
    # Read the CSV file
    df = pd.read_csv(csv_file)
    
    # Get unique URIs
    uris = df[uri_column].unique()
    
    results = []
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        # Create a list of futures
        future_to_url = {executor.submit(check_url, url): url for url in uris}
        
        for future in tqdm(as_completed(future_to_url), total=len(uris), desc="Checking URIs"):
            url, status = future.result()
            results.append({'uri': url, 'status': status})
    
    results_df = pd.DataFrame(results)
    
    total_uris = len(results_df)
    error_uris = results_df[results_df['status'] == 'Error']
    not_found_uris = results_df[results_df['status'] == 404]
    
    print(f"\nTotal URIs checked: {total_uris}")
    print(f"URIs returning errors: {len(error_uris)}")
    print(f"URIs returning 404 Not Found: {len(not_found_uris)}")
    
    # show issues
    if not error_uris.empty:
        print("\nURIs with errors:")
        print(error_uris['uri'].tolist())
    
    if not not_found_uris.empty:
        print("\nURIs returning 404 Not Found:")
        print(not_found_uris['uri'].tolist())
    
    # save
    results_df.to_csv('uri_verification_results.csv', index=False)
    print("\nDetailed results saved to 'uri_verification_results.csv'")