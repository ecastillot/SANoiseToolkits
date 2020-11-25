#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on tuesday Nov 24 10:00:00 2020
@author: Emmanuel_Castillo
last update: 24-11-2020 
"""

if __name__ == "__main__":
    import sys
    module_path = "/home/ecastillo/repositories/SANoiseLevels"
    sys.path.insert(0,module_path)

    from obspy.clients.fdsn import Client as FDSN_Client
    from obspy.core.utcdatetime import UTCDateTime
    from analyses.mass_ppsd.restrictions import (DownloadRestrictions,
                                                PPSDrestrictions)
    from analyses.mass_ppsd.downloader import MassPPSDHelper

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

    massppsd = MassPPSDHelper(client_tuple=client_tuple,
                        dld_restrictions = dldR,
                        my_storage=my_storage)
    
    massppsd.create_inventory()
    massppsd.download(inv_path="/home/ecastillo/SANL_results/inv.xml",ppsd_restrictions = ppsdR,
                    n_processor=8,concurrent_feature='thread')