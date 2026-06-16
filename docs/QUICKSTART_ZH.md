# AutoCAD Interior MCP 中文快速上手

这份文档给室内设计师和 CAD 绘图同事使用，目标是 10 分钟内跑通第一张图。

## 1. 先决条件

- Windows 电脑
- 已安装 AutoCAD
- Python 3.11 及以上

## 2. 安装

```powershell
cd C:\path\to\autocad-interior-mcp
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

## 3. 配置 MCP

将以下配置加入你的 MCP 客户端配置文件（按你的实际路径修改）：

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

## 4. 典型绘图流程（推荐顺序）

1. `cad_connect`
2. `cad_open_drawing`（可选）
3. `cad_setup_interior_layers`
4. `cad_draw_room` / `cad_draw_wall`
5. `cad_add_door` / `cad_add_window`
6. `cad_place_furniture`
7. `cad_add_linear_dimension`
8. `cad_hatch_by_boundary_handle`
9. `cad_save_drawing`

## 5. 示例：先搭一个卧室

- 画房间外框：`cad_draw_room(origin_x=0, origin_y=0, width_mm=3600, depth_mm=4200, room_name="BEDROOM")`
- 加门：`cad_add_door(..., offset_mm=300, door_width_mm=900, swing="left")`
- 放床：`cad_place_furniture(furniture_type="bed_queen", insertion_x=1800, insertion_y=2100, rotation_deg=0)`
- 加标注：`cad_add_linear_dimension(...)`

## 6. 常见问题

- 连接失败：先手动打开 AutoCAD，再执行 `cad_connect`。
- 坐标看起来不对：检查图纸单位和 UCS。
- 无法填充：确保边界是闭合对象，并传入正确的 `boundary_handle`。

## 7. 建议

- 公司有标准家具块库时，优先在 `cad_place_furniture` 传 `block_name_or_path`。
- 若某个流程还没封装成 tool，可先用 `cad_run_command` 过渡。
