"""
Script to query local FGB file for a specific fireID within a named region.

Outputs a CSV with a sorted timeseries of farea, primarykey, and perimeter centroids.

E.g. -> farea_CONUS_415.csv
"""
import sys
import pandas as pd
import geopandas as gpd

# Path to local FGB file
DOWNLOADED_FILEPATH = "~/Downloads/lf_perimeter.fgb"

FIRE_ID = 72552
REGION = "NRT_Europe_W_Siberia"
OUT_FILE_PREFIX = "farea"

gdf = gpd.read_file(DOWNLOADED_FILEPATH)

# Filter by fire ID and region
filtered = gdf[(gdf["fireID"] == FIRE_ID) & (gdf["region"] == REGION)]

if len(filtered) < 1:
    print(f"No fires found matching {REGION} fireid {FIRE_ID}")
    sys.exit()

# Extract timestamp from primarykey
filtered["perim_t"] = pd.to_datetime(filtered["primarykey"].str.split('|').str[-1])

filtered = filtered.sort_values(by="perim_t", ascending=True)

filtered["centroid"] = filtered.geometry.centroid

outpath = "_".join([OUT_FILE_PREFIX, REGION, str(FIRE_ID)]) + ".csv"
filtered[["primarykey", "farea", "centroid"]].to_csv(outpath, index=False)

print(f"Wrote {len(filtered)} records to {outpath}")
