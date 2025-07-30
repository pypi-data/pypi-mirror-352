import subprocess
from typing import Optional

from quickstats import stdout

def get_glibcxx_datestamp() -> Optional[int]:
    """
    Retrieve the value of the `__GLIBCXX__` macro from the g++ preprocessor.

    Returns
    -------
    Optional[int]
        The integer value of `__GLIBCXX__` if found, or `None` if an error occurs.
    
    Raises
    ------
    RuntimeError
        If `__GLIBCXX__` value is not found in the preprocessor output.
    """
    try:
        # Define the temporary C++ program
        cpp_code = '#include <cstdio>\nint main() { printf("%d\\n", __GLIBCXX__); return 0; }'
        
        # Prepare the g++ command to preprocess the code
        cmd = ['g++', '-E', '-x', 'c++', '-']
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, 
                                stderr=subprocess.PIPE, text=True)
        
        # Run the command and capture output and error
        output, error = proc.communicate(input=cpp_code)
        
        # Check for errors in the subprocess execution
        if proc.returncode != 0:
            raise RuntimeError(f"g++ preprocessing failed: {error.strip()}")

        # Parse the output to find the __GLIBCXX__ value
        lines = output.strip().split('\n')
        for line in reversed(lines):
            if line.strip().isdigit():
                return int(line)
        
        raise RuntimeError('Could not find __GLIBCXX__ value in output')
    
    except FileNotFoundError:
        stdout.error("Error: g++ not found. Make sure you have g++ installed and available in your PATH.")
        return None
    except Exception as e:
        stdout.error(f"An unexpected error occurred: {e}")
        return None
