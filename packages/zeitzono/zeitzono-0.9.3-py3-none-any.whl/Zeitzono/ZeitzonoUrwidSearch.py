import urwid
from .ZeitzonoSearch import ZeitzonoSearch


class ZeitzonoUrwidSearch(urwid.WidgetWrap):
    _selectable = True

    def __init__(
        self, zeitzonowidgetswitcher, maincities, version, db, screen
    ):
        self.zeitzonowidgetswitcher = zeitzonowidgetswitcher
        self.bodypile = urwid.Pile([])
        self.hsearch = ZeitzonoSearch(db)
        self.maincities = maincities
        self.screen = screen
        self.results = None
        self.prompt = urwid.Edit(caption="zeitzono> ", align="left")
        prompt_attr = urwid.AttrMap(self.prompt, "search_prompt")
        self.search2pile("")

        blankline = urwid.Text("", wrap="clip")
        helpline = "? - help,  0-9: add city, Enter - add bottom city, Esc - return to main"
        helpline = urwid.Text(helpline, wrap="clip")
        helpline_attr = urwid.AttrMap(helpline, "main_helpline")
        footer = [blankline, helpline_attr, prompt_attr]
        footerpile = urwid.Pile(footer)

        htext = "zeitzono "
        htext_len = len(htext)
        zeitzono_ut = urwid.Text(htext, wrap="clip", align="right")
        zeitzono_ut_am = urwid.AttrMap(zeitzono_ut, "main_zeitzono")

        version_len = len(version)
        version_ut = urwid.Text(version, wrap="clip", align="right")
        version_ut_am = urwid.AttrMap(version_ut, "main_version")
        blank = urwid.Text("", align="right")
        versioncols = urwid.Columns(
            [
                ("weight", 99, blank),
                (htext_len, zeitzono_ut_am),
                (version_len, version_ut_am),
            ]
        )

        self.bodypilefiller = urwid.Filler(self.bodypile, valign="bottom")
        self.frame = urwid.Frame(
            self.bodypilefiller,
            header=versioncols,
            footer=footerpile,
            focus_part="footer",
        )
        urwid.connect_signal(self.prompt, "change", self.input_handler)
        super().__init__(self.frame)

    def input_handler(self, widget, newtext):
        if newtext:
            lastchar = newtext[-1]
            if lastchar == "?":
                return False
            if lastchar.isdigit():
                lastint = int(lastchar)
                num = self.results.numcities()
                if (num > 0) and (lastint + 1 <= num):
                    index = -1 - lastint
                    self.maincities.addcity(self.results.cities[index])
                    self.zeitzonowidgetswitcher.switch_widget_main()
        self.search2pile(newtext)

    def keypress(self, size, key):
        self.prompt.keypress((size[0],), key)
        if isinstance(key, str):
            if key == "ctrl g":
                self.prompt.set_edit_text("")
            if key == "?":
                self.prompt.set_edit_text("")
                self.zeitzonowidgetswitcher.switch_widget_help_search()
            if key == "enter":
                if self.results is not None:
                    if self.results.numcities() >= 1:
                        self.maincities.addcity(self.results.cities[-1])
                self.zeitzonowidgetswitcher.switch_widget_main()
            if key == "esc":
                self.results.clear()
                self.zeitzonowidgetswitcher.switch_widget_main()

    def _item2pileitem(self, item):
        options = ("weight", 1)
        pitem = (item, options)
        return pitem

    def _get_max_capacity(self):
        # this is kludgy because Urwid doesn't give us a really great way to
        # get the size of some widget
        cols, rows = self.screen.get_cols_rows()
        maxrows = rows - 6
        return maxrows

    def search2pile(self, terms):
        newlist = []

        terms = terms.strip()
        hcities = self.hsearch.search(terms, limit=self._get_max_capacity())
        numresults = hcities.numresults()

        numresults_t = urwid.Text("NUMRESULTS: ")
        numresultst_map = urwid.AttrMap(numresults_t, "numresults_str")
        numresults_num_t = urwid.Text("%s" % str(numresults))
        numresults_num_map = urwid.AttrMap(numresults_num_t, "numresults_num")
        numresultscols = urwid.Columns(
            [("pack", numresultst_map), ("pack", numresults_num_map)]
        )

        for idx, city in enumerate(hcities):
            stacknum = hcities.numcities() - idx - 1
            citys = str(city)
            if stacknum > 9:
                cityt = urwid.Text("   " + citys, wrap="clip", align="left")
            else:
                cityt = urwid.Text(
                    str(stacknum) + ": " + citys, wrap="clip", align="left"
                )
            newlist.append(cityt)
        newlist.append(urwid.Text("", align="right"))
        newlist.append(numresultscols)

        newlist = [self._item2pileitem(item) for item in newlist]

        self.bodypile.contents[:] = newlist
        self.results = hcities
