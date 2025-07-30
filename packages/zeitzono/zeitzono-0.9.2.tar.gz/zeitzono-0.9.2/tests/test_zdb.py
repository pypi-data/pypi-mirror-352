#!/usr/bin/env python

import pytest
from Zeitzono import ZeitzonoDB


@pytest.fixture
def zdb():
    zdb = ZeitzonoDB()
    return zdb


def test_zdb_search(zdb):
    zdb.db_search("new york city", limit=1)
    assert len(zdb.matches) == 1
    assert zdb.numresults == 3

    matches = []
    for i in zdb.match_cities():
        matches.append(i)
    assert len(matches) == 1
    match = matches[0]
    assert match["pop"] == 8175133


def test_zdb_random(zdb):
    zdb.random_cities(3)
    assert len(zdb.matches) == 3
    assert zdb.numresults == 3
