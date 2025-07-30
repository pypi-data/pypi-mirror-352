import json
import pytest
import os
from nbitk.config import Config
from nbitk.Services.Galaxy.TaxonValidator import TaxonValidator

# Location of the JSON file containing records, provided by @luuk.nolden
CSC_RECORDS_JSON = os.path.join(os.path.dirname(__file__), 'data', 'records.json')

@pytest.fixture
def galaxy_config():
    """
    Fixture to create a Galaxy configuration object.
    :return: A Config object with Galaxy settings.
    """
    config = Config()
    config.config_data = {}
    config.initialized = True
    config.set("galaxy_domain", "https://galaxy.naturalis.nl:443")
    #config.set("galaxy_api_key", "<KEY HERE>")
    config.set("log_level", "INFO")
    return config

@pytest.fixture
def records_dict():
    """
    Fixture to load records from a JSON file.
    :return: A dictionary containing records.
    """
    with open(CSC_RECORDS_JSON, 'r') as handle:
        records = json.load(handle)
    return records

# skip test if GALAXY_API_KEY is not set
@pytest.mark.skipif(
    os.environ.get('GALAXY_API_KEY') is None,
    reason="GALAXY_API_KEY environment variable not set"
)
def test_taxon_validator(galaxy_config, records_dict):
    """
    Test the TaxonValidator service client.
    """
    config = galaxy_config
    config.set("galaxy_api_key", os.environ.get('GALAXY_API_KEY'))

    # Now we instantiate the service client:
    tv = TaxonValidator(config)
    result = tv.validate_records(records_dict[0:1])
    assert result is not None, "Validation result should not be None"
