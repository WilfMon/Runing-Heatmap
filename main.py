import fitparse
import pandas as pd
import pydeck as pdk
from pathlib import Path

def clean_to_dataframe(fit_file):
    # Parse records into a list of dictionaries
    records = []
    for record in fit_file.get_messages("record"):
        row = {data.name: data.value for data in record}
        records.append(row)

    # Convert to a Pandas DataFrame
    df = pd.DataFrame(records)
    
    if 'position_lat' in df.columns and 'position_long' in df.columns:
        df = df.dropna(subset=['position_lat', 'position_long'])
        
        # Conversion factor from semicircles to degrees
        semicircle_to_deg = 180 / (2 ** 31)
        df['lat'] = df['position_lat'] * semicircle_to_deg
        df['lon'] = df['position_long'] * semicircle_to_deg
    else:
        raise ValueError("No GPS data found in this FIT file!")
        
    # Drop rows missing timestamps
    df = df.dropna(subset=['timestamp'])
    
    return df

def gen_heatmap_layer(dir_path):
    all_paths = []
    
    # Loop through all files in the directory
    for file_path in dir_path.iterdir():
        if file_path.suffix.lower() == ".fit":
            try:
                fit_file = fitparse.FitFile(str(file_path))
                df = clean_to_dataframe(fit_file)
                
                # Extract coordinate pairs [[lon, lat], [lon, lat], ...]
                coordinates = df[['lon', 'lat']].values.tolist()
                if len(coordinates) > 1:
                    all_paths.append({"path": coordinates})
            except Exception as e:
                print(f"Could not parse {file_path.name}: {e}")

    # Convert all combined routes into a single DataFrame
    path_df = pd.DataFrame(all_paths)

    # Create a single PathLayer with a semi-transparent RGBA color.
    # [255, 100, 0, 45] -> Fiery Orange with low opacity.
    # Overlapping paths will blend and accumulate intensity automatically!
    path_layer = pdk.Layer(
        "PathLayer",
        path_df,
        get_path="path",
        get_color=[255, 100, 0, 45],  # Low alpha creates the heatmap glow
        width_scale=5,
        width_min_pixels=3,
    )

    return path_layer

def render_deck(path_layer):
    # Set up the starting view center based on Birmingham
    view_state = pdk.ViewState(
        latitude=52.439508,
        longitude=-1.926828,
        zoom=13,
        pitch=30  # Slight tilt looks great for heatmaps
    )

    # Render the Deck with a dark map style to make the heatmap pop
    r = pdk.Deck(
        layers=[path_layer],
        initial_view_state=view_state,
        map_style=pdk.map_styles.DARK, # Dark background makes heatmaps look amazing
        tooltip={
            "style": {"backgroundColor": "steelblue", "color": "white"}
        }
    )

    r.to_html("workout_heatmap.html")
    print("Heatmap saved successfully as workout_heatmap.html!")

# --- Execution ---
dir_path = Path("./Data/raw")
heatmap_layer = gen_heatmap_layer(dir_path)
render_deck(heatmap_layer)