import mysql.connector
import pandas as pd
import json
import os

#This is to direct the path to get the data as states

import os
path = 'C:/Users/Neil/Documents/Suresh/Phonepe/pulse/data/top/insurance/country/india/state/'
topins_state_list = os.listdir(path)
topins_state_list
#Topins_state_list--> to get the list of states in India

#This is to extract the data's to create a dataframe

clm={'State':[], 'Year':[], 'Quarter':[], 'Level':[], 'Name':[], 'Insurance_count':[], 'Insurance_amount':[]}

for i in topins_state_list:
    p_i=path+i+"/"
    topins_yr=os.listdir(p_i)

    for j in topins_yr:
        p_j=p_i+j+"/"
        topins_yr_list=os.listdir(p_j)

        for k in topins_yr_list:
            p_k=p_j+k

            with open(p_k,'r') as Data:
                D=json.load(Data)


                 # Helper function to extract metrics safely
                def extract_data(level_key, level_name):
                    if level_key in D['data'] and D['data'][level_key]:
                        for z in D['data'][level_key]:
                            clm['State'].append(i)
                            clm['Year'].append(int(j))
                            clm['Quarter'].append(int(k.strip('.json')))
                            clm['Level'].append(level_name)
                            clm['Name'].append(z['entityName'])
                            clm['Insurance_count'].append(z['metric']['count'])
                            clm['Insurance_amount'].append(z['metric']['amount'])

                extract_data('states', 'State')
                extract_data('districts', 'District')
                extract_data('pincodes', 'Pincode')

# Create DataFrame
Top_Insurance_df = pd.DataFrame(clm)

# --- 2. DATABASE CONNECTION ---
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Beast@9202",
    database="phonepe_pulse"    
)
cursor = mydb.cursor()

# Create table
create_table_query = """
CREATE TABLE IF NOT EXISTS top_insurance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    State VARCHAR(100),
    Year INT,
    Quarter INT,
    Level VARCHAR(50),
    Name VARCHAR(100),
    Insurance_count BIGINT,
    Insurance_amount DOUBLE
);
"""
cursor.execute(create_table_query)

# --- 3. FIXING THE NaN ISSUE FOR INSERTION ---

# Convert columns to correct types while keeping NaN for missing values
Top_Insurance_df["Year"] = pd.to_numeric(Top_Insurance_df["Year"], errors='coerce')
Top_Insurance_df["Quarter"] = pd.to_numeric(Top_Insurance_df["Quarter"], errors='coerce')
Top_Insurance_df["Insurance_count"] = pd.to_numeric(Top_Insurance_df["Insurance_count"], errors='coerce')
Top_Insurance_df["Insurance_amount"] = pd.to_numeric(Top_Insurance_df["Insurance_amount"], errors='coerce')

# Convert DataFrame to list of lists
data_list = Top_Insurance_df.values.tolist()

# The "Firewall": Explicitly replace any NaN with Python's None (SQL NULL)
rows = [tuple(None if pd.isna(item) else item for item in row) for row in data_list]

# Insert data
insert_query = """
INSERT INTO top_insurance
(State, Year, Quarter, Level, Name, Insurance_count, Insurance_amount)
VALUES (%s, %s, %s, %s, %s, %s, %s)
"""

print(f"{len(rows)} rows ready to insert.")

try:
    cursor.executemany(insert_query, rows)
    mydb.commit()
    print(f"{cursor.rowcount} rows inserted successfully.")
except mysql.connector.Error as err:
    print(f"Error: {err}")

cursor.close()
mydb.close()