"""
Script to query local FGB file for a list of fireID within a named region.

Outputs a shapefile with each perimeter for each fire. If fireline data are also available, 
additionally outputs a shapefile with each fireline for each fire. 

Might want to combine this with 'get_farea_history_local'
"""
import sys
import pandas as pd
import geopandas as gpd
import os
import csv


# Machine-specific main directory

# This is how the 'brewer' partition of the 'dansgaard' RAID mounted on the 'hammer' machine
# MACHINEROOT = "/autofs/brewer/rfield1/storage/observations/FIRMS/VIIRS/FEDS/LOCAL/"

# laptop
MACHINEROOT = "/Users/rfield1/data/observations/FEDS/LOCAL/"
 
# Path to local FGB file
FEDSDATANAME = "NRT_Europe_West_Siberia_20201125_PM_lf_perimeter"
FEDSFIRELINENAME = "" 

DOWNLOADED_FILEPATH = MACHINEROOT + FEDSDATANAME + ".fgb"
DOWNLOADED_FLINE_FILEPATH = MACHINEROOT  + FEDSFIRELINENAME + ".fgb" 

# output location and prefix
OUT_DIR = MACHINEROOT + "OUTPUT/"

# Path to csv of FEDS IDs to extract time series for
FIRE_ID_PATH = OUT_DIR + "Centroids_NRT_Europe_West_Siberia_20201125_PM_lf_perimeter_20250101_20251231.csv"


# MAAP settings for testing 
# MACHINEROOT = "/projects/my-public-bucket/FEDSstaging/FEDSoutput-v3/NRT_Europe_W_Siberia/2025/CombinedLargefire/20251231PM/"
# OUT_DIR = "./output/"
# FEDSDATANAME = "lf_perimeter"
# FEDSFIRELINENAME = "lf_fireline"
# FIRE_ID_PATH = "Europe_example_20250702_20250714.csv"


# below, should add option for the old way of specifying a single fire or list of fires
#FIRE_ID_LIST = 72552
#FIRE_ID_PATH = [];

# should probably be constructing the above from this REGION variable, except that they're not quite the same yet
# also need to consider if this can change across FEDS objects in an *.fgb file
REGION = "NRT_Europe_W_Siberia"
OUT_FILE_PREFIX = "perimeters"
OUT_FILE_PREFIX_FIRELINE = "firelines"

##########################################################################################
#
# All settings above here please
#
##########################################################################################
perims = gpd.read_file(DOWNLOADED_FILEPATH)

if os.path.isfile(DOWNLOADED_FLINE_FILEPATH):
    flines = gpd.read_file(DOWNLOADED_FLINE_FILEPATH) 
    use_firelines = True 
else: 
    use_firelines = False
    print("No fireline file found. Continuing with perimeters only.")
    
    
if not os.path.exists(OUT_DIR):
    os.mkdir(OUT_DIR)


# read the coordinates in the csv
with open(FIRE_ID_PATH, newline='') as csvfile:
    fireIDTable = csv.DictReader(csvfile)
    for row in fireIDTable:
        FIRE_ID = int(float(row['fireid']))

        filtered = perims[(perims["fireID"] == FIRE_ID) & (perims["region"] == REGION)].copy()

        if len(filtered) < 1:
            print(f"No fire perimeters found matching {REGION} fireid {FIRE_ID}")
            #sys.exit()

        else:
            print(f"{len(filtered)} perimeters for {REGION} fireid {FIRE_ID}.")

            # Extract timestamp from primarykey
            filtered["perim_t"] = pd.to_datetime(filtered["primarykey"].str.split('|').str[-1])
            filtered = filtered.sort_values(by="perim_t", ascending=True)
            filtered["perim_t"] = filtered["perim_t"].astype(str)
            filtered["t_st"] = filtered["t_st"].astype(str) 
            filtered["t_ed"] = filtered["t_ed"].astype(str)

            outpath = OUT_DIR + OUT_FILE_PREFIX + '_' + REGION +'_' + str(FIRE_ID)
            filtered.to_file(outpath, index=False)

            print(f"Wrote perimeters shapefile to {outpath}")

        if use_firelines: 
            filtered = flines[(flines["fireID"] == FIRE_ID) & (flines["region"] == REGION)].copy()

            if len(filtered) < 1:
                print(f"No firelines found matching {REGION} fireid {FIRE_ID}")
            
            # Extract timestamp from primarykey
            filtered["perim_t"] = pd.to_datetime(filtered["primarykey"].str.split('|').str[-1])
            filtered = filtered.sort_values(by="perim_t", ascending=True)
            filtered["perim_t"] = filtered["perim_t"].astype(str)
            filtered["t_st"] = filtered["t_st"].astype(str) 
            filtered["t_ed"] = filtered["t_ed"].astype(str)

            outpath = OUT_DIR + OUT_FILE_PREFIX_FIRELINE + '_' + REGION +'_' + str(FIRE_ID)
            filtered.to_file(outpath, index=False)

            print(f"Wrote firelines shapefile to {outpath}")
            
