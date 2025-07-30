import urwid
import base64
import bz2
import re


class ZeitzonoUrwidSplashScreen(urwid.WidgetWrap):
    _selectable = True

    def __init__(self, zeitzonowidgetswitcher, version, dbversion):
        self.zeitzonowidgetswitcher = zeitzonowidgetswitcher
        b64 = """
        QlpoOTFBWSZTWZTfzlIAACH/gDoQIQBQjoBAAAJAIPQAAAQwAMMCREJ6kZMmmEKD
        Ro0GQGgkJE1HqZGjRk4oM2tgesad9SYwCDSCUQn2UrOVS38KX5rcZ6eGFO1OMxy0
        L2yZjG83yvza0wxsIyI5ZFk2uiOXCmy86IhXumSUcPJkgbOr5+Wwjhgmw7QacRrz
        dBuc3lEDqbD9u2TJKr0iDd07LfQgMIEvAa6UuFjDN21xYf7zVBcNktFVhkYzEZR/
        F3JFOFCQlN/OUg==
        """

        urltext = "zeitzono.org"

        bz2bin = base64.b64decode(b64)
        splashtext = bz2.decompress(bz2bin)
        splashtext = splashtext.decode("ascii")

        splashtext_lines = splashtext.splitlines()
        splash = []
        # import sys
        # sys.exit(splashtext_lines)
        splash_regex = re.compile(r"[+|\-/]")
        for line in splashtext_lines:
            if splash_regex.search(line):
                line_array = []
                for char in line:
                    ut = urwid.Text(char, wrap="clip")
                    if splash_regex.search(char):
                        attmap = urwid.AttrMap(ut, "splash_main_clock")
                    else:
                        attmap = urwid.AttrMap(ut, "splash_main")
                    line_array.append(attmap)
                line_col = urwid.Columns(line_array)
                splash.append(line_col)
            else:
                ut = urwid.Text(line, wrap="clip")
                attmap = urwid.AttrMap(ut, "splash_main")
                splash.append(attmap)

        splashpile = urwid.Pile(splash)

        presskeytext = "[Press any key to continue]\n"
        presskey = urwid.Text(presskeytext, wrap="clip", align="center")
        presskeymap = urwid.AttrMap(presskey, "splash_presskey")

        authortext = "by N.J. Thomas"
        author = urwid.Text(authortext, wrap="clip", align="right")
        authormap = urwid.AttrMap(author, "splash_author")

        url = urwid.Text(urltext, wrap="clip")
        urlmap = urwid.AttrMap(url, "splash_url")

        version_ut = urwid.Text(version, wrap="clip", align="right")
        versionmap = urwid.AttrMap(version_ut, "splash_version")

        dbversion_ut = urwid.Text(dbversion, wrap="clip", align="right")
        dbversionmap = urwid.AttrMap(dbversion_ut, "splash_version")

        topcols = urwid.Columns([urlmap, authormap])
        mainpile = urwid.Pile([topcols, splashpile, versionmap, dbversionmap])

        mainpad = urwid.Padding(mainpile, align="center", width=77)

        f = urwid.Filler(mainpad)

        frame = urwid.Frame(body=f, footer=presskeymap)
        super().__init__(frame)

    def keypress(self, size, key):
        self.zeitzonowidgetswitcher.switch_widget_main()
