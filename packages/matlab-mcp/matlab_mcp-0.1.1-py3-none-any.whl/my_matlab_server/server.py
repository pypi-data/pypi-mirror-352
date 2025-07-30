import os
from pathlib import Path
import base64
import subprocess
import sys
from typing import Optional, Dict, Any
from mcp.server.fastmcp import FastMCP, Image, Context
import io
from contextlib import redirect_stdout


# Get MATLAB path from environment variable with default fallback
MATLAB_PATH = os.getenv('MATLAB_PATH', '/Applications/MATLAB_R2024a.app')

# Initialize FastMCP server with dependencies
mcp = FastMCP(
    "MATLAB",
    dependencies=[
        "mcp[cli]"
    ]
)

# Global variables for MATLAB engine
eng = None
MATLAB_DIR = None

def ensure_matlab_engine():
    """Ensure MATLAB engine is installed for the current Python environment."""
    try:
        import matlab.engine
        return True
    except ImportError:
        if not os.path.exists(MATLAB_PATH):
            raise RuntimeError(
                f"MATLAB installation not found at {MATLAB_PATH}. "
                "Please set MATLAB_PATH environment variable to your MATLAB installation directory."
            )
        
        # Try to install MATLAB engine
        engine_setup = Path(MATLAB_PATH) / "extern/engines/python/setup.py"
        if not engine_setup.exists():
            raise RuntimeError(
                f"MATLAB Python engine setup not found at {engine_setup}. "
                "Please verify your MATLAB installation."
            )
        
        print(f"Installing MATLAB engine from {engine_setup}...", file=sys.stderr)
        try:
            # First try to install setuptools if missing
            try:
                import setuptools
            except ImportError:
                print("Installing setuptools...", file=sys.stderr)
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "setuptools"],
                    check=True,
                    capture_output=True,
                    text=True
                )
            
            subprocess.run(
                [sys.executable, str(engine_setup), "install"],
                check=True,
                capture_output=True,
                text=True
            )
            print("MATLAB engine installed successfully.", file=sys.stderr)
            import matlab.engine
            return True
        except subprocess.CalledProcessError as e:
            error_msg = f"Failed to install MATLAB engine: {e.stderr}\n"
            if "distutils" in str(e.stderr) or "setuptools" in str(e.stderr):
                error_msg += (
                    "\nThis error is likely due to missing setuptools. Try:\n"
                    "1. Install setuptools: pip install setuptools\n"
                    "2. Or manually install MATLAB engine:\n"
                    f"   cd \"{MATLAB_PATH}\\extern\\engines\\python\"\n"
                    "   python setup.py install\n"
                )
            raise RuntimeError(error_msg)

def initialize_matlab():
    """Initialize MATLAB engine and directories."""
    global eng, MATLAB_DIR
    
    print(f"MATLAB_PATH: {MATLAB_PATH}")
    
    # Try to initialize MATLAB engine
    ensure_matlab_engine()
    import matlab.engine
    eng = matlab.engine.start_matlab()
    
    print(f"engine: {eng}")
    
    # Create a directory for MATLAB scripts if it doesn't exist
    MATLAB_DIR = Path("matlab_scripts")
    MATLAB_DIR.mkdir(exist_ok=True)

@mcp.tool()
def create_matlab_script(script_name: str, code: str) -> str:
    """Create a new MATLAB script file.
    
    Args:
        script_name: Name of the script (without .m extension)
        code: MATLAB code to save
    
    Returns:
        Path to the created script
    """
    if eng is None:
        raise RuntimeError("MATLAB engine not initialized. Please ensure MATLAB is properly installed.")
        
    if not script_name.isidentifier():
        raise ValueError("Script name must be a valid MATLAB identifier")
    
    script_path = MATLAB_DIR / f"{script_name}.m"
    with open(script_path, 'w') as f:
        f.write(code)
    
    return str(script_path)

@mcp.tool()
def create_matlab_function(function_name: str, code: str) -> str:
    """Create a new MATLAB function file.
    
    Args:
        function_name: Name of the function (without .m extension)
        code: MATLAB function code including function definition
    
    Returns:
        Path to the created function file
    """
    if eng is None:
        raise RuntimeError("MATLAB engine not initialized. Please ensure MATLAB is properly installed.")
        
    if not function_name.isidentifier():
        raise ValueError("Function name must be a valid MATLAB identifier")
    
    # Verify code starts with function definition
    if not code.strip().startswith('function'):
        raise ValueError("Code must start with function definition")
    
    function_path = MATLAB_DIR / f"{function_name}.m"
    with open(function_path, 'w') as f:
        f.write(code)
    
    return str(function_path)

@mcp.tool()
def open_matlab_editor(script_name: str) -> str:
    """Open MATLAB editor for the specified script.
    
    Args:
        script_name: Name of the script (without .m extension)
    
    Returns:
        Status message
    """
    if eng is None:
        raise RuntimeError("MATLAB engine not initialized. Please ensure MATLAB is properly installed.")
        
    script_path = MATLAB_DIR / f"{script_name}.m"
    if not script_path.exists():
        raise FileNotFoundError(f"Script {script_name}.m not found")
    
    try:
        # Open the script in MATLAB editor
        eng.edit(str(script_path), nargout=0)
        return f"Opened {script_name}.m in MATLAB editor"
    except Exception as e:
        raise RuntimeError(f"Failed to open MATLAB editor: {str(e)}")

@mcp.tool()
def execute_matlab_script(script_name: str, args: Optional[Dict[str, Any]] = None) -> dict:
    """Execute a MATLAB script and return results."""
    if eng is None:
        raise RuntimeError("MATLAB engine not initialized. Please ensure MATLAB is properly installed.")
        
    script_path = MATLAB_DIR / f"{script_name}.m"
    if not script_path.exists():
        raise FileNotFoundError(f"Script {script_name}.m not found")

    # Add script directory to MATLAB path
    eng.addpath(str(MATLAB_DIR))
    
    # Open the script in MATLAB editor before execution
    try:
        eng.edit(str(script_path), nargout=0)
    except Exception as e:
        print(f"Warning: Could not open editor: {e}", file=sys.stderr)
    
    # Clear previous figures
    eng.close('all', nargout=0)
    
    # Create a temporary file for MATLAB output
    temp_output_file = MATLAB_DIR / f"temp_output_{script_name}.txt"
    
    # Execute the script
    result = {}
    try:
        if args:
            # Convert Python types to MATLAB types
            import matlab.engine
            matlab_args = {k: matlab.double([v]) if isinstance(v, (int, float)) else v 
                         for k, v in args.items()}
            eng.workspace['args'] = matlab_args
        
        # Set up diary to capture output
        eng.eval(f"diary('{temp_output_file}')", nargout=0)
        eng.eval(script_name, nargout=0)
        eng.eval("diary off", nargout=0)
        
        # Read captured output
        if temp_output_file.exists():
            with open(temp_output_file, 'r') as f:
                printed_output = f.read().strip()
            # Clean up temp file
            os.remove(temp_output_file)
        else:
            printed_output = "No output captured"
        
        result['printed_output'] = printed_output
        
        # Rest of your code for figures and workspace variables...
        
        # Capture figures if any were generated
        figures = []
        fig_handles = eng.eval('get(groot, "Children")', nargout=1)
        if fig_handles:
            for i, fig in enumerate(fig_handles):
                # Save figure to temporary file
                temp_file = f"temp_fig_{i}.png"
                eng.eval(f"saveas(figure({i+1}), '{temp_file}')", nargout=0)
                
                # Read the file and convert to base64
                with open(temp_file, 'rb') as f:
                    img_data = f.read()
                figures.append(Image(data=img_data, format='png'))
                
                # Clean up temp file
                os.remove(temp_file)
        
        result['figures'] = figures
        
        # Get workspace variables
        var_names = eng.eval('who', nargout=1)
        for var in var_names:
            if var != 'args':  # Skip the args we passed in
                val = eng.workspace[var]
                # Clean variable name for JSON compatibility
                clean_var_name = var.strip().replace(' ', '_')       
  
                val_str = str(val)
                # Truncate long values to prevent excessive output
                max_length = 1000  # Maximum length for variable values
                if len(val_str) > max_length:
                    val_str = val_str[:max_length] + "... [truncated]"
                
                val = val_str  # Replace the original value with the string representation
                result[clean_var_name] = val
        
    except Exception as e:
        raise RuntimeError(f"MATLAB execution error: {str(e)}")
        
    return result

@mcp.tool()
def call_matlab_function(function_name: str, args: Any) -> dict:
    """Call a MATLAB function with arguments."""
    if eng is None:
        raise RuntimeError("MATLAB engine not initialized. Please ensure MATLAB is properly installed.")
        
    function_path = MATLAB_DIR / f"{function_name}.m"
    if not function_path.exists():
        raise FileNotFoundError(f"Function {function_name}.m not found")

    # Add function directory to MATLAB path
    eng.addpath(str(MATLAB_DIR))
    
    # Open the function in MATLAB editor before execution
    try:
        eng.edit(str(function_path), nargout=0)
    except Exception as e:
        print(f"Warning: Could not open editor: {e}", file=sys.stderr)
    
    # Clear previous figures
    eng.close('all', nargout=0)
    
    # Create a temporary file for MATLAB output
    temp_output_file = MATLAB_DIR / f"temp_output_{function_name}.txt"
    
    # Convert Python arguments to MATLAB types
    import matlab.engine
    matlab_args = []
    for arg in args:
        if isinstance(arg, (int, float)):
            matlab_args.append(matlab.double([arg]))
        elif isinstance(arg, list):
            matlab_args.append(matlab.double(arg))
        else:
            matlab_args.append(arg)
    
    result = {}
    try:
        # Set up diary to capture output
        eng.eval(f"diary('{temp_output_file}')", nargout=0)
        
        # Call the function
        output = getattr(eng, function_name)(*matlab_args)
        
        # Turn off diary
        eng.eval("diary off", nargout=0)
        
        # Read captured output
        if temp_output_file.exists():
            with open(temp_output_file, 'r') as f:
                printed_output = f.read().strip()
            # Clean up temp file
            os.remove(temp_output_file)
        else:
            printed_output = "No output captured"
            
        result['output'] = str(output)
        result['printed_output'] = printed_output
        
        # Capture figures - rest of your code remains the same
        figures = []
        fig_handles = eng.eval('get(groot, "Children")', nargout=1)
        if fig_handles:
            for i, fig in enumerate(fig_handles):
                # Save figure to temporary file
                temp_file = f"temp_fig_{i}.png"
                eng.eval(f"saveas(figure({i+1}), '{temp_file}')", nargout=0)
                
                # Read the file and convert to base64
                with open(temp_file, 'rb') as f:
                    img_data = f.read()
                figures.append(Image(data=img_data, format='png'))
                
                # Clean up temp file
                os.remove(temp_file)
        
        result['figures'] = figures
        
    except Exception as e:
        raise RuntimeError(f"MATLAB execution error: {str(e)}")
        
    return result

@mcp.resource("matlab://scripts/{script_name}")
def get_script_content(script_name: str) -> str:
    """Get the content of a MATLAB script.
    
    Args:
        script_name: Name of the script (without .m extension)
    
    Returns:
        Content of the MATLAB script
    """
    if MATLAB_DIR is None:
        raise RuntimeError("MATLAB engine not initialized. Please ensure MATLAB is properly installed.")
        
    script_path = MATLAB_DIR / f"{script_name}.m"
    if not script_path.exists():
        raise FileNotFoundError(f"Script {script_name}.m not found")
    
    with open(script_path) as f:
        return f.read()

def main():
    """Main entry point for the MATLAB MCP server."""
    try:
        initialize_matlab()
    except Exception as e:
        print(f"Warning: Failed to initialize MATLAB: {e}", file=sys.stderr)
        print("The server will start but MATLAB functionality will be limited.", file=sys.stderr)
        print("To fix this, ensure MATLAB is properly installed and try:", file=sys.stderr)
        print(f"  pip install setuptools", file=sys.stderr)
        print(f"  cd \"{MATLAB_PATH}\\extern\\engines\\python\"", file=sys.stderr)
        print(f"  python setup.py install", file=sys.stderr)
    
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main() 
