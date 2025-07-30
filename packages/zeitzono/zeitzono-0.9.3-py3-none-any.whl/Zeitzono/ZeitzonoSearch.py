from .ZeitzonoCities import ZeitzonoCitySearch
from .ZeitzonoCity import ZeitzonoCity


class ZeitzonoSearch:
    """
    will search for city names
    returns Cities object with number of results found

    """

    def __init__(self, db):
        self.zdb = db

    def _format_db_results(self):
        cities = []
        for city in self.zdb.match_cities():
            name = city["ascii"]
            country = city["cc"]
            admin1 = city["admin1"]
            admin2 = city["admin2"]
            tz = city["tz"]
            city = ZeitzonoCity(name, country, admin1, admin2, tz)
            cities.append(city)

        return ZeitzonoCitySearch(cities=cities, results=self.zdb.numresults)

    def search(self, search, limit=None):
        if not search:
            return ZeitzonoCitySearch()

        self.zdb.db_search(search, limit)

        numresults = self.zdb.numresults

        if numresults <= 0:
            return ZeitzonoCitySearch()

        return self._format_db_results()

    def random1(self):
        self.zdb.random_cities(1)
        return self._format_db_results()

    def random10(self):
        self.zdb.random_cities(10)
        return self._format_db_results()
