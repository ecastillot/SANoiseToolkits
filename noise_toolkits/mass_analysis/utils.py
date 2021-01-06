#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on tuesday Nov 24 10:00:00 2020
@author: Emmanuel_Castillo
last update: 29-12-2020 
"""
import pygmt
from obspy.core.inventory.inventory import read_inventory
import pandas as pd
import matplotlib.pyplot as plt
from obspy.signal.spectral_estimation import PPSD

def get_availability(massive_paths,startdate,enddate, save=None,
                figsize=(14,10)):
    """
    It returns the masssive ppsds availability 

    Parameters:
    -----------
    masssive_paths: dict
        keys are contents: network.station.location.channel
        values are paths of the massive ppsds.
    startdate: UTCDateTime
        Start date to graph the figure. 
    enddate: UTCDateTime
        End date to graph the figure.
    save: str
        Pathe to save the figure
    figsize: tuple
        Size of the figure
    """

    UTC_startdate = startdate.matplotlib_date
    UTC_enddate = enddate.matplotlib_date
    
    fig = plt.figure(figsize=figsize)

    for i, (content,path) in enumerate(massive_paths.items()):
        try:
            ppsd = PPSD.load_npz(path)
            times = ppsd.times_data
            gaps = ppsd.times_gaps
            

            ax = plt.subplot(len(massive_paths),1,i+1)
            ax.set_yticks([])
            ax.xaxis_date()

            net, sta, loc ,cha = content.split('.')
            ax.set_ylabel(sta+'\n'+loc)

            for j, (start, end) in enumerate(times):
                start = start.matplotlib_date
                end = end.matplotlib_date

                if j == 0:
                    print(content)
                    if UTC_startdate < start:
                        ax.axvspan(UTC_startdate, start, 0, 1, facecolor="w", lw=0)

                elif j == len(times)-1:
                    if end < UTC_enddate:
                        ax.axvspan(end, UTC_enddate, 0, 1, facecolor="w", lw=0)

                ax.axvspan(start, end, 0, 1, facecolor="g", lw=0)

            for start, end in gaps:
                
                start = start.matplotlib_date
                end = end.matplotlib_date
                ax.axvspan(start, end, 0, 1, facecolor="w", lw=0)

            if i != len(massive_paths)-1:
                ax.set_xticks([])

            else:
                for label in ax.get_xticklabels():
                    label.set_rotation(40)
                    label.set_horizontalalignment('right')
                # ax.xaxis.set_major_formatter('%d %b %Y')
        except: pass

    if save != None:
        plt.savefig(save, dpi=300)
    else:
        plt.show()

def xml2df(xml):
    """
    Parameters
    ----------
    xml: str
        xml path

    Returns
    -------
    all_coords : DataFrame
        DataFrame with the coordinates info
        of each channel of station in each network
    """

    inv = read_inventory(xml)
    all_coords = [] 
    for network in inv:
        for station in network:
            for channel in  station:
                sta_coords = {}
                sta_coords['network'] = network.code
                sta_coords['station'] = station.code
                sta_coords['location_id'] = channel.location_code
                sta_coords['channel'] = channel.code
                sta_coords['latitude'] = station.latitude
                sta_coords['longitude'] = station.longitude
                sta_coords["elevation"] = station.elevation

                all_coords.append(sta_coords)
    return pd.DataFrame(all_coords)

def get_contents(xml, indicator='location_id',
                       filter_indicator =['00','20'] ):
    """
    Returns contents values ('latitude','longitude','elevation')
    in one dataframe. You can filtered it according to 'indicator'
    parameter.

    Parameters
    ----------
    xml : str
        xml or dataless file path
    indicator : str
        It's the indicator that will be filtered.
        available indicators: network, station, location_id, channel,  
                             latitude, longitude,  elevation
    filter_indicator: list
        List of strings related to the 'indicator' value that
        will be filtered.
    
    Returns
    -------
    new_df : DataFrame
        Filtered Dataframe 
    """
    all_df = xml2df(xml)

    if indicator == None:
        return all_df

    fi0 = filter_indicator[0]
    new_df = all_df[(all_df[indicator] == fi0)]
    for fi in filter_indicator[1:]:
        df = all_df[(all_df[indicator] == fi)]
        new_df.append(df, ignore_index = True) 

    new_df.drop_duplicates(subset = ["latitude","longitude"],
                            keep='first',inplace=True,
                            ignore_index=True)
    return new_df

def get_map(reg,df,xml_dict=None):
    """
    Returns a map of the stations

    parameters
    ----------
    reg: list
        Coordinates 
    df: DataFrame
        Contains network,station,location,channel,latitude, longitude
    xml_dict: dict
        keys-> path,indicator,filter_indicator
        path : str
            xml or dataless file path
        indicator : str
            It's the indicator that will be filtered.
            available indicators: network, station, location_id, channel,  
                                latitude, longitude,  elevation
        filter_indicator: list
            List of strings related to the 'indicator' value that
            will be filtered.
    """
    fig = pygmt.Figure()
    proj = 'M6i'
    fig.grdimage('@earth_relief_01m',
                region=reg,
                projection=proj,
                cmap='etopo1',
                shading=True,)
    fig.coast(region=reg,
                projection=proj,
                shorelines=True,
                water='lightblue',
                rivers= ['1/blue','2/blue'],
                # land='grey',
                # water='white',
                borders='1/1p,black',
                frame="afg",)

    if xml_dict != None:
        df_coords = get_contents(xml_dict["path"], indicator=xml_dict["indicator"],
                       filter_indicator=xml_dict["filter_indicator"] )
        colors = xml_dict["colors"]
        if isinstance(df_coords, pd.DataFrame):
            networks = df_coords.network.unique()
            for i,net in enumerate(networks):
                df2 = df_coords.loc[df_coords['network'] == net]
                lat = df2['latitude'].to_numpy()
                lon = df2['longitude'].to_numpy()

                fig.plot(lon,lat,
                        style='t0.15i',
                        color=colors[i],
                        label=net,
                            )

    if df is not None:
        if isinstance(df, pd.DataFrame):
            stations = df.station.unique()

            for i,sta in enumerate(stations):
                df3 = df.loc[df['station'] == sta]
                lat = df3['latitude'].to_numpy()
                lon = df3['longitude'].to_numpy()
                colors = df3['color'].to_numpy()
                fig.plot(lon,lat,
                        style='t0.15i',
                        color=colors[0],
                        label=sta,
                            )

    if (df is not None) or (xml_dict != None):
        fig.legend()

    fig.shift_origin(xshift='0i',yshift='0i')  # Shift for next call
    proj = 'G-70/0/2.0i'
    fig.grdimage(
                '@earth_relief_10m',
                region='g',
                projection=proj,
                cmap='globe',
                shading=True,
             )
    fig.coast(
                region='g',
                projection=proj,
                shorelines=True,
                water='white',
                borders='1/1p,black',
                land='grey',
                frame=True,
            )

    x_reg = [reg[0], reg[1], reg[1], reg[0], reg[0]]
    y_reg = [reg[2], reg[2], reg[3], reg[3], reg[2]]
    fig.plot(x_reg,y_reg,
            pen="2p,red")
    return fig


if __name__ == "__main__":
    from obspy import UTCDateTime
    # massive_paths = {"CM.BAR2.10.HNZ":"/home/ecastillo/SANL_results/CM.BAR2.10.HNZ/MassPPSD/CM.BAR2.10.HNZ__20190101T000000Z__20190104T000000Z.npz",
    #                 "CM.PRA.00.HHZ":"/home/ecastillo/SANL_results/CM.PRA.00.HHZ/MassPPSD/CM.PRA.00.HHZ__20190101T000000Z__20190104T000000Z.npz"}
    # startdate,enddate = UTCDateTime("20190102T000000Z"), UTCDateTime("20190104T000000Z")
    # get_availability(massive_paths,startdate,enddate, save="prove.jpg",
    #             figsize=(14,10))

    df1 = pd.read_csv("/home/ecastillo/repositories/SANoiseToolkits/noise_toolkits/mass_analysis/data_rssb.csv")
    df2 = pd.read_csv("/home/ecastillo/repositories/SANoiseToolkits/noise_toolkits/mass_analysis/data_ideam.csv")
    df = pd.concat([df2,df1])
    reg = [-79, -70, 2, 8]
    # reg = [-85, -65, -5, 15]
    xml_dict = {"path":"/home/ecastillo/SANL_results/inv.xml",
                "indicator":"location_id",
                "filter_indicator":["00"],
                "colors":['darkblue','magenta','orangered','black']}
    figmM = get_map(reg, df=df)
    # figmM = get_map(reg, df=df,xml_dict=xml_dict)
    figmM.savefig('map.png',dpi=300)
    