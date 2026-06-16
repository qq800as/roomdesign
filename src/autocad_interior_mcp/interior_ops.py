from __future__ import annotations

import math
from typing import Sequence

from .autocad_client import AutoCADClient, Point2D

DEFAULT_LAYERS = {
    "WALL": {"name": "A-WALL", "color": 8},
    "DOOR": {"name": "A-DOOR", "color": 1},
    "WINDOW": {"name": "A-WIND", "color": 4},
    "FURNITURE": {"name": "A-FURN", "color": 3},
    "HATCH": {"name": "A-HATCH", "color": 9},
    "TEXT": {"name": "A-TEXT", "color": 2},
    "DIM": {"name": "A-DIMS", "color": 6},
}

FURNITURE_PRESET_MM = {
    "bed_queen": (1800.0, 2000.0, "BED"),
    "sofa_3seat": (2200.0, 900.0, "SOFA"),
    "dining_table_6": (1600.0, 900.0, "DINING"),
    "wardrobe": (1800.0, 600.0, "WARDROBE"),
    "desk": (1400.0, 700.0, "DESK"),
    "coffee_table": (1200.0, 600.0, "COFFEE"),
}


def _ensure_nonzero(dx: float, dy: float) -> tuple[float, float, float]:
    length = math.hypot(dx, dy)
    if length == 0:
        raise ValueError("Start and end cannot be the same point.")
    return dx, dy, length


def _normalize(dx: float, dy: float) -> tuple[float, float]:
    _, _, length = _ensure_nonzero(dx, dy)
    return dx / length, dy / length


def _rotate(point: Point2D, angle_rad: float) -> Point2D:
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    return (point[0] * cos_a - point[1] * sin_a, point[0] * sin_a + point[1] * cos_a)


def setup_interior_layers(client: AutoCADClient, *, prefix: str = "A") -> dict:
    created: list[str] = []
    for item in DEFAULT_LAYERS.values():
        layer_name = f"{prefix}-{item['name'].split('-', 1)[1]}"
        client.ensure_layer(layer_name, color=item["color"])
        created.append(layer_name)
    return {"layers": created}


def draw_wall_segment(
    client: AutoCADClient,
    start: Sequence[float],
    end: Sequence[float],
    *,
    thickness_mm: float = 240.0,
    layer: str = "A-WALL",
) -> dict:
    sx, sy = float(start[0]), float(start[1])
    ex, ey = float(end[0]), float(end[1])
    ux, uy = _normalize(ex - sx, ey - sy)
    px, py = -uy, ux
    half = float(thickness_mm) / 2.0

    p1 = (sx + px * half, sy + py * half)
    p2 = (ex + px * half, ey + py * half)
    p3 = (ex - px * half, ey - py * half)
    p4 = (sx - px * half, sy - py * half)

    poly = client.add_lwpolyline([p1, p2, p3, p4], closed=True, layer=layer)
    return {"wall_outline_handle": poly["handle"], "corners": [p1, p2, p3, p4]}


def draw_room_box(
    client: AutoCADClient,
    origin: Sequence[float],
    width_mm: float,
    depth_mm: float,
    *,
    wall_thickness_mm: float = 240.0,
    wall_layer: str = "A-WALL",
    text_layer: str = "A-TEXT",
    room_name: str | None = None,
) -> dict:
    x0, y0 = float(origin[0]), float(origin[1])
    w = float(width_mm)
    d = float(depth_mm)
    if w <= 0 or d <= 0:
        raise ValueError("Room width and depth must be > 0.")

    outer = [(x0, y0), (x0 + w, y0), (x0 + w, y0 + d), (x0, y0 + d)]
    outer_handle = client.add_lwpolyline(outer, closed=True, layer=wall_layer)["handle"]

    result = {"outer_handle": outer_handle}
    t = float(wall_thickness_mm)
    if t > 0 and w > 2 * t and d > 2 * t:
        inner = [(x0 + t, y0 + t), (x0 + w - t, y0 + t), (x0 + w - t, y0 + d - t), (x0 + t, y0 + d - t)]
        inner_handle = client.add_lwpolyline(inner, closed=True, layer=wall_layer)["handle"]
        result["inner_handle"] = inner_handle

    if room_name:
        cx = x0 + w / 2.0
        cy = y0 + d / 2.0
        label = client.add_text(room_name, (cx, cy, 0.0), height=300.0, layer=text_layer)
        result["label_handle"] = label["handle"]

    return result


def add_door_symbol(
    client: AutoCADClient,
    wall_start: Sequence[float],
    wall_end: Sequence[float],
    *,
    offset_mm: float,
    door_width_mm: float = 900.0,
    swing: str = "left",
    layer: str = "A-DOOR",
) -> dict:
    sx, sy = float(wall_start[0]), float(wall_start[1])
    ex, ey = float(wall_end[0]), float(wall_end[1])
    ux, uy = _normalize(ex - sx, ey - sy)
    px, py = -uy, ux

    offset = float(offset_mm)
    width = float(door_width_mm)
    p0 = (sx + ux * offset, sy + uy * offset)
    p1 = (p0[0] + ux * width, p0[1] + uy * width)

    swing_normalized = swing.lower().strip()
    if swing_normalized not in {"left", "right"}:
        raise ValueError("swing must be 'left' or 'right'.")

    if swing_normalized == "left":
        hinge = p0
        leaf_end = (hinge[0] + px * width, hinge[1] + py * width)
        jamb = p1
    else:
        hinge = p1
        leaf_end = (hinge[0] - px * width, hinge[1] - py * width)
        jamb = p0

    leaf_line = client.add_line((hinge[0], hinge[1], 0.0), (leaf_end[0], leaf_end[1], 0.0), layer=layer)
    opening_line = client.add_line((p0[0], p0[1], 0.0), (p1[0], p1[1], 0.0), layer=layer)

    start_angle = math.atan2(jamb[1] - hinge[1], jamb[0] - hinge[0])
    end_angle = math.atan2(leaf_end[1] - hinge[1], leaf_end[0] - hinge[0])
    arc = client.add_arc((hinge[0], hinge[1], 0.0), width, start_angle, end_angle, layer=layer)

    return {
        "leaf_handle": leaf_line["handle"],
        "opening_handle": opening_line["handle"],
        "swing_arc_handle": arc["handle"],
    }


def add_window_symbol(
    client: AutoCADClient,
    wall_start: Sequence[float],
    wall_end: Sequence[float],
    *,
    offset_mm: float,
    window_width_mm: float = 1500.0,
    marker_depth_mm: float = 120.0,
    layer: str = "A-WIND",
) -> dict:
    sx, sy = float(wall_start[0]), float(wall_start[1])
    ex, ey = float(wall_end[0]), float(wall_end[1])
    ux, uy = _normalize(ex - sx, ey - sy)
    px, py = -uy, ux

    offset = float(offset_mm)
    width = float(window_width_mm)
    depth = float(marker_depth_mm)

    p0 = (sx + ux * offset, sy + uy * offset)
    p1 = (p0[0] + ux * width, p0[1] + uy * width)

    c0 = client.add_line((p0[0], p0[1], 0.0), (p1[0], p1[1], 0.0), layer=layer)
    a0 = client.add_line(
        (p0[0] - px * depth / 2.0, p0[1] - py * depth / 2.0, 0.0),
        (p0[0] + px * depth / 2.0, p0[1] + py * depth / 2.0, 0.0),
        layer=layer,
    )
    a1 = client.add_line(
        (p1[0] - px * depth / 2.0, p1[1] - py * depth / 2.0, 0.0),
        (p1[0] + px * depth / 2.0, p1[1] + py * depth / 2.0, 0.0),
        layer=layer,
    )

    return {"window_line": c0["handle"], "marker_a": a0["handle"], "marker_b": a1["handle"]}


def draw_rotated_rect(
    client: AutoCADClient,
    center: Sequence[float],
    width_mm: float,
    depth_mm: float,
    *,
    rotation_deg: float = 0.0,
    layer: str = "A-FURN",
    label: str | None = None,
    text_layer: str = "A-TEXT",
) -> dict:
    cx, cy = float(center[0]), float(center[1])
    hw = float(width_mm) / 2.0
    hd = float(depth_mm) / 2.0
    angle = math.radians(float(rotation_deg))

    local = [(-hw, -hd), (hw, -hd), (hw, hd), (-hw, hd)]
    points: list[Point2D] = []
    for p in local:
        rx, ry = _rotate(p, angle)
        points.append((cx + rx, cy + ry))

    body = client.add_lwpolyline(points, closed=True, layer=layer)
    result = {"outline_handle": body["handle"]}
    if label:
        text = client.add_text(label, (cx, cy, 0.0), height=180.0, rotation_deg=rotation_deg, layer=text_layer)
        result["label_handle"] = text["handle"]
    return result


def place_furniture(
    client: AutoCADClient,
    *,
    furniture_type: str,
    insertion_point: Sequence[float],
    rotation_deg: float = 0.0,
    block_name_or_path: str | None = None,
    layer: str = "A-FURN",
) -> dict:
    if block_name_or_path:
        block = client.insert_block(
            block_name_or_path=block_name_or_path,
            insertion_point=insertion_point,
            rotation_deg=rotation_deg,
            layer=layer,
        )
        return {"mode": "block", "handle": block["handle"], "name": furniture_type}

    key = furniture_type.strip().lower()
    if key not in FURNITURE_PRESET_MM:
        supported = ", ".join(sorted(FURNITURE_PRESET_MM))
        raise ValueError(f"Unsupported furniture_type '{furniture_type}'. Supported: {supported}")

    width, depth, label = FURNITURE_PRESET_MM[key]
    rect = draw_rotated_rect(
        client,
        insertion_point,
        width,
        depth,
        rotation_deg=rotation_deg,
        layer=layer,
        label=label,
    )
    return {"mode": "proxy", "name": furniture_type, **rect}
