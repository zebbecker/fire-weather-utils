"""
Script to query FEDS API: 

For each large fire that is active in the input bbox 
and between the queried dates, output its start time, 
end or latest time, end or latest area, and current centroid. 

Output: example20241201_20241208.csv
"""
import sys 
import requests
import datetime as dt 
import geopandas as gpd 
from owslib.ogcapi.features import Features 

# start date for query, inclusive 
START = "2025-01-01T00:00:00+00:00"

# end date for query, exclusive
STOP = "2025-01-13T00:00:00+00:00"

OUT_FILE_PREFIX = "example"

# assumes WGS84
# BBOX = ["-126.4", "24.0", "-61.4", "49.4"] # CONUS, roughly
BBOX = [] # no bbox

OGC_URL = "https://firenrt.delta-backend.com"
api = Features(url=OGC_URL)


# Initial query to get IDs of active fires 
res = api.collection_items(
    "public.eis_fire_lf_perimeter_nrt", 
    bbox=BBOX, 
    datetime=[START + "/" + STOP], 
    limit=8000
)

if len(res["features"]) < 1:
    print("No fires found matching this query.")
    sys.exit()

gdfs = [gpd.GeoDataFrame.from_features(res["features"])]
next_link = next(
    (link['href'] for link in res['links'] if link['rel'] == 'next'), None
)

while next_link:
    res = requests.get(next_link).json()
    
    gdfs.append(
        gpd.GeoDataFrame.from_features(res["features"])
    )
    
    next_link = next(
        (link['href'] for link in perims['links'] if link['rel'] == 'next'), None
    )


perims = gpd.pd.concat(gdfs, ignore_index=True)

print(f"Returned {len(perims)} perimeters")

ids = perims.fireid.astype(int).unique()


# Second query to get full history of these fires, 
# even if they started or ended outside of date range
res = api.collection_items(
    "public.eis_fire_lf_perimeter_nrt", 
    bbox=BBOX, 
    limit=8000,
    filter="fireid IN (" + ",".join([str(i) for i in ids]) + ")"
    # filter="farea>5 AND fireid IN (" + ",".join([str(i) for i in ids]) + ")"
)

gdfs = [gpd.GeoDataFrame.from_features(res["features"]).set_crs("EPSG:4326")]
next_link = next(
    (link['href'] for link in res['links'] if link['rel'] == 'next'), None
)
while next_link:
    # print("Retrieving next page ...")
    res = requests.get(next_link).json()
    gdfs.append(
        gpd.GeoDataFrame.from_features(res["features"]).set_crs("epsg:4326")
    )

    next_link = next(
        (link['href'] for link in res['links'] if link['rel'] == 'next'), None
    )

gdf = gpd.pd.concat(gdfs, ignore_index=True)

# output csv with centroid, start time, latest time, latest size for each fireid
fires = []
for fid in gdf.fireid.unique():
    
    id_rows = gdf[gdf["fireid"] == fid]
    for region in id_rows.region.unique():
        
        rows = id_rows[id_rows["region"] == region].sort_values(by='t', ascending=False)
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









