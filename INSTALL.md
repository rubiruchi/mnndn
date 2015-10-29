# mnndn: installation

**mnndn** is developed on Ubuntu 14.04 Server 64-bit.

## Installation

1.  install [Mininet](http://mininet.org/) from [GitHub repository](https://github.com/mininet/mininet)

    command line: `util/install.sh -fnv`

2.  install NDN [packages](https://launchpad.net/~named-data/+archive/ubuntu/ppa):

    * `ndn-cxx-dev`
    * `nfd`
    * `nlsr`
    * `ndn-tools`

3.  clone **mnndn** repository; no installation is necessary

## Verification

1.  copy `examples/minimal_ping.py` from **mnndn** to anywhere on your system
2.  execute `sudo PYTHONPATH=/where/is/mnndn python ./minimal_ping.py`
3.  when the CLI starts, try `h1 ndnping /h2` and `h2 ndnping /h1`
