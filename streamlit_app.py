import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Display Title and Description
st.title("Vendor Management Portal")

spreadsheet = "https://docs.google.com/spreadsheets/d/1jOXDRWpif2QUIL7FvZdR6Izu-NbEd5fpckpWsR8ZDcM"

# Establishing a Google Sheets connection
conn = st.connection("gsheets", type=GSheetsConnection)

# Fetch existing vendors data
existing_data = conn.read(spreadsheet=spreadsheet, usecols=list(range(5)))
existing_data = existing_data.dropna(how="all")