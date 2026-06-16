# Tool Reference

This server exposes the following MCP tools.

## Connection and Files

- `cad_connect(visible=True, start_if_needed=True)`
- `cad_document_info()`
- `cad_open_drawing(path)`
- `cad_save_drawing(path=None)`

## Layer Management

- `cad_list_layers()`
- `cad_setup_interior_layers(prefix="A")`
- `cad_set_active_layer(name)`

## Interior Geometry

- `cad_draw_wall(start_x, start_y, end_x, end_y, thickness_mm=240, layer="A-WALL")`
- `cad_draw_room(origin_x, origin_y, width_mm, depth_mm, wall_thickness_mm=240, room_name=None, wall_layer="A-WALL", text_layer="A-TEXT")`
- `cad_add_door(wall_start_x, wall_start_y, wall_end_x, wall_end_y, offset_mm, door_width_mm=900, swing="left", layer="A-DOOR")`
- `cad_add_window(wall_start_x, wall_start_y, wall_end_x, wall_end_y, offset_mm, window_width_mm=1500, marker_depth_mm=120, layer="A-WIND")`

## Furniture

- `cad_place_furniture(furniture_type, insertion_x, insertion_y, rotation_deg=0, block_name_or_path=None, layer="A-FURN")`

Proxy furniture types:

- `bed_queen`
- `sofa_3seat`
- `dining_table_6`
- `wardrobe`
- `desk`
- `coffee_table`

## Annotation and Hatch

- `cad_add_text(content, x, y, height_mm=250, rotation_deg=0, layer="A-TEXT")`
- `cad_add_linear_dimension(start_x, start_y, end_x, end_y, dim_line_x, dim_line_y, layer="A-DIMS")`
- `cad_hatch_by_boundary_handle(boundary_handle, pattern_name="SOLID", layer="A-HATCH")`

## Blocks and Commands

- `cad_list_blocks()`
- `cad_run_command(command)`
- `cad_zoom_extents()`

## Notes

- Coordinates are interpreted using the active drawing coordinate system.
- Dimension, text size, and furniture sizes are not auto-scaled to annotation scale.
- `cad_hatch_by_boundary_handle` requires a closed boundary entity handle.
