#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
utilities for developing Massive Probabilistic Power Spectral Density download helper.

:copyright:
    Emmanuel Castillo (ecastillot@unal.edu.co), 2020
:license:
    GNU Lesser General Public License, Version 3
    (https://www.gnu.org/copyleft/lesser.html)
"""

from obspy.clients.fdsn.mass_downloader import domain
from obspy.core.inventory.inventory import read_inventory

def solve_dldR(client=None, from_xml=None, download_restrictions=None):
    """
    Parameters
    ----------
    client: obspy.Client object
        fdsn client
    download_restrictions: DownloadRestrictions object
        It is necessary to restrict some features of the data
    
    Returns:
    --------
    inv_new: Inventory object
        Restricted inventory according to download_Restrictions
    """
    if from_xml != None:
        inv = read_inventory(from_xml, format="STATIONXML")
        inv = inventory.select(network=download_restrictions.network,
                                    station=download_restrictions.station,
                                    location=download_restrictions.location,
                                    channel=download_restrictions.channel,
                                    starttime=download_restrictions.starttime,
                                    endtime=download_restrictions.endtime)
    else:
        inv = client.get_stations(
                            network=download_restrictions.network,
                            station=download_restrictions.station, 
                            location=download_restrictions.location,
                            channel=download_restrictions.channel,
                            starttime=download_restrictions.starttime,
                            endtime=download_restrictions.endtime, 
                            level="response")

    # Lets go with feature restrictions.
    if download_restrictions is not None:
        if not download_restrictions.exclude:
            pass
        else:
            inv_new = inv.copy()
            for to_exclude in download_restrictions.exclude:
                net,sta,loc,cha = to_exclude
                net,sta,loc,cha = list(map(lambda x:x.split(","), 
                                                [net,sta,loc,cha]))
                for n in net:
                    for s in sta:
                        for l in loc:
                            for c in cha:
                                inv_new = inv_new.remove(network=n,
                                                        station=s,
                                                        location=l,
                                                        channel=c)
        inv = inv_new.copy()

    return inv

def get_npz_name_by_day(path, year, network, station,
                        location, channel, jul_day ):
    """
    Parameters:
    -----------
    path: str
        Specific path where will be located the ppsd information
        in npz format. Only one format is accepted in path str.
        it must contain the next information
        {network}{station}{location}{channel}{year}{jul_day}
    year: int or str
        Corresponding year
    network: str
        Name of the network
    station: str
        Name of the station
    locarion: str
        Name of the station
    channel: str
        Name of the channel
    jul_day: int or str
        Corresponding julian day

    Returns:
    --------
    npz_path:
        Name of the npz file by day.
    """
                        
    if ("{network}" in path) and ("{station}" in path) and \
        ("{location}" in path) and ("{channel}" in path) and \
        ("{year}" in path) and ("{jul_day}" in path):
        npz_path = path.format(year=year, network=network,
                    station=station, location=location,
                    channel=channel,jul_day=jul_day)
    
    else:
        raise TypeError("'%s' is not a day filepath." % str(path))

    return npz_path

if __name__ == "__main__":
    path = "downloadprove/{year}/{network}/{station}/{location}/{channel}/{network}.{station}.{location}.{channel}.{year}.{jul_day}"
    npz_name_by_day = get_npz_name_by_day(path, year="2015", network="BT", station="USME",
                        location="00", channel="HHZ", jul_day="123" )
    print(npz_name_by_day)