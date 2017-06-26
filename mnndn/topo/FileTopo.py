from mininet.topo import Topo

SECTION_NODES = '[nodes]'
SECTION_LINKS = '[links]'

class FileTopo(Topo):
    """Topology created from file."""

    @staticmethod
    def parseAttributes(tokens):
        return dict([ kv for kv in [ token.split('=') for token in tokens ] if len(kv) == 2 ])

    def build(self, filename):
        """Build topology from file.
           filename: Mini-NDN style topology file."""

        currentSection = None
        with open(filename) as f:
            for line in f:
                line = line.strip()
                if line == SECTION_NODES or line == SECTION_LINKS:
                    currentSection = line
                elif currentSection == SECTION_NODES:
                    nodeName, attributes = line.split(': ')
                    attributes = self.parseAttributes(attributes.split(' ')[1:])
                    self.addHost(nodeName, mnndn=attributes)
                elif currentSection == SECTION_LINKS:
                    tokens = line.split(' ')
                    node1, node2 = tokens[0].split(':')
                    attributes = self.parseAttributes(tokens[1:])
                    self.addLink(node1, node2, mnndn=attributes)

def toTopoFile(topo, out, excludeHosts=set()):
    """Write topology to file.
       out: output file object.
       excludeHosts: set of hosts to exclude from output."""
    out.write(SECTION_NODES + '\n')
    for host in topo.nodes(False):
        if host in excludeHosts:
            continue
        out.write('%s: _' % host)
        attributes = topo.nodeInfo(host).get('mnndn', dict())
        for kv in attributes.iteritems():
            out.write(' %s=%s' % kv)
        out.write('\n')

    out.write(SECTION_LINKS + '\n')
    for (src, dst) in topo.iterLinks():
        if src in excludeHosts or dst in excludeHosts:
            continue
        out.write('%s:%s' % (src, dst))
        attributes = topo.linkInfo(src, dst).get('mnndn', dict())
        for kv in attributes.iteritems():
            out.write(' %s=%s' % kv)
        out.write('\n')

if __name__ == '__main__':
    import sys
    topo = FileTopo(sys.argv[1])
    toTopoFile(topo, sys.stdout)
