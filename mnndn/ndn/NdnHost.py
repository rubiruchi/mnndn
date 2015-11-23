from mininet.node import Host

class NdnHost(Host):
    """NDN host."""
    def __init__(self, *opts, **params):
        """Construct NDN host.
           fw: forwarder constructor
           rout: routing constructor"""
        OVERRIDE_DIRS = ['/etc/ndn', '/var/log/ndn', '/var/run', '/root']
        privateDirs = params.get('privateDirs', [])
        privateDirs = [ pd for pd in privateDirs if pd[0] not in OVERRIDE_DIRS ]
        for d in OVERRIDE_DIRS:
            privateDirs.append((d, '/tmp/mnndn/%(name)s' + d))
        params['privateDirs'] = privateDirs

        Host.__init__(self, *opts, **params)
        self.cmd('export HOME=/root')

        from NfdForwarder import NfdForwarder
        from NlsrRouting import NlsrRouting
        self.fwCtor = params.pop('fw', NfdForwarder)
        self.routCtor = params.pop('rout', NlsrRouting)

        self.fw = None
        self.rout = None

    def openFile(self, fileName, mode):
        realPath = fileName
        for d in self.privateDirs:
            if fileName.startswith(d[0] + '/'):
                realPath = (d[1] % self.__dict__) + fileName[len(d[0]):]
                break
        return open(realPath, mode)

    def popen(self, *args, **params):
        if len(args) == 1:
            if isinstance(args[0], list):
                # popen([cmd, arg1, arg2...])
                cmd = args[0]
            elif isinstance(args[0], basestring):
                # popen("cmd arg1 arg2...")
                cmd = args[0].split()
            else:
                raise TypeError('popen() requires a string or list')
        elif len(args) > 0:
            # popen( cmd, arg1, arg2... )
            cmd = list(args)

        if cmd[0][0] != '/' and cmd[0] != 'which':
            cmdPath, _, whichExit = self.pexec('which', cmd[0])
            if whichExit == 0:
                cmd[0] = cmdPath.rstrip()

        env = params.get('env', None)
        if env is None:
            env = {}
        env['HOME'] = '/root'
        params['env'] = env
        return Host.popen(self, cmd, **params)

    @staticmethod
    def __collectNdnPeers(nodeIntf):
        if isinstance(nodeIntf.node, NdnHost):
            return [ nodeIntf ]
        ndnPeerIntfs = []
        for intf in nodeIntf.node.intfList():
            link = intf.link
            if not link:
                continue
            intf1, intf2 = link.intf1, link.intf2
            if intf1.node == nodeIntf.node and intf1 != nodeIntf:
                ndnPeerIntfs += NdnHost.__collectNdnPeers(intf2)
            elif intf2.node == nodeIntf.node and intf2 != nodeIntf:
                ndnPeerIntfs += NdnHost.__collectNdnPeers(intf1)
        return ndnPeerIntfs

    def getPeers(self):
        """Return (myIntf, peerIntf, [ndnHostIntfs]) for all intfs connecting to."""
        peers = []
        for intf in self.intfList():
            link = intf.link
            if not link:
                continue
            node1, node2 = link.intf1.node, link.intf2.node
            if node1 == self:
                peers += [ (link.intf1, link.intf2, NdnHost.__collectNdnPeers(link.intf2)) ]
            elif node2 == self:
                peers += [ (link.intf2, link.intf1, NdnHost.__collectNdnPeers(link.intf1)) ]
        return peers

    def getFw(self, **params):
        if self.fw is None:
            if self.fwCtor is None:
                return None
            self.fw = self.fwCtor(self, **params)
        return self.fw

    def getRout(self, **params):
        if self.rout is None:
            if self.routCtor is None:
                return None
            self.rout = self.routCtor(self, **params)
        return self.rout
