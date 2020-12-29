
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on tuesday Nov 24 10:00:00 2020
@author: Emmanuel_Castillo
last update: 25-11-2020 
"""
import os
import concurrent.futures
from . import utils 
from obspy.core.inventory.inventory import read_inventory

class MassivePPSD(object):
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
        """
        It creates an inventory according to dld_restrictions

        parameters:
        -----------
        inv_path: str
            Where you want to locate the restricted inventory.
            If None, it saves in my storage
        from_xml: str
            Path from xml file. If there is not a get station service, 
            so you can use it from xml. 

        returns
        -------
        inv_path:str
            Restricted inventory path
        """
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
        """
        Download all ppsd according to download and ppsd restrictions.

        parameters:
        -----------
        inv_path: str
            Inventory that contain the metadata
        ppsd_restrictions: PPSDRestrictions object
            Class that contain all parameters to calculate the PPSD.
        n_processor: int
            Number maximum of threads
        concurrent_feature: str
            'thread' or 'process'. Proccess is obsolete until now.

        Returns:
        --------
            PPSD saved in my_storage/{network}.{station}.{location}.{channel}/ppsd
        """

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
                if n_processor > len(channels_contents):
                    n_processor = len(channels_contents)

                with concurrent.futures.ThreadPoolExecutor(max_workers=n_processor) as executor:
                    executor.map(run_ppsd,channels_contents)

    def join(self,inv_path,
            n_processor=1,concurrent_feature="thread"):
        """
        Gathering all npz downloaded files and create one MassivePPSD file
        according to dld_restrictions. 

        parameters:
        -----------
        inv_path: str
            Inventory that contain the metadata of the
            filtered stations in dld_restrictions.

        Returns:
        --------
            Massive PPSD saved in my_storage/{network}.{station}.{location}.{channel}/mass_ppsd/
        """

        inv = read_inventory(inv_path)
        channels_contents = inv.get_contents()['channels']
        times = utils.get_chunktimes(starttime=self.dld_restrictions.starttime,
                    endtime = self.dld_restrictions.endtime,
                    chunklength_in_sec=self.dld_restrictions.chunklength,
                    overlap_in_sec=self.dld_restrictions.overlap)

        for single_cha_contents in channels_contents:
            if n_processor == 1:
                paths = []
                for starttime, endtime in times:
                    path = utils.get_path2join_ppsd(my_storage=self.my_storage,                              
                                            content=single_cha_contents,
                                            starttime=starttime,
                                            endtime=endtime)
                    paths.append(path)
                utils.get_MassPPSD(self.my_storage,paths,self.dld_restrictions)

            else:
                def run_get_path2join_ppsd(times):
                    path = utils.get_path2join_ppsd(my_storage=self.my_storage,                              
                                            content=single_cha_contents,
                                            starttime=times[0],
                                            endtime=times[1])
                    return path

                if n_processor > len(times):
                    n_processor = len(times)

                with concurrent.futures.ThreadPoolExecutor(max_workers=n_processor) as executor:
                    paths = executor.map(run_get_path2join_ppsd,times) 
                    utils.get_MassPPSD(self.my_storage,list(paths),self.dld_restrictions)  

            


if __name__ == "__main__":
    from obspy.clients.fdsn import Client as FDSN_Client
    from obspy.core.utcdatetime import UTCDateTime
    from .restrictions import (DownloadRestrictions,PPSDrestrictions)

    client_tuple = ('fdsn',FDSN_Client('http://10.100.100.232:8091'))
    dldR = DownloadRestrictions(network="CM", 
                                station="URMC,BAR2,RUS,PRA,PTA,DBB",
                                location="00,10", 
                                channel="*",
                                starttime=UTCDateTime(2019, 1, 1,0),
                                endtime=UTCDateTime(2019, 1, 2,0),
                                chunklength=86400,
                                overlap=None,
                                exclude=[("*","DBB,BAR2","[10]0","HH[ENZ]")],
                                plot_trace=True)
    ppsdR = PPSDrestrictions(skip_on_gaps=False,
                            db_bins=(-200, -50, 1.0), 
                            ppsd_length=3600.0, 
                            overlap=0.5, 
                            special_handling=None, 
                            period_smoothing_width_octaves=1.0, 
                            period_step_octaves=0.125, 
                            period_limits=None)
    my_storage = "/home/ecastillo/SANL_results"

    massppsd = MassivePPSD(client_tuple=client_tuple,
                        dld_restrictions = dldR,
                        my_storage=my_storage)
    
    # massppsd.create_inventory()
    # massppsd.download(inv_path="/home/ecastillo/SANL_results/inv.xml",ppsd_restrictions = ppsdR,
    #                 n_processor=8,concurrent_feature='thread')
    # massppsd.join(inv_path="/home/ecastillo/SANL_results/inv.xml")


    
        