from mininet.link import TCIntf

class LinkFailure:
    """Allow failing and recovering links, and simulating link delays.
       To use this helper, Mininet must be created with `link=TCLink`."""

    def __init__(self, net, sched):
        """net: a Mininet instance
           sched: a sched.scheduler instance"""
        self.net = net
        self.sched = sched
        self.failedIntfs = set()
        self.intfDelays = {}

    def parseCmd(self, cmd):
        """Parse command line argument.
           cmd: t,fail,h1-h2
                t,recover,h1-h2
                t,delay,h1-h2,ms"""
        a = cmd.split(',')
        h1, h2 = a[2].split('-')
        if a[1] == 'fail':
            self.fail(h1, h2, float(a[0]))
        elif a[1] == 'recover':
            self.recover(h1, h2, float(a[0]))
        elif a[1] == 'delay':
            self.delay(h1, h2, int(a[3]), float(a[0]))

    def _getHosts(self, h1, h2, sort=True):
        h1 = h1 if not isinstance(h1, basestring) else self.net[h1]
        h2 = h2 if not isinstance(h2, basestring) else self.net[h2]
        if h1.name == h2.name:
            raise LookupError('h1 and h2 are the same')
        if sort and h1.name > h2.name:
            h1, h2 = h2, h1
        return h1, h2

    def _iterIntf(self, h1, h2):
        connections = h1.connectionsTo(h2)
        for (intf1, intf2) in connections:
            yield intf1
            yield intf2

    def _config(self, intf):
        if not isinstance(intf, TCIntf):
            raise TypeError('interface is not TCIntf')

        isFailed = intf in self.failedIntfs
        delay = self.intfDelays.get(intf, 0)
        intf.config(bw=1000, loss=(100 if isFailed else 0), delay=('%dms' % delay))

    def fail(self, h1, h2, t=None, cb=None):
        """Fail links between h1 and h2.
           h1, h2: mininet.node.Node, or node name
           t: if not None, schedule at a future time
           cb: if callable, call this function after failing link"""
        if t is not None:
            if self.sched is None:
                raise TypeError('scheduler is unavailable')
            self.sched.enter(t, 0, self.fail, (h1, h2, None, cb))
            return

        h1, h2 = self._getHosts(h1, h2)
        for intf in self._iterIntf(h1, h2):
            self.failedIntfs.add(intf)
            self._config(intf)

        if hasattr(cb, '__call__'):
            cb()

    def recover(self, h1, h2, t=None, cb=None):
        """Recover links between h1 and h2.
           h1, h2: mininet.node.Node, or node name
           t: if not None, schedule at a future time
           cb: if callable, call this function after recovering link"""
        if t is not None:
            if self.sched is None:
                raise TypeError('scheduler is unavailable')
            self.sched.enter(t, 0, self.recover, (h1, h2, None, cb))
            return

        h1, h2 = self._getHosts(h1, h2)
        for intf in self._iterIntf(h1, h2):
            self.failedIntfs.discard(intf)
            self._config(intf)

        if hasattr(cb, '__call__'):
            cb()

    def delay(self, h1, h2, delay, t=None, cb=None):
        """Set unidirectional delay on links from h1 to h2.
           h1, h2: mininet.node.Node, or node name
           t: if not None, schedule at a future time
           cb: if callable, call this function after setting delay"""
        if t is not None:
            if self.sched is None:
                raise TypeError('scheduler is unavailable')
            self.sched.enter(t, 0, self.delay, (h1, h2, delay, None, cb))
            return

        h1, h2 = self._getHosts(h1, h2, sort=False)
        for intf in self._iterIntf(h1, h2):
            if intf.node != h1:
                continue
            self.intfDelays[intf] = delay
            self._config(intf)

        if hasattr(cb, '__call__'):
            cb()
