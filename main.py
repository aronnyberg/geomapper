"""Overlay flood risk areas with property locations, count at-risk properties, and plot results."""

import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx
import json


def load_geojson(file_path):
    """Loads a GeoJSON file into a GeoDataFrame.

    Args:
        file_path (str): Path to the GeoJSON file.

    Returns:
        gpd.GeoDataFrame: GeoDataFrame containing the loaded data.
    """
    return gpd.read_file(file_path)


def overlay_maps(flood_risk_gdf, property_gdf):
    """Identifies properties at risk of flooding.

    Args:
        flood_risk_gdf (gpd.GeoDataFrame): GeoDataFrame of flood risk areas.
        property_gdf (gpd.GeoDataFrame): GeoDataFrame of property locations.

    Returns:
        gpd.GeoDataFrame: GeoDataFrame of properties that intersect flood risk areas.
    """
    at_risk_properties = gpd.overlay(property_gdf, flood_risk_gdf, how='intersection')
    return at_risk_properties


def save_geojson(gdf, output_path):
    """Saves a GeoDataFrame to a GeoJSON file.

    Args:
        gdf (gpd.GeoDataFrame): GeoDataFrame to save.
        output_path (str): Path to save the GeoJSON file.
    """
    gdf.to_file(output_path, driver='GeoJSON')


def plot_and_save_properties(flood_risk_gdf, property_gdf, at_risk_properties, plot_title):
    """Plots properties, flood risk areas, and highlights at-risk properties.

    Args:
        flood_risk_gdf (gpd.GeoDataFrame): Flood risk areas.
        property_gdf (gpd.GeoDataFrame): All properties.
        at_risk_properties (gpd.GeoDataFrame): Properties at risk of flooding.
    """
    fig, ax = plt.subplots(figsize=(12, 10))

    # Plot layers
    flood_risk_gdf.plot(ax=ax, color='blue', alpha=0.4, edgecolor='k', label='Flood Risk Area')
    property_gdf.plot(ax=ax, color='gray', markersize=10, label='All Properties')
    at_risk_properties.plot(ax=ax, color='red', markersize=15, label='At-Risk Properties')

    # Add basemap
    ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)

    # Customize plot
    ax.set_title(plot_title)
    ax.set_axis_off()
    plt.legend()
    plt.savefig(plot_title)
    #plt.show()
    
def extract_config(file_path):
    """Extracts configuration items from a JSON config file.

    Args:
        file_path (str): Path to the JSON configuration file.

    Returns:
        list: A list of dictionaries, each representing an input configuration.
    """
    with open(file_path, 'r') as file:
        config = json.load(file)

    extracted_items = []
    
    for item in config.get('inputs', []):
        extracted_items.append({
            'risk_layer_path': item.get('risk_layer_path', ''),
            'asset_layer_path': item.get('asset_layer_path', ''),
            'command_read_out': item.get('command_read_out', ''),
            'plot_title': item.get('plot_title', '')
        })
    
    return extracted_items

def main():
    """Main function to run the flood risk analysis."""

    config_items = extract_config('config.json')

    for idx, item in enumerate(config_items):
        risk_layer_path = item['risk_layer_path']
        asset_layer_path = item['asset_layer_path']
        command_read_out = item['command_read_out']
        plot_title = item['plot_title']

    output_path = plot_title+'.json'

    # Load data
    risk_layer_gdf = load_geojson(risk_layer_path)
    asset_gdf = load_geojson(asset_layer_path)

    # Ensure data uses the same coordinate reference system (CRS)
    asset_gdf = asset_gdf.to_crs(risk_layer_gdf.crs)

    # Identify at-risk properties
    at_risk_properties = overlay_maps(risk_layer_gdf, asset_gdf)

    # Save results
    save_geojson(at_risk_properties, output_path)

    # Print count of at-risk properties
    print(command_read_out+str(len(at_risk_properties)))

    # Plot results
    plot_and_save_properties(risk_layer_gdf, asset_gdf, at_risk_properties, plot_title)


if __name__ == '__main__':
    main()
