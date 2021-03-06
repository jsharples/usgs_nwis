
__all__ = ['SitesQuery', 'BaseQuery', 'DataBySites']

from urllib import parse, request
import json
from datetime import datetime, timedelta
import gzip
import io


class pyUSGSError(Exception):
        pass


class BaseQuery(object):
    """
    The basic query class to access the USGS water data service
    
    Parameters
    ----------
    major_filter: dict 
        Single key value pair, values can be lists, keys must be one of:
        * sites - for a list of specifc site ids
        * stateCd - for a state abbreviaiton e.g. "ny"
        * huc - for a list of Hydrologic Unit Codes
        * bBox - specifiying a lat long bounding box
        * countyCd - for a list of county numbers 
        Each query to the USGS NWIS must include one, and only one, of these filters.
    service: str
        The service to query, 'dv' for daily values, 'iv' for instantaneous
    data_format: str
        The format in which to get the data. Defult is `json`, if changed the `get_data` funciton will not work.
        
        
    """
  
  
    def __init__(self, major_filter, service='dv', data_format = 'json'):

        self._format = {'format': data_format}
        self.allowed_filters = ["sites","stateCd","huc","bBox","countyCd"]
        
        if list(major_filter.keys())[0] in self.allowed_filters:        
            self.major_filter = major_filter
        else:
            raise ValueError("major_filter must be one of: {}".format(', '.join(self.allowed_filters)))
        
        self.base_url = "https://waterservices.usgs.gov/nwis/{}/?".format(service)
        self.data = None
        self.raw_data = None
  
    
    def get_data(self, **kwargs):
        """
        Get data form the USGS webservice and parse to a python dictionary.
        
        Parameters
        ----------
        **kwargs : dict
            A dictionary specifying the search and filter items for this query.
        
        Returns
        ----------
        dict
            A dictionary of the requested data
        """
        
        if not self.raw_data:
            self._get_raw_data(**kwargs)
            
        self.data = json.loads(self.raw_data)
        
        return self.data
    
    def _make_request_url(self, **kwargs):
        """
        Make the request URL from kwargs
        """
        kwargs.update(self.major_filter)
        kwargs.update(self._format)
        
        for arg in kwargs.keys():
            
            try:
                assert not isinstance(kwargs[arg], str)
                #multiple values must be seperated by a comma
                kwargs[arg] = ','.join(map(str, kwargs[arg]))
                
            except:
                pass
       
        return self.base_url + parse.urlencode(kwargs, doseq=True)
   
   
    def _get_raw_data(self, **kwargs):
        """
        Get the raw data response 
        """
        
        self.request_url = self._make_request_url(**kwargs)
        
        #the USGS requests that users use gzip where possible
        data_request = request.Request(
                    self.request_url,
                    headers={"Accept-Encoding": "gzip"})
        data_response = request.urlopen(data_request)
        
        if data_response.info().get('Content-Encoding') == 'gzip':
            result = gzip.decompress(data_response.read())
        else:
            result = data_response.read()
            
        self.raw_data = result.decode(data_response.info().get_content_charset('utf-8'))
       
        return self.raw_data
    
    @staticmethod
    def _date_parse(str_date):
        """
        Function for parsing dates.
        
        Note that the USGS use ISO_8601 for date formats, including a ':' in the timezone. 
        There does not appear to be a simple way to parse this to a datetime object.
        """
        if len(str_date) == 29 and str_date[-3]==':':
            str_date = str_date[:-3]+str_date[-2:]
            return datetime.strptime(str_date,'%Y-%m-%dT%H:%M:%S.%f%z')
        
        if len(str_date) == 23:
            return datetime.strptime(str_date,'%Y-%m-%dT%H:%M:%S.%f')
        
        if len(str_date) == 19:
            return datetime.strptime(str_date,'%Y-%m-%dT%H:%M:%S')
        
        if len(str_date) == 16:
            return datetime.strptime(str_date,'%Y-%m-%dT%H:%M')
        
        if len(str_date) == 10:
            return datetime.strptime(str_date,'%Y-%m-%d')
        

class SitesQuery(BaseQuery):
    """
    Class to access the Site Service
    
    Parameters
    ----------
    major_filter: dict 
        Single key value pair, values can be lists, keys must be one of:
        * sites - for a list of specifc site ids
        * stateCd - for a state abbreviaiton e.g. "ny"
        * huc - for a list of Hydrologic Unit Codes
        * bBox - specifiying a lat long bounding box
        * countyCd - for a list of county numbers 
        Each query to the USGS NWIS must include one, and only one, of these filters.
    service: str
        The service to query, 'dv' for daily values, 'iv' for instantaneous
    data_format: str
        The format in which to get the data. Defult is `json`, if changed the `get_data` funciton will not work.
        
        
    """

    
    def __init__(self, major_filter):
        
        super().__init__(major_filter = major_filter, service = 'site', data_format = 'rdb')
        self.sites = None
    
    #we cannot use BaseQuery.get_data because the Site Service does not offer JSON    
    def get_data(self, **kwargs): 
        """
        Get data form the USGS Site Service and parse to a python dictionary.
        
        Parameters
        ----------
        **kwargs : dict
            A dictionary specifying the search and filter items for this query.
        
        Returns
        ----------
        dict
            A dictionary of the requested site data
        """

        
        if not self.raw_data:
            self.raw_data = self._get_raw_data(**kwargs)
        
        info = ''
        header = []
        data = []
        n=0

        for l in self.raw_data.split('\n'):
            if len(l) > 0:
                if l[0] == '#':
                    info += l + '\n'
                else:
                    if n <3:
                        header.append(l.split('\t'))
                        n += 1
                    else:
                        data.append(l.split('\t'))

        data = [{header[0][x]: y[x] for x in range(len(header[0]))} for y in data]
        self.data = {'data':data, 'info':info}
       
        return self.data
    
    def get_site_ids(self, **kwargs):
        """
        Create a list of the sites found by this query.
        
        Parameters
        ----------
        **kwargs : dict
            A dictionary specifying the search and filter items for this query.
        
        Returns
        ----------
        list
            A list of site IDs matching the search and filters for this query.
        """
        if not self.data:
            self.get_data(**kwargs)
        self.sites = [s['site_no'] for s in self.data['data']]
        return self.sites
            
   
   
class DataBySites(BaseQuery):
    """
    Class to access data bases on a list of sites. 
    
    Parameters
    ----------
    sites: list 
        A list of sites IDs to query for data
    service: str
        The service to query, 'dv' for daily values, 'iv' for instantaneous
    **kwargs : dict
        A dictionary specifying the search and filter items for this query. 
        
    """
    def __init__(self, sites, service='dv', **kwargs):
        
        super().__init__(major_filter = {"sites":sites}, service=service)

        self.data = self.get_data(**kwargs)
        self.core_data = None
    
    def make_core_data(self):
        """
        Make a simplified version of the data containing only 'core' data fields.
    
        Parameters
        ----------
        none
        
        Returns
        ----------
        dict
            A simplified dictionary of the requested site data
        """
        core_data = []
        for ts in self.data['value']['timeSeries']:
            
            core_data.append(dict(
            location = ts['sourceInfo']['geoLocation']['geogLocation'],
            name = ts['sourceInfo']['siteName'],
            site = ts['sourceInfo']['siteCode'][0]['value'],
            unit = ts['variable']['unit']['unitCode'],
            description = ts['variable']['variableDescription'],
            qual_codes = {x['qualifierCode']: x['qualifierDescription'] for x in ts['values'][0]['qualifier']},
            data = ts['values'][0]['value'],
            time_zone = ts['sourceInfo']['timeZoneInfo']['defaultTimeZone']['zoneOffset']
            ))
        
        self.core_data = core_data
        
        return self.core_data