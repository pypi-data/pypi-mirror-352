import datetime
import pytz


class ZeitzonoCity:
    """
    a city object

    """

    def __init__(self, name, country, admin1, admin2, tz):
        self.name = name
        self.country = country
        self.admin1 = admin1
        self.admin2 = admin2
        self.tz = tz

    def get_tz(self):
        return self.tz

    def utc_offset(self):
        # return this city's UTC offset in seconds
        #
        # (assumes given time right now, so takes DST into consideration)
        #
        #
        timenow_tz = datetime.datetime.now(tz=pytz.timezone(self.tz))
        utcoffset_td = timenow_tz.utcoffset()
        return utcoffset_td.total_seconds()

    def _tolist(self):
        # some places like 'UTC' don't have an admin1
        if not self.admin1:
            return [self.name, self.country]

        # many places (eg. in China) don't have an admin2
        if not self.admin2:
            return [self.name, self.country, self.admin1]

        return [self.name, self.country, self.admin1, self.admin2]

    def __repr__(self):
        return str(self._tolist())

    def __str__(self):
        return str(" - ".join(self._tolist()))
