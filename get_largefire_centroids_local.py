"""
Script to query local FGB file:

For each large fire that is active in the input bbox
and between the queried dates, output its start time,
end or latest time, end or latest area, and current centroid.

Output: example20241201_20241208.csv
"""

import datetime as dt
import pandas as pd
import geopandas as gpd

# Path to local FGB file
DOWNLOADED_FILEPATH = "/Users/work/Downloads/lf_perimeter.fgb"

# start date for query, inclusive
START = "2025-07-02T00:00:00+00:00"

# end date for query, exclusive
STOP = "2025-07-14T00:00:00+00:00"

OUT_FILE_PREFIX = "Europe_example_"

# assumes WGS84
# BBOX = ["-126.4", "24.0", "-61.4", "49.4"] # CONUS, roughly
BBOX = []  # no bbox

df = gpd.read_file(DOWNLOADED_FILEPATH)

df.t = pd.to_datetime(df.t, utc=True)
start = pd.to_datetime(START)
stop = pd.to_datetime(STOP)

if BBOX:
    df = df.cx[BBOX[0] : BBOX[2], BBOX[1] : BBOX[3]]

# get ids of fires active in timestep
ids = df[(df["t"] >= start) & (df["t"] <= stop)].fireID.unique()

# get all timesteps for fires that were active in date range even if some timesteps are outside of date range
# note that unlike with API version, this could lead to having dates after the STOP param
filtered = df[df["fireID"].isin(ids)]

fires = []

for fid in filtered.fireID.unique():
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

fires = gpd.GeoDataFrame.from_dict(fires, geometry="centroid", crs=filtered.crs)

fires = fires.to_crs(crs="epsg:4326")


start_str = dt.datetime.fromisoformat(START).strftime("%Y%m%d")
stop_str = dt.datetime.fromisoformat(STOP).strftime("%Y%m%d")
outpath = OUT_FILE_PREFIX + start_str + "_" + stop_str + ".csv"
fires.to_csv(outpath, index=False)

print(f"Wrote {len(fires)} fires to {outpath}")
