"""
Core calculation logic for GeoCalc.

Routes each layer to the appropriate calculation based on its geometry type,
performs ellipsoidal measurements via QgsDistanceArea, and writes the result
to a new (or overwritten) field on the layer.
"""

from qgis.core import (
    QgsField, QgsWkbTypes, QgsDistanceArea, QgsProject,
    QgsVectorDataProvider,
)

from .units import AREA_UNITS, LENGTH_UNITS, coord_field_names


# ─────────────────────────────────────────────
# Qt5 / Qt6 COMPATIBILITY
# ─────────────────────────────────────────────

def _make_double_field(name):
    """
    Create a QgsField of double precision in a way that works on both
    Qt5 (QGIS 3.x) and Qt6 (QGIS 4.x).

    Qt5 expects QVariant.Double; Qt6 expects QMetaType.Double.
    We try the new API first and fall back to the old one.
    """
    try:
        from qgis.PyQt.QtCore import QMetaType
        field = QgsField(name, QMetaType.Type.Double)
    except (ImportError, AttributeError, TypeError):
        from qgis.PyQt.QtCore import QVariant
        field = QgsField(name, QVariant.Double)

    field.setTypeName("double precision")  # important for PostGIS
    field.setLength(20)
    field.setPrecision(6)
    return field


# ─────────────────────────────────────────────
# CALCULATOR CLASS
# ─────────────────────────────────────────────

class Calculator:
    """
    Process a list of vector layers and compute geometric attributes.

    Parameters
    ----------
    area_unit : str
        Key from AREA_UNITS (e.g. 'ha', 'm2').
    length_unit : str
        Key from LENGTH_UNITS (e.g. 'km', 'm').
    log_callback : callable, optional
        Function(message: str, level: str) called for each layer processed.
        level is one of 'info', 'success', 'warning', 'critical'.
    """

    def __init__(self, area_unit, length_unit, log_callback=None):
        self.area_unit = area_unit
        self.length_unit = length_unit
        self.log = log_callback or (lambda msg, level='info': None)

        self.processed_count = 0
        self.skipped_count = 0

    # ─────────────────────────────────────
    # ENTRY POINT
    # ─────────────────────────────────────

    def process_layers(self, layers):
        """Process all given layers, dispatching by geometry type."""
        for layer in layers:
            try:
                if not self._is_editable(layer):
                    self.skipped_count += 1
                    continue

                geom_type = layer.geometryType()

                if geom_type == QgsWkbTypes.PolygonGeometry:
                    self._process_area(layer)
                elif geom_type == QgsWkbTypes.LineGeometry:
                    self._process_length(layer)
                elif geom_type == QgsWkbTypes.PointGeometry:
                    self._process_coordinates(layer)
                else:
                    self.skipped_count += 1

            except Exception as e:
                self.log(f"Error processing '{layer.name()}': {e}", 'critical')
                self.skipped_count += 1

    # ─────────────────────────────────────
    # CHECKS
    # ─────────────────────────────────────

    @staticmethod
    def _is_editable(layer):
        """True if the layer's provider supports adding and changing attributes."""
        if not layer or not layer.dataProvider():
            return False
        caps = layer.dataProvider().capabilities()
        needed = (
            QgsVectorDataProvider.AddAttributes |
            QgsVectorDataProvider.ChangeAttributeValues |
            QgsVectorDataProvider.DeleteAttributes
        )
        return bool(caps & needed)

    # ─────────────────────────────────────
    # AREA
    # ─────────────────────────────────────

    def _process_area(self, layer):
        unit = AREA_UNITS[self.area_unit]
        field_name = unit['field']
        factor = unit['factor']

        idx = self._reset_field(layer, field_name)
        if idx is None:
            return

        d = self._make_distance_area(layer)

        values = {}
        for feat in layer.getFeatures():
            geom = feat.geometry()
            if not geom or geom.isEmpty():
                continue
            area_m2 = d.measureArea(geom)
            value = round(area_m2 * factor, 4)
            values[feat.id()] = {idx: value}

        if values:
            layer.dataProvider().changeAttributeValues(values)

        self.log(
            f"✓ {layer.name()}: area in {self.area_unit} → {field_name}",
            'success'
        )
        self.processed_count += 1

    # ─────────────────────────────────────
    # LENGTH
    # ─────────────────────────────────────

    def _process_length(self, layer):
        unit = LENGTH_UNITS[self.length_unit]
        field_name = unit['field']
        factor = unit['factor']

        idx = self._reset_field(layer, field_name)
        if idx is None:
            return

        d = self._make_distance_area(layer)

        values = {}
        for feat in layer.getFeatures():
            geom = feat.geometry()
            if not geom or geom.isEmpty():
                continue
            length_m = d.measureLength(geom)
            value = round(length_m * factor, 4)
            values[feat.id()] = {idx: value}

        if values:
            layer.dataProvider().changeAttributeValues(values)

        self.log(
            f"✓ {layer.name()}: length in {self.length_unit} → {field_name}",
            'success'
        )
        self.processed_count += 1

    # ─────────────────────────────────────
    # COORDINATES (POINTS)
    # ─────────────────────────────────────

    def _process_coordinates(self, layer):
        x_field, y_field = coord_field_names(layer.crs())

        idx_x = self._reset_field(layer, x_field)
        idx_y = self._reset_field(layer, y_field)
        if idx_x is None or idx_y is None:
            return

        values = {}
        for feat in layer.getFeatures():
            geom = feat.geometry()
            if not geom or geom.isEmpty():
                continue

            # Handle both single and multi-point geometries
            if geom.isMultipart():
                points = geom.asMultiPoint()
                if not points:
                    continue
                pt = points[0]  # use the first point for multi-point features
            else:
                pt = geom.asPoint()

            values[feat.id()] = {
                idx_x: round(pt.x(), 6),
                idx_y: round(pt.y(), 6),
            }

        if values:
            layer.dataProvider().changeAttributeValues(values)

        self.log(
            f"✓ {layer.name()}: coordinates → {x_field}, {y_field}",
            'success'
        )
        self.processed_count += 1

    # ─────────────────────────────────────
    # FIELD MANAGEMENT
    # ─────────────────────────────────────

    @staticmethod
    def _reset_field(layer, field_name):
        """
        Drop the field if it exists, then create it as double precision.
        Returns the new field index, or None on failure.
        """
        prov = layer.dataProvider()

        # Drop existing field if present
        idx = layer.fields().indexFromName(field_name)
        if idx != -1:
            prov.deleteAttributes([idx])
            layer.updateFields()

        # Create the field (Qt5/Qt6 compatible)
        field = _make_double_field(field_name)

        if not prov.addAttributes([field]):
            return None

        layer.updateFields()
        new_idx = layer.fields().indexFromName(field_name)
        return new_idx if new_idx != -1 else None

    @staticmethod
    def _make_distance_area(layer):
        """Return a QgsDistanceArea configured with the project ellipsoid."""
        d = QgsDistanceArea()
        d.setSourceCrs(layer.crs(), QgsProject.instance().transformContext())
        ellipsoid = QgsProject.instance().ellipsoid()
        if ellipsoid and ellipsoid != 'NONE':
            d.setEllipsoid(ellipsoid)
        return d