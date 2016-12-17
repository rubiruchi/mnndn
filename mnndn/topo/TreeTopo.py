from mininet.topo import Topo

class TreeTopo(Topo):
    """Tree topology."""

    def build(self, depth=1, fanout=2):
        assert fanout > 0
        self.depth = depth
        self.fanout = fanout
        self.addHost('root')
        self.__addTree('root', depth, fanout)

    def __addTree(self, root, depth, fanout):
        if depth <= 1:
            return
        for i in range(fanout):
            host = 'h%d' % i if root == 'root' else '%sx%d' % (root, i)
            self.addHost(host)
            self.addLink(root, host)
            self.__addTree(host, depth - 1, fanout)
