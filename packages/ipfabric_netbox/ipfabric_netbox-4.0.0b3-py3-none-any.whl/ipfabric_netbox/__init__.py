from netbox.plugins import PluginConfig


class NetboxIPFabricConfig(PluginConfig):
    name = "ipfabric_netbox"
    verbose_name = "NetBox IP Fabric SoT Plugin"
    description = "Sync IP Fabric into NetBox"
    version = "4.0.0b3"
    base_url = "ipfabric"
    min_version = "4.2.4"


config = NetboxIPFabricConfig
