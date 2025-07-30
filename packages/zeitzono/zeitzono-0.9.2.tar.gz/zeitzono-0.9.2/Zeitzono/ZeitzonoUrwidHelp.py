import urwid
import importlib
import os


class ZeitzonoUrwidHelp(urwid.WidgetWrap):
    _selectable = True

    def __init__(self, zeitzonowidgetswitcher, helpfile, prev_is_main):
        self.zeitzonowidgetswitcher = zeitzonowidgetswitcher
        self.prev_is_main = prev_is_main

        traversible = importlib.resources.files("Zeitzono")
        helpmaintext_file = traversible / "data" / helpfile
        helpmaintext = helpmaintext_file.read_text().strip()

        helpmaintext = helpmaintext.split("\n")
        helpmaintext_u = [
            urwid.Text(line, wrap="clip") for line in helpmaintext
        ]
        self.listwalker = urwid.SimpleListWalker(helpmaintext_u)
        self.listbox = urwid.ListBox(self.listwalker)

        frame = urwid.Frame(self.listbox, focus_part="body")
        super().__init__(frame)

    def go_previous_screen(self):
        if self.prev_is_main:
            self.zeitzonowidgetswitcher.switch_widget_main()
        else:
            self.zeitzonowidgetswitcher.switch_widget_search()

    def keypress(self, size, key):
        self.listbox.keypress(size, key)
        if isinstance(key, str):
            if key.isalpha():
                if key.lower() == "k":
                    self.listbox.keypress(size, "up")
                    return True
                if key.lower() == "j":
                    self.listbox.keypress(size, "down")
                    return True
                if key == "G":
                    self.listbox.keypress(size, "end")
                    return True
                if key == "g":
                    self.listbox.keypress(size, "home")
                    return True
                if (key.lower() == "q") or (key == "esc"):
                    self.go_previous_screen()
                    return True
                if (key == "backspace") or (key == "delete"):
                    self.listbox.keypress(size, "page up")
                    return True
            if key == " ":
                self.listbox.keypress(size, "page down")
                return True


class ZeitzonoUrwidHelpMain(ZeitzonoUrwidHelp):
    def __init__(self, zeitzonowidgetswitcher):
        helpfile = "helpmain.txt"
        prev_is_main = True
        super().__init__(zeitzonowidgetswitcher, helpfile, prev_is_main)


class ZeitzonoUrwidHelpSearch(ZeitzonoUrwidHelp):
    def __init__(self, zeitzonowidgetswitcher):
        helpfile = "helpsearch.txt"
        prev_is_main = False
        super().__init__(zeitzonowidgetswitcher, helpfile, prev_is_main)
