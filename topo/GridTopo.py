from mininet.topo import Topo

class GridTopo(Topo):
    "Grid topology."
    def build(self, nRows=2, nCols=2):
        self.nRows = nRows
        self.nCols = nCols
        for row in range(1, nRows + 1):
            for col in range(1, nCols + 1):
                host = self.addHost('h%sx%s' % (row, col))
                if col > 1:
                    self.addLink('h%sx%s' % (row, col - 1), host)
                if row > 1:
                    self.addLink('h%sx%s' % (row - 1, col), host)

    def getPortAndIp(self, hostName, side):
        (row, col) = [ int(x) for x in hostName[1:].split('x') ]
        otherHost = None
        n = None
        if side == 'L':
            otherHost = 'h%sx%s' % (row, col - 1)
            col = col - 1
            n = 2
        elif side == 'R':
            otherHost = 'h%sx%s' % (row, col + 1)
            n = 1
        elif side == 'U':
            otherHost = 'h%sx%s' % (row - 1, col)
            row = row - 1
            n = 6
        elif side == 'D':
            otherHost = 'h%sx%s' % (row + 1, col)
            n = 5

        if otherHost is None:
            return (None, None)

        ports = self.port(hostName, otherHost)
        if len(ports) < 1:
            return (None, None)

        return (ports[0], '10.%s.%s.%s' % (row, col, n))

    def getIp(self, hostName, side):
        return self.getPortAndIp(hostName, side)[1]
        
    def assignIps(self, net):
        """Assign IP addresses to a built network.
           LEFT 10.row.col.2, RIGHT 10.row.col.1, UP 10.row.col.6, DOWN 10.row.col.5"""
        for row in range(1, self.nRows + 1):
            for col in range(1, self.nCols + 1):
                hostName = 'h%sx%s' % (row, col)
                host = net.get(hostName)

                for side in ['L', 'R', 'U', 'D']:
                    (port, ip) = self.getPortAndIp(hostName, side)
                    if port is not None:
                        intf = host.intfNames()[port]
                        host.setIP(ip, 30, intf)
