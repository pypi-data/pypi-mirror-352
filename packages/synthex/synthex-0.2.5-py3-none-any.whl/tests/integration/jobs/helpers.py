from typing import Callable, Protocol, TypeVar
import time


# Define a protocol for the status object
class HasProgress(Protocol):
    progress: float

T = TypeVar("T", bound=HasProgress)


def wait_for_job_completion(
    get_status_fn: Callable[[], T],
    check_interval: float = 5.0,
    timeout: float = 300.0
) -> T:
    """
    Polls the job status until progress reaches 1.0, or a timeout is reached.
    Args:
        get_status_fn (Callable[[], T]): A function that returns a job status object with a `progress` attribute.
        check_interval (float): Time to wait between checks (in seconds).
        timeout (float): Maximum time to wait for completion (in seconds).
    Returns:
        T: The final job status object with progress >= 1.0.
    Raises:
        TimeoutError: If the job does not complete within the timeout period.
    """
    
    start_time = time.time()
    status = get_status_fn()

    while status.progress < 1:
        if time.time() - start_time > timeout:
            raise TimeoutError("Job did not complete within the timeout period.")
        time.sleep(check_interval)
        status = get_status_fn()

    return status
