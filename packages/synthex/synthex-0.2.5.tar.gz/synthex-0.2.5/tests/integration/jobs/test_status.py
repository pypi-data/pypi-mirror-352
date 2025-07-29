import pytest
from typing import Any

from synthex import Synthex
from synthex.models import JobStatusResponseModel, JobStatus
from synthex.exceptions import ValidationError


@pytest.mark.integration
def test_status(synthex: Synthex, generate_data_params: dict[Any, Any]):
    """
    Tests the `JobsAPI.status` method by starting a job and checking its status before it starts and after it completes.
    Args:
        synthex (Synthex): An instance of the Synthex system to interact with.
        generate_data_params (dict[Any, Any]): A dictionary containing parameters 
            required to create a job, including:
            - schema_definition
            - examples
            - requirements
            - number_of_samples
    """

    # Start a job
    job_id = synthex.jobs._create_job( # type: ignore
        schema_definition=generate_data_params["schema_definition"],
        examples=generate_data_params["examples"],
        requirements=generate_data_params["requirements"],
        number_of_samples=generate_data_params["number_of_samples"]
    )
    
    # Check its status: it should be ON_HOLD
    job_status = synthex.jobs.status()
        
    assert isinstance(job_status, JobStatusResponseModel)
    assert job_status.status == JobStatus.ON_HOLD
    assert job_status.progress == 0.0
    
    # Fetch all job data
    response = synthex.jobs._get_job_data(job_id=job_id) # type: ignore
    while response.status_code == 206:            
        response = synthex.jobs._get_job_data(job_id=job_id) # type: ignore
        
    # Check job status again: it should be COMPLETED
    job_status = synthex.jobs.status()
    assert isinstance(job_status, JobStatusResponseModel)
    assert job_status.status == JobStatus.COMPLETED
    assert job_status.progress == 1.0
    
    
@pytest.mark.integration
def test_status_no_job_running(short_lived_synthex: Synthex):
    """
    Tests the `JobsAPI.status` method when no job has been started yet. In this case, the method should raise a 
    ValidationError.
    Args:
        synthex (Synthex): An instance of the Synthex system to interact with.
        generate_data_params (dict[Any, Any]): A dictionary containing parameters 
            required to create a job, including:
            - schema_definition
            - examples
            - requirements
            - number_of_samples
    """
        
    # Check status without starting a job
    with pytest.raises(ValidationError):
        short_lived_synthex.jobs.status()