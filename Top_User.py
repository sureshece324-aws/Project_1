import mysql.connector
import pandas as pd
import json
import os

# Path (update accordingly)
path = "C:/Users/Neil/Documents/Suresh/Phonepe/pulse/data/top/user/country/india/state/"

# State list
topuser_state_list = os.listdir(path)

# Data dictionary
clm = {
    'State': [],
    'Year': [],
    'Quarter': [],
    'Level': [],
    'Name': [],
    'Registered_Users': []
}

for i in topuser_state_list:
    p_i=path+i+"/"
    topuser_yr=os.listdir(p_i)

    for j in topuser_yr:
        p_j=p_i+j+"/"
        topuser_yr_list=os.listdir(p_j)

        for k in topuser_yr_list:
            p_k=p_j+k

            with open(p_k, 'r') as Data:
                D = json.load(Data)

                # STATES
                if 'states' in D['data'] and D['data']['states']:
                    for z in D['data']['states']:
                        clm['State'].append(i)
                        clm['Year'].append(j)
                        clm['Quarter'].append(int(k.strip('.json')))
                        clm['Level'].append('State')
                        clm['Name'].append(z['name'])
                        clm['Registered_Users'].append(z['registeredUsers'])

                # DISTRICTS
                if 'districts' in D['data'] and D['data']['districts']:
                    for z in D['data']['districts']:
                        clm['State'].append(i)
                        clm['Year'].append(j)
                        clm['Quarter'].append(int(k.strip('.json')))
                        clm['Level'].append('District')
                        clm['Name'].append(z['name'])
                        clm['Registered_Users'].append(z['registeredUsers'])

                # PINCODES
                if 'pincodes' in D['data'] and D['data']['pincodes']:
                    for z in D['data']['pincodes']:
                        clm['State'].append(i)
                        clm['Year'].append(j)
                        clm['Quarter'].append(int(k.strip('.json')))
                        clm['Level'].append('Pincode')
                        clm['Name'].append(z['name'])
                        clm['Registered_Users'].append(z['registeredUsers'])

# Create DataFrame
Top_User_df = pd.DataFrame(clm)

# Preview
Top_User_df

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
CREATE TABLE IF NOT EXISTS top_users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    State VARCHAR(100),
    Year INT,
    Quarter INT,
    Level VARCHAR(50),
    Name VARCHAR(100),
    Registered_Users BIGINT
);
"""
cursor.execute(create_table_query)

# --- 3. FIXING THE NaN ISSUE FOR INSERTION ---

# Convert columns to correct types while keeping NaN for missing values
Top_User_df["Year"] = pd.to_numeric(Top_User_df["Year"], errors='coerce')
Top_User_df["Quarter"] = pd.to_numeric(Top_User_df["Quarter"], errors='coerce')
Top_User_df["Registered_Users"] = pd.to_numeric(Top_User_df["Registered_Users"], errors='coerce')

# Convert DataFrame to list of lists
data_list = Top_User_df.values.tolist()

# The "Firewall": Explicitly replace any NaN with Python's None (SQL NULL)
rows = [tuple(None if pd.isna(item) else item for item in row) for row in data_list]

# Insert data
insert_query = """
INSERT INTO top_users
(State, Year, Quarter, Level, Name, Registered_Users)
VALUES (%s, %s, %s, %s, %s, %s)
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