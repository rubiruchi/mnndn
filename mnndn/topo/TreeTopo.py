from mininet.topo import Topo

class TreeTopo(Topo):
    """Tree topology."""

    def build(self, height=1, degree=2, prefix='h'):
        assert height > 0
        assert degree > 0
        assert degree <= 26
        assert prefix != ''
        self.height = height
        self.degree = degree
        self.addHost(prefix, mnndn_tree_depth=0)
        self.__addTree(prefix, height, degree)

    def __addTree(self, root, height, degree):
        """Add subtree."""
        if height <= 0:
            return
        for i in range(degree):
            host = '%s%s' % (root, chr(i + ord('a')))
            self.addHost(host, mnndn_tree_depth=(self.height - height + 1))
            self.addLink(root, host)
            self.__addTree(host, height - 1, degree)
