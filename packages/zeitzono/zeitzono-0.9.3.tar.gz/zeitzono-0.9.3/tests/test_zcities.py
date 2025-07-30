#!/usr/bin/env python

import pytest
from Zeitzono import ZeitzonoCity
from Zeitzono import ZeitzonoCities
from Zeitzono.ZeitzonoCities import ZeitzonoCitySearch
from hashlib import md5
import io

# -------------------------------------------------------------------------
# generic ZeitzonoCities stuff


@pytest.fixture
def zcities():
    cities = """
    Canberra,AU,ACT,,Australia/Sydney
    New Delhi,IN,,,Asia/Kolkata
    Staten Island,USA,NY,Richmond County,America/New_York
    San Diego,USA,CA,San Diego County,America/Los_Angeles
    """

    zcities = ZeitzonoCities()

    for city in cities.strip().split("\n"):
        cl = city.strip().split(",")
        zcities.addcity(ZeitzonoCity(*cl))
    return zcities


def test_zcity(zcities):
    zcity = zcities.cities[0]
    assert zcity.get_tz() == "America/Los_Angeles"
    uoff = zcity.utc_offset()
    assert isinstance(uoff, float)
    assert uoff == -25200.0


def test_zcities_isempty(zcities):
    assert not zcities.isempty()
    zcities.clear()
    assert zcities.isempty()


def test_zcities_numcities(zcities):
    assert zcities.numcities() == 4


def test_zcities_del_first(zcities):
    zcities.del_first()
    assert zcities.numcities() == 3
    assert zcities.cities[0].name == "Staten Island"


def test_zcities_del_last(zcities):
    zcities.del_last()
    assert zcities.numcities() == 3
    assert zcities.cities[0].name == "San Diego"


def test_zcities_del_index(zcities):
    assert zcities.cities[3].name == "Canberra"

    zcities.del_index(2)
    assert zcities.numcities() == 3
    assert zcities.cities[2].name == "Canberra"

    zcities.del_index(1)
    assert zcities.numcities() == 2
    assert zcities.cities[1].name == "Canberra"

    zcities.del_index(0)
    assert zcities.numcities() == 1
    assert zcities.cities[0].name == "Canberra"

    zcities.del_index(0)

    assert zcities.numcities() == 0


def test_sort_utc_offset(zcities):
    assert zcities.cities[0].name == "San Diego"
    zcities.sort_utc_offset()
    assert zcities.cities[0].name == "Canberra"
    zcities.sort_utc_offset(reverse=True)
    assert zcities.cities[0].name == "San Diego"


def test_rotate_left_right(zcities):
    assert zcities.cities[0].name == "San Diego"
    zcities.rotate_right()
    assert zcities.cities[0].name == "Canberra"
    zcities.rotate_left()
    assert zcities.cities[0].name == "San Diego"
    zcities.rotate_left()
    assert zcities.cities[0].name == "Staten Island"


def test_roll_2(zcities):
    zcities.roll_2()
    assert zcities.cities[0].name == "Staten Island"


def test_roll_3(zcities):
    zcities.roll_3()
    zcities.roll_3()
    assert zcities.cities[0].name == "New Delhi"


def test_roll_4(zcities):
    zcities.roll_4()
    zcities.roll_4()
    zcities.roll_4()
    assert zcities.cities[0].name == "Canberra"


# -------------------------------------------------------------------------
# undo/redo


def test_undo(zcities):
    zcities.del_first()
    zcities.del_first()
    zcities.del_first()
    zcities.del_first()
    assert zcities.numcities() == 0

    zcities.undo()
    assert zcities.numcities() == 1
    assert zcities.cities[0].name == "Canberra"

    zcities.undo()
    assert zcities.numcities() == 2
    assert zcities.cities[0].name == "New Delhi"

    zcities.undo()
    assert zcities.numcities() == 3
    assert zcities.cities[0].name == "Staten Island"

    zcities.undo()
    assert zcities.numcities() == 4
    assert zcities.cities[0].name == "San Diego"


def test_redo(zcities):
    zcities.del_first()
    zcities.del_first()
    zcities.del_first()
    zcities.del_first()
    assert zcities.numcities() == 0
    zcities.undo()
    zcities.undo()
    zcities.undo()
    zcities.undo()
    assert zcities.numcities() == 4

    zcities.redo()
    assert zcities.numcities() == 3
    assert zcities.cities[0].name == "Staten Island"

    zcities.redo()
    assert zcities.numcities() == 2
    assert zcities.cities[0].name == "New Delhi"

    zcities.redo()
    assert zcities.numcities() == 1
    assert zcities.cities[0].name == "Canberra"

    zcities.redo()
    assert zcities.numcities() == 0


# -------------------------------------------------------------------------
# ZeitzonoCitySearch


@pytest.fixture
def zcitysearch(zcities):
    zcitysearch = ZeitzonoCitySearch(zcities.cities, results=400)
    return zcitysearch


def test_citysearch(zcitysearch):
    assert zcitysearch.numcities() == 4
    assert zcitysearch.numresults() == 400


# -------------------------------------------------------------------------
# json stuff


@pytest.fixture(name="zjson")
def zcities_json(zcities):
    with io.StringIO() as fh:
        zcities.toJSON(fh)
        fh.seek(0)
        jsons = fh.read()
    return jsons


def test_to_json(zjson):
    m = md5()
    m.update(zjson.encode("utf-8"))
    md5sum = m.hexdigest()
    assert md5sum == "9b1388b7367811340055ec6793651e13"


def test_from_json(zjson):
    zjsonio = io.StringIO(zjson)
    zjsonio.seek(0)
    zcities = ZeitzonoCities()
    zcities.fromJSON(zjsonio)
    assert zcities.numcities() == 4
    assert zcities.cities[0].name == "San Diego"
    assert zcities.cities[3].name == "Canberra"
