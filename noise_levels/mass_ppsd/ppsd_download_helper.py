#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Massive Probabilistic Power Spectral Density download helper.

:copyright:
    Emmanuel Castillo (ecastillot@unal.edu.co), 2020
:license:
    GNU Lesser General Public License, Version 3
    (https://www.gnu.org/copyleft/lesser.html)
"""
import os

class StationQuality(object):
    def __init__(self, network, station, 
                location, channel, npz_path_by_day):

        self.network = network
        self.station = station
        self.location = location
        self.channel = channel
        self.npz_path_by_day = npz_path_by_day

    @property
    def has_existing_file_by_day(self):
        existence = os.path.isfile(self.npz_path_by_day)
        return existence

        
class PPSDDownloaderHelper(object):
    def __init__(self, client, download_restrictions, 
                ppsd_restrictions,storage):
        self.client = client
        self.download_restrictions = download_restrictions
        self.ppsd_restrictions = ppsd_restrictions
        self.storage = storage

    # def download_ppsd(self, threads_per_client):

        
        # def star_download(stream):



            # if str(isinstance("Hello", ())

        

if __name__ == "__main__":
    from restrictions import DownloadRestrictions 
    from utils import solve_dldR 
    from obspy.clients.fdsn.client import Client
    from obspy.core.utcdatetime import UTCDateTime

    client = Client("http://10.100.100.232:8091")   
    dldR =  DownloadRestrictions(
                        network="CM", 
                        station="URMC,BAR2,RUS,PRA,PTA,DBB",
                        location="00,10", 
                        channel="*",
                        starttime=UTCDateTime(2019, 1, 1,0),
                        endtime=UTCDateTime(2019, 1, 2,0),
                        exclude=[("*","DBB,BAR2","[10]0","HH[ENZ]")])

    constrain_solver = solve_dldR(client,
                                dldR)

    print(constrain_solver)
