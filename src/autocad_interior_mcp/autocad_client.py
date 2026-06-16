from __future__ import annotations

import math
from array import array
from pathlib import Path
from threading import RLock
from typing import Iterable, Sequence

import pythoncom
import win32com.client

Point2D = tuple[float, float]
Point3D = tuple[float, float, float]


class AutoCADError(RuntimeError):
    """Raised when AutoCAD COM interaction fails."""


def _co_initialize() -> None:
    pythoncom.CoInitialize()


def _to_point3d(point: Sequence[float]) -> Point3D:
    if len(point) < 2:
        raise ValueError("Point must have at least x and y.")
    x = float(point[0])
    y = float(point[1])
    z = float(point[2]) if len(point) > 2 else 0.0
    return (x, y, z)


def _to_polyline_coords(points: Iterable[Sequence[float]]) -> array:
    coords = array("d")
    for point in points:
        if len(point) < 2:
            raise ValueError("Polyline point must have at least x and y.")
        coords.extend((float(point[0]), float(point[1])))
    return coords


class AutoCADClient:
    """Thin AutoCAD COM wrapper for interior layout workflows."""

    def __init__(self) -> None:
        self._app = None
        self._lock = RLock()

    @property
    def is_connected(self) -> bool:
        return self._app is not None

    def connect(self, *, visible: bool = True, start_if_needed: bool = True) -> dict:
        with self._lock:
            _co_initialize()
            if self._app is None:
                try:
                    self._app = win32com.client.GetActiveObject("AutoCAD.Application")
                except Exception:
                    if not start_if_needed:
                        raise AutoCADError("AutoCAD is not running.")
                    self._app = win32com.client.Dispatch("AutoCAD.Application")

            self._app.Visible = bool(visible)
            return {
                "connected": True,
                "visible": bool(self._app.Visible),
                "version": str(getattr(self._app, "Version", "unknown")),
            }

    @property
    def app(self):
        if self._app is None:
            raise AutoCADError("AutoCAD is not connected. Call connect first.")
        return self._app

    def get_active_document(self):
        with self._lock:
            _co_initialize()
            try:
                return self.app.ActiveDocument
            except Exception as exc:
                raise AutoCADError("No active drawing found.") from exc

    def open_document(self, path: str):
        with self._lock:
            _co_initialize()
            resolved = Path(path).expanduser().resolve()
            if not resolved.exists():
                raise FileNotFoundError(f"Drawing not found: {resolved}")
            doc = self.app.Documents.Open(str(resolved))
            return doc

    def document_info(self) -> dict:
        doc = self.get_active_document()
        return {
            "name": str(doc.Name),
            "full_name": str(doc.FullName),
            "path": str(Path(doc.Path)) if doc.Path else "",
        }

    def save_document(self, path: str | None = None) -> dict:
        with self._lock:
            _co_initialize()
            doc = self.get_active_document()
            if path:
                resolved = Path(path).expanduser().resolve()
                doc.SaveAs(str(resolved))
                return {"saved_to": str(resolved)}
            doc.Save()
            return {"saved_to": str(doc.FullName)}

    def list_layers(self) -> list[dict]:
        with self._lock:
            _co_initialize()
            doc = self.get_active_document()
            rows: list[dict] = []
            for layer in doc.Layers:
                rows.append(
                    {
                        "name": str(layer.Name),
                        "color": int(layer.color),
                        "linetype": str(layer.Linetype),
                        "is_locked": bool(layer.Lock),
                        "is_frozen": bool(layer.Freeze),
                        "is_on": bool(layer.LayerOn),
                    }
                )
            return rows

    def ensure_layer(
        self,
        name: str,
        *,
        color: int | None = None,
        linetype: str | None = None,
        lineweight: int | None = None,
    ):
        with self._lock:
            _co_initialize()
            doc = self.get_active_document()
            try:
                layer = doc.Layers.Item(name)
            except Exception:
                layer = doc.Layers.Add(name)

            if color is not None:
                layer.color = int(color)
            if linetype:
                layer.Linetype = str(linetype)
            if lineweight is not None:
                layer.Lineweight = int(lineweight)
            return layer

    def set_active_layer(self, name: str) -> dict:
        with self._lock:
            _co_initialize()
            doc = self.get_active_document()
            layer = doc.Layers.Item(name)
            doc.ActiveLayer = layer
            return {"active_layer": str(doc.ActiveLayer.Name)}

    def add_lwpolyline(
        self,
        points: Iterable[Sequence[float]],
        *,
        closed: bool = False,
        layer: str | None = None,
    ) -> dict:
        with self._lock:
            _co_initialize()
            doc = self.get_active_document()
            coords = _to_polyline_coords(points)
            if len(coords) < 4:
                raise ValueError("Polyline must include at least two points.")

            entity = doc.ModelSpace.AddLightWeightPolyline(coords)
            entity.Closed = bool(closed)
            if layer:
                entity.Layer = layer
            return {"handle": str(entity.Handle), "object_name": str(entity.ObjectName)}

    def add_line(self, start: Sequence[float], end: Sequence[float], *, layer: str | None = None) -> dict:
        with self._lock:
            _co_initialize()
            doc = self.get_active_document()
            entity = doc.ModelSpace.AddLine(_to_point3d(start), _to_point3d(end))
            if layer:
                entity.Layer = layer
            return {"handle": str(entity.Handle), "object_name": str(entity.ObjectName)}

    def add_arc(
        self,
        center: Sequence[float],
        radius: float,
        start_angle_rad: float,
        end_angle_rad: float,
        *,
        layer: str | None = None,
    ) -> dict:
        with self._lock:
            _co_initialize()
            doc = self.get_active_document()
            start = float(start_angle_rad)
            end = float(end_angle_rad)
            while end <= start:
                end += 2.0 * math.pi

            entity = doc.ModelSpace.AddArc(_to_point3d(center), float(radius), start, end)
            if layer:
                entity.Layer = layer
            return {"handle": str(entity.Handle), "object_name": str(entity.ObjectName)}

    def add_text(
        self,
        content: str,
        point: Sequence[float],
        *,
        height: float = 200.0,
        rotation_deg: float = 0.0,
        layer: str | None = None,
    ) -> dict:
        with self._lock:
            _co_initialize()
            doc = self.get_active_document()
            entity = doc.ModelSpace.AddText(str(content), _to_point3d(point), float(height))
            entity.Rotation = math.radians(float(rotation_deg))
            if layer:
                entity.Layer = layer
            return {"handle": str(entity.Handle), "object_name": str(entity.ObjectName)}

    def add_aligned_dimension(
        self,
        start: Sequence[float],
        end: Sequence[float],
        dim_line_location: Sequence[float],
        *,
        layer: str | None = None,
    ) -> dict:
        with self._lock:
            _co_initialize()
            doc = self.get_active_document()
            entity = doc.ModelSpace.AddDimAligned(
                _to_point3d(start),
                _to_point3d(end),
                _to_point3d(dim_line_location),
            )
            if layer:
                entity.Layer = layer
            return {"handle": str(entity.Handle), "object_name": str(entity.ObjectName)}

    def insert_block(
        self,
        block_name_or_path: str,
        insertion_point: Sequence[float],
        *,
        scale_x: float = 1.0,
        scale_y: float = 1.0,
        scale_z: float = 1.0,
        rotation_deg: float = 0.0,
        layer: str | None = None,
    ) -> dict:
        with self._lock:
            _co_initialize()
            doc = self.get_active_document()
            entity = doc.ModelSpace.InsertBlock(
                _to_point3d(insertion_point),
                str(block_name_or_path),
                float(scale_x),
                float(scale_y),
                float(scale_z),
                math.radians(float(rotation_deg)),
            )
            if layer:
                entity.Layer = layer
            return {"handle": str(entity.Handle), "object_name": str(entity.ObjectName)}

    def get_object_by_handle(self, handle: str):
        with self._lock:
            _co_initialize()
            doc = self.get_active_document()
            return doc.HandleToObject(str(handle))

    def hatch_from_boundary(
        self,
        boundary_handle: str,
        *,
        pattern_name: str = "SOLID",
        layer: str | None = None,
    ) -> dict:
        with self._lock:
            _co_initialize()
            doc = self.get_active_document()
            boundary = self.get_object_by_handle(boundary_handle)
            hatch = doc.ModelSpace.AddHatch(0, str(pattern_name), True)
            outer_loop = win32com.client.VARIANT(
                pythoncom.VT_ARRAY | pythoncom.VT_DISPATCH, (boundary,)
            )
            hatch.AppendOuterLoop(outer_loop)
            hatch.Evaluate()
            if layer:
                hatch.Layer = layer
            return {"handle": str(hatch.Handle), "object_name": str(hatch.ObjectName)}

    def list_blocks(self) -> list[str]:
        with self._lock:
            _co_initialize()
            doc = self.get_active_document()
            rows: list[str] = []
            for block in doc.Blocks:
                try:
                    if bool(block.IsLayout):
                        continue
                except Exception:
                    pass
                rows.append(str(block.Name))
            rows.sort()
            return rows

    def send_command(self, command: str) -> dict:
        with self._lock:
            _co_initialize()
            doc = self.get_active_document()
            payload = command.rstrip()
            if not payload:
                raise ValueError("Command cannot be empty.")
            if not payload.endswith(" "):
                payload = payload + " "
            doc.SendCommand(payload + "\n")
            return {"sent_command": payload}

    def zoom_extents(self) -> dict:
        return self.send_command("._ZOOM _E")
