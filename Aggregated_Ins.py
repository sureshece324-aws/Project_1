import mysql.connector
import pandas as pd
import json
import os

#Path to the data

path = "C:/Users/Neil/Documents/Suresh/Phonepe/pulse/data/aggregated/insurance/country/india/state/"
Ins_state_list=os.listdir(path)
Ins_state_list
#Insurance_state_list--> to get the list of states in India

#This is to extract the data's to create a dataframe

clm={'State':[], 'Year':[],'Quarter':[],'Insurance_type':[], 'Insurance_count':[], 'Insurance_amount':[]}

for i in Ins_state_list:
    p_i=path+i+"/"
    Ins_yr=os.listdir(p_i)
    for j in Ins_yr:
        p_j=p_i+j+"/"
        Ins_yr_list=os.listdir(p_j)
        for k in Ins_yr_list:
            p_k=p_j+k
            Data=open(p_k,'r')
            D=json.load(Data)
            for z in D['data']['transactionData']:
              Name=z['name']
              count=z['paymentInstruments'][0]['count']
              amount=z['paymentInstruments'][0]['amount']
              clm['Insurance_type'].append(Name)
              clm['Insurance_count'].append(count)
              clm['Insurance_amount'].append(amount)
              clm['State'].append(i)
              clm['Year'].append(j)
              clm['Quarter'].append(int(k.strip('.json')))
#Succesfully created a dataframe
Ins = pd.DataFrame(clm)
print("Data extracted:", len(Ins))

#Connect to MySQL
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Beast@9202",
    database="phonepe_pulse"
)

cursor = mydb.cursor()

#Create correct table
create_table_query = """
CREATE TABLE IF NOT EXISTS aggregated_insurance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    State VARCHAR(100),
    Year INT,
    Quarter INT,
    Insurance_type VARCHAR(100),
    Insurance_count BIGINT,
    Insurance_amount DOUBLE
);
"""
cursor.execute(create_table_query)

#Insert data
insert_query = """
INSERT INTO aggregated_insurance
(State, Year, Quarter, Insurance_type, Insurance_count, Insurance_amount)
VALUES (%s, %s, %s, %s, %s, %s)
"""

rows = list(Ins.astype({
    "Year": int,
    "Quarter": int,
    "Insurance_count": int,
    "Insurance_amount": int
}).itertuples(index=False, name=None))

print(f"{len(rows)} rows ready to insert.")

cursor.executemany(insert_query, rows)
mydb.commit()

print(f"{cursor.rowcount} rows inserted successfully.")

cursor.close()
mydb.close()