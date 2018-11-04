"""
This is the main module which contains the Airfoil class.
"""

# IMPORT EXTERNAL MODULES #
import numpy as np
import scipy.interpolate as sp
import matplotlib.pyplot as plt
import math

# IMPORT INTERNAL MODULES #
import uiuc



# --- PLOT AIRFOIL --- #
# @code  -> String:   Airfoil id
# @*args -> Tuple(s): Airfoil (x, y) coordinates
#                     multiple tuples may be supplied to plot suction and pressure surfaces separately
def plot(code, *args):

		plt.figure(figsize=(20, 10),                                                              					# Figure dimensions (width [in], height [in]) 
		           dpi=80,              														  					# Figure resolution
		           facecolor='black')                  											 					# Figure (not axes) background color

		plt.style.use(['dark_background', './aerofoil.mplstyle'])                                 					# Apply .mplystyle custom styles
		
		colours = ["blue", "red"]
		for i,data_set in enumerate(args):																			# Loop through input data-sets
			plt.plot(data_set[0], data_set[1], "x", color=colours[i]) 												# Plot current data set
		plt.axis('equal')																		 					# Set equal x,y axis ranges

		# # FOR TESTING/DEBUGGING PURPOSES ONLY - Airfoil.plot(...)#
		# for data_set in args:
		# 	for x,y in zip(data_set[0], data_set[1]):
		# 		plt.plot(x, y, "x", color="white")
		# 		plt.pause(1)
		# print("DONE PLOTTING...")

		ax = plt.gca()																			  					# Get axes object
		ax.spines['right'].set_visible(False)													  					# Switch off the right plot border
		ax.spines['top'].set_visible(False)														  					# Switch off the top plot border
		
		ax.set_xlabel('X [m]')																	  					# Set x-axis label
		ax.set_ylabel('Y [m]')																	  					# Set y-axis label
		ax.set_title(code)																		  					# Set plot title
		plt.show()																				  					# Display plot



# --- PARSE RAW AIRFOIL COORDINATES TO CONSISTENT FORMAT --- #
# @x -> List: x-coordinates as received from uiuc.requestAirfoilCoordinates
# @y -> List: y-coordinates as received from uiuc.requestAirfoilCoordinates
def parseCoordinates(x, y):

	temp = np.argsort(x) 																							# Indices that WOULD sort x-coordinates in ascending order
	limits_surf1 = sorted([min(temp[:2]), min(temp[-2:])]) 															# (x,y) indices spanning one of the distinct airfoil surfaces
	limits_surf2 = sorted([max(temp[:2]), max(temp[-2:])]) 															# (x,y) indices spanning the other distinct airfoil surface
	x1, y1 = x[limits_surf1[0]:limits_surf1[1] + 1], y[limits_surf1[0]:limits_surf1[1] + 1] 						# (x,y) coordinates of one of the distinct airfoil surfaces
	x2, y2 = x[limits_surf2[0]:limits_surf2[1] + 1], y[limits_surf2[0]:limits_surf2[1] + 1] 						# (x,y) coordinates of the other distinct airfoil surface

	if max(y1) > max(y2): 		  																					# Determine if surface is suction or pressure																						
		x_s, y_s = list(zip(* [(0.0, 0.0)] + sorted(list(zip(x1, y1)))[1:-1] + [(1.0, 0.0)] )) 						# Extract suction coordinates -> Overwrite end-points				
		x_p, y_p = list(zip(* [(0.0, 0.0)] + sorted(list(zip(x2, y2)))[1:-1] + [(1.0, 0.0)] )) 						# Extract pressure coordinates -> Overwrite end points
	else:
		x_s, y_s = list(zip(* [(0.0, 0.0)] + sorted(list(zip(x2, y2)))[1:-1] + [(1.0, 0.0)] ))
		x_p, y_p = list(zip(* [(0.0, 0.0)] + sorted(list(zip(x1, y1)))[1:-1] + [(1.0, 0.0)] ))

	# Concatenate suction and pressure surfaces to obtain (x,y) coordinates of 
	# complete Airfoil in counterclockwise order starting from TE
	# N.B. First and last points both have coordinates (xTE, yTE) - no other duplicates
	x_c = x_p[::-1][:-1] + x_s
	y_c = y_p[::-1][:-1] + y_s

	return {"x": list(x_c), "y": list(y_c), 																		# All values of returned dictionary are lists
			"x_suction": list(x_s), "y_suction": list(y_s),
			"x_pressure": list(x_p), "y_pressure": list(y_p)}



# --- SPLINE INTERPOLATION OF PARSED AIRFOIL COORDINATES --- #
# @coords     -> Dictionary: Coordinates as received from parseCoordinates
# @n          -> Integer:    Number of points for interpolated Airfoil
# @pnl_scheme -> String:     Whether to interpolate airfoil along chord or along a circle
# 						     with unit diameter
# @pnl_rule   -> Float:      Fraction by which interval length decreases for each interval
# 						     (along chord or circle dependent on @pnl_scheme)
def splineInterpolation(coords, n, pnl_scheme, pnl_rule):
	
	n_pnls = int(n/2) - 1 																							# Num. of intervals (panels) is one less num. of points 
	sum_series = np.sum(np.repeat(pnl_rule, n_pnls)**np.linspace(0, n_pnls - 1, n_pnls)) 							# Sum of power series (pnl_rule)^i where 0<i<n_pnls-1
	if pnl_scheme == "chord": 																						# Sample x-coordinates along Airfoil chord line
		delta_max = 1 / sum_series 																					# Length of maximum length interval
		delta = delta_max*pnl_rule**(n_pnls - np.linspace(1, n_pnls, n_pnls)) 										# Length of intervals
		x = np.insert(np.cumsum(delta), 0, 0) 																		# Sampled x-coordinates
	else: 																											# Sample x-coordinates along circle with unit diameter
		delta_max = math.pi / sum_series
		delta = delta_max*pnl_rule**(np.linspace(1, n_pnls, n_pnls) - 1)
		x = np.flip(0.5 + 0.5*np.cos(np.insert(np.cumsum(delta), 0, 0)), axis=0)

	coords_interp = {} 																								# Initialise empty dictionary for airfoil coordinates
	
	for suffix in ("suction", "pressure"): 																			# Loop through suction and pressure surfaces
		f = sp.CubicSpline(coords["x_" + suffix], coords["y_" + suffix], bc_type="clamped", extrapolate=None) 		# Spline interpolation function
		y = f(x) 																									# Interpolated y-coordinates
		coords_interp["x_" + suffix] = list(x) 																		# Cast interpolated x-coordinate array to list -> Update dict.
		coords_interp["y_" + suffix] = list(y) 																		# Cast interpolated y-coordinate array to list -> Update dict.

	# Concatenate interpolated suction and pressure surfaces to obtain interpolated 
	# (x,y) coordinates of complete Airfoil in counterclockwise order starting from TE
	# N.B. First and last points both have coordinates (xTE, yTE) - no other duplicates
	coords_interp["x"] = coords_interp["x_pressure"][::-1][:-1] + coords_interp["x_suction"]                   
	coords_interp["y"] = coords_interp["y_pressure"][::-1][:-1] + coords_interp["y_suction"]

	return coords_interp 																							# All values of returned dictionary are lists					



# --- AIRFOIL API --- #
class Airfoil:

	def __init__(self, code, fetchfrom="online"):
		if fetchfrom == "online": 																					# Fetch airfoil coordinates directly from online DB
			airfoil = uiuc.requestAirfoilCoordinates(code)
		self.code = code
		self.xraw = airfoil["x"]
		self.yraw = airfoil["y"]
		self.coordinates = parseCoordinates(self.xraw, self.yraw)


	def splineInterpolation(self, n=100, pnl_scheme="chord", pnl_rule=0.9):
		self.coordinates = splineInterpolation(self.coordinates, n, pnl_scheme, pnl_rule)


	def plot(self, sep="y"):
		if sep == "y":
			plt_suction = (self.coordinates["x_suction"], self.coordinates["y_suction"])
			plt_pressure = (self.coordinates["x_pressure"], self.coordinates["y_pressure"])
			plot(self.code, plt_suction, plt_pressure)
		else:
			plot(self.code, (self.coordinates["x"], self.coordinates["y"]))




# DEMO
#####
# airfoil = Airfoil("b707c")
# airfoil.splineInterpolation(n=50, pnl_scheme="circle", pnl_rule=1.0)
# airfoil.plot()



# FORTHCOMING FUNCTIONALITY
###########################
# 1) SOURCE PANEL CODE
# 2) VORTEX PANEL CODE
# 3) EULER BERNOULLI STRESS/STRAIN ANALYSIS
# 4) QUASI-LINEAR REGRESSION OPTIMISATION