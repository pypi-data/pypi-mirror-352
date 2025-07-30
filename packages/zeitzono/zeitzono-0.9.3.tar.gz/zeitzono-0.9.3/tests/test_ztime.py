#!/usr/bin/env python

import pytest
from Zeitzono import ZeitzonoTime


@pytest.fixture
def ztime():
    ztime = ZeitzonoTime()
    errno = ztime.set_time_nlp("july 4th, 1776 at 3:33 am")
    assert errno
    return ztime


def test_check_date(ztime):
    assert ztime.time.year == 1776
    assert ztime.time.month == 7
    assert ztime.time.day == 4


def test_check_time(ztime):
    assert ztime.time.hour == 3
    assert ztime.time.minute == 33
    ztime.add_sec()
    assert ztime.time.second == 1

    ztime.zero_sec()
    ztime.zero_min()

    assert ztime.time.minute == 0
    assert ztime.time.second == 0


def test_now(ztime):
    ztime.set_time_now()
    string_time = str(ztime.time.year)

    # just fyi, this will fail after 2029-12-31
    assert string_time.startswith("202")


def test_nlp_bad_string(ztime):
    errno = ztime.set_time_nlp("random incorrect string")
    assert not errno
