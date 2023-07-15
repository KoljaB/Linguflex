from core import cfg, log, DEBUG_LEVEL_MAX
from linguflex_functions import linguflex_function
import geocoder

default_city = cfg('city', default="")

@linguflex_function
def get_user_location():
    "Returns location of the user (city)"

    if default_city: 
        return default_city

    return geocoder.ip('me').city