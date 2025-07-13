#!/usr/bin/env python
import pandas as pd
import streamlit as st

# Load your DataFrame however you like:
df = pd.read_excel("Database_Media.xlsx")

# Basic viewer:
st.dataframe(df, use_container_width=True)

# — or — add a simple color-gradient on each column:
# st.dataframe(
#     df.style.background_gradient(axis=0),
#     use_container_width=True
# )
