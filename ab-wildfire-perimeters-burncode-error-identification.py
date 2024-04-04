import geopandas as gpd
import pandas as pd

wildfire_perimeters_path = "WildfirePerimeters1931to2022.shp"
wildfire_perimeters = gpd.read_file(wildfire_perimeters_path)
wildfire_perimeters = wildfire_perimeters.to_crs(epsg=3400)
in_province_codes = ["B", "PB", "I", "B_NP", "PB_NP", "I_NP"]
out_of_province_codes = list(
    set(wildfire_perimeters["BURNCODE"].unique()) - set(in_province_codes)
)

canada_provincial_perimeter_path = "lpr_000a16a_e.shp"
canada_provincial_perimeters = gpd.read_file(canada_provincial_perimeter_path)
alberta_perimeter = canada_provincial_perimeters[
    canada_provincial_perimeters["PRNAME"] == "Alberta"
]
alberta_perimeter = alberta_perimeter.to_crs(epsg=3400)

wildfire_perimeters["burncode_within_AB"] = wildfire_perimeters["BURNCODE"].isin(
    in_province_codes
)
wildfire_perimeters["intersects_AB"] = wildfire_perimeters.intersects(
    alberta_perimeter.unary_union
)
wildfire_perimeters["within_AB"] = wildfire_perimeters.within(
    alberta_perimeter.unary_union
)
# wildfire_perimeters['outside_AB'] = ~wildfire_perimeters['within_AB'] & wildfire_perimeters['intersects_AB']
wildfire_perimeters["straddles_AB"] = (
    wildfire_perimeters["intersects_AB"] & ~wildfire_perimeters["within_AB"]
)
wildfire_perimeters["mislabeled_AB"] = (
    (wildfire_perimeters["burncode_within_AB"] & ~wildfire_perimeters["within_AB"])
    | (~wildfire_perimeters["burncode_within_AB"] & wildfire_perimeters["within_AB"])
    | wildfire_perimeters["straddles_AB"]
)
