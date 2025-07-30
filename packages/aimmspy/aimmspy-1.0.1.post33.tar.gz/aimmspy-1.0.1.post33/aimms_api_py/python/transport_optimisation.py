import streamlit as st
import pandas as pd
import numpy as np
from utils.rendering import (
    load_html_style,
    render_title_and_intro,
    render_sidebar,
    render_supply_and_demand_tabs,
    render_transport_cost_tab,
    render_heatmap_tab,
    render_coordinates_tab,
    render_map_tab
)

from aimms.project.project import DataReturnTypes, Project 

import pandas as pd

from typing import TYPE_CHECKING

import os
import geopy.distance

if TYPE_CHECKING:
    from benchmark_existing_project_with_reflection_pandas import Project

@st.cache_resource
def get_aimms_project():
    aimms_path : str = os.getenv("AIMMSPATH", os.path.join( ".", "aimms", "latest", "RelWithDebInfo", "Bin"))
    print (f"aimms_path: {aimms_path}")

    my_aimms = Project(
        aimms_path=aimms_path,
        aimms_project_path=os.path.abspath(os.path.join( os.path.dirname(__file__), "test_models", "transport_optimization_reflection", "transport_optimization.aimms")),
        exposed_identifier_set_name="AllIdentifiers",
        checked=False,
        data_type_preference= DataReturnTypes.PANDAS
    )
    my_aimms.generate_stub_file(os.path.join( os.path.dirname(__file__), f"{os.path.splitext(os.path.basename(__file__))[0]}.pyi"))
    return my_aimms

@st.cache_resource
def initialize_data():
    warehouse_names = ["Dallas", "Atlanta", "New York"]
    customer_names = ["San Francisco", "Seattle", "Miami"]
    all_locations = warehouse_names + customer_names

    warehouse_supply = [100.0, 150.0, 50.0]
    customer_demand = [50.0, 70.0, 80.0]

    # Cache for coordinates
    location_cache = {
        "Dallas": (32.7767, -96.7970),
        "Atlanta": (33.7490, -84.3880),
        "San Francisco": (37.7749, -122.4194),
        "Seattle": (47.6062, -122.3321),
        "Miami": (25.7617, -80.1918),
        "New York": (40.7128, -74.0060),
    }

    # Calculate transport costs based on haversine distance
    transport_costs = np.zeros((len(warehouse_names), len(customer_names)))
    for i, warehouse in enumerate(warehouse_names):
        for j, customer in enumerate(customer_names):
            lat1, lon1 = location_cache[warehouse]
            lat2, lon2 = location_cache[customer]
            transport_costs[i, j] = geopy.distance.distance((lat1, lon1), (lat2, lon2)).km * 0.5  # Example cost per km

    supply_df = pd.DataFrame({"warehouses": warehouse_names, "supply": warehouse_supply})
    demand_df = pd.DataFrame({"customers": customer_names, "demand": customer_demand})
    cost_df = pd.DataFrame({
        "warehouses": np.repeat(warehouse_names, len(customer_names)),
        "customers": customer_names * len(warehouse_names),
        "unit_transport_cost": transport_costs.flatten()
    })
    
    total_transport_cost = 0.0

    return warehouse_names, customer_names, all_locations, supply_df, demand_df, cost_df, location_cache, total_transport_cost

def main_page():
    # Fetch initial data
    warehouse_names, customer_names, all_locations, supply_df, demand_df, cost_df, location_cache, total_transport_cost = initialize_data()

    # Allow modifications to the data
    supply_df = st.session_state.get("supply_df", supply_df)
    demand_df = st.session_state.get("demand_df", demand_df)
    cost_df = st.session_state.get("cost_df", cost_df)
    transport_df = st.session_state.get("transport_df", pd.DataFrame())
    total_transport_cost = st.session_state.get("total_transport_cost", 0)

    load_html_style("custom.css")

    my_aimms: Project = get_aimms_project()

    render_title_and_intro()
    heatmap_colormap, map_color_theme = render_sidebar()
    
    if st.sidebar.button("Solve", key="solve-button", type="tertiary", use_container_width=True):
        my_aimms.locations.assign(all_locations)
        my_aimms.warehouses.assign(warehouse_names)
        my_aimms.customers.assign(customer_names)
        my_aimms.demand.assign(demand_df)
        my_aimms.supply.assign(supply_df)
        my_aimms.unit_transport_cost.assign(cost_df)
        
        my_aimms.MainExecution()
        
        transport_df = my_aimms.transport.data()
        total_transport_cost = my_aimms.total_transport_cost.data()
        
        st.session_state["transport_df"] = transport_df
        st.session_state["total_transport_cost"] = my_aimms.total_transport_cost.data()
        
    st.markdown(
        f"""
        <div style="
            padding: 20px; 
            border-radius: 10px; 
            text-align: center; 
            border: 1px solid var(--primary-color); 
            background-color: var(--background-secondary-color); 
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);">
            <h2 style="color: var(--text-color); margin-bottom: 10px;">💰 Total Transport Cost</h2>
            <p style="font-size: 24px; font-weight: bold; color: var(--text-color);">${total_transport_cost:,.2f}</p>
            <p style="font-size: 14px; color: var(--text-secondary-color);">This is the total cost calculated by the transport optimization model.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Create two columns for layout
    col1, col2 = st.columns([2, 1], gap="large")

    with col1:
        # Render tables
        supply_df, demand_df = render_supply_and_demand_tabs(supply_df, demand_df)
        st.session_state["supply_df"] = supply_df
        st.session_state["demand_df"] = demand_df

        cost_df = render_transport_cost_tab(cost_df)
        st.session_state["cost_df"] = cost_df
        
    with col2:        
        render_heatmap_tab(transport_df, heatmap_colormap)
        
            
    render_map_tab(
        warehouse_names, customer_names, 
        supply_df["supply"].tolist(), demand_df["demand"].tolist(), 
        map_color_theme, transport_df, location_cache
    )

def data_page():
    st.title("📊 AIMMS Data Overview")
    st.write("Explore the data used in the transport optimization model. Below, you can view the results, assigned data, and other key metrics.")

    # Fetch the AIMMS project
    my_aimms: Project = get_aimms_project()
    warehouse_names, customer_names, all_locations, supply_df, demand_df, cost_df, location_cache, total_transport_cost = initialize_data()

    # Solve Data Overview Section
    st.subheader("🚚 Solve Data Overview")

    # Use expandable sections for better organization
    with st.expander("📍 Locations"):
        st.dataframe(my_aimms.locations.data(), use_container_width=True)

    with st.expander("🏢 Warehouses"):
        st.dataframe(my_aimms.warehouses.data(), use_container_width=True)

    with st.expander("👥 Customers"):
        st.dataframe(my_aimms.customers.data(), use_container_width=True)

    with st.expander("📦 Demand"):
        st.dataframe(my_aimms.demand.data(), use_container_width=True)

    with st.expander("🏭 Supply"):
        st.dataframe(my_aimms.supply.data(), use_container_width=True)

    with st.expander("💲 Unit Transport Costs"):
        st.dataframe(my_aimms.unit_transport_cost.data(), use_container_width=True)

    with st.expander("🗺️ Coordinates"):
        render_coordinates_tab(all_locations, location_cache)

def main():

    st.set_page_config(layout="wide")

    pg = st.navigation([
        st.Page(main_page, title="Main Page", icon="🏠"),
        st.Page(data_page, title="Data Page", icon="📊"),
    ])
    pg.run()

if __name__ == "__main__":
    main()