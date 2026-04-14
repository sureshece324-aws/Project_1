import mysql.connector
import pandas as pd
import json
import os

from Aggregated_Ins import Ins

#Path to the data
path = "C:/Users/Neil/Documents/Suresh/Phonepe/pulse/data/aggregated/user/country/india/state/"
User_state_list=os.listdir(path)
User_state_list
#User_state_list--> to get the list of states in India

#This is to extract the data's to create a dataframe

clm = {
    'State': [],
    'Year': [],
    'Quarter': [],
    'Registered_Users': [],
    'App_Opens': [],
    'Brand': [],
    'User_Count': [],
    'Percentage': []}

for i in User_state_list:
    p_i=path+i+"/"
    User_yr=os.listdir(p_i)

    for j in User_yr:
        p_j=p_i+j+"/"
        User_yr_list=os.listdir(p_j)

        for k in User_yr_list:
            p_k=p_j+k
            Data=open(p_k,'r')
            D=json.load(Data)

            # Extract aggregated data outside the device loop but inside quarter loop
            reg_users = D['data']['aggregated']['registeredUsers']
            app_opens = D['data']['aggregated']['appOpens']

            # Add a check to ensure 'usersByDevice' is not None before iterating
            if 'usersByDevice' in D['data'] and D['data']['usersByDevice']:
                for z in D['data']['usersByDevice']:
                    brand = z['brand']
                    count = z['count']
                    percent = z['percentage']

                    # Append to dictionary inside the loop, including new keys
                    clm['State'].append(i)
                    clm['Year'].append(j)
                    clm['Quarter'].append(int(k.strip('.json')))
                    clm['Registered_Users'].append(reg_users)
                    clm['App_Opens'].append(app_opens)
                    clm['Brand'].append(brand)
                    clm['User_Count'].append(count)
                    clm['Percentage'].append(percent)

# Create DataFrame
User_Device_df = pd.DataFrame(clm)
print(User_Device_df)

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
CREATE TABLE IF NOT EXISTS aggregated_user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    State VARCHAR(100),
    Year INT,
    Quarter INT,
    Registered_Users BIGINT,
    App_Opens BIGINT,
    Brand VARCHAR(100),
    User_Count BIGINT,
    Percentage DOUBLE
);
"""
cursor.execute(create_table_query)

#Insert data
insert_query = """
INSERT INTO aggregated_user
(State, Year, Quarter, Registered_Users, App_Opens, Brand, User_Count, Percentage)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""

rows = list(User_Device_df.astype({
    "Year": int,
    "Quarter": int,
    "Registered_Users": int,
    "App_Opens": int,
    "User_Count": int,
    "Percentage": float
}).itertuples(index=False, name=None))

print(f"{len(rows)} rows ready to insert.")

cursor.executemany(insert_query, rows)
mydb.commit()

print(f"{cursor.rowcount} rows inserted successfully.")

cursor.close()
mydb.close()