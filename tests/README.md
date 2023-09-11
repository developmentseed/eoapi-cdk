# Integration tests

Standard integration tests for a suite of deployed [eoAPI](https://github.com/developmentseed/eoAPI) services. 

## Environment

See `eoapi_tests/settings.py` that defines the required and optional environment variables. 

## Installation & Usage

```
python -m venv .testing_environment
source .testing_environment/bin/activate
pip install -e .
pytest eoapi_tests
```