'''
Tests for yfinance downloader.
'''
import alens.pricedl.quotes.yfinance_downloader as dl


def test_vanguard():
    '''test downloading vanguard fund prices from yahoo finance'''
    symbol = 'VAN0104AU.AX'
    result = dl.show_info(symbol)

    assert result is not None

