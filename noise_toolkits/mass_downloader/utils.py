#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
utilities for developing Massive Probabilistic Power Spectral Density download helper.

:copyright:
    Emmanuel Castillo (ecastillot@unal.edu.co), 2020
:license:
    GNU Lesser General Public License, Version 3
    (https://www.gnu.org/copyleft/lesser.html)

last update: 28/12/2020
"""

from obspy.clients.fdsn.mass_downloader import domain
from obspy.core.inventory.inventory import read_inventory
from obspy.signal import PPSD
from obspy.clients.fdsn.mass_downloader.utils import get_mseed_filename
import datetime as dt
import os

PPSD_DIRNAME = 'ppsd'
MASSPPSD_DIRNAME = 'MassPPSD'
PLOT_TRACE_DIRNAME = 'plot_trace'

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4'

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
        Path to save a specific ppsd analyses
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

    """
    Calculates the ppsd object according to starttime, endtime
    and ppsd_restrictions parameters. It will be save in  
    my_storage/{network}.{station}.{location}.{channel}/ppsd

    Parameters:
    -----------
    my_storage: str
        Path to save all ppsd analyses
    client: Client object from obspy
        To use get_waveforms method
    inv: Inventory object from obspy
        To recognize the filtered stations that you want to
        calculate the ppsd
    ppsd_restrictions: PPSDRestrictions
        Information about the PPSD parameters
    single_cha_contents: 'str'
        network.station.location.channel
    starttime: UTCDateTime
        Start time that will be used to calculate the ppsd.
    endtime: UTCDateTime
        End time that will be used to calculate the ppsd.
    plot_trace: Boolean
        Plot the stream (It consumes a little bit time)
    """

    network,station,location,channel = single_cha_contents.split('.')
    try:
        st = client.get_waveforms(network=network,
                                    station=station, 
                                    location=location,
                                    channel=channel,
                                    starttime=starttime,
                                    endtime=endtime)

    except:
        strftime = "%Y%m%dT%H%M%SZ"
        st_warn = (f"{network}."
                    f"{station}."
                    f"{location}."
                    f"{channel}"
                    f"__{starttime.strftime(strftime)}"
                    f"__{endtime.strftime(strftime)}")
        st = None


    now = dt.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    if st == None:
        print_logs(job='load_trace',content=single_cha_contents,
                        status='no',
                        path=st_warn)
        return None

    if plot_trace == True:
        
        plotst_path = get_path(my_storage,PLOT_TRACE_DIRNAME,
                            single_cha_contents,starttime,
                            endtime,extension_file='jpg')

        filename = os.path.basename(plotst_path)
        if os.path.isfile(plotst_path) == True:
            print_logs(job='save_trace',content=single_cha_contents,
                        status='exist',
                        path=filename)

        else:
            plotst_dir = os.path.dirname(plotst_path)
            if os.path.isdir(plotst_dir) == False:
                os.makedirs(plotst_dir)

            st.plot(outfile=plotst_path)
            
            print_logs(job='save_trace',content=single_cha_contents,
                        status='ok',
                        path=filename)

    now = dt.datetime.now().strftime("%Y/%m/%d %H:%M:%S")

    try:
        ppsd_path = get_path(my_storage,PPSD_DIRNAME,
                            single_cha_contents,starttime,
                            endtime,extension_file='npz')

        filename = os.path.basename(ppsd_path)
        if os.path.isfile(ppsd_path ) == True:
            print_logs(job='save_ppsd',content=single_cha_contents,
                        status='exist',
                        path=filename)
        else:
            ppsd_dir = os.path.dirname(ppsd_path)
            if os.path.isdir(ppsd_dir) == False:
                os.makedirs(ppsd_dir)
            tr=st[0]
            ppsd = PPSD(tr.stats, metadata=inv, **ppsd_restrictions.__dict__)
            ppsd.add(st)
            ppsd.save_npz(ppsd_path)
            print_logs(job='save_ppsd',content=single_cha_contents,
                        status='ok',
                        path=filename)
    except:
        print_logs(job='save_ppsd',content=single_cha_contents,
                    status='exist',
                    path=filename)

def get_path2join_ppsd(my_storage,content,starttime,endtime):
    """
    parameters:
    -----------
    my_storage: str
        Path to save all ppsd analyses
    content: 'str'
        network.station.location.channel
    starttime: UTCDateTime
        Start time that will be used to begin the ppsd searching
        and be able to gathering each ppsd in one Massive PPSD
    endtime: UTCDateTime
        End time that will be used to finish the ppsd searching
        and be able to gathering each ppsd in one Massive PPSD

    returns
    -------
        path: list
            Paths of each ppsd that will be gather in one Massive PPSD

    """
    path = get_path(my_storage,PPSD_DIRNAME,
                    content,starttime,endtime,extension_file='npz')
    return path

def print_logs(job,content,status,path):
    """
    To print log information in the next format:
    [date][job][content][status]: path

    parameters:
    -----------
    job: 'str'
        Job in progress
    content: 'str'
        network.station.location.channel
    status: 'str' or Bolean
        Printing in colors according the status: 
        ok->green, false->red, exist->cyan, 
    path: 'str'
        Referencing the file path in progress
    """

    if status in ('ok','OK','TRUE','true',True):
        color_status = bcolors.OKGREEN 
    elif status in ('no','NO','FALSE','false',False):
        color_status = bcolors.FAIL 
    elif status in ('-','exist','EXIST'):
        color_status = bcolors.OKCYAN

    now = dt.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    if job in('FAILED','failed'):
        color_warning = bcolors.FAIL 
        text = (f"\n{color_warning}\{now}[{job}][{content}]{bcolors.ENDC}"
        +f"{color_status}[{status}]{bcolors.ENDC}: {path}\n")
    elif job in('OK','ok'):
        color_warning = bcolors.OKGREEN 
        text = (f"\n{color_warning}\{now}[{job}][{content}]{bcolors.ENDC}"
        +f"{color_status}[{status}]{bcolors.ENDC}: {path}\n")
    else:
        color_warning = bcolors.WARNING
        text = (f"{color_warning}\{now}[{job}][{content}]{bcolors.ENDC}"
            +f"{color_status}[{status}]{bcolors.ENDC}: {path}")
 
    print(text)

def get_MassPPSD(my_storage,paths,dld_restrictions):
    """
    parameters
    ----------
    my_storage: str
            Path to save all ppsd analyses
    paths: list
        list of paths that will be loaded or added in one Massive PPSD
    dld_restrictions: DownloadRestrictions object
            Class storing non-PPSD restrictions for a downloading
            ppsd calculations

    returns:
        save MassPPSD in my_storage/{network}.{station}.{location}.{channel}/Mass_PPSD/
    """
    content = paths[0].split('/')[-1].split('__')[0]

    ## to find the path for saving the MassPPSD file
    network,station,location,channel = content.split('.')
    _str = "{network}.{station}.{location}.{channel}__{starttime}__{endtime}"
    filename = get_mseed_filename(_str, network, station, location, channel,
                            dld_restrictions.starttime, 
                            dld_restrictions.endtime)
    filename = filename + f'.npz'
    path2save = os.path.join(my_storage,content,MASSPPSD_DIRNAME)
    if os.path.isdir(path2save) == False:
        os.makedirs(path2save)
    else: pass
    path2save = os.path.join(path2save,filename)
    ####

    if os.path.isfile(path2save) == True:
        text = f"This file already exists: {path2save}"
        print_logs(job='OK',content=content,status='exist',
                        path=text)
    else:

        loaded = False
        index = 0
        while loaded == False:
            try:
                ppsd = PPSD.load_npz(paths[index])
                loaded = True
                print_logs(job='loaded_npz',content=content,status='ok',
                            path=paths[index])
            except:
                print_logs(job='loaded_npz',content=content,status='no',
                            path=paths[index])
                
                if index == len(paths)-1:
                    loaded = None
                else:   
                    pass

                index += 1

        if loaded == True: 
            for path in paths[index+1::]:
                print_logs(job='to_added_npz',content=content,status='-',
                            path=path)

                ppsd.add_npz(path)

            try:
                ppsd.save_npz(path2save)
                print_logs(job='MassPPSD',content=content,status='ok',
                            path=path2save)
            except:
                print_logs(job='MassPPSD',content=content,status='no',
                            path=path2save)

            text = f"{content}"
            print_logs(job='OK',content=content,status='ok',
                            path=text)

        else: 
            text = f"Not be able to load any npz in {content}"
            print_logs(job='FAILED',content=content,status='no',
                            path=text)

if __name__ == "__main__":
    path = "downloadprove/{year}/{network}/{station}/{location}/{channel}/{network}.{station}.{location}.{channel}.{year}.{jul_day}"
    npz_name_by_day = get_npz_name_by_day(path, year="2015", network="BT", station="USME",
                        location="00", channel="HHZ", jul_day="123" )
    print(npz_name_by_day)