"""
Script to query local FGB file for a list of fireIDs from a CSV file

For each fireID, outputs a CSV with a sorted timeseries of farea, primarykey, and perimeter centroids.

E.g. -> farea_NRT_Europe_W_Siberia_337.csv
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
DOWNLOADED_FILEPATH = MACHINEROOT + FEDSDATANAME + ".fgb"

# output location and prefix
OUT_DIR = MACHINEROOT + "OUTPUT/"

# Path to csv of FEDS IDs to extract time series for
FIRE_ID_PATH = OUT_DIR + "Centroids_NRT_Europe_West_Siberia_20201125_PM_lf_perimeter_20250101_20251231.csv"

# below, should add option for the old way of specifying a single fire or list of fires
#FIRE_ID_LIST = 72552
#FIRE_ID_PATH = [];

# should probably be constructing the above from this REGION variable, except that they're not quite the same yet
# also need to consider if this can change across FEDS objects in an *.fgb file
REGION = "NRT_Europe_W_Siberia"
OUT_FILE_PREFIX = "farea"


##########################################################################################
#
# All settings above here please
#
##########################################################################################
if not os.path.exists(OUT_DIR):
    os.mkdir(OUT_DIR)

gdf = gpd.read_file(DOWNLOADED_FILEPATH)

# read the coordinates in the csv
with open(FIRE_ID_PATH, newline='') as csvfile:
    fireIDTable = csv.DictReader(csvfile)
    for row in fireIDTable:
        FIRE_ID = int(float(row['fireid']))
		
        # Filter by fire ID and region
        filtered = gdf[(gdf["fireID"] == FIRE_ID) & (gdf["region"] == REGION)].copy()

        if len(filtered) < 1:
            print(f"No fires found matching {REGION} fireid {FIRE_ID}")
            #sys.exit()
        else:
            # Extract timestamp from primarykey
            filtered["perim_t"] = pd.to_datetime(filtered["primarykey"].str.split('|').str[-1])
            filtered = filtered.sort_values(by="perim_t", ascending=True)
            filtered["centroid"] = filtered.geometry.centroid
            outpath = OUT_DIR + "_".join([OUT_FILE_PREFIX, REGION, str(FIRE_ID)]) + ".csv"
            filtered[["primarykey", "farea", "centroid"]].to_csv(outpath, index=False)
            print(f"Wrote {len(filtered)} records to {outpath}")
