import os
import polars as pl
pl.Config.set_tbl_hide_dataframe_shape(True)
pl.Config.set_tbl_formatting('NOTHING')
pl.Config.set_tbl_hide_column_data_types(True)

from aimms.project.project import DataReturnTypes, Project 

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from dataframe_test_polars import Project

my_aimms = Project(
    aimms_path=os.path.join( ".", "aimms", "latest", "RelWithDebInfo", "Bin"),
    aimms_project_path=os.path.join( os.path.dirname(__file__), "test_models", "transport_optimization_reflection", "transport_optimization.aimms"),
    exposed_identifier_set_name="AllIdentifiers",
    checked=False,
    data_type_preference= DataReturnTypes.POLARS,
)
my_aimms.generate_stub_file(os.path.join( os.path.dirname(__file__), f"{os.path.splitext(os.path.basename(__file__))[0]}.pyi"))

warehouses_set =  ["NewYork", "LosAngeles", "Chicago"]
customers_set = ["Houston", "Phoenix", "Philadelphia"]
locations_set = warehouses_set + customers_set

demand_df = pl.DataFrame({
    "c": customers_set,
    "demand": [50.0, 60.0, 40.0]
})

supply_df = pl.DataFrame(data={
    "w": warehouses_set,
    "supply": [70.0, 80.0, 60.0]
})

unit_transport_cost_df = pl.DataFrame({
    "w": ["NewYork", "NewYork", "NewYork", "LosAngeles", "LosAngeles", "LosAngeles", "Chicago", "Chicago", "Chicago"],
    "c": ["Houston", "Phoenix", "Philadelphia", "Houston", "Phoenix", "Philadelphia", "Houston", "Phoenix", "Philadelphia"],
    "unit_transport_cost": [5.0, 6.0, 4.0, 3.0, 2.0, 7.0, 4.0, 5.0, 3.0]
})

my_aimms.demand.assign( demand_df)
my_aimms.supply.assign( supply_df)
my_aimms.unit_transport_cost.assign( unit_transport_cost_df)
my_aimms.MainExecution()

from utils.testing import check_dataframe_equality, check_set_equality
check_set_equality(my_aimms.locations.data(), locations_set)
check_set_equality(my_aimms.customers.data(), customers_set)
check_set_equality(my_aimms.warehouses.data(), warehouses_set)

check_dataframe_equality(my_aimms.demand.data(), demand_df)
check_dataframe_equality(my_aimms.supply.data(), supply_df)
check_dataframe_equality(my_aimms.unit_transport_cost.data(), unit_transport_cost_df)

if not my_aimms.transport.data().equals(pl.DataFrame({
    "w": ["NewYork", "LosAngeles", "LosAngeles", "Chicago", "Chicago"],
    "c": ["Houston", "Houston", "Phoenix", "Houston", "Philadelphia"],
    "transport": [10.0, 20.0, 60.0, 20.0, 40.0]
})):
    print( "transport data is not correct")
    exit(1)

if my_aimms.total_transport_cost.data() != 430.0:
    print( "total_transport_cost data is not correct")
    exit(1)