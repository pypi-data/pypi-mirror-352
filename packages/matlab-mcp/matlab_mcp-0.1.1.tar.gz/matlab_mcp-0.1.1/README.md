# MATLAB MCP Server

A Model Context Protocol (MCP) server that provides AI assistants with the ability to execute MATLAB code, create scripts and functions, and interact with MATLAB's computational environment.

## Features

- 🔧 Create and execute MATLAB scripts and functions
- 📊 Capture MATLAB figures and visualizations
- 📝 Open MATLAB editor for script editing
- 🔍 Access workspace variables and outputs
- 🚀 Seamless integration with AI assistants via MCP

## Installation

### Using uvx (Recommended)

```bash
uvx matlab-mcp
```

### Using pip

```bash
pip install matlab-mcp
```

## Prerequisites

- MATLAB installation (R2024a or later recommended)
- Python 3.11 or later
- MATLAB Engine for Python (automatically installed if missing)

## Configuration

### Claude Desktop

Add the following to your Claude Desktop config file:

```json
{
    "mcpServers": {
        "matlab": {
            "command": "uvx",
            "args": ["matlab-mcp"],
            "env": {
                "MATLAB_PATH": "/path/to/your/matlab/installation"
            }
        }
    }
}
```

### Environment Variables

Set the `MATLAB_PATH` environment variable to your MATLAB installation directory:

- **Windows**: `C:\Program Files\MATLAB\R2024a`
- **macOS**: `/Applications/MATLAB_R2024a.app`
- **Linux**: `/usr/local/MATLAB/R2024a`

## Available Tools

- `create_matlab_script(script_name, code)` - Create a new MATLAB script
- `create_matlab_function(function_name, code)` - Create a new MATLAB function
- `execute_matlab_script(script_name, args)` - Execute a MATLAB script
- `call_matlab_function(function_name, args)` - Call a MATLAB function
- `open_matlab_editor(script_name)` - Open MATLAB editor for a script

## Example Usage

Ask your AI assistant to:

- "Create a MATLAB script that plots a sine wave"
- "Execute the MATLAB script with custom parameters"
- "Create a function to calculate the mean of an array"
- "Open the MATLAB editor to review the script"

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
