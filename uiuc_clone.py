"""
This module defines a function to clone the entirity of the UIUC 
online Airfoil database to a given MongoDB instance.

27 distinct collections are created, one for each letter of the
alphabet a,b,c,...,z and an additional one called "numeric".

Each airfoil is stored in a separate document with the following
fields:
_id  -> ObjectID
code -> String: Airfoil Code
x    -> List:   Airfoil x-coordinates
y    -> List:   Airfoil y-coordinates
"""


# IMPORT EXTERNAL MODULES #
from pymongo import MongoClient


# IMPORT INTERNAL MODULES #
import uiuc



# --- CLONE UIUC AIRFOIL DATABASE TO GIVEN MONGODB INSTANCE --- #
# @conn   -> String: connection string to MongoDB instance e.g. "mongodb://localhost:27017"
# @dbname -> String: database name
# @return -> None 
def cloneDB(conn, dbname):

	client = MongoClient(conn)						                                                  # Connect to MongoDB instance
	db = client[dbname]                                                                               # Create/use the Aerofoils database

	index = uiuc.requestAirfoilIndex()																  # GET dictionary {letter: [airfoil-codes]} for all airfoils in UIUC online DB
	key_list = " | ".join(list(index.keys()))

	for key in index.keys():																		  # Loop through alphabetic keys of @index dictionary
		print("CURRENT KEY: ", key, " of ", key_list, "\n")
		n = len(index[key])
		i = 1
		for code in index[key]:																		  # Loop through all airfoil codes starting with @key
			doc = uiuc.requestAirfoilCoordinates(code)												  # GET x,y coordinates of airfoil
			db[key].insert_one(doc)																	  # Insert x,y coordinates into MongoDB
			print("SUCCESSFULLY STORED ", code, " to MongoDB...", 
				  "(" + str(i) + "/" + str(n) + ")")
			i += 1



# # DEMO
# ######
# cloneDB(conn="mongodb://localhost:27017", dbname="airfoildbtest")