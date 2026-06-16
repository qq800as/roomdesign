# Contributing

Thanks for helping improve AutoCAD Interior MCP.

## Development Setup

```powershell
git clone <your-fork-url>
cd autocad-interior-mcp
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

## Local Validation

```powershell
python -m compileall src
python -c "from autocad_interior_mcp.server import mcp; print('ok')"
```

## Pull Request Guidelines

- Keep changes focused and explain why they are needed.
- Add or update docs for any user-facing behavior changes.
- Avoid breaking existing tool names unless absolutely necessary.
- If AutoCAD behavior changed, include a short reproducible flow in the PR description.

## Coding Notes

- Python 3.11+ compatible.
- Prefer small wrappers in `server.py` and keep CAD logic in `autocad_client.py` / `interior_ops.py`.
- Add comments only where intent is not obvious.
