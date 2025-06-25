from enum import Enum

class DropletRegion(str, Enum):
    NYC1 = "nyc1"
    NYC2 = "nyc2"
    NYC3 = "nyc3"
    AMS3 = "ams3"
    SFO2 = "sfo2"
    SFO3 = "sfo3"
    SGP1 = "sgp1"
    LON1 = "lon1"
    FRA1 = "fra1"
    TOR1 = "tor1"
    BLR1 = "blr1"
    SYD1 = "syd1"

class DropletSize(str, Enum):
    NANO = "s-1vcpu-512mb-10gb"
    MICRO = "s-1vcpu-1gb"
    SMALL = "s-1vcpu-2gb"
    MEDIUM = "s-2vcpu-2gb"
    LARGE = "s-2vcpu-4gb"
    XLARGE = "s-4vcpu-8gb"

class DropletImage(str, Enum):
    UBUNTU_24_10_X64 = "ubuntu-24-10-x64"
    UBUNTU_24_04_X64 = "ubuntu-24-04-x64"
    UBUNTU_22_04_X64 = "ubuntu-22-04-x64"
    UBUNTU_20_04_X64 = "ubuntu-20-04-x64"
    DEBIAN_11_X64 = "debian-11-x64"
    DEBIAN_12_X64 = "debian-12-x64"
