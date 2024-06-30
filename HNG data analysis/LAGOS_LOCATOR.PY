import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy.distance import geodesic
import requests

# Loading the dataset using pandas
filename = "LAGOS_crosschecked.csv"
df = pd.read_csv(filename)

def get_coordinates(address, api_key):
    base_url = "https://api.opencagedata.com/geocode/v1/json"
    params = {
        'address': address,
        'key': "850660e7983249068720ab178134f282"
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        results = response.json().get('results')
        if results:
            location = results[0]['geometry']['location']
            return location['lat'], location['lng']
    return None, None

# Your Google Maps API key
api_key = '850660e7983249068720ab178134f282'

# Function to add latitude and longitude to the dataframe
def add_coordinates(df, api_key):
    df['Address'] = df['Ward'] + ', ' + df['LGA'] + ', ' + df['State']
    df[['Latitude', 'Longitude']] = df['Address'].apply(lambda x: pd.Series(get_coordinates(x, api_key)))
    return df

# Add coordinates to the dataframe
df = add_coordinates(df, api_key)

# Save the dataset with latitude and longitude values to a new CSV file
geocoded_filename = "/mnt/data/IMO_geocoded.csv"
df.to_csv(geocoded_filename, index=False)

# Function to find neighboring polling units within a given radius
from geopy.distance import geodesic

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
sorted_outliers_filename = "/mnt/data/sorted_outliers.xlsx"
sorted_outliers.to_excel(sorted_outliers_filename, index=False)

print("Outlier detection completed. Results saved to 'sorted_outliers.xlsx'.")























# Initializing geolocator with a custom user agent
geolocator = Nominatim(user_agent="election-analysis")

# Function to geocode polling units and add latitude and longitude columns
def geocode_polling_units(df):
    # Combine location details to form address for geocoding
    df['Address'] = df['Ward'] + ', ' + df['LGA'] + ', ' + df['State']

    # Use RateLimiter to avoid hitting the geocoding service too rapidly
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
    
    # Apply geocoding to create Coordinates column
    df['Coordinates'] = df['Address'].apply(geocode)
    
    # Extract latitude and longitude from Coordinates
    df['Latitude'] = df['Coordinates'].apply(lambda loc: loc.latitude if loc else None)
    df['Longitude'] = df['Coordinates'].apply(lambda loc: loc.longitude if loc else None)
    
    return df

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


df = geocode_polling_units(df)

geocoded_filename = "LAGOS_crosschecked_geocoded.csv"
df.to_csv(geocoded_filename, index=False)


neighbours = find_neighbours(df)

outlier_scores = calculate_outlier_scores(df, neighbours)

outlier_df = pd.DataFrame(outlier_scores, columns=['Unit', 'Party', 'Outlier_Score'])


sorted_outliers = outlier_df.sort_values(by='Outlier_Score', ascending=False)

sorted_outliers_filename = "LAGOS_crosschecked_summary.xlsx"
sorted_outliers.to_excel(sorted_outliers_filename, index=False)

print("Outlier detection completed. Results saved to 'sorted_outliers.xlsx'.")
