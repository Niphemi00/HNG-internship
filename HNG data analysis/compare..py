import pandas as pd
import requests
from geopy.distance import geodesic

# Function to get coordinates using OpenCage Geocoding API
def get_coordinates(address, api_key):
    base_url = "https://api.opencagedata.com/geocode/v1/json"
    params = {
        'q': address,
        'key': api_key
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        results = response.json().get('results')
        if results:
            location = results[0]['geometry']
            return location['lat'], location['lng']
    return None, None

# Your OpenCage API key
api_key = '850660e7983249068720ab178134f282'

# Demo address
demo_address = "Isale/Idimangoro, Agege, Lagos"

# Get coordinates for the demo address
latitude, longitude = get_coordinates(demo_address, api_key)

# Print the coordinates for the demo address
print(f"Coordinates for '{demo_address}': Latitude = {latitude}, Longitude = {longitude}")

# Load the dataset
filename = "LAGOS_crosschecked.csv"  # Make sure this file is in the same directory as the script
df = pd.read_csv(filename)
print(df.head(20))
# Function to add latitude and longitude to the dataframe
def add_coordinates(df, api_key):
    latitudes = []
    longitudes = []
    for _, row in df.iterrows():
        address = f"{row['Ward']}, {row['LGA']}, {row['State']}"
        lat, lon = get_coordinates(address, api_key)
        latitudes.append(lat)
        longitudes.append(lon)
    df['Latitude'] = latitudes
    df['Longitude'] = longitudes
    return df

# Add coordinates to the dataframe
df = add_coordinates(df, api_key)

# Save the dataset with latitude and longitude values to a new CSV file
geocoded_filename = "LAGOS_geocoded.csv"
df.to_csv(geocoded_filename, index=False)

# Function to find neighboring polling units within a given radius
def find_neighbours(polling_units, radius=1):
    neighbours = {}
    for i, unit in polling_units.iterrows():
        unit_coords = (unit['Latitude'], unit['Longitude'])
        neighbours[i] = []
        for j, other_unit in polling_units.iterrows():
            if i != j:
                other_coords = (other_unit['Latitude'], other_unit['Longitude'])
                distance = geodesic(unit_coords, other_coords).km
                if distance <= radius:
                    neighbours[i].append(j)
    return neighbours

# Calculate outlier scores
def calculate_outlier_scores(polling_units, neighbours):
    outlier_scores = []
    parties = ['PDP', 'NNPP']  # List of parties
    for unit, neighbour_indices in neighbours.items():
        for party in parties:
            unit_votes = polling_units.at[unit, party]
            neighbour_votes = [polling_units.at[i, party] for i in neighbour_indices]
            avg_neighbour_votes = sum(neighbour_votes) / len(neighbour_votes) if neighbour_votes else 0
            outlier_score = abs(unit_votes - avg_neighbour_votes)
            outlier_scores.append((unit, party, outlier_score))
    return outlier_scores

# Find neighbours within a 1 km radius
neighbours = find_neighbours(df)

# Calculate outlier scores
outlier_scores = calculate_outlier_scores(df, neighbours)

# Create DataFrame from outlier scores
outlier_df = pd.DataFrame(outlier_scores, columns=['Unit', 'Party', 'Outlier_Score'])

# Sort by outlier scores
sorted_outliers = outlier_df.sort_values(by='Outlier_Score', ascending=False)

# Save the sorted outliers to an Excel file
sorted_outliers_filename = "sorted_outliers.xlsx"
sorted_outliers.to_excel(sorted_outliers_filename, index=False)

print("Outlier detection completed. Results saved to 'sorted_outliers.xlsx'.")
