'''
Test configuration
'''
from alens.pricedl.config import PriceDbConfig

# def test_config():
#     '''
#     Test if the configuration can be instantiated.
#     '''
#     cfg = PriceDbConfig()
#     assert cfg.prices_path is not None

def test_config_path():
    '''
    Test if the configuration path can be instantiated.
    '''
    cfg = PriceDbConfig()
    # The directory must exist.
    directory = cfg.config_path.parent
    assert directory is not None
    assert directory.exists()
