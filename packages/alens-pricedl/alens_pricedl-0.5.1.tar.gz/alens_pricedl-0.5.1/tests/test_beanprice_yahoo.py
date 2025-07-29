"""
Tests for the bean-price Vanguard downloader
"""

# from datetime import date, datetime, timedelta, timezone

from decimal import Decimal

# import pytest
import beanprice.price
from beanprice.price import DatedPrice, PriceSource

from alens.pricedl.beanprice import yahoo


def test_dl_vhy():
    """
    Test downloading the price for VHY.
    """
    source = yahoo.Source()

    price = source.get_latest_price("ASX:VHY")

    assert price is not None
    assert price.price != Decimal(0)
    assert price.quote_currency == "AUD"


def test_dl_a2b():
    """
    Test downloading the price for A2B. The symbol is delisted.
    Handle non-existing items.
    """
    source = yahoo.Source()

    price = source.get_latest_price("ASX:A2B")

    assert price is None


def test_xetra():
    """
    Test downloading the price for XETRA
    """
    source = yahoo.Source()

    price = source.get_latest_price("XETRA:DBK")

    assert price is not None
    assert price.price != Decimal(0)
    assert price.quote_currency == "EUR"


def test_wo_namespace():
    """
    Test downloading the price for ANGL, which has no namespace.
    """
    source = yahoo.Source()

    price = source.get_latest_price("ANGL")

    assert price is not None
    assert price.price != Decimal(0)
    assert price.quote_currency == "USD"


def test_call_beanprice():
    """
    Test calling beanprice
    """
    price_source = PriceSource(yahoo, "ASX:VHY", False)
    dated_price = DatedPrice(
        base="AUD", quote="VHY", date=None, sources=[price_source]
    )
    p = beanprice.price.fetch_price(dated_price)

    assert p is not None
    assert p.amount != Decimal(0)
    assert p.currency == "AUD"
