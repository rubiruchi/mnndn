class Routing:
    "NDN routing protocol."
    def __init__(self, host):
        self.host = host

    def start(self):
        "Start the routing daemon."
        raise "not implemented"

    def stop(self):
        "Stop the routing daemon."
        raise "not implemented"

    def advertise(self, prefix):
        "Advertise a prefix."
        raise "not implemented"

    def withdraw(self, prefix):
        "Withdraw a prefix."
        raise "not implemented"
