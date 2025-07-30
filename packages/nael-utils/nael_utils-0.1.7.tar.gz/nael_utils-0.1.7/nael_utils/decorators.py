from time import sleep
from typing import Callable


def retry(retries: int = 3, delay: int = 1):
    """
    Decorator to retry a function a given number of times with a delay between retries.
    """
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            for i in range(retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if i == retries - 1:
                        raise e
                    sleep(delay)
        return wrapper
    return decorator


def forever(
    delay: int = 1, 
    retries: int = 3, 
    delay_between_retries: int = 1, 
    print_info: bool = True, 
    print_error: bool = True
):
    """
    Decorator to run a function indefinitely.
    If the function raises an exception, it will be retried a given number of times with a delay between retries.
    If the function raises an exception after the retries, the exception will be raised.
    """
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            counter = 0
            retries_left = retries
            
            while True:
                try:
                    func(*args, **kwargs)
                    retries_left = retries
                except Exception as e:
                    if print_error:
                        print(f"Error: {e}")
                    if retries_left > 0:
                        retries_left -= 1
                        if print_info:
                            print(f"Retrying in {delay_between_retries} seconds... (Retries left: {retries_left})")
                        sleep(delay_between_retries)
                    else:
                        raise e
                    
                sleep(delay)
                counter += 1
                
                if print_info:
                    print(f"Function {func.__name__} has been called {counter} times.")
                
        return wrapper
    return decorator