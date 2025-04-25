# Background worker to refresh all regions
from fetch_ram_data import fetch_ram_data

for region in ["us", "uk", "de"]:
    print(f"Refreshing: {region}")
    fetch_ram_data(region)
