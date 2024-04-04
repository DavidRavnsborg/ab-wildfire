import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np

wildfire_perimeters_path = "WildfirePerimeters1931to2022.shp"
wildfire_perimeters = gpd.read_file(wildfire_perimeters_path)
wildfire_perimeters = wildfire_perimeters.to_crs(epsg=3400)
burn_codes_to_exclude = ["I", "I_NP", "I_NWT", "I_SA", "I_BC", "I_MO"]
wildfire_perimeters_filtered = wildfire_perimeters[
    ~wildfire_perimeters["BURNCODE"].isin(burn_codes_to_exclude)
]

canada_provincial_perimeter_path = "lpr_000a16a_e.shp"
canada_provincial_perimeters = gpd.read_file(canada_provincial_perimeter_path)
alberta_perimeter = canada_provincial_perimeters[
    canada_provincial_perimeters["PRNAME"] == "Alberta"
]
alberta_perimeter = alberta_perimeter.to_crs(epsg=3400)

# Define a color map for wildfire_perimeter's `BURNCODE`
color_map = {
    "B": "red",
    "PB": "orange",
    "B_NP": "darkgreen",
    "PB_NP": "green",
}

# Set all wildfire zones outside AB to gray
default_color = "gray"
for burncode in wildfire_perimeters_filtered["BURNCODE"].unique():
    if burncode not in color_map:
        color_map[burncode] = default_color
wildfire_perimeters_filtered["color"] = (
    wildfire_perimeters_filtered["BURNCODE"].map(color_map).fillna(default_color)
)

# Create decades field based on YEAR and filter out the last decade 2020-2022
wildfire_perimeters_filtered["DECADE"] = (
    np.floor(wildfire_perimeters_filtered["YEAR"] / 10) * 10
).astype(int)
wildfire_perimeters_filtered = wildfire_perimeters_filtered[
    wildfire_perimeters_filtered["DECADE"] != 2020
]
decades = wildfire_perimeters_filtered["DECADE"].unique()
decades.sort()

# Calculate the number of rows and columns for the subplots
num_decades = len(decades)
num_columns = 2
num_rows = int(np.ceil(num_decades / num_columns))

# Set up the matplotlib figure and subplots
subplot_size = (3, 12)
fig, axes = plt.subplots(
    nrows=num_rows, ncols=num_columns, figsize=subplot_size, sharex="all", sharey="all"
)

# Loop through each decade and plot the data
ax_list = axes.flatten()
for i, decade in enumerate(decades):
    ax = ax_list[i]
    ax.set_xlabel("Longitude", fontsize="small")
    ax.set_ylabel("Latitude", fontsize="small")
    ax.set_title(
        f"{decade if decade != 1930 else 1931} - {decade + 9}"
    )  # Corrected end year
    alberta_perimeter.plot(ax=ax, color="lightgrey", edgecolor="black")
    data = wildfire_perimeters_filtered[
        wildfire_perimeters_filtered["DECADE"] == decade
    ]
    if not data.empty:
        data.plot(ax=ax, color=data["color"])
# Turn off visibility instead of deleting to avoid index errors
ax_list[-1].axis("off")

legend_descriptions = {
    "B": "Burned area (AB)",
    "PB": "Partially burned area (AB)",
    "B_NP": "Burned area (AB National Park)",
    "PB_NP": "Partially burned area (AB National Park)",
}
legend_handles = [
    Line2D(
        [0],
        [0],
        marker="o",
        color="w",
        label=desc,
        markerfacecolor=color_map[code],
        markersize=10,
    )
    for code, desc in legend_descriptions.items()
]
legend_handles.append(
    Line2D(
        [0],
        [0],
        marker="o",
        color="w",
        label="Adjacent province/territory/state",
        markerfacecolor=default_color,
        markersize=10,
    )
)

# Add the shared legend at the top
fig.legend(
    handles=legend_handles,
    loc="upper center",
    ncol=3,
    title="Burn Code",
    fontsize="large",
)

fig.subplots_adjust(top=0.93)
fig.set_size_inches(subplot_size[0] * 3.6, subplot_size[1] * 3, forward=True)

plt.suptitle(
    "Alberta Wildfire Perimeters by Decade (1931 to 2019)", fontsize="x-large", y=0.96
)
plt.show()
