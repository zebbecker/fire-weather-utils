"""
Script to query local FGB file for a specific fireID within a named region.

Outputs a shapefile with each perimeter for that fire.
"""
import sys
import pandas as pd
import geopandas as gpd

# Path to local FGB file
DOWNLOADED_FILEPATH = "~/Downloads/lf_perimeter.fgb"

FIRE_ID = 72552
REGION = "NRT_Europe_W_Siberia"
OUT_FILE_PREFIX = "perimeters"

gdf = gpd.read_file(DOWNLOADED_FILEPATH)

filtered = gdf[(gdf["fireID"] == FIRE_ID) & (gdf["region"] == REGION)]

if len(filtered) < 1:
    print(f"No fires found matching {REGION} fireid {FIRE_ID}")
    sys.exit()

print(f"{len(filtered)} perimeters for {REGION} fireid {FIRE_ID}.")

# Extract timestamp from primarykey
filtered["perim_t"] = pd.to_datetime(filtered["primarykey"].str.split('|').str[-1])
filtered = filtered.sort_values(by="perim_t", ascending=True)
filtered["perim_t"] = filtered["perim_t"].astype(str)

outpath = "_".join([OUT_FILE_PREFIX, REGION, str(FIRE_ID)])
filtered.to_file(outpath, index=False)

print(f"Wrote shapefile to {outpath}")
