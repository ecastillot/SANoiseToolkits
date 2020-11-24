from obspy.signal import PPSD
from obspy.core.utcdatetime import UTCDateTime
from obspy.clients.fdsn import Client
from obspy.imaging.cm import pqlx


client = Client("IRIS")
st = client.get_waveforms(network="IU",
                        station="ANMO",
                        location="00",
                        channel="LHZ",
                        starttime=UTCDateTime("2010-02-27T06:00:00.000"), 
                        endtime=UTCDateTime("2010-03-27T14:00:00.000"))
print(st)
inv = client.get_stations(network="IU",
                            station="ANMO", 
                            location="00",
                            channel="LHZ",
                            starttime=UTCDateTime("2010-02-27T06:00:00.000"),
                            endtime=UTCDateTime("2010-03-27T14:00:00.000"), 
                            level="response")
tr = st[0]
ppsd = PPSD(tr.stats,inv)
ppsd.calculate_histogram(starttime=UTCDateTime("2010-02-27T06:00:00.000"), 
                        endtime=UTCDateTime("2010-02-27T08:00:00.000"))
ppsd.add(st)
print("acabe")
# ppsd.plot()
# print(ppsd.psd_values)
ppsd.plot("prove.jpg",cmap=pqlx)