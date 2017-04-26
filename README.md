# USGS NWIS

A lightweight extensible package to interact with the US Geological Survey's [National Water Information System.](https://waterservices.usgs.gov/) This package should be used by those familiar with the service, or willing to read it's documentation.


## Features

* Written in Python 3 
* Uses gzip for all requests
* Requires only the standard library 


## Usage

Let's suppose we want stream flow data for Montague County, Texas (yeehaw Smokey) for the last 30 days. The relevant county code is `48337` as we can see from the USGS [state and county codes](https://help.waterdata.usgs.gov/code/county_query?fmt=html).  

```python
>>> import usgs_nwis as us
>>> my_sites = us.SitesQuery(major_filter = {'countyCd':'48337'})
>>> my_sites.get_site_ids(**{'period':'P30D', 'siteType':'ST'})
['07315525']
```

There is only one site with stream flow data in the past 30 days.
Let's get the the data:

```python
>>> my_data = us.DataBySites(sites=['07315525'],**{'period':'P30D', 'siteType':'ST'})
>>> my_data.make_core_data()
```

The full data, including all explanatory information and metadata, can be accessed as a nested dict via `my_data.data`. A greatly simplified selection of the data can be accessed via `my_data.core_data`


For more information on available filters refer to the useful links below, particularly the testing tools.

### Notes on plotting and pandas

#### matplotlib
Since I have stuck with the standard library for this project, there is no plotting functionality included. However, for those wishing to plot the data using `matplotlib` the following function will give basic plots from a `core_data` dict.

```python
import matplotlib.pyplot as plt
def plot_core_data(core_data):

    for ts in core_data:
        plt.figure(figsize=(15,7))
        plt.plot([us.BaseQuery._date_parse(x['dateTime']) for x in ts['data']],[x['value'] for x in ts['data']])
        plt.title(ts['site']+': '+ts['name'])
        plt.ylabel(ts['description'])
        #include plot customisation here
        plt.show()
```

#### pandas
For `pandas` users, each time series in the `core_data` dict can be converted to a `DataFrame` like so:

```python
import pandas as pd
pd.DataFrame(my_data.core_data[0]['data'])
```

## Useful links

* [Instantaneous value testing tool](https://waterservices.usgs.gov/rest/IV-Test-Tool.html)
* [Daily value testing tool](https://waterservices.usgs.gov/rest/DV-Test-Tool.html)
* [Parameter listing: Physical](https://help.waterdata.usgs.gov/code/parameter_cd_query?group_cd=PHY)
* [Hydrological Unit Codes (HUC)](https://water.usgs.gov/GIS/huc_name.html)
* [state and County codes](https://help.waterdata.usgs.gov/code/county_query?fmt=html)
           

## Licence
MIT