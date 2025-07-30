import os

import pandas as pd
from datetime import datetime

from aimms.project.project import DataReturnTypes, Project
from utils.testing import assertEqual
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from test_existing_project_with_different_datatypes import Project

aimms_path : str = os.getenv("AIMMSPATH", os.path.join( ".", "aimms", "latest", "Debug", "Bin"))
print (f"aimms_path: {aimms_path}")
aimms_project_path : str = os.path.join( os.path.dirname(__file__), "test_models", "datatypes", "datatypes.aimms")
print (f"aimms_project_path: {aimms_project_path}")

my_aimms = Project(
    aimms_path=aimms_path,
    aimms_project_path=aimms_project_path,
    exposed_identifier_set_name="AllIdentifiers",
    checked=True,
    data_type_preference= DataReturnTypes.DICT
)
my_aimms.generate_stub_file(os.path.join( os.path.dirname(__file__), f"{os.path.splitext(os.path.basename(__file__))[0]}.pyi"))

abbreviations_A = pd.DataFrame({
    "i_states": ['Alabama','Alaska','Arizona','Arkansas','American Samoa'],
    "StateAbbreviation": ['AL','AK','AZ','AR','AS']
})
my_aimms.StateAbbreviation.assign(abbreviations_A)

abbreviations_C = pd.DataFrame({
    "i_states": ['California','Colorado','Connecticut'],
    "StateAbbreviation": ['CA','CO','CT']
})
my_aimms.StateAbbreviation.update(abbreviations_C)

expected_abbreviations = {   
    ("Alabama"): "AL",
    ("Alaska"): "AK",
    ("Arizona"): "AZ",
    ("Arkansas"): "AR",
    ("American Samoa"): "AS",
    ("California"): "CA",
    ("Colorado"): "CO",
    ("Connecticut"): "CT"
}
actual_abbreviations = my_aimms.StateAbbreviation.data()
print(f"state abbreviations: {actual_abbreviations}")
if (not assertEqual(actual_abbreviations,expected_abbreviations)):
    print("state abbreviation data does not match expected values")
    exit(1)

abbreviations_invalid_state = pd.DataFrame({
    "i_states": ['Invalid State'],
    "StateAbbreviation": ['IS']
})
#invalid set elements are (silently) skipped
try:
    my_aimms.StateAbbreviation.update(abbreviations_invalid_state, {'checking': True})
    print("Invalid set element did not raise an error (while it should)")
    exit(1)
except Exception as e:
    print(f"Invalid set element raised an error as expected: {e}")

actual_abbreviations2 = my_aimms.StateAbbreviation.data()
if (not assertEqual(actual_abbreviations2,expected_abbreviations)):
    print("state abbreviation data does not match expected values")
    exit(1)

# current date and time
demand_data = pd.DataFrame({
    "t": [ datetime(2025, 5, 19, 12), datetime(2025, 5, 21, 6)],
    "Demand": [50.0, 60.0]
})
my_aimms.Demand.assign(demand_data)
expected_demand_data = {
    (datetime(2025, 5, 19, 12)): 50.0,
    (datetime(2025, 5, 21, 6)): 60.0
}
actual_demand_data = my_aimms.Demand.data()
if (not assertEqual(actual_demand_data,expected_demand_data)):
    print("demand data does not match expected values")
    exit(1)

print("Test passed")