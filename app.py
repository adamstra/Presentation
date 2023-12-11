import streamlit as st
import geopandas as gpd
import matplotlib.pyplot as plt
import contextily as ctx
import osmnx as ox
from shapely.geometry import LineString
import plotly.express as px
from shapely.geometry import LineString
from shapely.geometry import Point


def main():
    # Chemin vers les fichiers shapefile
    chemin_shp = "/Users/AdamsTra/Desktop/HACKHATON/KEUR MASSAR/Batis.shp"

    # Lecture des fichiers shapefile
    gdf = gpd.read_file(chemin_shp)

    # Affichage des premières lignes du GeoDataFrame dans Streamlit
    st.title("Affichage des premières lignes du GeoDataFrame")
    st.write(gdf.head())
    
    # Visualisation de la carte
    st.title('Visualisation des données géospatiales')
    fig, ax = plt.subplots()
    gdf.plot(ax=ax)
    plt.title('Visualisation des données géospatiales')
    st.pyplot(fig)
    

    # Conversion du GeoDataFrame en WGS84
    gdf = gdf.to_crs('EPSG:4326')

    # Filtrage des données basé sur des conditions
    condition = (gdf['Shape_Area'] > 0)  # Vous pouvez ajuster la condition selon vos besoins spécifiques
    gdf_filtered = gdf[condition]
    
    # Ajout d'une liste déroulante pour choisir la colonne
    selected_column = st.selectbox('Choisir la colonne à afficher', ['Hauteur', 'Shape_Area', 'Shape_Leng'])

    # Visualisation de la carte filtrée
    st.title('Visualisation des données géospatiales filtrées')
    fig, ax = plt.subplots(figsize=(10, 10))
    gdf_filtered.plot(ax=ax, cmap='jet', edgecolor='black', column=selected_column, legend=True)
    ax.set_title('WGS84 (lat/lon)')
    st.pyplot(fig)
    
    # Visualisation de la carte filtrée avec basemap
    st.title('Visualisation des données géospatiales filtrées avec basemap')
    fig, ax = plt.subplots(figsize=(10, 10))
    gdf_filtered.plot(ax=ax, cmap='jet', edgecolor='black', column=selected_column, alpha=0.5, legend=True)
    ax.set_title("EPSG:4326, WGS 84")

    # Ajout de la basemap
    ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik, crs=gdf_filtered.crs.to_string())

    # Afficher la carte dans Streamlit
    st.pyplot(fig)
    
    # Nom du lieu
    place_name = "Keur Massar"

    # Récupération du réseau OSM
    graph = ox.graph_from_address(place_name, network_type='walk')

    # Affichage du graphique dans Streamlit
    st.title("Graphique du réseau OSM")
    st.write("Réseau OSM pour la zone :", place_name)

    # Affichage du graphique
    fig, ax = ox.plot_graph(graph, show=False)
    st.pyplot(fig)
    
    # Conversion du graphique en GeoDataFrames
    nodes, edges = ox.graph_to_gdfs(graph)

    # Affichage des types de routes les plus fréquents
    st.subheader("Types de routes les plus fréquents :")
    st.write(edges['highway'].value_counts())

    # Affichage des statistiques de base
    st.subheader("Statistiques de base du réseau :")
    st.write(ox.basic_stats(graph))
    
    # Ajouter un curseur pour le paramètre dist
    dist_range = st.slider('Sélectionnez la distance (en mètres)', 50, 5000, 500)
    # Récupération des empreintes des bâtiments
    buildings = ox.geometries.geometries_from_address(place_name, tags={'building': True}, dist=dist_range)
    buildings = buildings.to_crs(edges.crs)

    # Affichage des empreintes des bâtiments dans Streamlit
    st.title("Empreintes des bâtiments à proximité")
    st.write("Empreintes des bâtiments pour la zone :", place_name)

    # Affichage des empreintes des bâtiments
    fig, ax = ox.plot_footprints(buildings, show=False)
    st.pyplot(fig)
    
    # Récupération des empreintes des bâtiments
    buildings = ox.geometries.geometries_from_address(place_name, tags={'building': True}, dist=1500)
    buildings = buildings.to_crs("EPSG:4326")  # Assurez-vous que les données sont dans un système de coordonnées géographiques

    # Réinitialiser l'index pour éviter le problème MultiIndex
    buildings = buildings.reset_index(drop=True)

    # Affichage des empreintes des bâtiments dans Streamlit avec Plotly Express
    st.title("Empreintes des bâtiments à proximité")
    st.write("Empreintes des bâtiments pour la zone :", place_name)

    # Utilisation de Plotly Express pour la visualisation interactive
    fig = px.choropleth_mapbox(buildings, 
                            geojson=buildings.geometry, 
                            locations=buildings.index, 
                            color='building',  # Vous pouvez remplacer 'building' par une autre colonne pour la couleur
                            opacity=0.5,
                            mapbox_style="open-street-map",
                            center={"lat": buildings.geometry.centroid.y.mean(), "lon": buildings.geometry.centroid.x.mean()},
                            zoom=15,
                            )
    # Mettre à jour la disposition du graphique
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    # Afficher le graphique interactif dans Streamlit
    st.plotly_chart(fig)

# Lancez l'application
if __name__ == "__main__":
    main()
