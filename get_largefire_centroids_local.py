"""
Script to query local FGB file:

For each large fire that is active in the input bbox
and between the queried dates, output its start time,
end or latest time, end or latest area, and current centroid.

Output example: Centroids_NRT_Europe_West_Siberia_20201125_PM_lf_perimeter_20250101_20251231.csv
"""

import datetime as dt
import pandas as pd
import geopandas as gpd
import os.path
import csv

# Machine-specific main directory

# This is how the 'brewer' partition of the 'dansgaard' RAID mounted on the 'hammer' machine
# MACHINEROOT = "/autofs/brewer/rfield1/storage/observations/FIRMS/VIIRS/FEDS/LOCAL/"

# laptop
MACHINEROOT = "/Users/rfield1/data/observations/FEDS/LOCAL/"

# Path to local FGB file
FEDSDATANAME = "NRT_Europe_West_Siberia_20201125_PM_lf_perimeter"
DOWNLOADED_FILEPATH =  MACHINEROOT + FEDSDATANAME + ".fgb"

# start date for query, inclusive
START = "2025-01-01T00:00:00+00:00"

# end date for query, exclusive
STOP = "2025-12-31T23:59:00+00:00"

# output location and prefix
OUT_DIR = MACHINEROOT + "OUTPUT/"
OUT_FILE_PREFIX = "Centroids"

# assumes WGS84
# BBOX = ["-126.4", "24.0", "-61.4", "49.4"] # CONUS, roughly

# haven't tried this filter yet
BBOX_NAME = FEDSDATANAME 
BBOX = [] #["-180", "-90", "180", "90"] 

##########################################################################################
#
# All settings above here please
#
##########################################################################################
if not os.path.exists(OUT_DIR):
   os.mkdir(OUT_DIR)   

df = gpd.read_file(DOWNLOADED_FILEPATH)
rows, columns = df.shape
print(f"Number of rows: {rows}, Number of columns: {columns}")

df.t = pd.to_datetime(df.t, utc=True)
start = pd.to_datetime(START)
stop = pd.to_datetime(STOP)

if BBOX:
    df = df.cx[BBOX[0] : BBOX[2], BBOX[1] : BBOX[3]]

# get ids of fires active in timestep
ids = df[(df["t"] >= start) & (df["t"] <= stop)].fireID.unique()
print(f"Number of unique IDs in time range: {len(ids)}")

# get all timesteps for fires that were active in date range even if some timesteps are outside of date range
# note that unlike with API version, this could lead to having dates after the STOP param
filtered = df[df["fireID"].isin(ids)]

fires = []

print(f"Processing {rows} fires")
for fid in filtered.fireID.unique():
    print(f"Current fid: {fid} ")
    rows = filtered[filtered["fireID"] == fid].sort_values(by="t", ascending=False)
    fire = {
        "fireid": fid,
        "start_t": rows.t.min(),
        "latest_t": rows.t.max(),
        "max_farea": rows.farea.max(),
        "centroid": rows.centroid.iloc[0],  # of latest perimeter
        "region": rows.region.iloc[0],
    }
    fires.append(fire)

print(f"Processed {len(fires)} fires")
fires = gpd.GeoDataFrame.from_dict(fires, geometry="centroid", crs=filtered.crs)

fires = fires.to_crs(crs="epsg:4326")

start_str = dt.datetime.fromisoformat(START).strftime("%Y%m%d")
stop_str = dt.datetime.fromisoformat(STOP).strftime("%Y%m%d")
outpath = OUT_DIR + OUT_FILE_PREFIX + "_" + BBOX_NAME + "_" + start_str + "_" + stop_str + ".csv"
fires.to_csv(outpath, index=False)

print(f"Wrote {len(fires)} fires to {outpath}")
