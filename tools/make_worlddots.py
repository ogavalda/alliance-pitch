"""One-off: builds content/worlddots.json (land dots of a simple world map) from Natural Earth (geopandas 0.14 bundled data).
Run: pip install geopandas==0.14.4 ; python tools/make_worlddots.py"""
import json, warnings
warnings.filterwarnings("ignore")
import geopandas as gpd
from shapely.geometry import Point
w = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
w = w[w["name"] != "Antarctica"]
land = w.unary_union
step = 2.6
dots = []
lat = 82.0
row = 0
while lat > -57:
    lon = -180.0 + (step / 2 if row % 2 else 0)   # offset rows for a denser look
    while lon < 180:
        if land.contains(Point(lon, lat)):
            dots.append([round(lon, 1), round(lat, 1)])
        lon += step
    lat -= step
    row += 1
json.dump({"step": step, "dots": dots}, open("content/worlddots.json", "w"), separators=(",", ":"))
print(len(dots), "dots")
