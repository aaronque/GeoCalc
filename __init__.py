def classFactory(iface):
    from .plugin import GeoCalcPlugin
    return GeoCalcPlugin(iface)
