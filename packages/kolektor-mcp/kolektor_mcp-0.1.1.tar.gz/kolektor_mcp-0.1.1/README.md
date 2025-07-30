# Kolektor MCP

Secure IFC processing MCP server for Claude Desktop.

## Installation

```bash
pip install kolektor-mcp
```

Or with uvx:

```bash
uvx kolektor-mcp
```

## Claude Desktop Configuration

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "kolektor-mcp": {
      "command": "uvx",
      "args": ["kolektor-mcp"]
    }
  }
}
```

## Available Tools

- **load_ifc_file**: Load an IFC file for analysis
- **query_elements**: Query elements by type and properties
- **extract_properties**: Extract properties from IFC elements
- **get_spatial_structure**: Analyze the spatial hierarchy
- **analyze_systems**: Analyze MEP systems
- **export_data**: Export data in various formats (JSON, CSV, Excel)

## License

Proprietary - All rights reserved.
