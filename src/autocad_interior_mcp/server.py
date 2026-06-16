from __future__ import annotations

from threading import Lock
from typing import Literal

from mcp.server.fastmcp import FastMCP

from .autocad_client import AutoCADClient
from .interior_ops import (
    add_door_symbol,
    add_window_symbol,
    draw_room_box,
    draw_wall_segment,
    place_furniture,
    setup_interior_layers,
)

mcp = FastMCP("autocad-interior-designer")
_client_lock = Lock()
_client: AutoCADClient | None = None


def _get_client() -> AutoCADClient:
    global _client
    with _client_lock:
        if _client is None:
            _client = AutoCADClient()
        return _client


def _connected_client() -> AutoCADClient:
    client = _get_client()
    if not client.is_connected:
        client.connect(visible=True, start_if_needed=True)
    return client


@mcp.tool()
def cad_connect(visible: bool = True, start_if_needed: bool = True) -> dict:
    """Connect to AutoCAD COM application."""
    return _get_client().connect(visible=visible, start_if_needed=start_if_needed)


@mcp.tool()
def cad_document_info() -> dict:
    """Return active drawing metadata."""
    return _connected_client().document_info()


@mcp.tool()
def cad_open_drawing(path: str) -> dict:
    """Open an existing DWG drawing by absolute path."""
    doc = _connected_client().open_document(path)
    return {"name": str(doc.Name), "full_name": str(doc.FullName)}


@mcp.tool()
def cad_save_drawing(path: str | None = None) -> dict:
    """Save active drawing. Use path for SaveAs."""
    return _connected_client().save_document(path)


@mcp.tool()
def cad_list_layers() -> list[dict]:
    """List drawing layers."""
    return _connected_client().list_layers()


@mcp.tool()
def cad_setup_interior_layers(prefix: str = "A") -> dict:
    """Create standard interior-design layers."""
    return setup_interior_layers(_connected_client(), prefix=prefix)


@mcp.tool()
def cad_set_active_layer(name: str) -> dict:
    """Switch active layer."""
    return _connected_client().set_active_layer(name)


@mcp.tool()
def cad_draw_wall(
    start_x: float,
    start_y: float,
    end_x: float,
    end_y: float,
    thickness_mm: float = 240.0,
    layer: str = "A-WALL",
) -> dict:
    """Draw one wall segment as a closed wall-outline polyline."""
    return draw_wall_segment(
        _connected_client(),
        (start_x, start_y),
        (end_x, end_y),
        thickness_mm=thickness_mm,
        layer=layer,
    )


@mcp.tool()
def cad_draw_room(
    origin_x: float,
    origin_y: float,
    width_mm: float,
    depth_mm: float,
    wall_thickness_mm: float = 240.0,
    room_name: str | None = None,
    wall_layer: str = "A-WALL",
    text_layer: str = "A-TEXT",
) -> dict:
    """Draw a room box with optional inner wall boundary and room label."""
    return draw_room_box(
        _connected_client(),
        (origin_x, origin_y),
        width_mm,
        depth_mm,
        wall_thickness_mm=wall_thickness_mm,
        wall_layer=wall_layer,
        text_layer=text_layer,
        room_name=room_name,
    )


@mcp.tool()
def cad_add_door(
    wall_start_x: float,
    wall_start_y: float,
    wall_end_x: float,
    wall_end_y: float,
    offset_mm: float,
    door_width_mm: float = 900.0,
    swing: Literal["left", "right"] = "left",
    layer: str = "A-DOOR",
) -> dict:
    """Add a 2D door symbol (opening line + leaf + swing arc)."""
    return add_door_symbol(
        _connected_client(),
        (wall_start_x, wall_start_y),
        (wall_end_x, wall_end_y),
        offset_mm=offset_mm,
        door_width_mm=door_width_mm,
        swing=swing,
        layer=layer,
    )


@mcp.tool()
def cad_add_window(
    wall_start_x: float,
    wall_start_y: float,
    wall_end_x: float,
    wall_end_y: float,
    offset_mm: float,
    window_width_mm: float = 1500.0,
    marker_depth_mm: float = 120.0,
    layer: str = "A-WIND",
) -> dict:
    """Add a 2D window symbol on top of a wall baseline."""
    return add_window_symbol(
        _connected_client(),
        (wall_start_x, wall_start_y),
        (wall_end_x, wall_end_y),
        offset_mm=offset_mm,
        window_width_mm=window_width_mm,
        marker_depth_mm=marker_depth_mm,
        layer=layer,
    )


@mcp.tool()
def cad_place_furniture(
    furniture_type: str,
    insertion_x: float,
    insertion_y: float,
    rotation_deg: float = 0.0,
    block_name_or_path: str | None = None,
    layer: str = "A-FURN",
) -> dict:
    """
    Place furniture.
    - If block_name_or_path is provided: insert CAD block.
    - Otherwise: draw a proxy by built-in furniture presets.
    """
    return place_furniture(
        _connected_client(),
        furniture_type=furniture_type,
        insertion_point=(insertion_x, insertion_y, 0.0),
        rotation_deg=rotation_deg,
        block_name_or_path=block_name_or_path,
        layer=layer,
    )


@mcp.tool()
def cad_add_text(
    content: str,
    x: float,
    y: float,
    height_mm: float = 250.0,
    rotation_deg: float = 0.0,
    layer: str = "A-TEXT",
) -> dict:
    """Add a text label."""
    return _connected_client().add_text(
        content=content,
        point=(x, y, 0.0),
        height=height_mm,
        rotation_deg=rotation_deg,
        layer=layer,
    )


@mcp.tool()
def cad_add_linear_dimension(
    start_x: float,
    start_y: float,
    end_x: float,
    end_y: float,
    dim_line_x: float,
    dim_line_y: float,
    layer: str = "A-DIMS",
) -> dict:
    """Add an aligned linear dimension."""
    return _connected_client().add_aligned_dimension(
        start=(start_x, start_y, 0.0),
        end=(end_x, end_y, 0.0),
        dim_line_location=(dim_line_x, dim_line_y, 0.0),
        layer=layer,
    )


@mcp.tool()
def cad_hatch_by_boundary_handle(
    boundary_handle: str,
    pattern_name: str = "SOLID",
    layer: str = "A-HATCH",
) -> dict:
    """Create hatch from a closed boundary entity handle."""
    return _connected_client().hatch_from_boundary(
        boundary_handle=boundary_handle,
        pattern_name=pattern_name,
        layer=layer,
    )


@mcp.tool()
def cad_list_blocks() -> list[str]:
    """List block names in current drawing."""
    return _connected_client().list_blocks()


@mcp.tool()
def cad_run_command(command: str) -> dict:
    """Send raw command string to AutoCAD command line."""
    return _connected_client().send_command(command)


@mcp.tool()
def cad_zoom_extents() -> dict:
    """Zoom extents."""
    return _connected_client().zoom_extents()


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
