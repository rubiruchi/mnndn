import atexit
import os

class NdnPing:
    """NDN reachability testing client."""

    DEFAULT_INTERVAL = 1000

    def __init__(self, host, prefix, interval=DEFAULT_INTERVAL, count=None, clientSpecifier=True, cmdArgs=None):
        """host: NdnHost instance
           prefix: NDN prefix of NdnPingServer
           interval: interval between probes (in milliseconds)
           count: total number of probes
           clientSpecifier: whether to add a client specifier in probe name
           cmdArgs: additional command line argument (as a string) to ndnping program"""
        self.host = host
        self.prefix = prefix
        self.interval = interval
        self.count = count
        self.clientSpecifier = clientSpecifier
        if clientSpecifier is True:
            self.clientSpecifier = self.host.name
        self.cmdArgs = cmdArgs

        self.isStarted = False
        atexit.register(self.stop)

    def start(self, logFile=None):
        if self.isStarted:
            raise "ndnping is already started"
        self.isStarted = True

        if logFile is None:
            self.log = open(os.devnull, 'wb')
        else:
            self.log = self.host.openFile(logFile, 'w')

        opts = ['-t', '-i', str(self.interval)]
        if self.clientSpecifier is not False:
            opts += ['-p', self.clientSpecifier]
        if self.count is not None:
            opts += ['-c', str(self.count)]
        if self.cmdArgs is not None:
            opts += self.cmdArgs.split(' ')
        opts.append(self.prefix)
        from subprocess import STDOUT
        self.process = self.host.popen('ndnping', *opts,
                                       stderr=STDOUT, stdout=self.log)

    def stop(self):
        if not self.isStarted:
            return
        self.process.send_signal(2)
        self.process.wait()
        self.process = None
        self.log.close()
        self.isStarted = False

class NdnPingServer:
    "NDN reachability testing server."
    def __init__(self, host, prefix):
        self.host = host
        self.prefix = prefix

        self.isStarted = False
        atexit.register(self.stop)

    def start(self):
        if self.isStarted:
            raise "ndnpingserver is already started"
        self.isStarted = True

        self.log = open(os.devnull, 'wb')
        from subprocess import STDOUT
        self.process = self.host.popen('ndnpingserver', self.prefix,
                                       stderr=STDOUT, stdout=self.log)

    def stop(self):
        if not self.isStarted:
            return
        self.process.kill()
        self.process.wait()
        self.process = None
        self.log.close()
        self.isStarted = False
