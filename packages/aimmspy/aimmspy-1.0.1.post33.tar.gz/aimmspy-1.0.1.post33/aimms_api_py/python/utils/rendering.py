import numpy as np
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium
import pandas as pd
from utils.geolocation import get_coordinates
import os

def load_html_style(path):
    """
    Load custom HTML styles for the Streamlit app.
    """
    # relative to the current file
    # this file path
    this_file = __file__
    this_file = os.path.abspath(this_file)
    this_dir = os.path.dirname(this_file)
    path = this_dir + "\\" + path
    
    with open(path, "r") as file:
        st.html( f"<style>{file.read()}</style>")

def render_title_and_intro():
    """
    Render the title and introduction of the Streamlit app.
    """
    st.title("🚚 Transport Optimization Model")
    st.markdown("""
        <div style="font-size: 18px; line-height: 1.6;">
            Welcome to the <b>Transport Optimization Model</b>! <br>
            This tool helps you optimize the transportation of goods between <b>warehouses</b> and <b>customers</b>. <br>
        </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """
    Render the sidebar with settings and instructions.
    """
    st.sidebar.title("⚙️ Transport Optimization Settings")

    st.sidebar.subheader("📈 Heatmap Settings")
    heatmap_colormap = st.sidebar.selectbox(
        "Colormap", 
        options=["coolwarm", "mako", "YlGnBu", "viridis", "plasma"], 
        index=0
    )
    st.sidebar.subheader("🗺️ Map Color Settings")
    map_color_theme = st.sidebar.selectbox(
        "Map Theme", 
        options=["CartoDB dark_matter", "OpenStreetMap"], 
        index=0
    )
    return heatmap_colormap, map_color_theme

def render_supply_and_demand_tabs(supply_df, demand_df):
    """
    Render the Supply & Demand tab.

    Args:
        supply_df (pd.DataFrame): DataFrame containing warehouse supply data.
        demand_df (pd.DataFrame): DataFrame containing customer demand data.
    """
    st.title("📦 Supply")
    supply_df = st.data_editor(supply_df, use_container_width=True)

    st.title("📦 Demand")
    demand_df = st.data_editor(demand_df, use_container_width=True)
    return supply_df, demand_df

def render_transport_cost_tab(cost_df):
    """
    Render the Transport Costs tab.

    Args:
        cost_df (pd.DataFrame): DataFrame containing transport cost data.
    """
    st.title("💰 Transport Costs")
    st.markdown("""
        <div style="font-size: 18px; line-height: 1.6;">
            The table below shows the <b>transport costs</b> from each <b>warehouse</b> to each <b>customer</b>. <br>
            You can edit the values to tweak the data where needed.
        </div>
    """, unsafe_allow_html=True)
    cost_df = st.data_editor(cost_df, use_container_width=True)
    return cost_df

def render_heatmap_tab(transport_df, heatmap_colormap):
    """
    Render the Heatmap tab.

    Args:
        transport_df (pd.DataFrame): DataFrame containing transport cost data.
        heatmap_colormap (str): Selected colormap for the heatmap.
    """
    
    if transport_df.empty:
        st.warning("No transport costs data available.")
        return
    # flatten the DataFrame for better display
    flat_transport_df = transport_df.pivot(index="warehouses", columns="customers", values="transport")
    
    st.title("📈 Transport Heatmap")
    fig, ax = plt.subplots(figsize=(8, 6))
    heatmap = sns.heatmap(
        flat_transport_df, 
        fmt="d", 
        cmap=heatmap_colormap, 
        ax=ax, 
        cbar_kws={'label': 'transport'},
    )
    ax.set_title("Transport Heatmap", fontsize=16, color="white")
    ax.tick_params(colors="white")
    ax.xaxis.label.set_color("white")
    ax.yaxis.label.set_color("white")
    fig.patch.set_facecolor('#2E2E2E')
    ax.set_facecolor('#2E2E2E')

    colorbar = heatmap.collections[0].colorbar
    colorbar.ax.yaxis.label.set_color("white")
    colorbar.ax.tick_params(colors="white")
    # Add custom annotations to the heatmap

    for y in range(flat_transport_df.shape[0]):
        for x in range(flat_transport_df.shape[1]):
            value = flat_transport_df.iloc[y, x]
            # Get the color of the current cell
            rgba_color = heatmap.findobj()[0].get_facecolors()[y * flat_transport_df.shape[1] + x]
            rgb_color = rgba_color[:3]  # Extract only the RGB part
            # Calculate luminance
            luminance = 0.2126 * rgb_color[0] + 0.7152 * rgb_color[1] + 0.0722 * rgb_color[2]
            # Choose text color based on luminance
            text_color = "white" if luminance < 0.5 else "black"
            ax.text(
                x + 0.5,
                y + 0.5,
                f"{value}",
                horizontalalignment='center',
                verticalalignment='center',
                color=text_color,  # Set the text color
            )
    st.pyplot(fig)

    
def render_coordinates_tab(all_locations, location_cache):
    """
    Render the Coordinates Data tab.

    Args:
        all_locations (list): List of all locations (warehouses and customers).
    """
    st.markdown("""
        <div style="font-size: 18px; line-height: 1.6;">
            The table below shows the <b>coordinates</b> for <b>warehouses</b> and <b>customers</b>. <br>
            This data is fetched using the <b>Geopy library</b> and cached for performance.
        </div>
    """, unsafe_allow_html=True)
    coordinates_data = []
    for location in all_locations:
        coordinates = get_coordinates(location, location_cache)
        if coordinates:
            coordinates_data.append({"Location": location, "Latitude": coordinates[0], "Longitude": coordinates[1]})
        else:
            coordinates_data.append({"Location": location, "Latitude": "N/A", "Longitude": "N/A"})
    
    coordinates_df = pd.DataFrame(coordinates_data)
    st.dataframe(coordinates_df, use_container_width=True)

def render_map_tab(warehouse_names, customer_names, warehouse_supply, customer_demand, map_color_theme, transport_table, location_cache):
    
    def own_curve(start, end, curve=0.3, num_points=100):
    
        mirrorstart = (-start[1], start[0])
        mirrorend = (-end[1], end[0])   
        # Control points
        control_points = np.array([
            start, 
            end,
            mirrorstart,
            mirrorend,    
        ])
            # Generate t values
        t_values = np.linspace(0, 1, num_points)
        
        curve_points = []
        for t in t_values:
            point = t * control_points[0] + (1-t) * control_points[1] + curve*t*(1-t)*(control_points[2] - control_points[3])   
            curve_points.append(tuple(point))
        
        return curve_points    
    
    """
    Render the Warehouses and Customers Map tab.

    Args:
        warehouse_names (list): List of warehouse names.
        customer_names (list): List of customer names.
        warehouse_supply (list): List of warehouse supply values.
        customer_demand (list): List of customer demand values.
        map_color_theme (str): Selected map color theme.
        transport_table (pyarrow.Table): PyArrow Table containing transport data with columns 
                                          ['warehouse', 'customer', 'quantity'].
    """

    map_object = folium.Map(
        location=(37.0902, -95.7129),  # Center of the USA
        zoom_start=4,                  # Zoom level
        control_scale=True,
        tiles=map_color_theme,
        prefer_canvas=True,
    )

    # Add warehouse markers
    for warehouse in warehouse_names:
        coordinates = get_coordinates(warehouse, location_cache)
        if coordinates:
            folium.Marker(
                location=coordinates, 
                popup=folium.Popup(f"<b>Warehouse:</b> {warehouse}", max_width=300),
                icon=folium.Icon(color="green", icon="warehouse", prefix="fa")
            ).add_to(map_object)

    # Add customer markers
    for customer in customer_names:
        coordinates = get_coordinates(customer,location_cache)
        if coordinates:
            folium.Marker(
                location=coordinates, 
                popup=folium.Popup(f"<b>Customer:</b> {customer}", max_width=300),
                icon=folium.Icon(color="orange", icon="shopping-cart", prefix="fa")
            ).add_to(map_object)

    # Add warehouse supply circles
    for i, warehouse in enumerate(warehouse_names):
        coordinates = get_coordinates(warehouse, location_cache)
        if coordinates:
            folium.Circle(
                location=coordinates,
                radius=warehouse_supply[i] * 1000,
                color='green',
                fill=True,
                fill_opacity=0.4,
                popup=folium.Popup(
                    f"<b>Warehouse:</b> {warehouse}<br><b>Supply:</b> {warehouse_supply[i]}", 
                    max_width=300
                )
            ).add_to(map_object)

    # Add customer demand circles
    for i, customer in enumerate(customer_names):
        coordinates = get_coordinates(customer, location_cache)
        if coordinates:
            folium.Circle(
                location=coordinates,
                radius=customer_demand[i] * 1000,
                color='orange',
                fill=True,
                fill_opacity=0.4,
                popup=folium.Popup(
                    f"<b>Customer:</b> {customer}<br><b>Demand:</b> {customer_demand[i]}", 
                    max_width=300
                )
            ).add_to(map_object)

    
    if not transport_table.empty:
        # Add transport lines
        for _, row in transport_table.iterrows():
            warehouse = row["warehouses"]
            customer = row["customers"]
            quantity = row["transport"]
            
            warehouse_coordinates = get_coordinates(warehouse, location_cache)
            customer_coordinates = get_coordinates(customer,location_cache   )
            
            if warehouse_coordinates and customer_coordinates:
                folium.PolyLine(
                    locations=own_curve(warehouse_coordinates, customer_coordinates),
                    color='white',
                    weight=3,
                    opacity=0.6,
                    popup=folium.Popup(f"<b>Warehouse:</b> {warehouse}<br><b>Customer:</b> {customer}<br><b>Transport Quantity:</b> {quantity}", max_width=300),
                    tooltip=f"<b>Warehouse:</b> {warehouse}<br><b>Customer:</b> {customer}<br><b>Transport Quantity:</b> {quantity}",
                ).add_to(map_object)

    st_folium(map_object, width=5000, height=800)