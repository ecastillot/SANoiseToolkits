
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on tuesday Nov 24 10:00:00 2020
@author: Emmanuel_Castillo
last update: 24-11-2020 
"""
import os
import warnings
import concurrent.futures
from . import utils 
from obspy.core.inventory.inventory import read_inventory

class MassPPSDHelper(object):
    def __init__(self,client_tuple, dld_restrictions, 
                my_storage):
        """
        parameters:
        -----------
        client_tuple: tuple
            The format of the tuple is (client_type, client)
            where client type can be 'sds' or 'fdsn'
        dld_restrictions: DownloadRestrictions object
            Class storing non-PPSD restrictions for a downloading
            ppsd calculations
        ppsd_restrictions: PPSDRestrictions object
            Class storing PPSD restrictions for a query
        my_storage: str
            Path to save all ppsd analyses
        """
        self.client_type, self.client = client_tuple
        self.dld_restrictions = dld_restrictions
        self.my_storage = my_storage

    def create_inventory(self,inv_path=None,from_xml=None):
        myinv =  utils.solve_dldR(client=self.client,
                    from_xml=from_xml,
                    download_restrictions=self.dld_restrictions)
            
        if inv_path == None:
            inv_path = os.path.join(self.my_storage,"inv.xml")
        inv_dir = os.path.dirname(inv_path)
        if os.path.isdir(inv_dir) == False:
            os.makedirs(inv_dir)
        
        myinv.write(inv_path,format="STATIONXML")
        return inv_path

    def download(self,inv_path,ppsd_restrictions,
                n_processor=1,concurrent_feature="thread"):

        times = utils.get_chunktimes(starttime=self.dld_restrictions.starttime,
                    endtime = self.dld_restrictions.endtime,
                    chunklength_in_sec=self.dld_restrictions.chunklength,
                    overlap_in_sec=self.dld_restrictions.overlap)

        inv = read_inventory(inv_path)
        channels_contents = inv.get_contents()['channels']

        for starttime, endtime in times:
            def run_ppsd(single_cha_contents):
                utils.get_ppsd(self.my_storage,self.client,inv,
                        ppsd_restrictions,
                        single_cha_contents,starttime,endtime,
                        self.dld_restrictions.plot_trace)
                
            if n_processor == 1:
                for single_cha_contents in channels_contents:
                    utils.get_ppsd(self.my_storage,self.client,inv,
                                ppsd_restrictions,
                                single_cha_contents,starttime,endtime,
                                self.dld_restrictions.plot_trace)
            else:
                with concurrent.futures.ThreadPoolExecutor(max_workers=n_processor) as executor:
                    executor.map(run_ppsd,channels_contents)
        #         try:
        #             st = self.client.get_waveforms(network=self.dld_restrictions.network,
        #                                         station=self.dld_restrictions.station, 
        #                                         location=self.dld_restrictions.location,
        #                                         channel=self.dld_restrictions.channel,
        #                                         starttime=starttime,
        #                                         endtime=endtime)
        #             st_dict = st._groupby('{network}.{station}.{channel}')
        #             st_values = list(st_dict.values())

        #         except:
        #             st_warn = (f"{self.dld_restrictions.network}."
        #                         f"{self.dld_restrictions.station}."
        #                         f"{self.dld_restrictions.location}."
        #                         f"{self.dld_restrictions.channel}."
        #                         f"{starttime}."
        #                         f"{endtime}")
        #             warnings.warn(f"No:\t{st_warn}") 
        #             st_values = None
            
        #         print(st_values[0])

    
        