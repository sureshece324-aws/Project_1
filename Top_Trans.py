import mysql.connector
import pandas as pd
import json
import os

# --- 1. DATA EXTRACTION ---
path = 'C:/Users/Neil/Documents/Suresh/Phonepe/pulse/data/top/transaction/country/india/state/'
toptrans_state_list = os.listdir(path)

clm = {
    'State': [], 'Year': [], 'Quarter': [], 'Level': [], 
    'Name': [], 'Transaction_count': [], 'Transaction_amount': []
}

for i in toptrans_state_list:
    p_i = path + i + "/"
    topTrans_yr = os.listdir(p_i)

    for j in topTrans_yr:
        p_j = p_i + j + "/"
        topTrans_yr_list = os.listdir(p_j)

        for k in topTrans_yr_list:
            p_k = p_j + k

            with open(p_k, 'r') as Data:
                D = json.load(Data)

                # Helper function to extract metrics safely
                def extract_data(level_key, level_name):
                    if level_key in D['data'] and D['data'][level_key]:
                        for z in D['data'][level_key]:
                            clm['State'].append(i)
                            clm['Year'].append(int(j))
                            clm['Quarter'].append(int(k.strip('.json')))
                            clm['Level'].append(level_name)
                            clm['Name'].append(z['entityName'])
                            clm['Transaction_count'].append(z['metric']['count'])
                            clm['Transaction_amount'].append(z['metric']['amount'])

                extract_data('states', 'State')
                extract_data('districts', 'District')
                extract_data('pincodes', 'Pincode')

# Create DataFrame
Top_Transaction_df = pd.DataFrame(clm)

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
CREATE TABLE IF NOT EXISTS top_transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    State VARCHAR(100),
    Year INT,
    Quarter INT,
    Level VARCHAR(50),
    Name VARCHAR(100),
    Transaction_count BIGINT,
    Transaction_amount DOUBLE
);
"""
cursor.execute(create_table_query)

# --- 3. FIXING THE NaN ISSUE FOR INSERTION ---

# Convert columns to correct types while keeping NaN for missing values
Top_Transaction_df["Year"] = pd.to_numeric(Top_Transaction_df["Year"], errors='coerce')
Top_Transaction_df["Quarter"] = pd.to_numeric(Top_Transaction_df["Quarter"], errors='coerce')
Top_Transaction_df["Transaction_count"] = pd.to_numeric(Top_Transaction_df["Transaction_count"], errors='coerce')
Top_Transaction_df["Transaction_amount"] = pd.to_numeric(Top_Transaction_df["Transaction_amount"], errors='coerce')

# Convert DataFrame to list of lists
data_list = Top_Transaction_df.values.tolist()

# The "Firewall": Explicitly replace any NaN with Python's None (SQL NULL)
rows = [tuple(None if pd.isna(item) else item for item in row) for row in data_list]

# Insert data
insert_query = """
INSERT INTO top_transactions
(State, Year, Quarter, Level, Name, Transaction_count, Transaction_amount)
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