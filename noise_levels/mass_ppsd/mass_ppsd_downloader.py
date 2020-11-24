from obspy.clients.fdsn.mass_downloader import MassDownloader


class MassPPSD(MassDownloader):
    def __init__(self,providers,debug=False):
        MassDownloader.__init__(self,providers,debug)

    # def 





print(MassPPSD(providers=["IRIS"]).download)