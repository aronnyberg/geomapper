# Flood Risk Analysis Script
# This script overlays two GeoJSON files to identify properties at risk of flooding.

# Load necessary libraries
library(sf)
library(dplyr)

#' Load GeoJSON File
#'
#' @param filepath Path to the GeoJSON file
#' @return An sf object representing the spatial data
load_geojson <- function(filepath) {
  read_sf(filepath)
}

#' Overlay Flood Risk and Properties
#'
#' @param flood_geojson sf object representing flood zones
#' @param property_geojson sf object representing property locations
#' @return A data frame of properties within flood zones
identify_flood_risk <- function(flood_geojson, property_geojson) {
  st_intersection(property_geojson, flood_geojson) %>%
    st_drop_geometry() %>%
    mutate(at_risk = TRUE)
}

#' Save Results to GeoJSON
#'
#' @param at_risk_properties Data frame of at-risk properties
#' @param output_path Path to save the resulting GeoJSON
save_results <- function(at_risk_properties, output_path) {
  st_as_sf(at_risk_properties, coords = c("longitude", "latitude"), crs = 4326) %>%
    st_write(output_path, delete_dsn = TRUE)
}

# Main Execution
main <- function() {
  # File paths
  flood_path <- "data/flood_zones.geojson"
  property_path <- "data/properties.geojson"
  output_path <- "output/at_risk_properties.geojson"
  
  # Load data
  flood_zones <- load_geojson(flood_path)
  properties <- load_geojson(property_path)
  
  # Ensure the CRS (Coordinate Reference System) matches
  properties <- st_transform(properties, st_crs(flood_zones))
  
  # Identify properties at risk
  at_risk_properties <- identify_flood_risk(flood_zones, properties)
  
  # Save output
  save_results(at_risk_properties, output_path)
  
  # Print summary
  print(glue::glue("Total properties at risk: {nrow(at_risk_properties)}"))
}

# Run the script
main()
