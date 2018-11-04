"""
This module contains a set of functions which taken together allow for web-scraping of
the UIUC online Airfoil database.
"""

# IMPORT EXTERNAL MODULES #
from urllib.request import urlopen																		
from bs4 import BeautifulSoup																			
from urllib.error import HTTPError																		
import re 																								



# --- GENERATE A DICTIONARY/KEY/INDEX OF ALL AIRFOILS IN THE UIUC DATABASE --- #
# @return -> Dictionary: Mapping from lowercase alphabetic char to list (of strings) 
#                        of all airfoils whose codes begin with that letter
def requestAirfoilIndex():
	# REQUEST AND STORE STRINGIFIED HTML FILE #
	url_index = "https://m-selig.ae.illinois.edu/ads/coord_database.html"								# URL string to index page on UIUC website
	html = urlopen(url_index)																			# Open socket connection to html page containing airfoil codes
	dom = BeautifulSoup(html, 'html.parser')															# Parse the html page to bs4's DOM object
	html.close()																						# Close socket connection

	# FILTER REQUESTED PAGE FOR AIRFOIL CODES #
	airfoil_tags = dom.findAll("a", {"href": re.compile("coord/[a-zA-Z0-9_]*(.dat)")})					# List of stringified html tags whose href attribute matches
																										# the following regex: "coord/{airfoil-code}.dat
    # PARSE AIRFOIL CODES #
	codes = {"a": [], "b": [], "c": [], "d": [], "e": [], "f": [], "g": [], "h": [],					# Intialise dictionary to store airfoil codes alphabetically
			 "i": [], "j": [], "k": [], "l": [], "m": [], "n": [], "o": [], "p": [],
			 "q": [], "r": [], "s": [], "t": [], "u": [], "v": [], "w": [], "x": [],
			 "y": [], "z": [], "numeric": []}

	for tag in airfoil_tags:																			# Loop through stringified html tags
		code = tag.get_text()[:-4].replace(" ", "")														# Extract the text content from the html tag and remove .dat extension
		codes[code[0].lower() if code[0].isalpha() else "numeric"].append(code)							# Append airfoil code to @codes dictionary

	return codes 																						# Return dictionary of airfoil codes



# --- SCRAPE AIRFOIL COORDINATES FROM UIUC DATABASE --- #
# @code    -> String: Airfoil Code
# @return  -> Dictionary: Lists of airfoil x,y coordinates
def requestAirfoilCoordinates(code):
	# REQUEST AND STORE STRINGIFIED .dat file #
	url_coords = "https://m-selig.ae.illinois.edu/ads/coord/"											# URL string to airfoil coordinates .dat file - must append {airfoil-code}.dat
	try:
		dat = urlopen(url_coords + code + ".dat")														# Open socket connection to .dat file containing airfoil coordinates
	except HTTPError:																					# Exit function in case of an HTTP error (most likely 404)
		return {}
	try:
		coords_str = dat.read().decode("utf8")															# Read byte-stream and decode to string
	except UnicodeDecodeError:
		coords_str = b"".join(dat.readlines()[1:]).decode("utf8")										# Account for non-utf8 characters in header -> remove first line of byte-stream
	dat.close()																							# Close socket connection

	# PARSE AIRFOIL COORDINATES #
	x = []																								# Initialise list of x-coordinates
	y = []																								# Initialise list of y-coordinates
	for line in coords_str.split("\n"):																	# Loop through lines of stringified .dat file
		temp = line.split()
		if len(temp) != 2:																				# Ignore line if it contains more than 2 items (header)
			continue
		if (len(temp[0].replace(".", "")) + len(temp[1].replace(".", ""))) <= 6:						# Ignore numeric headers e.g. "17.0		17.0"
			continue
		try:																							# Attempt to cast 2-item line to 2 separate floats
			x.append(float(temp[0]))																			
			y.append(float(temp[1]))
		except ValueError:																				# Catch ValueError and skip line (line contains non-coordinate content)
			pass

	return {"code": code, "x": x, "y": y}																# Return dictionary of airfoil coordinates