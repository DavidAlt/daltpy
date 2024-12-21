import pandas as pd
import requests

# Get the input data

# sample data for testing
#input_data = {
#    'last_name' : ['Alt', 'Stering', 'Toth', 'McPickles', 'Smith'],
#    'first_name': ['David', 'Jonathan', 'William', 'Danny', 'John']
#}
#sample_df = pd.DataFrame(input_data)

file_path = '<file_path>'
df = pd.read_excel(file_path)
df.head()

# Function to fetch data from NPI API
def fetch_npi_data(first_name, last_name):
    base_url = "https://npiregistry.cms.hhs.gov/api/"
    parameters = {
        'version': '2.1',
        'first_name': first_name,
        'last_name': last_name
    }
    response = requests.get(base_url, params=parameters)
    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

# Function to fetch data considering authorized official names
def fetch_data_with_multiple_names(first_name, last_name):
    # Query using first_name and last_name
    npi_data = fetch_npi_data(first_name, last_name)
    # Query using authorized_official_first_name and authorized_official_last_name
    auth_npi_data = fetch_npi_data(
        first_name.replace('first_name', 'authorized_official_first_name'),
        last_name.replace('last_name', 'authorized_official_last_name')
    )
    
    # Combine results
    combined_results = npi_data.get('results', []) + auth_npi_data.get('results', [])
    
    return {'results': combined_results}

# Function to process the results and extract relevant fields
def process_npi_results(npi_data):
    results = npi_data.get('results', [])
    if not results:
        return [{"NPI_number": "no match"}]
    
    extracted_data = []
    for result in results:
        addresses = result.get('addresses', []) + result.get('practiceLocations', [])
        concatenated_addresses = []
        
        for address in addresses:
            addr = ', '.join(filter(None, [
                address.get('address_1', ''),
                address.get('address_2', ''),
                address.get('city', ''),
                address.get('state', ''),
                address.get('postal_code', '')
            ]))
            if addr not in concatenated_addresses:
                concatenated_addresses.append(addr)
        
        address_fields = {
            f'address_{i+1}': concatenated_addresses[i] if i < len(concatenated_addresses) else ''
            for i in range(len(concatenated_addresses))
        }
        
        taxonomies = result.get('taxonomies', [])
        concatenated_taxonomies = []
        
        for taxonomy in taxonomies:
            tax = f"{taxonomy.get('code')} - {taxonomy.get('desc')}"
            if tax not in concatenated_taxonomies:
                concatenated_taxonomies.append(tax)
        
        taxonomy_fields = {
            f'taxonomy_{i+1}': concatenated_taxonomies[i] if i < len(concatenated_taxonomies) else ''
            for i in range(len(concatenated_taxonomies))
        }
        
        entry = {
            'NPI_number': result.get('number'),
            'first_name': result.get('basic', {}).get('first_name'),
            'last_name': result.get('basic', {}).get('last_name'),
            'authorized_official_first_name': result.get('basic', {}).get('authorized_official_first_name'),
            'authorized_official_last_name': result.get('basic', {}).get('authorized_official_last_name'),
            'credential': result.get('basic', {}).get('credential'),
            'enumeration_date': result.get('basic', {}).get('enumeration_date'),
            'last_updated': result.get('basic', {}).get('last_updated'),
            'status': result.get('basic', {}).get('status')
        }
        entry.update(address_fields)
        entry.update(taxonomy_fields)
        extracted_data.append(entry)
    
    return extracted_data

# Function to remove duplicate rows based on NPI number and taxonomy code
def remove_duplicates(df):
    return df.drop_duplicates(subset=['NPI_number', 'taxonomy_1'], keep='first')

# Function to concatenate taxonomy and address information for unique NPIs
def concatenate_info(df):
    address_columns = [col for col in df.columns if col.startswith('address_')]
    taxonomy_columns = [col for col in df.columns if col.startswith('taxonomy_')]
    
    for col in address_columns + taxonomy_columns:
        df[col] = df[col].astype(str)
    
    concatenated_data = df.groupby('NPI_number').agg({
        'first_name': 'first',
        'last_name': 'first',
        'authorized_official_first_name': 'first',
        'authorized_official_last_name': 'first',
        'credential': 'first',
        'enumeration_date': 'first',
        'last_updated': 'first',
        'status': 'first',
        **{col: lambda x: ', '.join(x.unique()) for col in address_columns + taxonomy_columns},
        'input_first_name': 'first',
        'input_last_name': 'first'
    }).reset_index()
    return concatenated_data
    
    
# Pull data using the API
# Create a list to store the results
all_results = []

# Iterate over each row in the DataFrame
for index, row in df.iterrows():
    first_name = row['first_name']
    last_name = row['last_name']
    npi_data = fetch_data_with_multiple_names(first_name, last_name)
    npi_results = process_npi_results(npi_data)
    for result in npi_results:
        result['input_first_name'] = first_name
        result['input_last_name'] = last_name
        all_results.append(result)

# Convert the results to a DataFrame
results_df = pd.DataFrame(all_results)


# Process the dataframe
# Check if the necessary columns are present before removing duplicates
if 'NPI_number' in results_df.columns and 'taxonomy_1' in results_df.columns:
    # Remove duplicate rows based on NPI number and taxonomy code
    results_df = remove_duplicates(results_df)

    # Concatenate taxonomy and address information for unique NPIs
    results_df = concatenate_info(results_df)

    # Reorder columns to ensure input_last_name, input_first_name, and NPI_number are first
    columns_order = ['input_last_name', 'input_first_name', 'NPI_number'] + [col for col in results_df.columns if col not in ['input_last_name', 'input_first_name', 'NPI_number']]
    results_df = results_df[columns_order]

    # Sort the DataFrame by input_last_name, input_first_name, and NPI_number
    results_df = results_df.sort_values(by=['input_last_name', 'input_first_name', 'NPI_number'])

    # Reset the index
    results_df = results_df.reset_index(drop=True)
    
    # Write the output to an Excel file
    output_file = 'npi_lookup_output.xlsx'  # Replace with your output file path
    results_df.to_excel(output_file, index=False)

    print("NPI lookup completed and results written to", output_file)
else:
    print("Necessary columns 'NPI_number' and 'taxonomy_1' not found in the results DataFrame.")
