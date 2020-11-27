#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on tuesday Nov 25 10:00:00 2020
@author: Emmanuel_Castillo
last update: 25-11-2020 
"""

class AnalysisRestrictions(object):
    def __init__(self, network, station, 
                    location, channel,
                    starttime, endtime,
                     time_of_weekday=None)
        """
        Class saves all parameters needed to analysis

        Paramaters:
        -----------
        network: str
            The network code. Can contain wildcards.
        station: str
            The station code. Can contain wildcards.
        location: str
            The location code. Can contain wildcards.
        channel: str
            The channel code. Can contain wildcards.
        starttime: UTCDateTime object
            The start time of the data.
        endtime: UTCDateTime object  
            The end time of the data.          
        time_of_weekday: list of (int, float, float) 3-tuples
            From obspy: If set, restricts the data that is included
            in the stack by time of day and weekday. Monday is `1`, Sunday is
            `7`, `-1` for any day of week. For example, using
            `time_of_weekday=[(-1, 0, 2), (-1, 22, 24)]` only individual
            spectra that have a starttime in between 10pm and 2am are used in
            the stack for all days of week, using
            `time_of_weekday=[(5, 22, 24), (6, 0, 2), (6, 22, 24), (7, 0, 2)]`
            only spectra with a starttime in between Friday 10pm to Saturdays
            2am and Saturday 10pm to Sunday 2am are used.
            Note that time of day is specified in UTC (time of day might have
            to be adapted to daylight saving time). Also note that this setting
            filters only by starttime of the used psd time slice, so the length
            of individual slices (set at initialization:
            :meth:`PPSD(..., ppsd_length=XXX, ...) <PPSD.__init__>` in seconds)
            has to be taken into consideration (e.g. with a `ppsd_length` of
            one hour and a `time_of_weekday` restriction to 10pm-2am
            actually includes data from 10pm-3am).
        """
        
        self.starttime = starttime
        self.endtime = endtime
        self.network = network
        self.station = station
        self.location = location
        self.channel = channel
        self.time_of_weekday = time_of_weekday

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other.__dict__  