'''
Test Yahoo Finance API
'''

from alens.pricedl.model import SecuritySymbol
from alens.pricedl.quotes.yahoo_finance_downloader import YahooFinanceDownloader


def test_dl():
    '''
    Test download.
    '''
    dl = YahooFinanceDownloader()
    symbol = SecuritySymbol("ASX", "VHY")
    actual = dl.download(symbol, 'AUD')

    assert actual is not None
    assert actual.value > 0
    assert actual.currency == "AUD"
    assert actual.symbol.mnemonic == "VHY"
    assert actual.symbol.namespace == "ASX"
    assert actual.date is not None
