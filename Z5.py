# -*- coding: utf-8 -*-
"""
Created on Tue Nov 14 01:33:54 2023

@author: lenovo
"""

import streamlit as st
import pandas as pd
from geopy.distance import geodesic

# Load the Excel sheets
@st.cache_data
def load_data(sheet1_path, sheet2_path):
    schools = pd.read_excel(sheet1_path)
    coaches = pd.read_excel(sheet2_path)
    return schools, coaches

# Function to find nearest coach for a given school
def find_nearest_coach(school, coaches):
    try:
        school_coords = (float(school['School Latitude']), float(school['School Longitude']))
    except (ValueError, TypeError):
        return None

    same_category_coaches = coaches[coaches['Coach Category'] == school['School Category']]
    if same_category_coaches.empty:
        return None

    try:
        same_category_coaches['Distance'] = same_category_coaches.apply(
            lambda row: geodesic((float(row['Coach Latitude']), float(row['Coach Longitude'])), school_coords).kilometers,
            axis=1
        )
        nearest_coach = same_category_coaches['Distance'].idxmin()
        return coaches.loc[nearest_coach], same_category_coaches.loc[nearest_coach]['Distance']
    except (ValueError, TypeError):
        return None, None

# Main function
def main():
    st.title("Coach Assignment App")

    # Upload files
    sheet1_path = st.file_uploader("Upload first Excel sheet (Schools)", type=["xlsx"])
    sheet2_path = st.file_uploader("Upload second Excel sheet (Coaches)", type=["xlsx"])

    if sheet1_path and sheet2_path:
        schools, coaches = load_data(sheet1_path, sheet2_path)

        # Assign coaches to schools
        assigned_data = []
        for _, school in schools.iterrows():
            nearest_coach, distance_km = find_nearest_coach(school, coaches)
            if nearest_coach is not None:
                assigned_data.append({
                    'School Name': school['School Name'],
                    'Coach Name': nearest_coach['Coach Name'],
                    'Distance (km)': distance_km
                })

        if assigned_data:
            # Display results
            assigned_df = pd.DataFrame(assigned_data)

            # Sort by Coach Name and Distance in ascending order
            assigned_df.sort_values(['Coach Name', 'Distance (km)'], inplace=True)

            # Rank distances within each coach group
            assigned_df['Rank'] = assigned_df.groupby('Coach Name')['Distance (km)'].rank(method="dense")

            # Highlight ranks 1 and 2 for each coach
            assigned_df['Highlight'] = assigned_df['Rank'].isin([1, 2])

            # Display the final dataframe
            st.subheader("Assigned Coaches to Schools with Distance (Sorted and Highlighted)")
            st.write(assigned_df.style.apply(lambda x: ['background: yellow' if x['Highlight'] else '' for i in x], axis=1, subset=['Highlight']))
        else:
            st.warning("No matches found for the given criteria.")

if __name__ == '__main__':
    main()
