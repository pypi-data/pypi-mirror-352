import io
import sys

def intercept_stdout(func):
    def decorated_func(*args, **kwargs) -> str:
        orig_stdout = sys.stdout
        with io.StringIO() as buf:
            # Save the original stdout
            sys.stdout = buf
            # Run the function
            func(*args, **kwargs)
            # Restore the original stdout
            sys.stdout = orig_stdout
            # Return intercepted stdout
            return buf.getvalue()
    return decorated_func