import json
import os
import csv

# Directory containing the JSON files
json_dir = '.'  # Replace with the path to your JSON files

# CSV file path
csv_file = 'combined_profiles.csv'

# Initialize an empty list to hold all profile data
all_profiles = []

# Loop through the JSON files
i = 1
while True:
    json_file = os.path.join(json_dir, f'profile_info_{i}.json')
    if not os.path.exists(json_file):
        break

    with open(json_file, 'r', encoding='utf-8') as f:
        profile_data = json.load(f)
        all_profiles.append(profile_data)

    i += 1

# Define the CSV columns based on the keys in the JSON files
csv_columns = [
    'name', 'headline', 'identify_as', 'about', 
    'experience_role_1', 'experience_company_1', 'experience_duration_1', 'experience_location_1', 'experience_description_1',
    'experience_role_2', 'experience_company_2', 'experience_duration_2', 'experience_location_2', 'experience_description_2',
    'experience_role_3', 'experience_company_3', 'experience_duration_3', 'experience_location_3', 'experience_description_3',
    'experience_role_4', 'experience_company_4', 'experience_duration_4', 'experience_location_4', 'experience_description_4',
    'experience_role_5', 'experience_company_5', 'experience_duration_5', 'experience_location_5', 'experience_description_5',
    'education_institute_1', 'education_degree_1',
    'education_institute_2', 'education_degree_2',
    'education_institute_3', 'education_degree_3',
    'education_institute_4', 'education_degree_4',
    'education_institute_5', 'education_degree_5'
]

# Create a function to flatten the JSON data
def flatten_profile(profile):
    flattened = {}
    flattened['name'] = profile.get('name', '')
    flattened['headline'] = profile.get('headline', '')
    flattened['identify_as'] = profile.get('identify_as', '')
    flattened['about'] = profile.get('about', '')

    # Flatten experience
    experiences = profile.get('experience', [])
    for idx, exp in enumerate(experiences, start=1):
        flattened[f'experience_role_{idx}'] = exp.get('role', '')
        flattened[f'experience_company_{idx}'] = exp.get('company', '')
        flattened[f'experience_duration_{idx}'] = exp.get('duration', '')
        flattened[f'experience_location_{idx}'] = exp.get('location', '')
        flattened[f'experience_description_{idx}'] = exp.get('job-description', '')

    # Flatten education
    educations = profile.get('education', [])
    for idx, edu in enumerate(educations, start=1):
        flattened[f'education_institute_{idx}'] = edu.get('Institute_Name', '')
        flattened[f'education_degree_{idx}'] = edu.get('Degree', '')

    return flattened

# Flatten all profiles
flattened_profiles = [flatten_profile(profile) for profile in all_profiles]

# Write to CSV
with open(csv_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=csv_columns)
    writer.writeheader()
    for profile in flattened_profiles:
        writer.writerow(profile)

print(f"Data has been written to {csv_file}")
