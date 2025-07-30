import os

from aimms.project.project import Project
from utils.testing import assertEqual
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from test_existing_project_with_reflection_parameter_domain_restriction_indexed import Project

aimms_path : str = os.getenv("AIMMSPATH", os.path.join( ".", "aimms", "latest", "Debug", "Bin"))
print (f"aimms_path: {aimms_path}")

my_aimms = Project(
    aimms_path=aimms_path,
    aimms_project_path=os.path.join( os.path.dirname(__file__), "test_models", "transport_optimization_reflection_parameter_domain_restriction_indexed", "transport_optimization.aimms"),
    exposed_identifier_set_name="AllIdentifiers",
    checked=True,
)
my_aimms.generate_stub_file(os.path.join( os.path.dirname(__file__), f"{os.path.splitext(os.path.basename(__file__))[0]}.pyi"))

# print( f"checking test identifier: {test.name}")
print( f"all identifiers: {my_aimms.exposed_identifier_set}")

expected_warehouses_set =  ["NewYork", "LosAngeles", "Chicago"]
expected_customers_set = ["Houston", "Phoenix", "Philadelphia"]
expected_locations_set = expected_warehouses_set + expected_customers_set

my_aimms.locations.assign( expected_locations_set )
my_aimms.warehouses.assign( expected_warehouses_set )
my_aimms.customers.assign( expected_customers_set )

my_aimms.demand_condition.assign({
    ("Houston"):1,
})

expected_demand_values = {
    ("Houston"): 20,
    ("Phoenix"): 60,
    ("Philadelphia"): 40,
}
my_aimms.demand.assign(expected_demand_values)

expected_supply_values = {
    ("NewYork"): 70,
    ("LosAngeles"): 80,
    ("Chicago"): 60
}
my_aimms.supply.assign(expected_supply_values)

expected_unit_transport_cost_values = {
    ("NewYork", "Houston"): 5.0,
    ("NewYork", "Phoenix"): 6.0,
    ("NewYork", "Philadelphia"): 4.0,
    ("LosAngeles", "Houston"): 3.0,
    ("LosAngeles", "Phoenix"): 2.0,
    ("LosAngeles", "Philadelphia"): 7.0,
    ("Chicago", "Houston"): 4.0,
    ("Chicago", "Phoenix"): 5.0,
    ("Chicago", "Philadelphia"): 3.0,
}
my_aimms.unit_transport_cost.assign(expected_unit_transport_cost_values)

actual_locations_set = my_aimms.locations.data()
print(f"locations: {actual_locations_set}")
if (not assertEqual(actual_locations_set,expected_locations_set)):
    print("locations data does not match expected values")
    exit(1)

actual_customers_set = my_aimms.customers.data()
print(f"customers: {actual_customers_set}")
if (not assertEqual(actual_customers_set,expected_customers_set)):
    print("customers data does not match expected values")
    exit(1)

actual_warehouses_set = my_aimms.warehouses.data()
print(f"warehouses: {actual_warehouses_set}")
if (not assertEqual(actual_warehouses_set,expected_warehouses_set)):
    print("warehouses data does not match expected values")
    exit(1)

actual_demand_values = my_aimms.demand.data()
print(f"demand: {actual_demand_values}")
if (not assertEqual(actual_demand_values,expected_demand_values)):
    print("demand data does not match expected values")
    exit(1)

print(f"demand_condition: {my_aimms.demand_condition.data()}")
# print(f"supply: {my_aimms.supply.data()}")
# print(f"unit_transport_cost: {my_aimms.unit_transport_cost.data()}")

my_aimms.MainExecution() # type: ignore

actual_total_transport_cost_value = my_aimms.total_transport_cost.data()
print(f"total_transport_cost: {actual_total_transport_cost_value}")
if (not assertEqual(actual_total_transport_cost_value,60.0)):
    print("total_transport_cost data does not match expected values")
    exit(1)

print(f"transport: {my_aimms.transport.data()}")

if my_aimms.total_transport_cost.data() == 0:
    exit(1)

print("Test passed")