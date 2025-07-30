import os
import sys
import random
from timeit import default_timer as timer

from aimms.project.project import Project 
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from benchmark_existing_project_with_reflection import Project

aimms_path : str = os.getenv("AIMMSPATH", os.path.join( ".", "aimms", "latest", "RelWithDebInfo", "Bin"))
print (f"aimms_path: {aimms_path}")

start = timer()
my_aimms = Project(
    aimms_path=aimms_path,
    aimms_project_path=os.path.join( os.path.dirname(__file__), "test_models", "transport_optimization_reflection", "transport_optimization.aimms"),
    exposed_identifier_set_name="AllIdentifiers",
    checked=False,
)
my_aimms.generate_stub_file(os.path.join( os.path.dirname(__file__), f"{os.path.splitext(os.path.basename(__file__))[0]}.pyi"))

stop = timer()
print(f"AimmsProject took {stop - start} seconds")

size = 1000

# Generate 10,000 random values for locations, warehouses, customers, demand, and supply
warehouses_array = [f"Warehouse{i}" for i in range(size)]
customers_array = [f"Customer{i}" for i in range(size)]
    
map(sys.intern, warehouses_array)
map(sys.intern, customers_array)

locations_array = warehouses_array + customers_array

demand_values = {f"Customer{i}": random.randint(1, 500) for i in range(size)}
supply_values = {f"Warehouse{i}": random.randint(500, 1000) for i in range(size)}

start = timer()
my_aimms.locations.assign(locations_array)
my_aimms.warehouses.assign(warehouses_array)
my_aimms.customers.assign(customers_array)
stop = timer()
print(f"set.assign took {stop - start} seconds")

my_aimms.demand.assign(demand_values)
my_aimms.supply.assign(supply_values)

# make a dictionary from tuples which is the cartesian product of customers and warehouses
# unit_transport_cost_values = {(warehouse, customer): random.randint(1, 100) for warehouse in warehouses_array for customer in customers_array}
unit_transport_cost_values = {(warehouse, customer): random.randint(1, 100)  for customer in customers_array for warehouse in warehouses_array}

print( f"len(unit_transport_cost_values): {len(unit_transport_cost_values)}")

start = timer()
my_aimms.unit_transport_cost.assign(unit_transport_cost_values)
stop = timer()
print(f"parameter.multi_assign took {stop - start} seconds")

start = timer()
my_aimms.unit_transport_cost.data()
stop = timer()
print(f"parameter.data took {stop - start} seconds")

start = timer()
my_aimms.unit_transport_cost.data()
stop = timer()
print(f"parameter.data took {stop - start} seconds")

start = timer()
my_aimms.unit_transport_cost.data()
stop = timer()
print(f"parameter.data took {stop - start} seconds")

my_aimms.MainExecution()
# print(f"transport: {my_aimms.transport.data()}")
print(f"total_transport_cost: {my_aimms.total_transport_cost.data()}")

# print the unit_transport_cost values to a csv file
# import csv
# with open('unit_transport_cost_values.csv', mode='w', newline='') as file:
#     writer = csv.writer(file)
#     writer.writerow(["origin", "destination", "cost"])
#     for (origin, destination), cost in unit_transport_cost_values.items():
#         writer.writerow([origin, destination, cost])


# my_aimms.MainExecution() # type: ignore