import os
import sys
import random
from timeit import default_timer as timer
from natsort import natsorted
from aimms.project.project import DataReturnTypes, Project 

import pandas as pd

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from benchmark_existing_project_with_reflection_pandas import Project

aimms_path : str = os.getenv("AIMMSPATH", os.path.join( ".", "aimms", "latest", "RelWithDebInfo", "Bin"))
print (f"aimms_path: {aimms_path}")

start = timer()
my_aimms = Project(
    aimms_path=aimms_path,
    aimms_project_path=os.path.join( os.path.dirname(__file__), "test_models", "transport_optimization_reflection","transport_optimization.aimms"),
    exposed_identifier_set_name="AllIdentifiers",
    checked=False,
    data_type_preference=DataReturnTypes.PANDAS,
)
my_aimms.generate_stub_file(os.path.join( os.path.dirname(__file__), f"{os.path.splitext(os.path.basename(__file__))[0]}.pyi"))

stop = timer()
print(f"AimmsProject took {stop - start} seconds")

size = 1000

warehouses_array =[f"Warehouse{i}" for i in range(size)]
customers_array = [f"Customer{i}" for i in range(size)]

map(sys.intern, warehouses_array)
map(sys.intern, customers_array)

locations_array = warehouses_array + customers_array

start = timer()
my_aimms.locations.assign(locations_array)
my_aimms.warehouses.assign(warehouses_array)
my_aimms.customers.assign(customers_array)
stop = timer()
print(f"set.assign took {stop - start} seconds")


nat_sorted_customers = natsorted(list(customers_array))
nat_sorted_warehouses = natsorted(list(warehouses_array))

demand_df = pd.DataFrame({
    "c": nat_sorted_customers,
    "demand": [random.uniform(1, 500) for _ in customers_array]
})

supply_df = pd.DataFrame({
    "w": nat_sorted_warehouses,
    "supply": [random.uniform(500, 1000) for _ in warehouses_array]
})

# cartesian product of customers and warehouses with random values
unit_transport_cost_df = pd.DataFrame({
    "w": [warehouse for warehouse in nat_sorted_warehouses for _ in nat_sorted_customers],
    "c": [customer for _ in nat_sorted_warehouses for customer in nat_sorted_customers],
    "unit_transport_cost": [random.uniform(1, 100) for _ in range(len(warehouses_array) * len(customers_array))]
})

my_aimms.demand.assign( demand_df)
my_aimms.supply.assign( supply_df)

start = timer()
my_aimms.unit_transport_cost.assign( unit_transport_cost_df)
stop = timer()
print(f"parameter.multi_assign took {stop - start} seconds")

start = timer()
unit_transport_cost_data = my_aimms.unit_transport_cost.data()
stop = timer()
print(f"parameter.data took {stop - start} seconds")

start = timer()
unit_transport_cost_data = my_aimms.unit_transport_cost.data()
stop = timer()
print(f"parameter.data took {stop - start} seconds")

start = timer()
unit_transport_cost_data = my_aimms.unit_transport_cost.data()
stop = timer()
print(f"parameter.data took {stop - start} seconds")

my_aimms.MainExecution()
print(f"transport: {my_aimms.transport.data()}")
print(f"total_transport_cost: {my_aimms.total_transport_cost.data()}")

print(my_aimms.transport.data())
