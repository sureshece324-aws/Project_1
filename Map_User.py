import mysql.connector
import pandas as pd
import json
import os

#path to get the data

path = "C:/Users/Neil/Documents/Suresh/Phonepe/pulse/data/map/user/hover/country/india/state/"
MapUser_state_list=os.listdir(path)
MapUser_state_list
#MapUser_state_list--> to get the list of states in India

#This is to extract the data's to create a dataframe

clm = {
    'State': [],
    'Year': [],
    'Quarter': [],
    'District': [],
    'Registered_Users': [],
    'App_Opens': [],
}

for i in MapUser_state_list:
    p_i=path+i+"/"
    MapUser_yr=os.listdir(p_i)

    for j in MapUser_yr:
        p_j=p_i+j+"/"
        MapUser_yr_list=os.listdir(p_j)

        for k in MapUser_yr_list:
            p_k=p_j+k
            Data=open(p_k,'r')
            D=json.load(Data)

            # Correctly access 'hoverData' and iterate through its items
            if 'hoverData' in D['data']:
              for district_name, district_data in D['data']['hoverData'].items():
        
                District = district_name.replace(" district", "").lower()

                clm['State'].append(i)
                clm['Year'].append(int(j))
                clm['Quarter'].append(int(k.replace('.json', '')))
                clm['District'].append(District)
                clm['Registered_Users'].append(district_data['registeredUsers'])
                clm['App_Opens'].append(district_data['appOpens'])

# Create DataFrame
Map_User_df = pd.DataFrame(clm)

#Preview
Map_User_df

#connect to mysql
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="Beast@9202",
  database="phonepe_pulse"
)
cursor = mydb.cursor()

#Create correct table
create_table_query = """
Create table if not exists map_user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    State VARCHAR(100),
    Year INT,
    Quarter INT,
    District VARCHAR(100),
    Registered_Users INT,
    App_Opens INT
)
"""
cursor.execute(create_table_query)

Insert_query = """
Insert into map_user
(State, Year, Quarter, District, Registered_Users, App_Opens)
values (%s, %s, %s, %s, %s, %s)
"""
rows = list(Map_User_df.astype({
    "Year": int,
    "Quarter": int,
    "District": str,
    "Registered_Users": int,
    "App_Opens": int
}).itertuples(index=False, name=None))

cursor.executemany(Insert_query, rows)
mydb.commit()

print(f"{cursor.rowcount} rows inserted.")
cursor.close()
mydb.close()

