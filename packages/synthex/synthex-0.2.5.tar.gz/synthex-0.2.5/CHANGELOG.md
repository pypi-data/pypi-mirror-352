## Release v0.2.5 - June 1, 2025

### Fixed

- Fixed `Pydantic` deprecation warning `PydanticDeprecatedSince20: Support for class-based `config` is deprecated, use ConfigDict instead`.
- Fixed bug causing `Synthex` to crash when an environment variable is defined which is not present in the `Config` class.

### Added

- Added `test_synthex_config_extra_env_variable_success`.

## Release v0.2.4 - May 28, 2025

### Added

- Add docstring to `CreditsAPI`

### Changed

- Updated `README.md`
- Updated docstring of `Synthex`
- Updated docstring in `APIClient`

### Fixed

- Fixed bug causing Pylance to issue a `stub file not found for synthex` warning on imports from `synthex`

## Release v0.2.3 - May 15, 2025

### Fixed

- Fixed bug preventing correct Synthex instantiation

### Added

- Added `test_synthex_config_no_env_file`

### Removed

- Removed dependency to `python-dotenv`
- Removed ambiguous API_KEY_TIER_1 environment variable, previously used solely for testing purposes
- Removed `test_generate_data_too_many_datapoints_for_user_plan`

### Changed

- Updated `README.md`

## Release v0.2.2 - May 2, 2025

### Fixed

- Fixed bug causing `Synthex` to not pick up environment variables defined in the `.env` file

## Release v0.2.1 - May 1, 2025

### Added

- Added handling of error responses with status code 422 inside `APIClient._handle_errors`
- Added `test_generate_data_too_many_datapoints_for_user_plan`
- Added fixture to simulate user being on different types of plan
- Added support for logging number of rows fetched through `JobsAPI.generate_data`, via `DEBUG_MODE`

### Changed

- Updated unit and integration tests for `JobsAPI.status` so that `JobsAPI._current_job_id` does not have to be manually set to None before the test starts, making the tests non-representative of the method's behavior
- Merged `test_generate_data_check_number_of_samples` and `test_generate_data_success`
- Removed validation on `number_of_samples` argument in `JobsAPI.generate_data` and `JobsAPI._create_job`
- Moved all config variables into a `Config` class
- Updated `README.md`

## Release v0.2.0 - April 25, 2025

### Added

- Added test to check number of datapoints correctness in output file
- Added test to check that `JobsAPI._get_job_data` does not generate more data than the job allows
- Added `JobsAPI.status`

### Changed

- Updated data fetching logic in `JobsAPI.generate_data`
- Updated `tests` folder layout
- Renamed `CreditModel` to `CreditResponseModel`
- Updated `test_generate_data_check_number_of_samples` to allow for `JobsAPI.generate_data` to generate more datapoints than
  are requested
- Modified return type of `JobsAPI.generate_data` from `SuccessResponse` to `ActionResult`
- Merged `handle_validation_errors` and `auto_validate_methods` into a single decorator
- Updated `README.md`

### Fixed

- Fixed bug causing some tests to delete the `.env` file

## Release v0.1.7 - April 13, 2025

### Fixed

- Fixed bug causing Pydantic to `raise ImportError('email-validator is not installed)`
- Fixed bug causing `JobsAPI.generate_data()` to crash when parameter `output_path` contains a file name but not a path
- Fixed bug causing `JobsAPI.generate_data()` to generate an incorrect number of datapoints

### Changed

- Updated `JobOutputType` and `JobOutputSchemaDefinition`

### Added

- Added `JobOutputFieldDatatype`