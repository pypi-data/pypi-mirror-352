# Import necessary modules
from peewee import SqliteDatabase

# Import the casbin peewee adapter
import casbin_peewee_adapter

# Import casbin
import casbin

# Import the os module
import os

# Define the database
DATABAEE = SqliteDatabase("casbin.sqlite")
# Bind the database to the CasbinRule model
casbin_peewee_adapter.CasbinRule._meta.database = DATABAEE
# Create the CasbinRule table if it doesn't exist
DATABAEE.create_tables([casbin_peewee_adapter.CasbinRule])
# Create the adapter
adapter = casbin_peewee_adapter.Adapter(database=DATABAEE)


# Define the function to get the enforcer
def get_enforcer() -> casbin.Enforcer:
    # Get the path to the model configuration file
    model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model.conf")
    # Create the enforcer
    e = casbin.Enforcer(model_path, adapter, True)
    # Return the enforcer
    return e
