import urwid
from .ZeitzonoTime import ZeitzonoTime
from .ZeitzonoCities import ZeitzonoCities
from .ZeitzonoUrwidSearch import ZeitzonoUrwidSearch
from .ZeitzonoSearch import ZeitzonoSearch
from .ZeitzonoDB import ZeitzonoDB


class ZeitzonoUrwidMain(urwid.WidgetWrap):
    _selectable = True

    def __init__(self, loop, zeitzonowidgetswitcher, cache, version):
        self.zeitzonotime = ZeitzonoTime()
        self.zeitzonocities = ZeitzonoCities()
        self.zeitzonodb = ZeitzonoDB()
        self.footerpile = None
        self.nlp_mode = (
            False  # if set, we are parsing keyboard input differently
        )
        self.clock_mode = True  # if set, we update the base clock in realtime
        self.loop = loop  # this is needed call set_alarm_in()
        self.index_mode = False  # if set, we are picking an item in list
        self.screen = urwid.raw_display.Screen()

        # if we are caching, read HoronoCities from cache
        self.cache = cache
        if cache is not None:
            try:
                with open(self.cache) as cachefile:
                    self.zeitzonocities.fromJSON(cachefile)
            except Exception:
                pass

        self.baset = urwid.Text("", wrap="clip", align="left")
        basetmap = urwid.AttrMap(self.baset, "main_base_time")
        self.basezc = urwid.Text("", wrap="clip", align="right")
        basezcmap = urwid.AttrMap(self.basezc, "main_basezc")

        self.basezc_is_c = False
        self.basezc_city = None
        self.baset_update()
        self.basezc_update()

        htext = "zeitzono "
        htext_len = len(htext)
        zeitzono_ut = urwid.Text(htext, wrap="clip", align="right")
        zeitzono_ut_am = urwid.AttrMap(zeitzono_ut, "main_zeitzono")

        self.version = version
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

        self.bodypile = urwid.Pile(self.body_gen())

        self.bodyfill = urwid.Filler(self.bodypile, valign="bottom")
        self.zeitzonowidgetswitcher = zeitzonowidgetswitcher

        cols = urwid.Columns([basetmap, basezcmap])
        blankline = urwid.Text("", wrap="clip")

        helpline = (
            "? - help,  c - add cities, n - display current time, Q - quit"
        )
        helpline = urwid.Text(helpline, wrap="clip")
        helpline_attr = urwid.AttrMap(helpline, "main_helpline")

        self.footer = [blankline, helpline_attr, cols]
        self.footerpile = urwid.Pile(
            self.footer, focus_item=len(self.footer) - 1
        )
        self.footer_bak = [(x, ("pack", None)) for x in self.footer]

        # ---------------------------------
        # create a footer pile for nlp mode

        helpline_nlp = "enter a human-readable date/time string:"
        helpline_nlp = urwid.Text(helpline_nlp, wrap="clip", align="left")
        helpline_nlp_attr = urwid.AttrMap(helpline_nlp, "main_helpline")
        self.nlp_prompt = urwid.Edit(caption="(NLP) zeitzono> ", align="left")
        nlp_prompt_attr = urwid.AttrMap(self.nlp_prompt, "search_prompt")
        nlp_pilelist = [blankline, helpline_nlp_attr, nlp_prompt_attr]
        self.nlp_pilelist = [(x, ("pack", None)) for x in nlp_pilelist]

        # ---------------------------------

        frame = urwid.Frame(
            self.bodyfill,
            header=versioncols,
            footer=self.footerpile,
            focus_part="footer",
        )

        super().__init__(frame)

    def _list_is_max_capacity(self, fakecap=None):
        cols, rows = self.screen.get_cols_rows()
        maxrows = rows - 4
        cap = self.zeitzonocities.numcities()

        if fakecap is not None:
            cap = cap + fakecap - 1

        if cap >= maxrows:
            return True

        return False

    def time_adjust(self, key):  # noqa
        if key in "SsMmHhXxFfDdWwOoYy0":
            self.clock_mode = False
            if key in ("S"):
                self.zeitzonotime.sub_sec()
            if key in ("s"):
                self.zeitzonotime.add_sec()
            if key in ("M"):
                self.zeitzonotime.sub_min()
            if key in ("m"):
                self.zeitzonotime.add_min()
            if key in ("H"):
                self.zeitzonotime.sub_hour()
            if key in ("h"):
                self.zeitzonotime.add_hour()
            if key in ("X"):
                self.zeitzonotime.sub_qday()
            if key in ("x"):
                self.zeitzonotime.add_qday()
            if key in ("F"):
                self.zeitzonotime.sub_qhour()
            if key in ("f"):
                self.zeitzonotime.add_qhour()
            if key in ("D"):
                self.zeitzonotime.sub_day()
            if key in ("d"):
                self.zeitzonotime.add_day()
            if key in ("W"):
                self.zeitzonotime.sub_week()
            if key in ("w"):
                self.zeitzonotime.add_week()
            if key in ("O"):
                self.zeitzonotime.sub_month()
            if key in ("o"):
                self.zeitzonotime.add_month()
            if key in ("Y"):
                self.zeitzonotime.sub_year()
            if key in ("y"):
                self.zeitzonotime.add_year()
            if key in ("0"):
                self.zeitzonotime.zero_sec()
                self.zeitzonotime.zero_min()
        if key in ("n"):
            self.zeitzonotime.set_time_now()
            self.clock_mode = True
            self.zeitzonotime.clock_mode_start()
            self.clock_update(self.loop, None)
        self.body_render()
        self.baset_update()
        return True

    def keypress(self, size, key):  # noqa
        if self.index_mode:
            index = self.label2index(key)
            if index is None:
                self.index_mode_off()
                return True
            else:
                if self.index_mode_type == "zone":
                    city = self.zeitzonocities.cities[index]
                    self.basezc_is_c = True
                    self.basezc_city = city.name
                    self.zeitzonotime.set_tz(city.tz)
                    self.basezc_update()

                if self.index_mode_type == "pop":
                    self.zeitzonocities.del_index(index)

                self.index_mode_off()
                return True

        if self.nlp_mode:
            self.nlp_prompt.keypress((size[0],), key)
            if key == "enter":
                x = self.nlp_prompt.get_edit_text()

                # exit if nothing entered
                if not x.strip():
                    self.nlp_prompt.set_edit_text("")
                    self.nlp_mode = False
                    self.footerpile.contents[:] = self.footer_bak

                # try and set time
                success = self.zeitzonotime.set_time_nlp(x)

                # if it doesn't work, try again
                if not success:
                    self.nlp_prompt.set_edit_text("")
                    return

                # if it does work, set clock and exit
                self.nlp_prompt.set_edit_text("")
                self.nlp_mode = False
                self.footerpile.contents[:] = self.footer_bak
                self.body_render()
                self.baset_update()
                return True
            return
        if key.lower() in ("q"):
            # if we are caching, write HoronoCities to cache before exiting
            if self.cache is not None:
                with open(self.cache, "w") as cachefile:
                    self.zeitzonocities.toJSON(cachefile)
            raise urwid.ExitMainLoop()
        if key in ("N"):
            self.clock_mode = False
            self.nlp_mode = True
            self.footerpile.contents[:] = self.nlp_pilelist
        if key == ("?"):
            self.zeitzonowidgetswitcher.switch_widget_help_main()
        if key in ("C"):
            self.zeitzonocities.clear()
        if key in ("c") and not self._list_is_max_capacity():
            zeitzonourwidsearch = ZeitzonoUrwidSearch(
                self.zeitzonowidgetswitcher,
                self.zeitzonocities,
                self.version,
                self.zeitzonodb,
                self.screen,
            )
            self.zeitzonowidgetswitcher.set_widget(
                "search", zeitzonourwidsearch
            )
            self.zeitzonowidgetswitcher.switch_widget_search()
        if key in ("L"):
            self.zeitzonotime.set_tz_local()
            self.basezc_is_c = False
            self.basezc_update()
            return True
        if key in ("p"):
            self.zeitzonocities.del_first()
            self.body_render()
            return True
        if key in ("P"):
            if self.zeitzonocities.numcities() > 0:
                self.index_mode_on(mode="pop")
            return True
        if key in ("."):
            self.zeitzonocities.rotate_right()
            self.body_render()
            return True
        if key in (","):
            self.zeitzonocities.rotate_left()
            self.body_render()
            return True
        if key in ("/"):
            self.zeitzonocities.roll_2()
            self.body_render()
            return True
        if key in ("'"):
            self.zeitzonocities.roll_3()
            self.body_render()
            return True
        if key in (";"):
            self.zeitzonocities.roll_4()
            self.body_render()
            return True
        if key in ("]"):
            self.zeitzonocities.sort_utc_offset()
            self.body_render()
            return True
        if key in ("["):
            self.zeitzonocities.sort_utc_offset(reverse=True)
            self.body_render()
            return True
        if key in ("z"):
            if self.zeitzonocities.numcities() > 0:
                city = self.zeitzonocities.cities[0]
                self.basezc_is_c = True
                self.basezc_city = city.name
                self.zeitzonotime.set_tz(city.tz)
                self.basezc_update()
            return True
        if key in ("Z"):
            if self.zeitzonocities.numcities() > 0:
                self.index_mode_on(mode="zone")
            return True
        if key in ("u"):
            self.zeitzonocities.undo()
        if key in ("r"):
            self.zeitzonocities.redo()
        if key in ("-"):
            if self._list_is_max_capacity():
                return True
            zsearch = ZeitzonoSearch(db=self.zeitzonodb)
            rcities = zsearch.random1()
            self.zeitzonocities.addcities(rcities)
            self.body_render()
            return True
        if key in ("="):
            if self._list_is_max_capacity(fakecap=10):
                return True
            zsearch = ZeitzonoSearch(db=self.zeitzonodb)
            rcities = zsearch.random10()
            self.zeitzonocities.addcities(rcities)
            self.body_render()
            return True
        self.time_adjust(key)
        self.body_render()

    def baset_update(self):
        # If we have a terminal that is sized ~80 columns wide (eg. 80x25),
        # adding the [C] in wall clock mode will truncate part of the base
        # time.
        #
        # So to get around that awkwardness, if we are smaller than some
        # arbitrary number of columns, we don't print the "base time: " string.
        cols, _ = self.screen.get_cols_rows()
        newstr = "base time: "
        if cols < 95:
            newstr = ""

        newstr = newstr + "%s" % self.zeitzonotime.get_time_str()
        newstr = [("main_base_time", newstr)]

        if self.clock_mode:
            newstr = newstr + [("main_base_time_current", " [C]")]
        self.baset.set_text(newstr)

    def basezc_update(self):
        newstr = "base zone: %s" % str(self.zeitzonotime.get_tz())
        if self.basezc_is_c:
            newstr = "base city: %s" % self.basezc_city
        self.basezc.set_text(newstr)
        self.baset_update()

    def body_gen(self, update=False, nourwid=False):
        bodylist = []
        for index, city in enumerate(self.zeitzonocities.cities):
            bodytext = str(self.zeitzonotime.get_time_tz_str(city.get_tz()))
            bodytext = bodytext + " "
            bodytext = bodytext + str(city)

            # if we are in indexmode, prepend a 0-9a-zA-Z to
            # the bottom 62 items on stack
            if self.index_mode:
                if index < 62:
                    index_label = self.index2label(index) + ": "
                else:
                    index_label = "   "

            # nourwid is true when in --list-cached mode
            if nourwid:
                rawtext = bodytext
            else:
                if self.index_mode:
                    rawtext = urwid.Text(
                        [("main_index", index_label), ("default", bodytext)],
                        wrap="clip",
                        align="left",
                    )
                else:
                    rawtext = urwid.Text(bodytext, wrap="clip", align="left")
            if nourwid:
                content = rawtext
            else:
                if update:
                    content = (rawtext, ("pack", None))
                else:
                    content = rawtext

            bodylist.append(content)
        bodylist.reverse()

        return bodylist

    def body_render(self):
        self.bodypile.contents = self.body_gen(update=True)

    def clock_update(self, loop, user_date=None):
        # we only update in clock mode
        if not self.clock_mode:
            return

        # check if clock mode timed out
        if self.zeitzonotime.is_clock_mode_timeout():
            self.clock_mode = False
            self.zeitzonotime.clock_mode_reset()
            # we don't return here,
            # because we want the function to run to completion,
            # onre last time, otherwise [C] display doesn't go away

        # update to current time
        self.zeitzonotime.set_time_now()

        # update clock
        self.baset_update()

        # update body
        self.body_render()

        # how long to wait between refreshes, in seconds
        sleeptime = 1

        # set alarm for next refresh
        self.loop.set_alarm_in(sleeptime, self.clock_update)

    def index_mode_on(self, mode=None):
        self.index_mode_type = mode
        self.index_mode = True
        self.body_render()

    def index_mode_off(self):
        self.index_mode = False
        self.body_render()

    def index2label(self, num):
        "given a stack number, return the index 0-9a-zA-Z, or None"

        nums = "0123456789"
        alpha_lower = "abcdefghijklmnopqrstuvwxyz"
        alpha_upper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

        code = nums + alpha_lower + alpha_upper

        if num < len(code):
            return code[num]

        return None

    def label2index(self, label):
        nums = "0123456789"
        alpha_lower = "abcdefghijklmnopqrstuvwxyz"
        alpha_upper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

        code = nums + alpha_lower + alpha_upper

        if label not in code:
            # a valid label was not entered
            return None

        index = code.index(label)

        if index >= len(self.zeitzonocities.cities):
            # a valid label was entered
            # but our list is not that long
            return None

        return index
