from mininet.topo import Topo

class HostLinearTopo(Topo):
    """Linear topology of k hosts.
       This differs from mininet.topo.LinearTopo in that no switch is used."""

    def build(self, k=2):
        self.k = k
        last = None
        for host in self.hosts():
            self.addHost(host)
            if last is not None:
                self.addLink(last, host)
            last = host

    def hosts(self):
        """Iterates host names."""
        for i in range(self.k):
            yield 'h%d' % i
