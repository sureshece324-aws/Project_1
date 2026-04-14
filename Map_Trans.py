import mysql.connector
import pandas as pd
import json
import os

#path to get the data 

path="C:/Users/Neil/Documents/Suresh/Phonepe/pulse/data/map/transaction/hover/country/india/state/"
Trans_state_list=os.listdir(path)
Trans_state_list
#Trans_state_list--> to get the list of states in India

#This is to extract the data's to create a dataframe

clm={'State':[], 'Year':[],'Quarter':[],'District':[], 'Transaction_count':[], 'Transaction_amount':[]}

for i in Trans_state_list:
    p_i=path+i+"/"
    Trans_yr=os.listdir(p_i)
    for j in Trans_yr:
        p_j=p_i+j+"/"
        Trans_yr_list=os.listdir(p_j)
        for k in Trans_yr_list:
            p_k=p_j+k
            Data=open(p_k,'r')
            D=json.load(Data)
            for z in D['data']['hoverDataList']:
              District=z['name'].replace(" district", "")
              count=z['metric'][0]['count']
              amount=z['metric'][0]['amount']
              clm['District'].append(District)
              clm['Transaction_count'].append(count)
              clm['Transaction_amount'].append(amount)
              clm['State'].append(i)
              clm['Year'].append(j)
              clm['Quarter'].append(int(k.strip('.json')))
#Succesfully created a dataframe
Trans=pd.DataFrame(clm)
Trans

#Connect to mysql
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="Beast@9202",
  database="phonepe_pulse" 
)
cursor = mydb.cursor()

#Create correct table
create_table_query = """
Create table if not exists map_transaction (
    id INT AUTO_INCREMENT PRIMARY KEY,
    State VARCHAR(100),
    Year INT,
    Quarter INT,
    District VARCHAR(100),
    Transaction_count BIGINT,
    Transaction_amount DOUBLE
);
"""
Insert_query = """
Insert into map_transaction 
(State, Year, Quarter, District, Transaction_count, Transaction_amount)
values (%s, %s, %s, %s, %s, %s)
"""
cursor.execute(create_table_query)

rows = list(Trans.astype({
    "Year": int,
    "Quarter": int,
    "District": str,
    "Transaction_count": int,
    "Transaction_amount": float
}).itertuples(index=False, name=None))

cursor.executemany(Insert_query, rows)
mydb.commit()

print(f"{cursor.rowcount} rows inserted successfully.")
cursor.close()
mydb.close()
