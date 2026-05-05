"""
Settings dialog for GeoCalc.

Lets the user pick units for area and length calculations, plus the number
of decimal places for the output values. Coordinate field names are derived
automatically from the layer CRS, so they are shown as read-only information.
"""

from qgis.PyQt.QtCore import QSettings
from qgis.PyQt.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QSpinBox,
    QGroupBox, QDialogButtonBox, QPushButton,
)

from .units import (
    AREA_UNITS, LENGTH_UNITS,
    AREA_DEFAULT, LENGTH_DEFAULT,
)


SETTINGS_GROUP = "GeoCalc"
DECIMALS_DEFAULT = 2
DECIMALS_MIN = 0
DECIMALS_MAX = 10


# ─────────────────────────────────────────────
# SETTINGS GETTERS / SETTERS
# ─────────────────────────────────────────────

def get_area_unit():
    return QSettings().value(f"{SETTINGS_GROUP}/area_unit", AREA_DEFAULT, type=str)


def get_length_unit():
    return QSettings().value(f"{SETTINGS_GROUP}/length_unit", LENGTH_DEFAULT, type=str)


def get_decimals():
    value = QSettings().value(
        f"{SETTINGS_GROUP}/decimals", DECIMALS_DEFAULT, type=int
    )
    # Clamp into valid range, just in case
    return max(DECIMALS_MIN, min(DECIMALS_MAX, value))


def set_area_unit(key):
    QSettings().setValue(f"{SETTINGS_GROUP}/area_unit", key)


def set_length_unit(key):
    QSettings().setValue(f"{SETTINGS_GROUP}/length_unit", key)


def set_decimals(value):
    QSettings().setValue(f"{SETTINGS_GROUP}/decimals", int(value))


# ─────────────────────────────────────────────
# DIALOG
# ─────────────────────────────────────────────

class SettingsDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("GeoCalc Settings")
        self.setMinimumWidth(440)
        self._build_ui()
        self._load_settings()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        # Area
        gb_area = QGroupBox("Polygon area")
        a_layout = QVBoxLayout(gb_area)

        h_a = QHBoxLayout()
        h_a.addWidget(QLabel("Unit:"))
        self.cmb_area = QComboBox()
        for key, info in AREA_UNITS.items():
            self.cmb_area.addItem(info['label'], key)
        self.cmb_area.currentIndexChanged.connect(self._update_field_previews)
        h_a.addWidget(self.cmb_area, 1)
        a_layout.addLayout(h_a)

        self.lbl_area_field = QLabel()
        self.lbl_area_field.setStyleSheet("color: gray;")
        a_layout.addWidget(self.lbl_area_field)
        layout.addWidget(gb_area)

        # Length
        gb_length = QGroupBox("Line length")
        l_layout = QVBoxLayout(gb_length)

        h_l = QHBoxLayout()
        h_l.addWidget(QLabel("Unit:"))
        self.cmb_length = QComboBox()
        for key, info in LENGTH_UNITS.items():
            self.cmb_length.addItem(info['label'], key)
        self.cmb_length.currentIndexChanged.connect(self._update_field_previews)
        h_l.addWidget(self.cmb_length, 1)
        l_layout.addLayout(h_l)

        self.lbl_length_field = QLabel()
        self.lbl_length_field.setStyleSheet("color: gray;")
        l_layout.addWidget(self.lbl_length_field)
        layout.addWidget(gb_length)

        # Coordinates (informational)
        gb_coords = QGroupBox("Point coordinates")
        c_layout = QVBoxLayout(gb_coords)
        info = QLabel(
            "Coordinates are extracted in each layer's CRS.\n"
            "Field names adapt automatically:\n"
            "  • Geographic CRS → lon_dd, lat_dd\n"
            "  • Projected (meters) → x_m, y_m\n"
            "  • Projected (feet) → x_ft, y_ft"
        )
        info.setStyleSheet("color: gray;")
        c_layout.addWidget(info)
        layout.addWidget(gb_coords)

        # Decimals
        gb_decimals = QGroupBox("Output precision")
        d_layout = QHBoxLayout(gb_decimals)
        d_layout.addWidget(QLabel("Number of decimals:"))
        self.spin_decimals = QSpinBox()
        self.spin_decimals.setRange(DECIMALS_MIN, DECIMALS_MAX)
        self.spin_decimals.setSingleStep(1)
        d_layout.addWidget(self.spin_decimals)
        d_layout.addStretch()
        layout.addWidget(gb_decimals)

        # Buttons
        bb = QDialogButtonBox()
        self.btn_reset = QPushButton("Reset defaults")
        bb.addButton(self.btn_reset, QDialogButtonBox.ButtonRole.ResetRole)
        bb.addButton(QDialogButtonBox.StandardButton.Cancel)
        bb.addButton(QDialogButtonBox.StandardButton.Ok)

        self.btn_reset.clicked.connect(self._reset_defaults)
        bb.accepted.connect(self.accept)
        bb.rejected.connect(self.reject)
        layout.addWidget(bb)

    # ─────────────────────────────────────
    # STATE
    # ─────────────────────────────────────

    def _load_settings(self):
        self._select_combo(self.cmb_area, get_area_unit())
        self._select_combo(self.cmb_length, get_length_unit())
        self.spin_decimals.setValue(get_decimals())
        self._update_field_previews()

    def _reset_defaults(self):
        self._select_combo(self.cmb_area, AREA_DEFAULT)
        self._select_combo(self.cmb_length, LENGTH_DEFAULT)
        self.spin_decimals.setValue(DECIMALS_DEFAULT)

    @staticmethod
    def _select_combo(combo, key):
        idx = combo.findData(key)
        if idx != -1:
            combo.setCurrentIndex(idx)

    def _update_field_previews(self):
        area_key = self.cmb_area.currentData()
        length_key = self.cmb_length.currentData()
        if area_key:
            self.lbl_area_field.setText(
                f"Field name: {AREA_UNITS[area_key]['field']}"
            )
        if length_key:
            self.lbl_length_field.setText(
                f"Field name: {LENGTH_UNITS[length_key]['field']}"
            )

    # ─────────────────────────────────────
    # SAVE
    # ─────────────────────────────────────

    def accept(self):
        set_area_unit(self.cmb_area.currentData())
        set_length_unit(self.cmb_length.currentData())
        set_decimals(self.spin_decimals.value())
        super().accept()
