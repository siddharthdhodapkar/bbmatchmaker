# -*- coding: utf-8 -*-
"""
Created on Tue Nov 14 00:00:17 2023

@author: lenovo
"""

import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim

def pincode_to_coordinates(pincode):
    geolocator = Nominatim(user_agent="pincode_converter")
    location = geolocator.geocode(f"{pincode}, India")
    if location:
        return location.latitude, location.longitude
    else:
        return None, None

def convert_excel(input_path, output_path):
    # Read input Excel sheet
    df = pd.read_excel(input_path)

    # Add columns for Latitude and Longitude
    df['Latitude'] = None
    df['Longitude'] = None

    # Update coordinates for each PIN code
    for index, row in df.iterrows():
        latitude, longitude = pincode_to_coordinates(row['PIN Codes'])
        df.at[index, 'Latitude'] = latitude
        df.at[index, 'Longitude'] = longitude

    # Save output Excel sheet
    df.to_excel(output_path, index=False)

def get_excel_download_link(df, download_text):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    writer.save()
    excel_file = output.getvalue()
    b64 = base64.b64encode(excel_file)
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{download_text}.xlsx">Download Excel File</a>'

def main():
    st.title("Indian PIN Code to Coordinates Converter")

    # Upload files
    input_file = st.file_uploader("Upload Excel sheet with PIN Codes", type=["xlsx"])

    if input_file is not None:
        st.info("File uploaded successfully!")
        st.subheader("Preview of Input Excel Sheet:")
        input_df = pd.read_excel(input_file)
        st.write(input_df)

        # Convert and display button
        if st.button("Convert"):
            # Temporary output path for Streamlit
            temp_output_path = "output_temp.xlsx"
            convert_excel(input_file, temp_output_path)

            # Display output
            st.subheader("Preview of Output Excel Sheet:")
            output_df = pd.read_excel(temp_output_path)
            st.write(output_df)

            # Provide download link for the output Excel sheet
            st.markdown(get_excel_download_link(output_df, "Download Output Excel Sheet"), unsafe_allow_html=True)

if __name__ == "__main__":
    main()
