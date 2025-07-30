# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 TU Wien.
#
# Invenio-Theme-TUW is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Utilities for generating various maps from data points."""


from pathlib import Path

import folium
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

type CountryList = list[str]
type CountList = list[int]
type FoliumMapObject = folium.Map


def map_folium(countries: CountryList, counts: CountList, **kwargs) -> FoliumMapObject:
    """Generate a Folium map with countries colored based on the counts.

    :param countries: List of country names (ISO 3166-1 alpha-3 ADM0_A3s).
    :param counts: List of counts corresponding to the countries.
    :return: Folium Map object.
    """
    # Get the world map data
    world = _fetch_and_combine_map_data(countries, counts)

    # Draw the map
    fmap = folium.Map(location=[0, 0], zoom_start=2, max_zoom=6, min_zoom=1, **kwargs)
    folium.Choropleth(
        geo_data=world,
        name="choropleth",
        data=world,
        columns=["ADM0_A3", "count"],
        key_on="feature.properties.ADM0_A3",
        fill_color="YlOrRd",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="Counts per Country",
    ).add_to(fmap)
    tooltip_style = (
        "background-color: white; color: black; font-size: 12px; padding: 5px;"
    )
    folium.GeoJson(
        world,
        style_function=lambda feature: {
            "fillColor": "transparent",  # Keep existing color
            "color": "black",  # Default border color
            "weight": 1,  # Border thickness
        },
        highlight_function=lambda feature: {
            "fillColor": "yellow",  # Temporary highlight color on hover
            "color": "red",  # Border color on hover
            "weight": 3,  # Thicker border on hover
        },
        tooltip=folium.GeoJsonTooltip(
            fields=["ADM0_A3", "count"],  # Show country name + access count
            aliases=["Country:", "Access Count:"],  # Label the fields
            localize=True,
            sticky=False,  # Tooltip stays when hovering
            labels=True,
            style=tooltip_style,
        ),
    ).add_to(fmap)
    folium.LayerControl().add_to(fmap)
    return fmap


def map_geopandas(countries: CountryList, counts: CountList) -> plt.Axes:
    """Generate a GeoPandas map with countries colored based on the counts.

    :param countries: List of country names (ISO 3166-1 alpha-3 ADM0_A3s).
    :param counts: List of counts corresponding to the countries.
    :return: Matplotlib Axes object.
    """
    _, ax = plt.subplots(figsize=(15, 10))
    world = _fetch_and_combine_map_data(countries, counts)
    world.plot(
        column="count",
        cmap="YlOrRd",
        linewidth=0.8,
        edgecolor="black",
        legend=True,
        ax=ax,
        missing_kwds={"color": "lightgrey"},
        scheme="quantiles",
    )
    ax.set_title("Count of dataset accesses per country")
    ax.set_axis_off()
    return ax


def map_plotly_express(countries: CountryList, counts: CountList):
    """Generate a Plotly Express map with countries colored based on the counts.

    :param countries: List of country names (ISO 3166-1 alpha-3 ADM0_A3s).
    :param counts: List of counts corresponding to the countries.
    :return: Plotly Express figure object.
    """
    df = _fetch_and_combine_map_data(countries, counts)
    fig = px.choropleth(
        df,
        locations="ADM0_A3",
        color="count",
        hover_name="ADM0_A3",
        color_continuous_scale=px.colors.sequential.Plasma,
    )
    return fig


def map_plotly_go(countries: CountryList, counts: CountList):
    """Generate a Plotly Graph Object map with countries colored based on the counts.

    :param countries: List of country names (ISO 3166-1 alpha-3 ADM0_A3s).
    :param counts: List of counts corresponding to the countries.
    :return: Plotly Express figure object.
    """
    df = _fetch_and_combine_map_data(countries, counts)

    fig = go.Figure(
        data=go.Choropleth(
            locations=df["ADM0_A3"],
            z=df["count"],
            text=df["ADM0_A3"],
            colorscale="Blues",
            autocolorscale=False,
            reversescale=False,
            marker_line_color="darkgray",
            marker_line_width=0.5,
            colorbar_tickprefix="",
            colorbar_title="Count",
        )
    )

    fig.update_layout(
        title_text="Repositories downloaded per country",
        geo=dict(
            showframe=False,
            showcoastlines=False,
            projection_type="equirectangular",
        ),
        annotations=[
            dict(
                x=0.55,
                y=0.1,
                xref="paper",
                yref="paper",
                text="Source: RDM team - TU wien",
                showarrow=False,
            )
        ],
    )
    return fig


def _fetch_and_combine_map_data(
    countries: CountryList, counts: CountList
) -> gpd.GeoDataFrame:
    # note: we're vendoring the ZIP file to reduce attack surface
    # it has been downloaded from nasciscdn.org on 2025-06-02:
    # https://naciscdn.org/naturalearth/110m/cultural/ne_110m_admin_0_countries.zip
    path = Path(__file__).parent / "data" / "ne_110m_admin_0_countries.zip"
    world: gpd.GeoDataFrame = gpd.read_file(path.absolute())
    data = pd.DataFrame({"country": countries, "count": counts})

    # Merge the world map data with the counts
    world = world.merge(data, left_on="ADM0_A3", right_on="country", how="left")
    return world
