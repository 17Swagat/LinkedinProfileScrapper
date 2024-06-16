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
    'experience', 'education'
]

# Create a function to flatten the JSON data
def flatten_profile(profile):
    flattened = {}
    flattened['name'] = profile.get('name', '')
    flattened['headline'] = profile.get('headline', '')
    flattened['identify_as'] = profile.get('identify_as', '')
    flattened['about'] = profile.get('about', '')

    # Combine experiences
    experiences = profile.get('experience', [])
    experience_list = []
    for exp in experiences:
        experience_str = f"Role: {exp.get('role', '')}, Company: {exp.get('company', '')}"
        if 'duration' in exp:
            experience_str += f", Duration: {exp.get('duration', '')}"
        if 'location' in exp:
            experience_str += f", Location: {exp.get('location', '')}"
        if 'job-description' in exp:
            experience_str += f", Description: {exp.get('job-description', '')}"
        experience_list.append(experience_str)
    flattened['experience'] = '\n'.join(experience_list)

    # Combine educations
    educations = profile.get('education', [])
    education_list = []
    for edu in educations:
        education_str = f"Institute: {edu.get('Institute_Name', '')}, Degree: {edu.get('Degree', '')}"
        education_list.append(education_str)
    flattened['education'] = '\n'.join(education_list)

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
