#-----------------------------------------------------------------------
# Name:        tests_huff (huff package)
# Purpose:     Tests for Huff Model package functions
# Author:      Thomas Wieland 
#              ORCID: 0000-0001-5168-9846
#              mail: geowieland@googlemail.com              
# Version:     1.3.5
# Last update: 2025-06-03 17:24
# Copyright (c) 2025 Thomas Wieland
#-----------------------------------------------------------------------


from huff.models import create_interaction_matrix, get_isochrones, load_geodata, load_interaction_matrix, modelfit
from huff.osm import map_with_basemap
from huff.gistools import buffers, point_spatial_join


# Customer origins (statistical districts):

Haslach = load_geodata(
    "data/Haslach.shp",
    location_type="origins",
    unique_id="BEZEICHN"
    )
# Loading customer origins (shapefile)

Haslach_buf = Haslach.buffers(
    segments_distance=[500,1000,1500],
    save_output=True,
    output_filepath="Haslach_buf.shp",
    output_crs="EPSG:31467"
    )
# Buffers for customer origins

Haslach.summary()
# Summary of customer origins

Haslach.define_marketsize("pop")
# Definition of market size variable

Haslach.define_transportcosts_weighting(
    param_lambda = -2.2
    )
# Definition of transport costs weighting (lambda)

Haslach.summary()
# Summary after update


# Supply locations (supermarkets):

Haslach_supermarkets = load_geodata(
    "data/Haslach_supermarkets.shp",
    location_type="destinations",
    unique_id="LFDNR"
    )
# Loading supply locations (shapefile)

Haslach_supermarkets.summary()
# Summary of supply locations

Haslach_supermarkets.define_attraction("VKF_qm")
# Defining attraction variable

Haslach_supermarkets.define_attraction_weighting(
    param_gamma=0.9
    )
# Define attraction weighting (gamma)

Haslach_supermarkets.isochrones(
    segments_minutes=[3, 6, 9, 12, 15],
    profile = "foot-walking",
    save_output=True,
    ors_auth="5b3ce3597851110001cf62480a15aafdb5a64f4d91805929f8af6abd",
    output_filepath="Haslach_supermarkets_iso.shp",
    output_crs="EPSG:31467"
    )
# Obtaining isochrones for walking (5 and 10 minutes)
# ORS API documentation: https://openrouteservice.org/dev/#/api-docs/v2/

Haslach_supermarkets.summary()
# Summary of updated customer origins

Haslach_supermarkets_isochrones = Haslach_supermarkets.get_isochrones_gdf()
# Extracting isochrones

print(Haslach_supermarkets_isochrones)


# Using customer origins and supply locations for building interaction matrix:

haslach_interactionmatrix = create_interaction_matrix(
    Haslach,
    Haslach_supermarkets
    )
# Creating interaction matrix

interaction_matrix = haslach_interactionmatrix.transport_costs(
    ors_auth="5b3ce3597851110001cf62480a15aafdb5a64f4d91805929f8af6abd"
    #network=False
    )
# Obtaining transport costs (default: driving-car)
# ORS API documentation: https://openrouteservice.org/dev/#/api-docs/v2/

interaction_matrix.summary()
# Summary of interaction matrix

print(interaction_matrix.hansen())
# Hansen accessibility for interaction matrix

interaction_matrix = interaction_matrix.flows()
# Calculating spatial flows for interaction matrix

huff_model = interaction_matrix.marketareas()
# Calculating total market areas for interaction matrix
# Result of class HuffModel

interaction_matrix = interaction_matrix.flows()
# Calculating spatial flows

huff_model = interaction_matrix.marketareas()
# Calculating total market areas

huff_model.summary()
# Summary of Huff model

print(huff_model.get_market_areas_df())
# Showing total market areas

print(interaction_matrix.get_interaction_matrix_df())
# Showing df of interaction matrix


# Multiplicative Competitive Interaction Model:

mci_fit = huff_model.mci_fit()
# Fitting via MCI

mci_fit.summary()
# Summary of MCI model

mci_fit.marketareas()
# MCI model market simulation

mci_fit.get_market_areas_df()
# MCI model market areas


# Loading own interaction matrix:
# Data source: Wieland 2015 (https://nbn-resolving.org/urn:nbn:de:bvb:20-opus-180753)

Wieland2015_interaction_matrix = load_interaction_matrix(
    data="data/Wieland2015.xlsx",
    customer_origins_col="Quellort",
    supply_locations_col="Zielort",
    attraction_col=[
        "VF", 
        "K", 
        "K_KKr"
        ],
    transport_costs_col="Dist_Min2",
    probabilities_col="MA",
    data_type="xlsx"
    )

Wieland2015_interaction_matrix.summary()
# Summary of interaction matrix

Wieland2015_fit = Wieland2015_interaction_matrix.mci_fit(
    cols=[
        "A_j", 
        "t_ij", 
        "K", 
        "K_KKr"
        ]
    )
# Fitting MCI model with four independent variables

Wieland2015_fit.summary()
# MCI model summary

Wieland2015_fit.probabilities()

Wieland2015_fit_interactionmatrix = Wieland2015_fit.get_interaction_matrix_df()
# Export interaction matrix

Wieland2015_fit.summary()
# MCI model summary


# Buffer analysis:

Haslach_supermarkets_gdf = Haslach_supermarkets.get_geodata_gpd_original()
Haslach_buffers = Haslach_buf.get_buffers_gdf()
# Extracting points and buffer polygons

Haslach_districts_buf = point_spatial_join(
    polygon_gdf = Haslach_buffers,
    point_gdf = Haslach_supermarkets_gdf,
    polygon_ref_cols = ["BEZEICHN", "segment"],
    point_stat_col = "VKF_qm"
)
# Spatial join with buffers and points
# Statistics for supermarket selling space by buffers of statistical districts
# (How much selling space in 500, 1000, and 1500 metres?)

Haslach_districts_buf[0].to_file("Haslach_districts_buf.shp")
# Save joined points as shapefile

print(Haslach_districts_buf[1])
# Showing df with overlay statistics


# Isochrones analysis:

Haslach_districts = Haslach.get_geodata_gpd_original()

Haslach_supermarkets_iso = point_spatial_join(
    polygon_gdf = Haslach_supermarkets_isochrones,
    point_gdf = Haslach_districts,
    polygon_ref_cols = ["LFDNR", "segment"],
    point_stat_col = "pop"
)
# Spatial join with isochrones and points
# Statistics for population by isochrones of supermarkets
# (How much population in 5, 10, and 15 minutes?)

Haslach_supermarkets_iso[0].to_file("Haslach_supermarkets_iso.shp")
# Save joined points as shapefile

print(Haslach_supermarkets_iso[1])
# Showing df with overlay statistics


# Creating map:

Haslach_gdf = Haslach.get_geodata_gpd_original()
Haslach_supermarkets_gdf = Haslach_supermarkets.get_geodata_gpd_original()
Haslach_supermarkets_gdf_iso = Haslach_supermarkets.get_isochrones_gdf()
# Extracttion geopandas.GeoDataFrames

map_with_basemap(
    layers = [
        Haslach_supermarkets_gdf_iso,
        Haslach_gdf, 
        Haslach_supermarkets_gdf
        ],
    styles={
        0: {
            "color": {
                "segm_min": {
                    "3": "green", 
                    "6": "yellow", 
                    "9": "orange", 
                    "12": "red", 
                    "13": "darkred"
                    }
                },
            "alpha": 0.3
        },
        1: {
            "color": "green",
            "alpha": 1
        },
        2: {
            "color": {
                "Name": {
                    "Aldi S├╝d": "blue",
                    "Edeka": "yellow",
                    "Lidl": "red",
                    "Netto": "orange",
                    "Real": "black",
                    "Treff 3000": "fuchsia"
                    }
                },
            "alpha": 1
        }
        },
    output_filepath = "Haslach_map.png"
    )
# Map with three layers and OSM basemap