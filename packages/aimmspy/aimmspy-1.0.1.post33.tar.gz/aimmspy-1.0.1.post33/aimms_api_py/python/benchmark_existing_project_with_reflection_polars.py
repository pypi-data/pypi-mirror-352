import os
import sys
import random
import polars as pl  # Changed from pandas to polars
from timeit import default_timer as timer
from natsort import natsorted
from aimms.project.project import DataReturnTypes, Project 
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from benchmark_existing_project_with_reflection_pandas import Project

aimms_path : str = os.getenv("AIMMSPATH", os.path.join( ".", "aimms", "latest", "RelWithDebInfo", "Bin"))
print (f"aimms_path: {aimms_path}")

start = timer()
my_aimms = Project(
    aimms_path=aimms_path,
    aimms_project_path=os.path.join( os.path.dirname(__file__), "test_models", "transport_optimization_reflection", "transport_optimization.aimms"),
    exposed_identifier_set_name="AllIdentifiers",
    checked=False,
    data_type_preference= DataReturnTypes.ARROW,
)
my_aimms.generate_stub_file(os.path.join( os.path.dirname(__file__), f"{os.path.splitext(os.path.basename(__file__))[0]}.pyi"))

stop = timer()
print(f"AimmsProject took {stop - start} seconds")

size = 1000

warehouses_array = [f"Warehouse{i}" for i in range(size)]
customers_array = [f"Customer{i}" for i in range(size)]

map(sys.intern, warehouses_array)
map(sys.intern, customers_array)

locations_array = warehouses_array + customers_array

start = timer()
my_aimms.locations.assign( locations_array)
my_aimms.warehouses.assign(warehouses_array)
my_aimms.customers.assign(customers_array)
stop = timer()
print(f"set.assign took {stop - start} seconds")

nat_sorted_customers = natsorted(seq=customers_array)
nat_sorted_warehouses = natsorted(seq=warehouses_array)

demand_df = pl.DataFrame({
    "c": nat_sorted_customers,
    "demand": [random.uniform(1, 500) for _ in customers_array]
})

supply_df = pl.DataFrame({
    "w": nat_sorted_warehouses,
    "supply": [random.uniform(500, 1000) for _ in warehouses_array]
})

# cartesian product of customers and warehouses with random values
unit_transport_cost_df = pl.DataFrame({
    "w": [warehouse for warehouse in nat_sorted_warehouses for _ in nat_sorted_customers],
    "c": [customer for _ in nat_sorted_warehouses for customer in nat_sorted_customers],
    "unit_transport_cost": [random.uniform(1, 100) for _ in range(len(warehouses_array) * len(customers_array))]
})

# print(f"locations: {my_aimms.locations.data()}")
# print(f"customers: {my_aimms.customers.data()}")
# print(f"warehouses: {my_aimms.warehouses.data()}")

my_aimms.demand.assign(demand_df)
print(my_aimms.demand.data())

my_aimms.supply.assign(supply_df)

# print(f"demand: {my_aimms.demand.data()}")
# print(f"supply: {my_aimms.supply.data()}")

print(f"len(unit_transport_cost_values): {len(unit_transport_cost_df)}")

start = timer()
# unit transport cost without the index column
my_aimms.unit_transport_cost.assign( unit_transport_cost_df)
stop = timer()
print(f"parameter.multi_assign took {stop - start} seconds")
# print (f"unit_transport_cost_df: {unit_transport_cost_df}")
# print (f"unit_transport_cost_df: {unit_transport_cost_df.to_arrow()}")
# print (f"unit_transport_cost_df: {unit_transport_cost_df.to_pandas()}")
# print (f"unit_transport_cost_df: {unit_transport_cost_df.to_numpy()}")
# print (f"unit_transport_cost_df: {unit_transport_cost_df.to_dict()}")

# output the unit_transport_cost_df to a CSV file
unit_transport_cost_df.write_csv('unit_transport_cost_values.csv')

start = timer()
unit_transport_cost_data = my_aimms.unit_transport_cost.data()
stop = timer()
print(f"parameter.data took {stop - start} seconds")
# print(f"unit_transport_cost: {unit_transport_cost_data}")

start = timer()
unit_transport_cost_data = my_aimms.unit_transport_cost.data()
stop = timer()
print(f"parameter.data took {stop - start} seconds")

start = timer()
unit_transport_cost_data = my_aimms.unit_transport_cost.data()
stop = timer()
print(f"parameter.data took {stop - start} seconds")

# print (f"supply: {my_aimms.supply.data()}")
# print( f"demand: {my_aimms.demand.data()}")
# print (f"unit_transport_cost_data: {unit_transport_cost_data}")

my_aimms.MainExecution()
print(f"transport: {my_aimms.transport.data()}")
print(f"total_transport_cost: {my_aimms.total_transport_cost.data()}")

# Optionally, save the unit_transport_cost values to a CSV file
# unit_transport_cost_df.to_csv('unit_transport_cost_values.csv', index=False)
