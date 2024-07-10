import pandas as pd
import numpy as np

# Create DataFrame
data = {
    'Name': ['Alice', 'Bob', 'Charlie'],
    'Age': [25, 30, 35],
    'City': ['New York', 'Los Angeles', 'Chicago']
}
df = pd.DataFrame(data)

# Function to apply red background to entire 'City' column
def highlight_city(column):
    return ['background-color: red' if c == 'City' else '' for c in column]

# Function to color text green if the name is 'Bob'
def highlight_bob(cell):
    return 'color: green' if cell == 'Bob' else ''

# Apply styling
styled_df = df.style.apply(highlight_city, subset=['City']) \
                    .applymap(highlight_bob, subset=['Name'])

# Save to Excel with OpenPyXL as the engine
styled_df.to_excel('styled_data.xlsx', engine='openpyxl', index=False)
