import unittest
from usgs_dv import *
import json


urls = [
'https://waterservices.usgs.gov/nwis/gwlevels/?format=json&bBox=-83.000000,36.500000,-81.000000,38.500000&siteType=GW&siteStatus=all',
'https://waterservices.usgs.gov/nwis/gwlevels/?format=json&bBox=-83.000000,36.500000,-81.000000,38.500000&siteType=GW&siteStatus=all',



]



class usgs_dvTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass 

    @classmethod
    def tearDownClass(cls):
        pass
        
    def testBaseQuery(self):
        