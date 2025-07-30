from aimms.model.identifiers.set import Set
from aimms.model.identifiers.parameter import Parameter
from aimms.model.identifiers.variable import Variable
from aimms.model.identifiers.index import Index
from aimms.model.identifiers.constraint import Constraint
from aimms.model.identifiers.mathematical_program import MathematicalProgram
from aimms.model.procedure import Procedure
from aimms.model.module import Module
from aimms.model.library import AimmsLibrary
import pyarrow
class Project:
    def multi_assign(self, data : pyarrow.Table): ...
    locations : Set = ...
    """
Set of all locations

"""
    l : Index = ...
    """
@range: locations 
"""
    warehouses : Set = ...
    """
"""
    w : Index = ...
    """
@range: warehouses 
"""
    customers : Set = ...
    """
"""
    c : Index = ...
    """
@range: customers 
"""
    demand : Parameter = ...
    """
@index domain: (c)
 
@unit :  
"""
    supply : Parameter = ...
    """
@index domain: (w)
 
@unit :  
"""
    unit_transport_cost : Parameter = ...
    """
@index domain: (w,c)
 
@unit :  
Cost of transporting one unit from warehouse indexed by w to customer indexed by c so for example ("Haarlem", "Amsterdam") = 1.0

"""
    satisfy_demand : Constraint = ...
    """
@index domain: c
 
@unit :  
"""
    satisfy_supply : Constraint = ...
    """
@index domain: w
 
@unit :  
"""
    transport : Variable = ...
    """
@index domain: (w,c)
 
@unit :  
"""
    total_transport_cost : Variable = ...
    """
"""
    MainInitialization : Procedure = ...
    """
Add initialization statements here that do NOT require any library being initialized already.

"""
    PostMainInitialization : Procedure = ...
    """
Add initialization statements here that require that the libraries are already initialized properly,
or add statements that require the Data Management module to be initialized.

"""
    MainExecution : Procedure = ...
    """
"""
    PreMainTermination : Procedure = ...
    """
Add termination statements here that require all libraries to be still alive.
Return 1 if you allow the termination sequence to continue.
Return 0 if you want to cancel the termination sequence.

"""
    MainTermination : Procedure = ...
    """
Add termination statements here that do not require all libraries to be still alive.
Return 1 to allow the termination sequence to continue.
Return 0 if you want to cancel the termination sequence.
It is recommended to only use the procedure PreMainTermination to cancel the termination sequence and let this procedure always return 1.

"""
