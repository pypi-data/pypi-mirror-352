import pytest
import os
import csv
from typing import Any
from pathlib import Path

from .helpers import wait_for_job_completion

from synthex.config import config
from synthex import Synthex


@pytest.mark.integration
def test_generate_data_success(tmp_path: Path, synthex: Synthex, generate_data_params: dict[Any, Any]):
    """
    Test the `generate_data` method of the `Synthex` class to ensure it generates
    a CSV file with the correct structure, content and number of datapoints, based on the provided schema,
    examples, requirements and number of samples parameters.
    Args:
        tmp_path (Path): The temporary path where the output file will be created.
        synthex (Synthex): An instance of the `Synthex` class used to generate data.
        generate_data_params (dict[Any, Any]): A dictionary containing the required parameters.
    """
    
    output_path = f"{tmp_path}/{generate_data_params["output_path"]}" 
    
    synthex.jobs.generate_data(
        schema_definition=generate_data_params["schema_definition"],
        examples=generate_data_params["examples"],
        requirements=generate_data_params["requirements"],
        number_of_samples=generate_data_params["number_of_samples"],
        output_type=generate_data_params["output_type"],
        output_path=output_path
    )

    # Wait for the job to complete
    wait_for_job_completion(synthex.jobs.status)
    
    # Check if the file exists.
    assert os.path.exists(output_path), "Output file was not created."

    # Verify the header of the CSV file.
    with open(output_path, mode="r") as file:
        reader = csv.reader(file)
        header = next(reader)
        expected_header = list(generate_data_params["schema_definition"].keys())
        assert header == expected_header, \
            f"CSV header does not match. Expected: {expected_header}, Found: {header}"
        # Count the number of rows in the CSV file.
        row_count = sum(1 for _ in reader)
        expected_samples = generate_data_params["number_of_samples"]
        #  Tolerance
        tolerance = 5
        # Check if the number of rows is within 5 units of the expected number of samples.
        assert row_count > expected_samples or abs(row_count - expected_samples) <= tolerance, \
            f"Number of rows in the CSV file ({row_count}) deviates from the expected number ({expected_samples}) by more than 5%."
        
       
@pytest.mark.integration
def test_no_more_datapoints_than_job_allows(
    synthex: Synthex, generate_data_params: dict[Any, Any]
):
    """
    Test to ensure that no more datapoints are generated than the job allows.
    This test creates a job with a specified number of samples and subsequently calls the private
    _get_job_data method more times than the job allows. The test checks that the number of datapoints
    generated does not exceed the specified limit. If more datapoints are generated, the test fails.
    Args:
        synthex (Synthex): The Synthex instance used to interact with the job system.
        generate_data_params (dict[Any, Any]): A dictionary containing parameters
            required to create the job, including schema definition, examples,
            requirements, and other configurations.
    """
    
    number_of_datapoints = 50
    
    # Create a job with a specific number of samples.
    new_job_id = synthex.jobs._create_job( # type: ignore
        schema_definition=generate_data_params["schema_definition"],
        examples=generate_data_params["examples"],
        requirements=generate_data_params["requirements"],
        number_of_samples=number_of_datapoints,
    )

    # Generate the maximum number of datapoints that the job allows.
    response = synthex.jobs._get_job_data(job_id=new_job_id) # type: ignore
    while response.status_code == 206:
        response = synthex.jobs._get_job_data(job_id=new_job_id) # type: ignore

    # Attempt to generate more datapoints.
    for _ in range(3):
        response = synthex.jobs._get_job_data(job_id=new_job_id) # type: ignore
        # response.data should not be None
        assert response.data is not None, "Response data is None."
        # If either the status code suggests that there is more data, or the data array
        # is not empty, then the test fails.
        if response.status_code == 206 or len(response.data) > 0:
            pytest.fail("More datapoints have been generated than the job allows.")


@pytest.mark.integration
def test_generate_data_output_type_extension_mismatch(
    tmp_path: Path, synthex: Synthex, generate_data_params: dict[Any, Any]
):
    """
    Test to ensure that, if the `output_path` and `output_type` parameters of the `generate_data` 
    method of the `Synthex` class are not consistent (e.g. output_type="csv" but output_path ends 
    in ".pdf"), the function replaces the incorrect extension with the correct one.
    Args:
        tmp_path (Path): The temporary path where the output file will be created.
        synthex (Synthex): An instance of the `Synthex` class.
        generate_data_params (dict[Any, Any]): A dictionary containing parameters
            required for the `generate_data` method.
    """

    incorrect_output_path = f"{tmp_path}/test_data/output.pdf"
    correct_output_path = f"{tmp_path}/test_data/output.{generate_data_params["output_type"]}"

    synthex.jobs.generate_data(
        schema_definition=generate_data_params["schema_definition"],
        examples=generate_data_params["examples"],
        requirements=generate_data_params["requirements"],
        number_of_samples=generate_data_params["number_of_samples"],
        output_type=generate_data_params["output_type"],
        output_path=incorrect_output_path
    )
    
    # Wait for the job to complete
    wait_for_job_completion(synthex.jobs.status)
    
    # Ensure that the file with the wrong extension was not created
    assert not os.path.exists(incorrect_output_path), "Output file was created with the wrong extension."
    # Check whether the file with the correct extension was created
    assert os.path.exists(correct_output_path), "Output file with the correct extension was not created."

    # Verify the header of the CSV file
    with open(correct_output_path, mode="r") as file:
        reader = csv.reader(file)
        header = next(reader)
        expected_header = list(generate_data_params["schema_definition"].keys())
        assert header == expected_header, \
            f"CSV header does not match. Expected: {expected_header}, Found: {header}"


@pytest.mark.integration
def test_generate_data_output_path_extensionless_file(
    tmp_path: Path, synthex: Synthex, generate_data_params: dict[Any, Any]
):
    """
    Test to ensure that, if the `output_path` parameter of the `generate_data` method of the `Synthex` class 
    specifies a file with no extension (e.g. "/output/test"), the function adds an extension that is consistent
    with the `output_type` parameter.
    Args:
        tmp_path (Path): The temporary path where the output file will be created.
        synthex (Synthex): An instance of the `Synthex` class.
        generate_data_params (dict[Any, Any]): A dictionary containing parameters
            required for the `generate_data` method.
    """
    
    extensionless_output_path = f"{tmp_path}/test_data/output"
    correct_output_path = f"{tmp_path}/test_data/output.{generate_data_params["output_type"]}"
        
    synthex.jobs.generate_data(
        schema_definition=generate_data_params["schema_definition"],
        examples=generate_data_params["examples"],
        requirements=generate_data_params["requirements"],
        number_of_samples=generate_data_params["number_of_samples"],
        output_type=generate_data_params["output_type"],
        output_path=extensionless_output_path
    )
    
    # Wait for the job to complete
    wait_for_job_completion(synthex.jobs.status)
    
    # Ensure that the extensionless file was not created
    assert not os.path.exists(extensionless_output_path), "Output file with no extension was created."
    # Check whether the file with the correct extension was created
    assert os.path.exists(correct_output_path), "Output file with the correct extension was not created."

    # Verify the header of the CSV file
    with open(correct_output_path, mode="r") as file:
        reader = csv.reader(file)
        header = next(reader)
        expected_header = list(generate_data_params["schema_definition"].keys())
        assert header == expected_header, \
            f"CSV header does not match. Expected: {expected_header}, Found: {header}"


@pytest.mark.integration
def test_generate_data_output_path_no_filename(
    tmp_path: Path, synthex: Synthex, generate_data_params: dict[Any, Any]
):
    """
    Test to ensure that, if the `output_path` parameter of the `generate_data` method of the `Synthex` class 
    specifies a path but not a file name, the function attaches the default file name with an extension that is
    consistent with the `output_type` parameter.
    Args:
        tmp_path (Path): The temporary path where the output file will be created.
        synthex (Synthex): An instance of the `Synthex` class.
        generate_data_params (dict[Any, Any]): A dictionary containing parameters
            required for the `generate_data` method.
    """
    
    output_path_with_no_filename = f"{tmp_path}/test_data/"
    correct_output_path = f"{tmp_path}/test_data/{config.OUTPUT_FILE_DEFAULT_NAME(generate_data_params["output_type"])}"
        
    synthex.jobs.generate_data(
        schema_definition=generate_data_params["schema_definition"],
        examples=generate_data_params["examples"],
        requirements=generate_data_params["requirements"],
        number_of_samples=generate_data_params["number_of_samples"],
        output_type=generate_data_params["output_type"],
        output_path=output_path_with_no_filename
    )
    
    # Wait for the job to complete
    wait_for_job_completion(synthex.jobs.status)
    
    # Check whether the file with the default name and correct extension was created
    assert os.path.exists(correct_output_path), "Output file with the correct extension was not created."

    # Verify the header of the CSV file
    with open(correct_output_path, mode="r") as file:
        reader = csv.reader(file)
        header = next(reader)
        expected_header = list(generate_data_params["schema_definition"].keys())
        assert header == expected_header, \
            f"CSV header does not match. Expected: {expected_header}, Found: {header}"