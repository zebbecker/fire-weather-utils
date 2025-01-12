"""
Script to query FEDS API for a specific fireID within a named region. 

Outputs a CSV with a sorted timeseries of farea, primarykey, and perimeter centroids.

E.g. -> farea_CONUS_415.csv
"""

import requests
import pandas as pd
import geopandas as gpd 
from owslib.ogcapi.features import Features 

FIRE_ID = 415
REGION = "CONUS"
OUT_FILE_PREFIX = "farea"

OGC_URL = "https://firenrt.delta-backend.com"
api = Features(url=OGC_URL)

res = api.collection_items(
    "public.eis_fire_lf_perimeter_nrt", 
    limit = 8000, 
    filter=f"fireid={str(FIRE_ID)} AND region='{REGION}'"
)


if len(res["features"]) < 1:
    print(f"No fires found matching {REGION} fireid {FIRE_ID}")
    exit()

gdf = gpd.GeoDataFrame.from_features(res["features"]).set_crs("epsg:4326")

print(f"Returned {len(gdf)} perimeters for {REGION} fireid {FIRE_ID}.")

gdf["perim_t"] = pd.to_datetime(gdf["primarykey"].str.split('|').str[-1])

gdf = gdf.sort_values(by="perim_t", ascending=True)
gdf["centroid"] = gdf.geometry.centroid

outpath = "_".join([OUT_FILE_PREFIX, REGION, str(FIRE_ID)]) + ".csv"

gdf[["primarykey", "farea", "centroid"]].to_csv(outpath, index=False) 
