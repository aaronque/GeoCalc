"""
Unit definitions and conversion factors for GeoCalc.

All calculations are performed in SI base units (square meters for areas,
meters for lengths) using QgsDistanceArea with the project ellipsoid, and
then converted to the user-selected output unit.
"""

# ─────────────────────────────────────────────
# AREA UNITS
# ─────────────────────────────────────────────

AREA_UNITS = {
    'm2':  {'label': 'square meters (m²)',     'factor': 1.0,                'field': 'area_m2'},
    'ha':  {'label': 'hectares (ha)',          'factor': 1.0 / 10000.0,      'field': 'area_ha'},
    'km2': {'label': 'square kilometers (km²)', 'factor': 1.0 / 1_000_000.0, 'field': 'area_km2'},
    'ft2': {'label': 'square feet (ft²)',      'factor': 10.7639104167,      'field': 'area_ft2'},
    'ac':  {'label': 'acres (ac)',             'factor': 1.0 / 4046.8564224, 'field': 'area_ac'},
    'mi2': {'label': 'square miles (mi²)',     'factor': 1.0 / 2_589_988.110336, 'field': 'area_mi2'},
}

AREA_DEFAULT = 'ha'


# ─────────────────────────────────────────────
# LENGTH UNITS
# ─────────────────────────────────────────────

LENGTH_UNITS = {
    'm':  {'label': 'meters (m)',      'factor': 1.0,           'field': 'length_m'},
    'km': {'label': 'kilometers (km)', 'factor': 1.0 / 1000.0,  'field': 'length_km'},
    'ft': {'label': 'feet (ft)',       'factor': 3.28083989501, 'field': 'length_ft'},
    'yd': {'label': 'yards (yd)',      'factor': 1.09361329834, 'field': 'length_yd'},
    'mi': {'label': 'miles (mi)',      'factor': 1.0 / 1609.344, 'field': 'length_mi'},
}

LENGTH_DEFAULT = 'km'


# ─────────────────────────────────────────────
# COORDINATE FIELD NAMES
# ─────────────────────────────────────────────

def coord_field_names(crs):
    """
    Return (x_field, y_field) names based on the CRS units.

    - Geographic CRS (degrees) → lon_dd, lat_dd
    - Projected CRS in meters  → x_m, y_m
    - Projected CRS in feet    → x_ft, y_ft
    - Anything else            → x, y
    """
    if crs.isGeographic():
        return ('lon_dd', 'lat_dd')

    # Projected CRS: inspect map units
    from qgis.core import QgsUnitTypes
    units = crs.mapUnits()

    if units == QgsUnitTypes.DistanceMeters:
        return ('x_m', 'y_m')
    if units == QgsUnitTypes.DistanceFeet:
        return ('x_ft', 'y_ft')
    if units == QgsUnitTypes.DistanceKilometers:
        return ('x_km', 'y_km')
    if units == QgsUnitTypes.DistanceMiles:
        return ('x_mi', 'y_mi')
    if units == QgsUnitTypes.DistanceYards:
        return ('x_yd', 'y_yd')
    if units == QgsUnitTypes.DistanceNauticalMiles:
        return ('x_nmi', 'y_nmi')

    return ('x', 'y')
