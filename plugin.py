"""
GeoCalc plugin entry point.

Registers a single toolbar button (run) and a Settings menu entry under the
QGIS Plugins menu. The toolbar button processes the currently selected layers
in the layer tree, dispatching by geometry type:

    Polygon → area (configurable unit)
    Line    → length (configurable unit)
    Point   → X, Y coordinates in layer CRS

Read-only layers are silently skipped.
"""

import os
import traceback

from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

from .calculator import Calculator
from .settings_dialog import (
    SettingsDialog, get_area_unit, get_length_unit,
)


PLUGIN_MENU = "&GeoCalc"


class GeoCalcPlugin:

    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)

        self.action_run = None
        self.action_settings = None

    # ─────────────────────────────────────
    # GUI LIFECYCLE
    # ─────────────────────────────────────

    def initGui(self):
        icon_path = os.path.join(self.plugin_dir, "icon.png")
        icon = QIcon(icon_path) if os.path.isfile(icon_path) else QIcon()

        # Toolbar button
        self.action_run = QAction(
            icon,
            "GeoCalc: compute geometry on selected layers",
            self.iface.mainWindow(),
        )
        self.action_run.setObjectName("geocalc_run")
        self.action_run.setToolTip(
            "Compute area / length / coordinates on selected layers"
        )
        self.action_run.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action_run)

        # Plugins menu → Settings
        self.action_settings = QAction(
            icon,
            "Settings…",
            self.iface.mainWindow(),
        )
        self.action_settings.triggered.connect(self.open_settings)
        self.iface.addPluginToMenu(PLUGIN_MENU, self.action_settings)

    def unload(self):
        if self.action_run:
            self.iface.removeToolBarIcon(self.action_run)
            self.action_run.deleteLater()
            self.action_run = None
        if self.action_settings:
            self.iface.removePluginMenu(PLUGIN_MENU, self.action_settings)
            self.action_settings.deleteLater()
            self.action_settings = None

    # ─────────────────────────────────────
    # ACTIONS
    # ─────────────────────────────────────

    def run(self):
        view = self.iface.layerTreeView()
        if not view:
            self.iface.messageBar().pushCritical(
                "GeoCalc", "Could not access the layer tree."
            )
            return

        layers = view.selectedLayers()
        if not layers:
            self.iface.messageBar().pushWarning(
                "GeoCalc", "No layers selected in the layer panel."
            )
            return

        canvas = self.iface.mapCanvas()
        canvas.setRenderFlag(False)

        try:
            calc = Calculator(
                area_unit=get_area_unit(),
                length_unit=get_length_unit(),
                log_callback=self._log,
            )
            calc.process_layers(layers)

            msg_parts = [f"{calc.processed_count} layer(s) processed"]
            if calc.skipped_count:
                msg_parts.append(f"{calc.skipped_count} skipped")
            self.iface.messageBar().pushSuccess(
                "GeoCalc", " · ".join(msg_parts)
            )

        except Exception as e:
            self.iface.messageBar().pushCritical("GeoCalc", str(e))
            traceback.print_exc()

        finally:
            canvas.setRenderFlag(True)

    def open_settings(self):
        dlg = SettingsDialog(self.iface.mainWindow())
        dlg.exec()

    # ─────────────────────────────────────
    # LOGGING
    # ─────────────────────────────────────

    def _log(self, message, level='info'):
        bar = self.iface.messageBar()
        if level == 'success':
            bar.pushSuccess("GeoCalc", message)
        elif level == 'warning':
            bar.pushWarning("GeoCalc", message)
        elif level == 'critical':
            bar.pushCritical("GeoCalc", message)
        else:
            bar.pushInfo("GeoCalc", message)
