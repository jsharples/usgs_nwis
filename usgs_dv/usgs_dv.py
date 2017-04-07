
__all__ = ['Daily_values', 'Streamflow_sites_DV']


class Daily_values(object):
  
    def __init__(self, major_filter):
        '''
        Args:
           major_filter: must be a dict with a singe key - value pair
           Keys must be one of:
               sites - for a list of specifc site ids
               stateCd - for a state abbreviaiton e.g. "ny"
               huc - for a list of Hydrologic Unit Codes
               bBox - specifiying a lat long bounding box
               countyCd - for a list of county numbers      
       
        '''
        self._format = {'format':'json'}
        self.allowed_filters = ["sites","stateCd","huc","bBox","countyCd"]
        
        if list(major_filter.keys())[0] in self.allowed_filters:        
            self.major_filter = major_filter
        else:
            raise ValueError("major_filter must be one of: {}".format(', '.join(self.allowed_filters)))
        
        self.base_url = "https://waterservices.usgs.gov/nwis/dv/?"
        self.data = None
  
    def _make_request_url(self, **kwargs):
       
        kwargs.update(self.major_filter)
        kwargs.update(self._format)
        
        for arg in kwargs.keys():
            if type(kwargs[arg]) is list:
                kwargs[arg] = ','.join(map(str,kwargs[arg]))
       
        return self.base_url + parse.urlencode(kwargs, doseq=True)
   
   
    def get_data(self, **kwargs):

        self.request_url = self._make_request_url(**kwargs)
        print(self.request_url)
     

        response = request.urlopen(self.request_url) 
        self.raw_data = response.read().decode(response.info().get_content_charset('utf-8'))
        self.data = json.loads(self.raw_data)
       
        data_cnt = sum([len(x['values'][0]['value']) for x in self.data['value']['timeSeries']])
       
        print("{} data points found".format(data_cnt))
       
        return self.data

   
    def Daily_valuesError(Exception):
        pass
       
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
   
   



class Streamflow_sites_DV(Daily_values):
    
    def __init__(self, sites, start_date, end_date, kwargs=None):
        
        if not kwargs:
            kwargs = {}
        
        super().__init__(major_filter = {"sites":sites})
              
        kwargs.update({"startDT":datetime.strftime(start_date,'%Y-%m-%d'), 
                       "endDT":datetime.strftime(end_date,'%Y-%m-%d'),
                       "parameterCd":"00060"
                      })
        
        self.data = self.get_data(**kwargs)
        self.core_data = None
    
    def make_core_data(self):
        
        core_data = []
        for ts in self.data['value']['timeSeries']:
            
            core_data.append(dict(
            location = ts['sourceInfo']['geoLocation']['geogLocation'],
            name = ts['sourceInfo']['siteName'],
            unit = ts['variable']['unit']['unitCode'],
            description = ts['variable']['variableDescription'],
            qual_codes = {x['qualifierCode']: x['qualifierDescription'] for x in ts['values'][0]['qualifier']},
            data = ts['values'][0]['value']
            ))
        
        self.core_data = core_data
        
    def plot_data(self):
        
        if not self.core_data:
            self.make_core_data()
        
        for ts in self.core_data:
                      
            plt.plot([datetime.strptime(x['dateTime'],'%Y-%m-%dT%H:%M:%S.%f') for x in ts['data']],[x['value'] for x in ts['data']])
            plt.show()
        
