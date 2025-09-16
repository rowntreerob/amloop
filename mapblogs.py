import json
from pathlib import Path
import streamlit as st
import folium
from streamlit.components.v1 import html as st_html

st.set_page_config(page_title="Great Loop Map", layout="wide")
st.title("America's Great Loop — Blog Map")

# Choose GeoJSON file
default_geo = Path("./greatloopplaces-001.geojson")
geo_path = st.file_uploader("Upload GeoJSON", type=["geojson"], accept_multiple_files=False)
if geo_path is None and default_geo.exists():
    geo_data = json.loads(default_geo.read_text(encoding="utf-8"))
elif geo_path is not None:
    geo_data = json.loads(geo_path.read().decode("utf-8"))
else:
    st.warning("Upload a GeoJSON file with features containing properties: url, title, place.")
    st.stop()

features = geo_data.get("features", [])

# Controls
limit = st.slider("Max markers to render", 10, max(10, len(features)), min(200, len(features)))
features = features[:limit]

# Build Folium map
m = folium.Map(location=[39, -84], zoom_start=5, tiles="OpenStreetMap", control_scale=True)
bounds = []

for ft in features:
    geom = ft.get("geometry", {})
    props = ft.get("properties", {})
    coords = geom.get("coordinates", [])
    if not coords or len(coords) != 2:
        continue
    lon, lat = coords
    place = props.get("place", "")
    title = props.get("title", "")
    url = props.get("url", "")
    popup_html = folium.Popup(
        f'<div style="min-width:220px">'
        f'<div style="font-weight:600;margin-bottom:4px">{place}</div>'
        f'<a href="{url}" target="_blank" rel="noopener">{title}</a>'
        f"</div>",
        max_width=300,
    )
    folium.Marker([lat, lon], popup=popup_html, tooltip=place).add_to(m)
    bounds.append((lat, lon))

if bounds:
    m.fit_bounds(bounds, padding=(20, 20))

# Render Folium inside Streamlit
st_html(m._repr_html_(), height=700)
