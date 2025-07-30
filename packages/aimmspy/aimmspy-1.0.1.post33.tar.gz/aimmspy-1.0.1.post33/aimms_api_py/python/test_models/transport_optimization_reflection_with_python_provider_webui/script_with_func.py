import os
from aimms.project.project import Project, aap
from aimms.model.enums.data_return_types import DataReturnTypes

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from model_stub import Project

my_aimms : Project = aap.AimmsAPI.get_current_aimms_api() 

def my_beautiful_function():
    my_aimms.data_type_preference = DataReturnTypes.DICT
    warehouses_set =  ["NewYork", "LosAngeles", "Chicago"]
    customers_set = ["Houston", "Phoenix", "Philadelphia"]
    locations_set = warehouses_set + customers_set

    my_aimms.locations.assign( locations_set )
    my_aimms.warehouses.assign( warehouses_set )
    my_aimms.customers.assign( customers_set )

    my_aimms.demand.assign({
        ("Houston"):50,
        ("Phoenix"):60,
        ("Philadelphia"):40,
    })

    my_aimms.supply.assign({
        ("NewYork"):70,
        ("LosAngeles"):80,
        ("Chicago"):60
    })

    my_aimms.unit_transport_cost.assign({
        ("NewYork", "Houston"): 5.0,
        ("NewYork", "Phoenix"): 6.0,
        ("NewYork", "Philadelphia"): 4.0,
        ("LosAngeles", "Houston"): 3.0,
        ("LosAngeles", "Phoenix"): 2.0,
        ("LosAngeles", "Philadelphia"): 7.0,
        ("Chicago", "Houston"): 4.0,
        ("Chicago", "Phoenix"): 5.0,
        ("Chicago", "Philadelphia"): 3.0,
    }) 

def execute_main():
    aap.AimmsAPI.get_current_aimms_api().MainExecution()

def make_stub_file():
    aap.AimmsAPI.get_current_aimms_api().generate_stub_file(os.path.join( os.path.dirname(__file__), f"model_stub.pyi"))

def increment_unit_transport_cost(amount : int):
    my_aimms.data_type_preference = DataReturnTypes.DICT
    to_increment = my_aimms.unit_transport_cost.data()
    
    # increment the demand by the amount
    for key in to_increment:
        to_increment[key] += amount
    my_aimms.unit_transport_cost.update(to_increment)