# AutoCAD Interior MCP

An MCP server for AutoCAD that focuses on day-to-day interior design drafting workflows.

## What You Get

- Standard interior layer bootstrap (`A-WALL`, `A-DOOR`, `A-WIND`, `A-FURN`, `A-TEXT`, `A-DIMS`, `A-HATCH`)
- Fast wall and room generation
- Door and window symbol helpers
- Furniture placement with:
  - proxy geometry presets
  - real block insertion from block name/path
- Label text, aligned dimensions, hatching from closed boundaries
- Raw command passthrough for custom office workflows

## Tech Stack

- Python 3.11+
- `mcp` (FastMCP server)
- `pywin32` COM bridge
- AutoCAD desktop on Windows

## Install

```powershell
cd C:\path\to\autocad-interior-mcp
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

## Run

```powershell
autocad-interior-mcp
```

Alternative:

```powershell
python -m autocad_interior_mcp.server
```

## MCP Client Config

Use the installed entry executable in your MCP client config:

```json
{
  "mcpServers": {
    "autocad-interior": {
      "command": "C:\\path\\to\\autocad-interior-mcp\\.venv\\Scripts\\autocad-interior-mcp.exe",
      "args": []
    }
  }
}
```

A ready template is available at `examples/mcp-config.json`.

## Quick Workflow

1. `cad_connect`
2. `cad_open_drawing` (optional)
3. `cad_setup_interior_layers`
4. `cad_draw_room` and/or `cad_draw_wall`
5. `cad_add_door` and `cad_add_window`
6. `cad_place_furniture`
7. `cad_add_linear_dimension`
8. `cad_hatch_by_boundary_handle`
9. `cad_save_drawing`

## Furniture Presets (Proxy Mode)

- `bed_queen`
- `sofa_3seat`
- `dining_table_6`
- `wardrobe`
- `desk`
- `coffee_table`

To insert real office blocks, pass `block_name_or_path` to `cad_place_furniture`.

## Documentation

- Tool reference: [docs/TOOL_REFERENCE.md](docs/TOOL_REFERENCE.md)
- Chinese quickstart: [docs/QUICKSTART_ZH.md](docs/QUICKSTART_ZH.md)
- Publish guide: [docs/PUBLISH_TO_GITHUB.md](docs/PUBLISH_TO_GITHUB.md)
- Contribution guide: [CONTRIBUTING.md](CONTRIBUTING.md)

## Limitations

- Windows + local AutoCAD only (COM dependency).
- Helpers do not auto-trim wall solids after adding door/window symbols.
- Units follow your drawing settings; `*_mm` parameter names are a workflow convention.

## License

MIT. See [LICENSE](LICENSE).
