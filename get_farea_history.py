"""
Script to query FEDS API for a specific fireID. 

Outputs a CSV with a sorted timeseries of farea, primarykey, and perimeter centroids.

E.g. -> farea_18007.csv
"""

import requests
import pandas as pd
import geopandas as gpd 
from owslib.ogcapi.features import Features 

FIRE_ID = 18007
OUT_FILE_PREFIX = "farea_"

OGC_URL = "https://firenrt.delta-backend.com"
api = Features(url=OGC_URL)

res = api.collection_items(
    "public.eis_fire_lf_perimeter_nrt", 
    limit = 8000, 
    filter = "fireid=" + str(FIRE_ID)
)

gdf = gpd.GeoDataFrame.from_features(res["features"]).set_crs("epsg:4326")

gdf["perim_t"] = pd.to_datetime(gdf["primarykey"].str.split('|').str[-1])

gdf = gdf.sort_values(by="perim_t", ascending=True)
gdf["centroid"] = gdf.geometry.centroid

gdf[["primarykey", "farea", "centroid"]].to_csv(OUT_FILE_PREFIX + str(FIRE_ID) + ".csv", index=False) 
