import os
import xarray as xr
import rioxarray as rxr
import geopandas as gpd
import pandas as pd
import xagg as xa
from tqdm import tqdm

# Define Inputs
ndvi_folder = r"D:\Users\ritvik\projects\GEOGLAM\Input\intermed\ndvi"  # Folder containing NDVI TIFF files
crop_mask_tif = r"D:\Users\ritvik\projects\GEOGLAM\Input\Global_Datasets\Masks\cropland_v9.tif"  # Crop mask file
shapefile_path = r"D:\Users\ritvik\projects\GEOGLAM\Input\Global_Datasets\Regions\Shps\Level_1.shp"  # Path to shapefile
output_nc = "ndvi_yearly.nc"  # Output NetCDF file
output_csv = "ndvi_regional_stats.csv"  # Output CSV for regional stats
year_of_interest = "2012"  # Year to filter NDVI files


# Step 1: Get NDVI files for the given year
def get_ndvi_files(folder, year):
    """
    Get all NDVI files for the specified year.
    """
    files = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith('.tif') and year in f]
    print(f"Found {len(files)} files for year {year}")
    return sorted(files)


ndvi_files = get_ndvi_files(ndvi_folder, year_of_interest)

# Step 2: Combine NDVI files into a single NetCDF
def create_nc_from_files(ndvi_files, output_nc):
    """
    Combine NDVI TIFF files into a single NetCDF file with a time dimension.
    """
    ndvi_data = []
    times = []

    for tif in tqdm(ndvi_files, desc="create nc"):
        # Open raster and parse time
        da = rxr.open_rasterio(tif, masked=True).squeeze()
        da = da.rename('ndvi')

        # Extract year and Julian day
        filename = os.path.basename(tif)
        parts = filename.split('.')
        year = int(parts[4])
        julian_day = int(parts[5])
        date = pd.to_datetime(f"{year}{julian_day:03d}", format="%Y%j")  # Convert to date

        # Append data with time
        da = da.expand_dims(time=[date])
        ndvi_data.append(da)
        times.append(date)

    # Combine all NDVI data
    ndvi_ds = xr.concat(ndvi_data, dim="time")
    ndvi_ds['time'] = pd.to_datetime(times)  # Ensure time format
    ndvi_ds.to_netcdf(output_nc)
    print(f"NDVI NetCDF saved to {output_nc}")

    return ndvi_ds


ndvi_ds = create_nc_from_files(ndvi_files, output_nc)


# Step 4: Extract regional statistics using xagg
def extract_regional_stats(masked_ndvi, weight_tif, shapefile_path, output_csv):
    """
    Extract regional statistics from NDVI data using the xagg library and a shapefile.
    """
    # Load shapefile
    regions = gpd.read_file(shapefile_path, engine="pyogrio")
    regions = regions.to_crs(masked_ndvi.rio.crs)  # Reproject to match NDVI CRS

    # Read weight_tif as a netcdf file
    weight_ds = rxr.open_rasterio(weight_tif, masked=True).squeeze()
    breakpoint()
    # with xa.set_options(silent=True):
    weightmap = xa.pixel_overlaps(masked_ndvi, regions, weights=weight_ds, impl='dot_product')

    # Flatten and save results
    aggregated = xa.aggregate(masked_ndvi, weightmap)



extract_regional_stats(ndvi_ds, crop_mask_tif, shapefile_path, output_csv)
