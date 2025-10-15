"""
Script to query FEDS API: 

For each large fire that is active in the input bbox 
and between the queried dates, output its start time, 
end or latest time, end or latest area, and current centroid. 

Output: example20241201_20241208.csv
"""
import sys 
import datetime as dt 
import pandas as pd
import geopandas as gpd 
from owslib.ogcapi.features import Features 
from helpers import iter_features_offset

# start date for query, inclusive 
START = "2025-01-01T00:00:00+00:00"

# end date for query, exclusive
STOP = "2025-01-13T00:00:00+00:00"

OUT_FILE_PREFIX = "fixed_example"

# assumes WGS84
# BBOX = ["-126.4", "24.0", "-61.4", "49.4"] # CONUS, roughly
BBOX = [] # no bbox

OGC_URL = "https://openveda.cloud/api/features"
api = Features(url=OGC_URL)

# Initial query to get IDs of active fires 
print("Fetching initial fire perimeters....")
features = iter_features_offset(
    api, 
    "public.eis_fire_lf_perimeter_nrt",
    params={"bbox": BBOX, "datetime": [START + "/" + STOP]},
    page_size=100, 
    progress=True
)

if len(features) < 1: 
    print(f"No fires found for {str(BBOX)} between {START} and {STOP}")
    sys.exit()

perims = gpd.GeoDataFrame.from_features(features).set_crs("EPSG:4326")

print(f"Returned {len(perims)} perimeters") 

ids = perims.fireid.astype(int).unique()


# Second query to get full history of these fires, 
# even if they started or ended outside of date range
print(f"Fetching full fire history for {len(ids)} fires...")

features = iter_features_offset(
    api, 
    "public.eis_fire_lf_perimeter_nrt", 
    params={
        "bbox": BBOX, 
        "filter": "fireid IN (" + ",".join([str(i) for i in ids]) +")"
    }, 
    page_size=100,
    progress=True
)

gdf = gpd.GeoDataFrame.from_features(features).set_crs("EPSG:4326") 

gdf["t"] = pd.to_datetime(gdf["t"])

start = pd.Timestamp(START).date() 
stop = pd.Timestamp(STOP).date() 

# output csv with centroid, start time, latest time, latest size for each fireid
fires = []
for fid in gdf.fireid.unique():
    
    id_rows = gdf[gdf["fireid"] == fid]
    for region in id_rows.region.unique():
        
        rows = id_rows[id_rows["region"] == region].sort_values(by='t', ascending=False)

        # need to filter out duplicate IDs from other regions that are totally outside the query range

        # if any t for this fire is within range, keep it. Else skip
        mask = (rows["t"].dt.date >= start) & (rows["t"].dt.date <= stop) 
        if mask.any():
            fire = {
                'fireid': fid, 
                'start_t': rows.t.min(), 
                'latest_t': rows.t.max(), 
                'max_farea': rows.farea.max(),
                'centroid': rows.centroid.iloc[0], # of latest perimeter
                'region': region 
            }
            fires.append(fire) 

fires = gpd.GeoDataFrame.from_dict(fires, geometry="centroid", crs="epsg:4326")

start = dt.datetime.fromisoformat(START).strftime("%Y%m%d")
stop = dt.datetime.fromisoformat(STOP).strftime("%Y%m%d")
outpath = OUT_FILE_PREFIX + start + "_" + stop + ".csv"
fires.to_csv(outpath)









