from mininet.topo import Topo

class FileTopo(Topo):
    """Topology created from file."""

    @staticmethod
    def parseAttributes(tokens):
        return dict([ token.split('=') for token in tokens ])

    def build(self, filename):
        """Build topology from file.
           filename: Mini-NDN style topology file."""
        SECTION_NODES = '[nodes]'
        SECTION_LINKS = '[links]'

        currentSection = None
        with open(filename) as f:
            for line in f:
                line = line.strip()
                if line == SECTION_NODES or line == SECTION_LINKS:
                    currentSection = line
                    continue
                if currentSection == SECTION_NODES:
                    nodeName, attributes = line.split(': ')
                    attributes = self.parseAttributes(attributes.split(' ')[1:])
                    self.addHost(nodeName, mnndn=attributes)
                if currentSection == SECTION_LINKS:
                    tokens = line.split(' ')
                    node1, node2 = tokens[0].split(':')
                    attributes = self.parseAttributes(tokens[1:])
                    self.addLink(node1, node2, mnndn=attributes)
