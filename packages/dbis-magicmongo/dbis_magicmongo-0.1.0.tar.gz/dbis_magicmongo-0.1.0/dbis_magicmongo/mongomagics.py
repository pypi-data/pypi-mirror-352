# mongomagics.py
# Description: An IPython extension for executing MongoDB shell commands,
#              with support for persistent connections.

from IPython.core.magic import Magics, magics_class, cell_magic, line_magic
from IPython.core.magic_arguments import argument, magic_arguments, parse_argstring
import subprocess
import tempfile
import os

@magics_class
class MongoMagics(Magics):
    """
    A magic class for executing MongoDB shell commands in IPython/Jupyter.

    Provides:
    - `%%mongo` cell magic for executing scripts.
    - `%mongo_connect` line magic for setting a default connection.
    """
    # Class attributes to store the current connection details
    _current_connection_uri = None
    _current_shell_path = 'mongosh' # Default shell path

    @magic_arguments()
    @argument(
        'connection_uri',
        type=str,
        nargs='?', # Optional for querying current, required for setting
        help=("MongoDB connection URI. "
              "Example: 'mongodb://localhost:27017/mydatabase'.")
    )
    @argument(
        '--shell_path',
        type=str,
        default=None, 
        help=("Path to the MongoDB shell executable (e.g., 'mongosh' or 'mongo'). "
              "Updates the default shell path.")
    )
    @line_magic
    def mongo_connect(self, line):
        """
        Sets or updates the default MongoDB connection URI and shell path.

        Usage:
        %mongo_connect <connection_uri> [--shell_path <path_to_executable>]

        Example:
        %mongo_connect mongodb://localhost:27017/mydatabase
        %mongo_connect mongodb+srv://user:pass@cluster.mongodb.net/test_db --shell_path /usr/local/bin/mongosh
        """
        args = parse_argstring(self.mongo_connect, line)

        if not args.connection_uri:
            print("Usage: %mongo_connect <connection_uri> [--shell_path <path>]")
            if MongoMagics._current_connection_uri:
                print(f"Current connection URI: {MongoMagics._current_connection_uri}")
                print(f"Current shell path: {MongoMagics._current_shell_path}")
            else:
                print("No connection URI is currently set.")
            return

        MongoMagics._current_connection_uri = args.connection_uri
        if args.shell_path: # If --shell_path is provided, args.shell_path will be its value, otherwise None
            MongoMagics._current_shell_path = args.shell_path
        
        print(f"Default MongoDB connection URI set to: {MongoMagics._current_connection_uri}")
        print(f"Default MongoDB shell path set to: {MongoMagics._current_shell_path}")

    @magic_arguments()
    @argument(
        'connection_uri',
        type=str,
        nargs='?', # Now fully optional, will fallback to stored URI
        help=("MongoDB connection URI. "
              "Example: 'mongodb://localhost:27017/mydatabase'. "
              "If not provided, uses the last set URI.")
    )
    @argument(
        '--shell_path',
        type=str,
        default=None, # Default to None, will use class attribute if not set
        help=("Path to the MongoDB shell executable (e.g., 'mongosh' or 'mongo'). "
              "Overrides the stored shell path for this execution if provided.")
    )
    @cell_magic
    def mongo(self, line, cell):
        """
        Execute MongoDB shell script provided in the cell body.

        Usage:
        %%mongo [connection_uri] [--shell_path <path_to_executable>]
        // Your MongoDB script commands go here

        If <connection_uri> is provided, it's used for this execution and
        becomes the new default. Otherwise, the previously set default is used.
        """
        args = parse_argstring(self.mongo, line)

        exec_connection_uri = None
        # Start with the class's current shell path. This will be 'mongosh' by default
        # or whatever was last set by mongo_connect or a previous %%mongo call with a URI and --shell_path.
        exec_shell_path = MongoMagics._current_shell_path 

        if args.connection_uri:
            # A connection URI is provided in the %%mongo line
            exec_connection_uri = args.connection_uri
            MongoMagics._current_connection_uri = args.connection_uri # Update stored URI
            if args.shell_path:
                # --shell_path is also provided with the new URI
                exec_shell_path = args.shell_path
                MongoMagics._current_shell_path = args.shell_path # Update stored shell path
            # If only URI is given, exec_shell_path remains MongoMagics._current_shell_path (the one stored)
        elif MongoMagics._current_connection_uri:
            # No connection URI in %%mongo line, use the stored one
            exec_connection_uri = MongoMagics._current_connection_uri
            if args.shell_path: 
                # --shell_path is provided, override shell path for this execution only
                # Does NOT update MongoMagics._current_shell_path in this case
                exec_shell_path = args.shell_path
        else:
            # No URI in %%mongo line and no stored URI
            print("MongoDB connection URI not set.\n"
                  "Use `%mongo_connect <connection_uri>` or provide it in the `%%mongo <connection_uri>` line first.")
            return

        script_content = cell.strip()
        if not script_content:
            print("No MongoDB commands provided in the cell.")
            return

        # Ensure exec_shell_path has a valid value (it should always have one from _current_shell_path)
        if not exec_shell_path: # Should ideally not happen if _current_shell_path has a default
             exec_shell_path = 'mongosh' # Fallback, though logic above should prevent this.

        try:
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.js', encoding='utf-8') as tmp_script:
                tmp_script.write(script_content)
                tmp_script_path = tmp_script.name
        except Exception as e:
            print(f"Error creating temporary script file: {e}")
            return

        try:
            cmd = [exec_shell_path, exec_connection_uri, tmp_script_path]
            
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False
            )

            output_printed = False
            if process.stdout:
                print("--- MongoDB Shell Output ---")
                print(process.stdout.strip())
                output_printed = True

            if process.stderr:
                print("--- MongoDB Shell Info/Errors (stderr) ---")
                print(process.stderr.strip())
                output_printed = True
            
            if process.returncode != 0:
                print(f"--- MongoDB script execution failed (Return Code: {process.returncode}) ---")
                if not output_printed:
                    print("No output from shell, but an error occurred. Check shell path and connection URI.")
            elif not output_printed:
                 print("--- MongoDB script executed successfully (No output produced by script) ---")

        except FileNotFoundError:
            print(f"Error: The MongoDB shell executable '{exec_shell_path}' was not found.")
            print("Please ensure it is installed and in your system's PATH, "
                  "or specify/update the full path using the --shell_path option "
                  "with `%mongo_connect` or `%%mongo`.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        finally:
            if os.path.exists(tmp_script_path):
                os.remove(tmp_script_path)

def load_ipython_extension(ipython):
    """
    This function is called when the extension is loaded.
    It registers the magic class.
    The @magic_arguments and @argument decorators are now directly
    on the method definitions within the MongoMagics class.
    """
    ipython.register_magics(MongoMagics)

def unload_ipython_extension(ipython):
    """
    This function is called when the extension is unloaded.
    (Optional: IPython typically handles unregistration of magics from a class)
    """
    # If specific cleanup beyond what IPython.unregister_magics(MongoMagics) does
    # were needed, it would go here. For this extension, it's likely not necessary.
    pass



