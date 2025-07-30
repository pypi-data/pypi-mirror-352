import os
# Decorator to create directory and remove it after test

def set_and_clean_test_dir(dir_path: str):
    def inner_decorator_wo_arugments(func):
        def wrapper(*args, **kwargs):
            # Create directory
            os.makedirs(dir_path, exist_ok=True)
            # Run test
            func(*args, **kwargs)
            # Remove directory
            os.removedirs(dir_path)
        return wrapper
    return inner_decorator_wo_arugments