import lzma
import importlib
import random

DB_FILE = "data/zeitzono.db"

# if a search returns more than MAX_LIMIT_AMT results
# only return at most MAX_LIMIT_AMT
MAX_LIMIT_AMT = 100


class ZeitzonoDB:
    # search types
    SEARCH_CITY_ALL = 0  # used to search all city fields
    SEARCH_CITY_NAME = 1  # used to search city names only
    SEARCH_CADMIN = 2  # used to search against country/admin codes

    def __init__(self):
        dbfile = importlib.resources.files("Zeitzono") / DB_FILE

        # - db contains a list of dictionaries,
        #   each dictionary has the following keys:
        #
        #     name      - the name of the city (lower case)
        #     ascii     - the ascii name of the city
        #     asciil    - the ascii name of the city (lower case)
        #     alt       - alternate names for the city (lower case)
        #     cc        - the country that the city is inc
        #     ccl       - the country that the city is in (lower case)
        #     admin1    - city's admin1 code
        #     admin1l   - city's admin1 code (lower case)
        #     admin2    - city's admin2 code
        #     admin2l   - city's admin2 code (lower case)
        #     pop       - the population of the city (used for sorting)
        #     tz        - the city's timezone
        #
        # - for stuff we don't display and only search against, we store
        #   only the lower case version
        #
        # - for stuff we both display and search against, we store both
        #
        self.db = self._db_load(dbfile)

        # this is set by db_search
        # it contains the number of matches returned by a search
        self.matches = []

        # - this is set by db_search
        # - it contains the number of matches returned by a search
        # - note that count may not match len(self.matches)
        #   because we truncate at MAX_LIMIT_AMT matches
        self.numresults = 0

    def _db_load(self, dbfile):
        # the Zeitzono db is just a compressed TSV file that we open and return
        # as a list of dictionaries

        dbfh = lzma.open(dbfile, mode="rt")
        db = []

        for line in dbfh:
            db.append(self._tsv_line_2_dict(line.strip()))

        return db

    def _tsv_line_2_dict(self, tsvline):
        # given a city entry
        # return a dict that contains things we need to search or display later

        city = tsvline.strip().split("\t")
        cityd = {}

        cityd["name"] = city[0].lower()
        cityd["ascii"] = city[1]
        cityd["asciil"] = cityd["ascii"].lower()
        cityd["alt"] = city[2].lower()
        cityd["cc"] = city[3]
        cityd["ccl"] = cityd["cc"].lower()
        cityd["admin1"] = city[4]
        cityd["admin1l"] = cityd["admin1"].lower()
        cityd["admin2"] = city[5]
        cityd["admin2l"] = cityd["admin2"].lower()
        cityd["pop"] = int(city[6])
        cityd["tz"] = city[7]

        # some null admin1/admin2 listings are labeled like this,
        # so we have to null them out manually
        if cityd["admin1"] == "00":
            cityd["admin1"] = ""
            cityd["admin1l"] = ""
        if cityd["admin2"] == "00":
            cityd["admin2"] = ""
            cityd["admin2l"] = ""

        return cityd

    def _search_parser(self, search):
        # given a search string, will tokenize and return a list of tuples
        #
        #   (pattern, SEARCH_TYPE) - pattern to search for
        #                            and search type const
        #
        patterns = []
        tokens = search.strip().split()
        for tok in tokens:
            if tok.startswith(":"):
                if len(tok) > 1:
                    patterns.append((tok[1:].lower(), self.SEARCH_CADMIN))
            elif tok.startswith("'"):
                if len(tok) > 1:
                    patterns.append((tok[1:].lower(), self.SEARCH_CITY_NAME))
            else:
                patterns.append((tok.lower(), self.SEARCH_CITY_ALL))
        return patterns

    def _city_name_only_search_match(self, pattern, city):
        # return True if pattern matches city name only
        if pattern in city["name"]:
            return True
        elif pattern in city["asciil"]:
            return True
        return False

    def _city_search_match(self, pattern, city):
        # return True if pattern matches city name of altname
        if self._city_name_only_search_match(pattern, city):
            return True
        elif pattern in city["alt"]:
            return True
        return False

    def _cadmin_search_match(self, pattern, city):
        # return True if pattern matches cc or admin
        if pattern in city["ccl"]:
            return True
        elif pattern in city["admin1l"]:
            return True
        elif pattern in city["admin2l"]:
            return True
        return False

    def _sort_matches(self, matches, limit=None):
        # given a list of matches (indexes into the database)
        # return a sorted list of cities
        #
        # will always truncate to MAX_LIMIT_AMT searches
        smatches = sorted(matches, key=lambda i: self.db[i]["pop"])

        maxresults = MAX_LIMIT_AMT
        if (limit is not None) and (limit < MAX_LIMIT_AMT):
            maxresults = limit

        if (limit is not None) and (limit < MAX_LIMIT_AMT):
            maxresults = limit

        self.numresults = len(matches)

        if self.numresults > maxresults:
            smatches = smatches[-maxresults:]

        self.matches = smatches

    def db_search(self, search, limit=None):
        # will return: list, boolean
        # list contains numbers, which correspond to cities in db
        # if boolean is true, max limit was reached
        #
        # if list is empty, no cities were found

        self._reset_search()

        # tokenize search string
        patterns = self._search_parser(search)

        # need at least one city to search for
        if not patterns:
            return [], False

        matched = range(len(self.db))

        # search through with patterns
        for pattern, search_type in patterns:
            newmatched = []

            for match in matched:
                if search_type == self.SEARCH_CITY_ALL:
                    if self._city_search_match(pattern, self.db[match]):
                        newmatched.append(match)
                elif search_type == self.SEARCH_CITY_NAME:
                    if self._city_name_only_search_match(
                        pattern, self.db[match]
                    ):
                        newmatched.append(match)
                elif search_type == self.SEARCH_CADMIN:
                    if self._cadmin_search_match(pattern, self.db[match]):
                        newmatched.append(match)

            if not newmatched:
                return [], False

            matched = newmatched

        self._sort_matches(matched, limit)

    def _reset_search(self):
        self.matches = []
        self.numresults = 0

    def random_cities(self, count):
        numrand = count if count < MAX_LIMIT_AMT else MAX_LIMIT_AMT
        population = range(len(self.db))
        randmatches = random.choices(population, k=numrand)
        self._sort_matches(randmatches)

    def match_cities(self):
        # generator that prints returns matched cities
        for m in self.matches:
            yield self.db[m]
