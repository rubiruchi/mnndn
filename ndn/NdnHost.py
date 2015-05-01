from mininet.node import Host
from NfdForwarder import NfdForwarder

class NdnHost(Host):
    "NDN host."
    def __init__(self, *opts, **params):
        OVERRIDE_DIRS = ['/etc/ndn', '/var/log/ndn', '/var/run', '/root']
        privateDirs = params.get('privateDirs', [])
        privateDirs = [ pd for pd in privateDirs if pd[0] not in OVERRIDE_DIRS ]
        for d in OVERRIDE_DIRS:
            privateDirs.append((d, '/tmp/mnndn/%(name)s' + d))
        params['privateDirs'] = privateDirs

        Host.__init__(self, *opts, **params)
        self.cmd('export HOME=/root')

        self.fw = None

    def openFile(self, fileName, mode):
        realPath = fileName
        for d in self.privateDirs:
            if fileName.startswith(d[0] + '/'):
                realPath = (d[1] % self.__dict__) + fileName[len(d[0]):]
                break
        return open(realPath, mode)

    def popen(self, *opts, **params):
        env = params.get('env', None)
        if env is None:
            env = {}
        env['HOME'] = '/root'
        params['env'] = env
        return Host.popen(self, *opts, **params)

    def getPeers(self):
        "Return (myIntf, peerIntf) for all intfs connecting to."
        connections = []
        for intf in self.intfList():
            link = intf.link
            if not link:
                continue
            node1, node2 = link.intf1.node, link.intf2.node
            if node1 == self:
                connections += [ (link.intf1, link.intf2) ]
            elif node2 == self:
                connections += [ (link.intf2, link.intf1) ]
        return connections

    def getFw(self, fw = NfdForwarder, **params):
        if self.fw is None:
            self.fw = fw(self, **params)
            self.fw.start()
        return self.fw
