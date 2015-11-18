from GridTopo import GridTopo

class GridSpikeTopo(GridTopo):
    """Grid topology, plus some end hosts connected to every node on the grid."""

    @staticmethod
    def makeHostName(row, col, spike=None):
        if spike is None:
            return GridTopo.makeHostName(row, col)
        return 'h%dx%ds%d' % (row, col, spike)

    def build(self, nRows=2, nCols=2, nSpikes=1):
        GridTopo.build(self, nRows, nCols)
        self.nRows, self.nCols, self.nSpikes = nRows, nCols, nSpikes
        for row in range(nRows):
            for col in range(nCols):
                gridHost = self.makeHostName(row, col)
                for spike in range(nSpikes):
                    host = self.addHost(self.makeHostName(row, col, spike))
                    self.addLink(gridHost, host)

    def assignIps(self, *args, **kwargs):
        raise TypeError("GridSpikeTopo does not support assignIps; " +
                        "use mnndn.topo.assignIps instead")

    def gridNodes(self):
        """Iterates node names of grid nodes."""
        for row in range(self.nRows):
            for col in range(self.nCols):
                yield self.makeHostName(row, col)

    def spikeNodes(self):
        """Iterates node names of spike nodes."""
        for row in range(self.nRows):
            for col in range(self.nCols):
                for spike in range(self.nSpikes):
                    yield self.makeHostName(row, col, spike)
