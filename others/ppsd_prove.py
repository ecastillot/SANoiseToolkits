from obspy.signal import PPSD
from obspy.core.utcdatetime import UTCDateTime
from obspy.clients.fdsn import Client
from obspy.imaging.cm import pqlx


client = Client("IRIS")
st = client.get_waveforms(network="IU",
                        station="ANMO",
                        location="00",
                        channel="LHZ",
                        starttime=UTCDateTime("2010-03-25T06:00:00.000"), 
                        endtime=UTCDateTime("2010-03-29T14:00:00.000"))
print(st)
inv = client.get_stations(network="IU",
                            station="ANMO", 
                            location="00",
                            channel="LHZ",
                            starttime=UTCDateTime("2010-03-25T06:00:00.000"),
                            endtime=UTCDateTime("2010-03-29T14:00:00.000"), 
                            level="response")
tr = st[0]
ppsd = PPSD(tr.stats,inv,time_of_weekday=[(-1, 0, 2), (-1, 22, 24)])
ppsd.add(st)
ppsd.calculate_histogram(time_of_weekday=[(-1, 0, 2), (-1, 22, 24)] )
# print("acabe")
# ppsd.plot()
# print(ppsd.times_processed)
ppsd.plot("prove.jpg",cmap=pqlx)

# ppsd = PPSD.load_npz("/home/ecastillo/SANL_results/CM.BAR2.10.HNZ/MassPPSD/CM.BAR2.10.HNZ__20190101T000000Z__20190104T000000Z.npz")
# ppsd.plot("prove.jpg",cmap=pqlx)