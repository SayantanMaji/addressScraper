import pandas as pd
import pgeocode
from geopy.geocoders import Nominatim

def extract_info_from_gb_postal_code(postal_code):
    nomi = pgeocode.Nominatim('GB')
    geolocator = Nominatim(user_agent="geoapiExercises")

    try:
        result = nomi.query_postal_code(postal_code)
        latitude = result['latitude']
        longitude = result['longitude']

        location = geolocator.reverse(f"{latitude}, {longitude}", exactly_one=True)
        if location:
            address = location.raw.get('address', {})
            city = address.get('city', '')
            state = address.get('state', '')
            country = address.get('country', '')
            zipcode = address.get('postcode', '')
            street_name = address.get('road', '')  # Retrieve the street name
        else:
            city, state, country, zipcode, street_name = None, None, None, None, None

        return postal_code, city, state, country, zipcode, street_name

    except Exception as e:
        print(f"Error occurred for postal code: {postal_code}. Code details not found.")
        return postal_code, None, None, None, None, None

# Read data from the Excel file
file_path = r'C:\Users\91967\Downloads\sample_data.xlsx'
df = pd.read_excel(file_path)

# Convert the postal codes to strings to preserve any leading zeros
df['postcode'] = df['postcode'].astype(str)

# Extract data from column E (assuming the column name is 'postcode')
postal_codes = df['postcode'].tolist()

# Add a space before the last three characters of each postal code if it doesn't exist
postal_codes_with_space = [code[:-3] + (' ' if len(code) > 3 and not code[-4].isspace() else '') + code[-3:] for code in postal_codes]

# Create an empty list to store the results
results = []

# Call the function with each postal code and store the results in the list
for postal_code in postal_codes_with_space:
    result = extract_info_from_gb_postal_code(postal_code)
    results.append(result)

# Create a DataFrame from the results list
df_output = pd.DataFrame(results, columns=['Postal Code', 'City', 'State', 'Country', 'Zip Code', 'Street Name'])

# Save the DataFrame to a new Excel file
output_file_path = r'C:\Users\91967\Downloads\output_data.xlsx'
df_output.to_excel(output_file_path, index=False)

print("Output data has been saved to 'output_data.xlsx'.")
