# GeoCalc

A minimalist QGIS plugin for one-click geometric calculations on selected layers. Computes **area** for polygons, **length** for lines, and **X/Y coordinates** for points — all from a single toolbar button, with configurable units.

No external dependencies. No bloat. One button, one click.

## Why another one?

The QGIS field calculator is powerful but verbose: every time you want to add an area or length field you have to open it, write the expression, pick a name, choose a type… GeoCalc removes all that friction. Select your layers, click the button, and the right field appears in each one — adapted to its geometry type.

## Features

- **One smart button:** detects each layer's geometry type and applies the correct calculation:
  - Polygons → area
  - Lines → length
  - Points → X / Y coordinates
- **Configurable units** for areas (m², ha, km², ft², ac, mi²) and lengths (m, km, ft, yd, mi).
- **Ellipsoidal calculations** using the project ellipsoid: results are correct in real-world units regardless of the layer CRS, including geographic CRS like EPSG:4326.
- **Coordinate field names adapt to the layer CRS:**
  - Geographic → `lon_dd`, `lat_dd`
  - Projected (meters) → `x_m`, `y_m`
  - Projected (feet) → `x_ft`, `y_ft`
- **Settings persisted** across sessions via `QSettings`.
- **Multi-layer support:** processes all selected layers at once.
- **Read-only layers are silently skipped.**

## Installation

### From the QGIS Plugin Repository


Install it from **Plugins → Manage and Install Plugins → All**, search for "GeoCalc".

### Manual installation

1. Download or clone this repository.
2. Copy the `GeoCalc` folder into your QGIS plugin directory:
   - **Linux:** `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/`
   - **Windows:** `%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\`
   - **macOS:** `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/`
3. Restart QGIS (or reload plugins).
4. Enable **GeoCalc** under **Plugins → Manage and Install Plugins → Installed**.

## Usage

1. Select one or more layers in the layer panel.
2. Click the **GeoCalc** button on the toolbar.
3. The plugin processes each layer according to its geometry type and adds (or overwrites) the corresponding fields.

To change units, go to **Plugins → GeoCalc → Settings…**.

### Field naming

| Geometry | Default unit | Field name |
|----------|--------------|------------|
| Polygon  | hectares     | `area_ha`  |
| Line     | kilometers   | `length_km`|
| Point    | (CRS units)  | `x_m`, `y_m` (or `lon_dd`, `lat_dd`) |

Field names automatically adapt when you change the unit in Settings.

## Compatibility

- QGIS 3.22 or newer.
- Compatible with both **Qt5** (QGIS 3.x) and **Qt6** (QGIS 4.x). All Qt imports go through `qgis.PyQt`.

## Limitations

- The plugin modifies layers in place. If a layer's data provider does not support adding/changing attributes (e.g. WMS, read-only services), the layer is silently skipped.
- Multipart point features use the first vertex for the X/Y coordinate calculation.

## Contributing

Bug reports and feature requests are welcome on the [issue tracker](https://github.com/aaronque/GeoCalc/issues). Pull requests are welcome too.

## License

GeoCalc is released under the GNU General Public License v3. See the [LICENSE](LICENSE) file for details.

## Author

Created by [Aarón Quesada](https://github.com/aaronque) at ISLAYA Consultoría Ambiental.
