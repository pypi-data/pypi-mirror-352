import collections
import json
from .ZeitzonoCity import ZeitzonoCity
import copy


class ZeitzonoCities:
    "a city list object"

    def __init__(self, cities=None):
        if cities is None:
            self.cities = []
        else:
            self.cities = cities

        self.undo_stack = []
        self.redo_stack = []

    def save_state(self):
        city_copy = copy.copy(self.cities)
        self.undo_stack.append(city_copy)
        self.redo_stack = []

        if len(self.undo_stack) > 10:
            self.undo_stack.pop(0)

    def undo(self):
        if len(self.undo_stack) > 0:
            old_state = self.undo_stack.pop()
            self.redo_stack.append(self.cities)
            self.cities = old_state

    def redo(self):
        if len(self.redo_stack) > 0:
            new_state = self.redo_stack.pop()
            self.undo_stack.append(self.cities)
            self.cities = new_state

    def numcities(self):
        return len(self.cities)

    def isempty(self):
        return self.numcities() == 0

    def addcity(self, city):
        self.save_state()
        self.cities.insert(0, city)

    def addcities(self, hcities):
        self.save_state()
        self.cities = hcities.cities + self.cities

    def clear(self):
        self.save_state()
        self.cities = []
        self.nresults = None

    def del_first(self):
        return self.del_index(0)

    def del_last(self):
        self.save_state()
        if self.cities:
            return self.cities.pop()

    def del_index(self, index):
        self.save_state()
        if self.cities:
            return self.cities.pop(index)

    def _rotate(self, n):
        if self.cities:
            self.save_state()
            deck = collections.deque(self.cities)
            deck.rotate(n)
            self.cities = list(deck)

    def rotate_right(self):
        self._rotate(1)

    def rotate_left(self):
        self._rotate(-1)

    def roll_4(self):
        if self.numcities() >= 4:
            self.save_state()
            city1 = self.del_first()
            city2 = self.del_first()
            city3 = self.del_first()
            city4 = self.del_first()

            self.addcity(city1)
            self.addcity(city4)
            self.addcity(city3)
            self.addcity(city2)

    def roll_3(self):
        if self.numcities() >= 3:
            self.save_state()
            city1 = self.del_first()
            city2 = self.del_first()
            city3 = self.del_first()
            self.addcity(city1)
            self.addcity(city3)
            self.addcity(city2)

    def roll_2(self):
        if self.numcities() >= 2:
            self.save_state()
            city1 = self.del_first()
            city2 = self.del_first()
            self.addcity(city1)
            self.addcity(city2)

    def sort_utc_offset(self, reverse=False):
        self.save_state()
        self.cities.sort(
            key=lambda city: city.utc_offset(), reverse=not reverse
        )

    def __iter__(self):
        return iter(self.cities)

    def _hcity_to_dict(self, c):
        # used by self.toJSON() to serialize
        return c.__dict__

    def toJSON(self, filehandle):
        return json.dump(
            self.cities, filehandle, default=self._hcity_to_dict, indent=4
        )

    def fromJSON(self, filehandle):
        string_cities = json.load(filehandle)
        self.cities = []
        for sc in string_cities:
            hc = ZeitzonoCity(**sc)
            self.cities.append(hc)


class ZeitzonoCitySearch(ZeitzonoCities):
    "this is basically ZeitzonoCities with search results"

    def __init__(self, cities=None, results=0):
        super().__init__(cities=cities)

        self.results = results

    def numresults(self):
        return self.results

    def clear(self):
        super.clear()
        self.results = 0
