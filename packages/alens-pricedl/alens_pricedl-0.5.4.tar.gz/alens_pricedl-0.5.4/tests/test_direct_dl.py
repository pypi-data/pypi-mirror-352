'''
Test the new logic, that downloads in memory.
'''
from alens.pricedl.direct_dl import dl_quotes
from alens.pricedl.model import SecurityFilter


def test_xetra_dl():
    '''
    EXH9
    '''
    sec_filter = SecurityFilter(None, None, None, 'EXH9')
    dl_quotes(sec_filter)

async def test_nasdaq_dl():
    '''
    OPI
    '''
    sec_filter = SecurityFilter(None, None, None, 'OPI')
    dl_quotes(sec_filter)

async def test_aud_rate():
    '''
    CURRENCY:AUD
    '''
    sec_filter = SecurityFilter(None, None, 'CURRENCY', 'AUD')
    dl_quotes(sec_filter)

async def test_aussie_stock():
    '''
    ASX:VHY
    '''
    sec_filter = SecurityFilter(None, None, 'ASX', 'VHY')
    dl_quotes(sec_filter)

async def test_vanguard():
    '''
    VANGUARD:HY
    '''
    sec_filter = SecurityFilter(None, None, 'VANGUARD', 'HY')
    dl_quotes(sec_filter)
