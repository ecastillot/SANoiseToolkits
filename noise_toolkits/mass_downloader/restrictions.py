#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Restrictions for the mass ppsd downloader.
Some parameters information had been taken from MassDownloader and PPSD class from obspy.

:copyright:
    Emmanuel Castillo (ecastillot@unal.edu.co), 2020
:license:
    GNU Lesser General Public License, Version 3
    (https://www.gnu.org/copyleft/lesser.html)
"""

from obspy.core.utcdatetime import UTCDateTime
from obspy.signal.spectral_estimation import PPSD

class DownloadRestrictions(object):
    """
    Class storing non-PPSD restrictions for a downloading ppsd calculations
    Parameters information taken from MassDownloader and PPSD class from obspy.

    :param starttime: The start time of the data to be downloaded.
    :type starttime: :class:`~obspy.core.utcdatetime.UTCDateTime`
    :param endtime: The end time of the data.
    :type endtime: :class:`~obspy.core.utcdatetime.UTCDateTime`
    :param network: The network code. Can contain wildcards.
    :type network: str
    :param station: The station code. Can contain wildcards.
    :type station: str
    :param location: The location code. Can contain wildcards.
    :type location: str
    :param channel: The channel code. Can contain wildcards.
    :type channel: str
    :param chunklength:  The length of one chunk in seconds. 
        If set, the time between starttime and endtime will be divided 
        into segments of chunklength_in_sec seconds.
    :type chunklength: int
    :param overlap: Overlap in the downloading in seconds
    :type overlap: int
    :param exclude: list
    :type exclude: list of 4-tuple ('network', 'station','location', 'channel') 
        where each element contains potentially wildcarded.
    """
    def __init__(self, network, station, 
                    location, channel,
                    starttime, endtime,
                    chunklength = 86400,
                    overlap=None,
                    exclude=[],
                    plot_trace=True):
        
        self.starttime = starttime
        self.endtime = endtime
        self.network = network
        self.station = station
        self.location = location
        self.channel = channel
        self.chunklength = chunklength
        self.overlap = overlap
        self.plot_trace = plot_trace

        if not exclude:
            pass
        else:   
            for i in exclude:
                assert len(i) == 4, (f"{i} is not a 4-tuple"
                                    "('network', 'station',"
                                    "'location', 'channel')")

        self.exclude = exclude

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other.__dict__         

class PPSDrestrictions(object):
    """
    Class storing PPSD restrictions for a query. 
    Parameters information taken from PPSD class from obspy 

    :type skip_on_gaps: bool, optional
    :param skip_on_gaps: Determines whether time segments with gaps should
            be skipped entirely. [McNamara2004]_ merge gappy
            traces by filling with zeros. This results in a clearly
            identifiable outlier psd line in the PPSD visualization. Select
            `skip_on_gaps=True` for not filling gaps with zeros which might
            result in some data segments shorter than `ppsd_length` not
            used in the PPSD.
    :type db_bins: tuple of three ints/floats
    :param db_bins: Specify the lower and upper boundary and the width of
            the db bins. The bin width might get adjusted to fit  a number
            of equally spaced bins in between the given boundaries.
    :type ppsd_length: float, optional
    :param ppsd_length: Length of data segments passed to psd in seconds.
            In the paper by [McNamara2004]_ a value of 3600 (1 hour) was
            chosen. Longer segments increase the upper limit of analyzed
            periods but decrease the number of analyzed segments.
    :type overlap: float, optional
    :param overlap: Overlap of segments passed to psd. Overlap may take
            values between 0 and 1 and is given as fraction of the length
            of one segment, e.g. `ppsd_length=3600` and `overlap=0.5`
            result in an overlap of 1800s of the segments.
    :type special_handling: str, optional
    :param special_handling: Switches on customized handling for
        data other than seismometer recordings. Can be one of: 'ringlaser'
        (no instrument correction, just division by
        `metadata["sensitivity"]` of provided metadata dictionary),
        'hydrophone' (no differentiation after instrument correction).
    :type period_smoothing_width_octaves: float
    :param period_smoothing_width_octaves: Determines over what
        period/frequency range the psd is smoothed around every central
        period/frequency. Given in fractions of octaves (default of ``1``
        means the psd is averaged over a full octave at each central
        frequency).
    :type period_step_octaves: float
    :param period_step_octaves: Step length on frequency axis in fraction
        of octaves (default of ``0.125`` means one smoothed psd value on
        the frequency axis is measured every 1/8 of an octave).
    :type period_limits: tuple/list of two float
    :param period_limits: Set custom lower and upper end of period range
        (e.g. ``(0.01, 100)``). The specified lower end of period range
        will be set as the central period of the first bin (geometric mean
        of left/right edges of smoothing interval). At the upper end of the
        specified period range, no more additional bins will be added after
        the bin whose center frequency exceeds the given upper end for the
        first time.
        
    """
    def __init__(self, skip_on_gaps=False, db_bins=(-200, -50, 1.0), 
                ppsd_length=3600.0, overlap=0.5, special_handling=None, 
                period_smoothing_width_octaves=1.0, 
                period_step_octaves=0.125, 
                period_limits=None):
        self.skip_on_gaps = skip_on_gaps
        self.db_bins = db_bins
        self.ppsd_length = ppsd_length
        self.overlap = overlap
        self.special_handling = special_handling
        self.period_smoothing_width_octaves = period_smoothing_width_octaves
        self.period_step_octaves = period_step_octaves
        self.period_limits = period_limits

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other  

if __name__ == '__main__':
    features_restrictions = DownloadRestrictions(
                    starttime=UTCDateTime(2012, 1, 1),
                    endtime=UTCDateTime(2012, 1, 2))

    ppsd_restrictions = PPSDrestrictions()