import mysql.connector
import pandas as pd
import json
import os

#path to get the data

path = "C:/Users/Neil/Documents/Suresh/Phonepe/pulse/data/map/insurance/hover/country/india/state/"
MapIns_state_list=os.listdir(path)
MapIns_state_list
#MapInsurance_state_list--> to get the list of states in India

#This is to extract the data's to create a dataframe

clm={'State':[], 'Year':[],'Quarter':[],'District':[], 'Insurance_count':[], 'Insurance_amount':[]}

for i in MapIns_state_list:
    p_i=path+i+"/"
    MapIns_yr=os.listdir(p_i)
    for j in MapIns_yr:
        p_j=p_i+j+"/"
        MapIns_yr_list=os.listdir(p_j)
        for k in MapIns_yr_list:
            p_k=p_j+k
            Data=open(p_k,'r')
            D=json.load(Data)
            for z in D['data']['hoverDataList']:
              District = z['name'].replace(" district", "")
              count=z['metric'][0]['count']
              amount=z['metric'][0]['amount']
              clm['District'].append(District)
              clm['Insurance_count'].append(count)
              clm['Insurance_amount'].append(amount)
              clm['State'].append(i)
              clm['Year'].append(j)
              clm['Quarter'].append(int(k.strip('.json')))
#Succesfully created a dataframe
MapIns = pd.DataFrame(clm)

#Preview
MapIns

#connect to mysql'
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="Beast@9202",
  database="phonepe_pulse"
)

cursor = mydb.cursor()

#Create correct table
create_table_query = """
Create table if not exists map_insurance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    State VARCHAR(100),
    Year INT,
    Quarter INT,
    District VARCHAR(100),
    Insurance_count BIGINT,
    Insurance_amount DOUBLE
);
"""
cursor.execute(create_table_query)

Insert_query = """
Insert into map_insurance
(State, Year, Quarter, District, Insurance_count, Insurance_amount)  
values (%s, %s, %s, %s, %s, %s)
"""
rows = list(MapIns.astype({
    "Year": int,
    "Quarter": int,
    "District": str,
    "Insurance_count": int,
    "Insurance_amount": float
}).itertuples(index=False, name=None))
cursor.executemany(Insert_query, rows)
mydb.commit()

print(f"{cursor.rowcount} rows inserted successfully.")

cursor.close()
mydb.close()
