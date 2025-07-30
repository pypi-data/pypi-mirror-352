from aimms.project.project import Project, aap

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from model_stub import Project

my_aimms : Project = aap.AimmsAPI.get_current_aimms_api() 
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
