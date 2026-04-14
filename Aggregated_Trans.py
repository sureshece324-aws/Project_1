import mysql.connector
import pandas as pd
import json
import os

#Path to the data
path = "C:/Users/Neil/Documents/Suresh/Phonepe/pulse/data/aggregated/transaction/country/india/state/"

Agg_state_list = os.listdir(path)

# Data container
clm = {
    "State": [],
    "Year": [],
    "Quarter": [],
    "Transaction_type": [],
    "Transaction_count": [],
    "Transaction_amount": []
}

# Extract data
for i in Agg_state_list:
    p_i = os.path.join(path, i)
    for j in os.listdir(p_i):
        p_j = os.path.join(p_i, j)
        for k in os.listdir(p_j):
            p_k = os.path.join(p_j, k)

            with open(p_k, "r") as Data:
                D = json.load(Data)

            data = D.get("data", {}).get("transactionData", [])

            if data:
                for z in data:
                    instruments = z.get("paymentInstruments", [])
                    if instruments:
                        clm["State"].append(i)
                        clm["Year"].append(int(j))
                        clm["Quarter"].append(int(k.replace(".json", "")))
                        clm["Transaction_type"].append(z.get("name"))
                        clm["Transaction_count"].append(instruments[0].get("count", 0))
                        clm["Transaction_amount"].append(instruments[0].get("amount", 0))

#Create DataFrame
Agg_Trans = pd.DataFrame(clm)
print("Data extracted:", len(Agg_Trans))

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
CREATE TABLE IF NOT EXISTS aggregated_transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    State VARCHAR(100),
    Year INT,
    Quarter INT,
    Transaction_type VARCHAR(100),
    Transaction_count BIGINT,
    Transaction_amount DOUBLE
);
"""
cursor.execute(create_table_query)

#Insert data
insert_query = """
INSERT INTO aggregated_transactions
(State, Year, Quarter, Transaction_type, Transaction_count, Transaction_amount)
VALUES (%s, %s, %s, %s, %s, %s)
"""

rows = list(Agg_Trans.astype({
    "Year": int,
    "Quarter": int,
    "Transaction_count": int,
    "Transaction_amount": float
}).itertuples(index=False, name=None))

print(f"{len(rows)} rows ready to insert.")

cursor.executemany(insert_query, rows)
mydb.commit()

print(f"{cursor.rowcount} rows inserted successfully.")

cursor.close()
mydb.close()