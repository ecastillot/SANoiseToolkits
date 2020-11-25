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
from obspy.signal import PPSD
from obspy.clients.fdsn.mass_downloader.utils import get_mseed_filename
import datetime as dt
import os

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

def get_path(my_storage, job,single_cha_contents,
                starttime, endtime,extension_file=None):
    """
    Gets path according to the job.

    parameters:
    -----------
    my_storage: str
        Path to save all ppsd analyses
    job: str
        Name of the job. ex. plot_trace, ppsd,...
    single_cha_contents: str
        format: network.station.location.channel
    starttime: UTCDateTime object
        Start time of the trace
    endtime: UTCDateTime object
        End time of the trace
    extension_file: str
        Extension name according to the job

    returns:
    --------

        Path of the filename according to the job.
    """
    network,station,location,channel = single_cha_contents.split('.')
    starttime_str = str(starttime.year)
    endtime_str = "{:02d}".format(starttime.month)
    _dir= os.path.join(my_storage,single_cha_contents,
                             job,starttime_str,endtime_str)

    _str = "{network}.{station}.{location}.{channel}__{starttime}__{endtime}"
    filename = get_mseed_filename(_str, network, station, location, channel,
                             starttime, endtime)
    
    if ".mseed" in filename:
        filename = filename.replace('.mseed',f'.{extension_file}')
    else:
        filename = filename + f'.{extension_file}'

    path = os.path.join(_dir,filename)
    return path

def get_chunktimes(starttime,endtime,chunklength_in_sec, overlap_in_sec=0):
    """
    Make a list that contains the chunktimes according to 
    chunklength_in_sec and overlap_in_sec parameters.
    Parameters:
    -----------
    starttime: obspy.UTCDateTime object
        Start time
    endtime: obspy.UTCDateTime object
        End time
    chunklength_in_sec: None or int
        The length of one chunk in seconds. 
        The time between starttime and endtime will be divided 
        into segments of chunklength_in_sec seconds.
    overlap_in_sec: None or int
        For more than one chunk, each segment will have overlapping seconds
    Returns:
    --------
    times: list
        List of tuples, each tuple has startime and endtime of one chunk.
    """

    if chunklength_in_sec == 0:
        raise Exception("chunklength_in_sec must be different than 0")
    elif chunklength_in_sec == None:
        return [(starttime,endtime)]

    if overlap_in_sec == None:
        overlap_in_sec = 0

    deltat = starttime
    dtt = dt.timedelta(seconds=chunklength_in_sec)
    overlap_dt = dt.timedelta(seconds=overlap_in_sec)

    times = []
    while deltat < endtime:
        # chunklength can't be greater than (endtime-startime)
        if deltat + dtt > endtime:
            break
        else:
            times.append((deltat,deltat+dtt))
            deltat += dtt - overlap_dt

    if deltat < endtime:    
        times.append((deltat,endtime))
    return times

def get_ppsd(my_storage,client,inv,ppsd_restrictions,
            single_cha_contents, starttime,endtime, plot_trace=False):
    network,station,location,channel = single_cha_contents.split('.')
    try:
        st = client.get_waveforms(network=network,
                                    station=station, 
                                    location=location,
                                    channel=channel,
                                    starttime=starttime,
                                    endtime=endtime)

    except:
        st_warn = (f"{network}."
                    f"{station}."
                    f"{location}."
                    f"{channel}"
                    f"__{starttime}."
                    f"__{endtime}")
        st = None


    now = dt.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    if st == None:
        print(f"{now}[Failed]:  {st_warn } ")
        return None

    if plot_trace == True:
        plotst_path = get_path(my_storage,'plot_trace',
                            single_cha_contents,starttime,
                            endtime,extension_file='jpg')
        plotst_dir = os.path.dirname(plotst_path)
        if os.path.isdir(plotst_dir) == False:
            os.makedirs(plotst_dir)

        st.plot(outfile=plotst_path)
        print(f"{now}[plot_trace]:  {plotst_path}")

    now = dt.datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    try:
        tr=st[0]
        ppsd = PPSD(tr.stats, metadata=inv, **ppsd_restrictions.__dict__)
        ppsd.add(st)
        print(f"{now}[ppsd]:  ok")
    except:
        print(f"{now}[ppsd]:  Failed")

# def get_ppsd(st,inv,ppsd_restrictions):
#     tr=st[0]
#     ppsd = PPSD(tr.stats, metadata=inv, **ppsd_restrictions)
#     ppsd.add(st)
#     print(ppsd.times_processed)
#     # ppsd.save_npz(ppsd_dir)
    # ppsd_bolean=True
    # print(f"#### {ppsd_dir}:{ppsd_bolean}")

# def get_ppsd(single):

# def write_ppsd(st,inv):


if __name__ == "__main__":
    path = "downloadprove/{year}/{network}/{station}/{location}/{channel}/{network}.{station}.{location}.{channel}.{year}.{jul_day}"
    npz_name_by_day = get_npz_name_by_day(path, year="2015", network="BT", station="USME",
                        location="00", channel="HHZ", jul_day="123" )
    print(npz_name_by_day)