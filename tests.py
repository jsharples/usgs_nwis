import unittest
from usgs_dv import *
import json
from datetime import datetime, timedelta

urls = [
'https://waterservices.usgs.gov/nwis/gwlevels/?format=json&bBox=-83.000000,36.500000,-81.000000,38.500000&siteType=GW&siteStatus=all',
'https://waterservices.usgs.gov/nwis/gwlevels/?format=json&bBox=-83.000000,36.500000,-81.000000,38.500000&siteType=GW&siteStatus=all',

]


general_kwargs = {'startDT': datetime.now() - timedelta(days=15), 'endDT': datetime.now(), 'parameterCd': '00060'}


class usgs_dvTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass 

    @classmethod
    def tearDownClass(cls):
        pass
        
    def testBaseQuery(self):
        bq = BaseQuery({'sites' :['16010000', '16019000', '16036000', '16049000', '16060000']})
        bq.get_data(**general_kwargs)
        
        self.assertIs(type(bq.data, dict))

        
# runs the unit tests in the module
if __name__ == '__main__':
  unittest.main()