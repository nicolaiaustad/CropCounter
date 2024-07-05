import geopandas as gpd
from shapely.geometry import Point
import matplotlib.pyplot as plt
import fiona
import matplotlib
import numpy as np
from pyproj import CRS, Transformer
import pandas as pd
import pyproj
import seaborn as sns
import matplotlib.ticker as ticker
from shapely.geometry import Point
import os

# # Create CRS objects
proj_wgs84 = pyproj.CRS('EPSG:4326')  # WGS84

# Function to get UTM zone dynamically
def get_utm_zone(longitude, latitude):
    zone_number = int((longitude + 180) // 6) + 1
    hemisphere = 'north' if latitude >= 0 else 'south'
    return zone_number, hemisphere

# # Function to create UTM projection based on latitude and longitude
# def create_utm_proj(zone_number, hemisphere):
#     #hemisphere, zone_number = get_utm_zone(longitude, latitude)
#     # utm_crs = pyproj.CRS(proj='utm', zone=zone_number, hemisphere=hemisphere)
#     # return utm_crs

#     proj_string = f"+proj=utm +zone={zone_number} +{hemisphere} +datum=WGS84 +units=m +no_defs"
#     return pyproj.CRS(proj_string)

def create_utm_proj(zone_number, hemisphere):
    proj_string = f"+proj=utm +zone={zone_number} +{'north' if hemisphere == 'north' else 'south'} +datum=WGS84 +units=m +no_defs"
    return pyproj.CRS(proj_string)

# Function to transform UTM to WGS84
def transform_to_wgs84(utm_x, utm_y, utm_crs):
    #utm_crs = create_utm_proj(latitude, longitude)
    transformer = pyproj.Transformer.from_crs(utm_crs, proj_wgs84, always_xy=True)
    longitude, latitude = transformer.transform(utm_x, utm_y)
    return longitude, latitude

# Function to transform WGS84 to UTM
def transform_to_utm(longitude, latitude, utm_crs):
    #utm_crs = create_utm_proj(lon, lat)
    transformer = pyproj.Transformer.from_crs(proj_wgs84, utm_crs, always_xy=True)
    utm_x, utm_y = transformer.transform(longitude, latitude)
    return utm_x, utm_y


BASE_DIR = '/home/nicolaiaustad/Desktop/CropCounter'
shapefile_path = os.path.join(BASE_DIR, "trygve","trygve.shp")


def shp_to_grid(filename, gridsize):
    
    
    # Set SHAPE_RESTORE_SHX config option to YES
    fiona.drvsupport.supported_drivers['ESRI Shapefile'] = 'raw'
    with fiona.Env(SHAPE_RESTORE_SHX='YES'):
        gdf = gpd.read_file(filename)

    # Set the CRS to WGS84 if not already set
    if gdf.crs is None:
        gdf.set_crs(epsg=4326, inplace=True)  # WGS84

    # Convert to a suitable projected CRS for accurate centroid calculation
    projected_gdf = gdf.to_crs(epsg=32633)  # Using UTM zone 33N (example)

    # Calculate the centroid in the projected CRS
    centroid_projected = projected_gdf.geometry.centroid.iloc[0]

    # Convert the centroid back to geographic CRS (WGS84) if needed
    centroid = gpd.GeoSeries([centroid_projected], crs=projected_gdf.crs).to_crs(epsg=4326).iloc[0]

    # Determine the UTM zone based on the centroid
    utm_zone, hemisphere = get_utm_zone(centroid.x, centroid.y)

    # Create UTM CRS
    utm_crs = create_utm_proj(utm_zone, hemisphere)
    gdf_utm = gdf.to_crs(utm_crs)

    # Get the boundary in UTM
    boundary_utm = gdf_utm.geometry.unary_union

    # Get boundary coordinates in UTM
    boundary_coords_utm = np.array(boundary_utm.exterior.coords)





    # Get the bounding box of the polygon in UTM
    minx, miny, maxx, maxy = boundary_utm.bounds

    # Define grid resolution in meters
    grid_size = gridsize  # Adjust as needed for desired grid size

    # Generate grid points in UTM
    x = np.arange(minx, maxx, grid_size)
    y = np.arange(miny, maxy, grid_size)
    xx, yy = np.meshgrid(x, y)
    grid_points = np.c_[xx.ravel(), yy.ravel()]

    # Filter points inside the polygon
    inside_points = [Point(p).within(boundary_utm) for p in grid_points]
    grid_points = grid_points[inside_points]

    # Optionally, convert grid points back to WGS84
    transformer = Transformer.from_crs(utm_crs, CRS.from_epsg(4326), always_xy=True)
    grid_points_wgs84 = np.array([transformer.transform(p[0], p[1]) for p in grid_points])
    
    
    # Plotting the grid and polygon
    plt.figure(figsize=(10, 10))
    plt.plot(boundary_coords_utm[:, 0], boundary_coords_utm[:, 1], 'r-', linewidth=2, label='Boundary')
    plt.scatter(grid_points[:, 0], grid_points[:, 1], s=1, c='blue', label='Grid Points')
    plt.xlabel('Easting (m)')
    plt.ylabel('Northing (m)')
    plt.title('Grid within Boundary (UTM)')
    plt.legend()
    plt.grid(True)
    plt.savefig('grid_plot_utm.png')
    plt.show()


    

    # Print the first few grid points in WGS84
    #print(grid_points_wgs84[:1])
    values = np.zeros(len(grid_points_wgs84))
    # print(values)
    df_gps = pd.DataFrame(grid_points_wgs84, columns=['x', 'y'])
    df_gps['values'] = values
    df_gps["measured"] = np.zeros(len(grid_points_wgs84), dtype=bool)
    #print(df_gps)
    
    values1 = np.zeros(len(grid_points))
    #print(values)
    df_utm = pd.DataFrame(grid_points, columns=['x', 'y'])
    df_utm['values'] = values1
    df_utm["measured"] = np.zeros(len(grid_points), dtype=bool)
    #print(df_utm)
    return grid_points, grid_points_wgs84, df_utm, df_gps

# grid_utm, grid_gps, df_utm, df_gps =shp_to_grid(shapefile_path, 5)
# print(df_gps)
# print(df_utm)
# import pyproj


# # Example usage
# longitude = 58.5
# latitude = 12.5

# zone_number, hemisphere = get_utm_zone(longitude, latitude)

# # WGS84 to UTM
# utm_x, utm_y = transform_to_utm(longitude, latitude, create_utm_proj(zone_number, hemisphere) )
# print(f"UTM Coordinates: Easting: {utm_x}, Northing: {utm_y}")

# # UTM to WGS84
# lon, lat = transform_to_wgs84(utm_x, utm_y, create_utm_proj(zone_number, hemisphere))
# print(f"WGS84 Coordinates: Longitude: {lon}, Latitude: {lat}")



def find_grid_cell(longitude, latitude, grid_size, df):                  
    # Get the minimum values of x and y from the DataFrame
    min_x = df['x'].min()
    min_y = df['y'].min()
    
    # Adjust the coordinates based on the grid starting point
    adjusted_longitude = longitude - min_x
    adjusted_latitude = latitude - min_y
    
    # Round to the nearest grid point
    cell_x = np.floor(adjusted_longitude / grid_size) * grid_size + min_x
    cell_y = np.floor(adjusted_latitude / grid_size) * grid_size + min_y

    # Return the corresponding row in the DataFrame
    row = df[(df['x'] == cell_x) & (df['y'] == cell_y)]
    if not row.empty:
        return row.index[0]
    return None



# data = {
#     'x': [0, 10, 20, 30, 40],
#     'y': [0, 10, 20, 30, 40],
#     'values': [0, 0, 0, 0, 0],
#     'measured': [False, False, False, False, False]
# }
# df = pd.DataFrame(data)
# test_utm_x = 25
# test_utm_y = 21
# grid_size = 10

# # Find the corresponding row
# df_row = find_grid_cell(test_utm_x, test_utm_y, grid_size, df)
# print(f"Identified DataFrame Row: {df_row}")




### Now must make color map
# Format axis numbers
    
def round(n, k):
    # function to round number 'n' up/down to nearest 'k'
    # use positive k to round up
    # use negative k to round down

    return n - n % k



    
# def make_heatmap_and_save(df_data, grid_size):
#     # Pivot the DataFrame to create a grid
#     pivot_table = df_data.pivot(index='y', columns='x', values='values')

#     # Create the heatmap
#     plt.figure(figsize=(10, 8))
#     sns.heatmap(pivot_table, cmap='YlOrRd', annot=False, fmt="f", cbar=True)
    
     
#     xticks = np.arange(df_data['x'].min(), df_data['x'].max() + grid_size, grid_size)
#     yticks = np.arange(df_data['y'].min(), df_data['y'].max() + grid_size, grid_size)

#     plt.gca().set_xticks(np.arange(len(xticks)))
#     plt.gca().set_yticks(np.arange(len(yticks)))

#     # Set the tick labels directly from the tick values
#     plt.gca().set_xticklabels([f'{int(x)}' for x in xticks], rotation=45, ha='right')
#     plt.gca().set_yticklabels([f'{int(y)}' for y in yticks])
    
#     # Format axis numbers
#     plt.xticks(rotation=45, ha='right')
#     #plt.yticks(yticks)
#     plt.yticks(rotation=0)
#     # Invert y-axis
#     plt.gca().invert_yaxis()
#     #ax1.set_yticks(yticks)
#     plt.title('Heatmap of Values')
#     plt.xlabel('UTM X Coordinate')
#     plt.ylabel('UTM Y Coordinate')
#     plt.savefig('/home/nicolaiaustad/Desktop/heatmap.png')
#     plt.close()  # Close the figure after saving

def save_heatmap_to_shapefile(df_data, grid_size, output_path, crs):
    # Convert the DataFrame to a GeoDataFrame
    geometry = [Point(xy) for xy in zip(df_data['x'], df_data['y'])]
    gdf = gpd.GeoDataFrame(df_data, crs=crs, geometry=geometry)

    # Transform the GeoDataFrame to geographic CRS (WGS84)
    gdf_wgs84 = gdf.to_crs(epsg=4326)

    # Save the GeoDataFrame as a shapefile
    gdf_wgs84.to_file(output_path, driver='ESRI Shapefile')
    print(f"Shapefile saved to {output_path}")


def make_heatmap_and_save(df_data, grid_size, heatmap_output_path, shapefile_output_path, crs):
    # Pivot the DataFrame to create a grid
    pivot_table = df_data.pivot(index='y', columns='x', values='values')
    
    # Create the heatmap
    plt.figure(figsize=(12, 10))
    sns.heatmap(pivot_table, cmap='YlOrRd', annot=False, fmt="f", cbar=True)
    
    # Set tick labels directly from the tick values
    xticks = np.arange(df_data['x'].min(), df_data['x'].max() + grid_size, grid_size)
    yticks = np.arange(df_data['y'].min(), df_data['y'].max() + grid_size, grid_size)

    plt.gca().set_xticks(np.arange(len(xticks)))
    plt.gca().set_yticks(np.arange(len(yticks)))

    plt.gca().set_xticklabels([f'{int(x)}' for x in xticks], rotation=45, ha='right')
    plt.gca().set_yticklabels([f'{int(y)}' for y in yticks])

    # Invert y-axis
    plt.gca().invert_yaxis()

    plt.title('Heatmap of Values')
    plt.xlabel('UTM X Coordinate')
    plt.ylabel('UTM Y Coordinate')
    plt.savefig(heatmap_output_path)
    plt.close()  # Close the figure after saving
    print(f"Heatmap saved to {heatmap_output_path}")

    # Save the heatmap values as a shapefile
    save_heatmap_to_shapefile(df_data, grid_size, shapefile_output_path, crs)