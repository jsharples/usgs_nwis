#%matplotlib inline
from urllib import parse, request
import json
from datetime import datetime, timedelta
import gzip
import io
import matplotlib.pyplot as plt

from .usgs_nwis import SitesQuery, BaseQuery, DataBySites