
#__all__ = ['SitesQuery', 'BaseQuery', 'DataBySites']


class pyUSGSError(Exception):
        pass


class BaseQuery(object):
    '''
        The basic query to access the USGS water data service
        
        Args:
           major_filter: must be a dict with a singe key - value pair
           Keys must be one of:
               sites - for a list of specifc site ids
               stateCd - for a state abbreviaiton e.g. "ny"
               huc - for a list of Hydrologic Unit Codes
               bBox - specifiying a lat long bounding box
               countyCd - for a list of county numbers      
       
    '''
  
  
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
        
        if not self.raw_data:
            self._get_raw_data(**kwargs)
            
        self.data = json.loads(self.raw_data)
        
        return self.data
    
    def _make_request_url(self, **kwargs):
       
        kwargs.update(self.major_filter)
        kwargs.update(self._format)
        
        for arg in kwargs.keys():
            
            try:
                assert not isinstance(kwargs[arg], str)
                kwargs[arg] = ','.join(map(str, kwargs[arg]))
                
            except:
                pass
       
        return self.base_url + parse.urlencode(kwargs, doseq=True)
   
   
    def _get_raw_data(self, **kwargs):

        self.request_url = self._make_request_url(**kwargs)
        print(self.request_url)
        
        
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
    
    
    def _date_parse(self, str_date):
        
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
        
    
    @staticmethod   
    def show_useful_links():
        '''
        print useful link
        '''
       
        updated = datetime(2017,4,6)
       
        useful_links = {
            "Daily value testing tool": "https://waterservices.usgs.gov/rest/DV-Test-Tool.html",
            "Parameter listing: Physical" : "https://help.waterdata.usgs.gov/code/parameter_cd_query?group_cd=PHY",
            "Hydrological Unit Codes (HUC)" : "https://water.usgs.gov/GIS/huc_name.html",
            "State and County codes" : "https://help.waterdata.usgs.gov/code/county_query?fmt=html"
           
        }
        
        print('\n'.join([x+" - "+useful_links[x] for x in useful_links.keys()]))
        print('\nLast updated {}'.format(updated))

        

class SitesQuery(BaseQuery):
    '''
        Query the USGS sites service
    '''
    
    def __init__(self, major_filter):
        
        super().__init__(major_filter = major_filter, service = 'site', data_format = 'rdb')
        
        
    def get_data(self, **kwargs): 
        
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

       
        #data_cnt = sum([len(x['values'][0]['value']) for x in self.data['value']['timeSeries']])
        #print("{} data points found".format(data_cnt))
        
        data = [{header[0][x]: y[x] for x in range(len(header[0]))} for y in data]
        self.data = {'data':data, 'info':info}
       
        return self.data
    
    def get_site_ids(self):
        
        if not self.data:
            self.get_data()
        
        return [s['site_no'] for s in self.data['data']]
            
   
   
class DataBySites(BaseQuery):
    '''
        Query class to get data by site ID
    '''
    def __init__(self, sites, start_date, end_date, service='dv', parameter="00060", **kwargs):
        
        super().__init__(major_filter = {"sites":sites}, service=service)
        
        if not kwargs:
            kwargs = {}
        
        if service == 'iv':
            _date_formatter = '%Y-%m-%dT%H:%M'
        else:
            _date_formatter = '%Y-%m-%d'
               
        kwargs.update({"startDT":datetime.strftime(start_date, _date_formatter), 
                       "endDT":datetime.strftime(end_date, _date_formatter),
                       "parameterCd":parameter
                      })
        
        self.data = self.get_data(**kwargs)
        self.core_data = None
    
    def make_core_data(self):
        
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
        
    def plot_data(self):
        
        if not self.core_data:
            self.make_core_data()
        
        for ts in self.core_data:
            plt.figure(figsize=(15,7))          
            plt.plot([self._date_parse(x['dateTime']) for x in ts['data']],[x['value'] for x in ts['data']])
            plt.title(ts['site']+': '+ts['name'])
            plt.ylabel(ts['description'])
            plt.show()