#!/usr/bin/env python

import sys
import urwid
import argparse
import xdg
import os

from Zeitzono import ZeitzonoUrwidMain
from Zeitzono import ZeitzonoWidgetSwitcher
from Zeitzono import ZeitzonoUrwidSplashScreen
from Zeitzono import ZeitzonoUrwidHelpMain
from Zeitzono import ZeitzonoUrwidHelpSearch
from Zeitzono import ZeitzonoUrwidPalette

VERSION = "v0.9.2"
VERSION_DB = "GeoNames DB: 2024-07-31"


def default_cache():
    return default_cache_dir() / "cache"


def default_cache_dir():
    return xdg.XDG_CACHE_HOME / "zeitzono"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', '-v', action='version',
                        version=f"zeitzono {VERSION} ({VERSION_DB})")

    help = "start without splash screen"
    parser.add_argument("--no-splash", "-S", action="store_true", help=help)

    help = "don't use colors"
    parser.add_argument("--no-color", "-C", action="store_true", help=help)

    help = "don't cache cities on exit; don't use cache on startup"
    parser.add_argument("--no-cache", action="store_true", help=help)

    help = "print out current time in cached cities and exit"
    parser.add_argument("-L", "--list-cached", action="store_true", help=help)

    help = "use colors that look good on a light background"
    parser.add_argument("--bg-light", action="store_true", help=help)

    args = parser.parse_args()

    if args.no_cache and args.list_cached:
        parser.error("--list--cache makes no sense if --no-cache is set")

    return args


def main():

    args = parse_args()

    zeitzonowidgetswitcher = ZeitzonoWidgetSwitcher()

    version = VERSION
    dbversion = VERSION_DB

    zeitzonourwidsplashscreen = ZeitzonoUrwidSplashScreen(
        zeitzonowidgetswitcher, version, dbversion
    )

    cache = None
    if args.no_cache is False:
        if not os.path.exists(default_cache_dir()):
            os.mkdir(default_cache_dir())
        cache = default_cache()

    zeitzonourwidmain = ZeitzonoUrwidMain(None, zeitzonowidgetswitcher, cache, version)

    mainframe = urwid.Frame(zeitzonourwidsplashscreen, focus_part="body")

    # help screens
    zeitzonourwidhelpmain = ZeitzonoUrwidHelpMain(zeitzonowidgetswitcher)
    zeitzonourwidhelpsearch = ZeitzonoUrwidHelpSearch(zeitzonowidgetswitcher)
    zeitzonowidgetswitcher.set_mainframe(mainframe)
    zeitzonowidgetswitcher.set_widget_help_main(zeitzonourwidhelpmain)
    zeitzonowidgetswitcher.set_widget_help_search(zeitzonourwidhelpsearch)

    zeitzonowidgetswitcher.set_widget("splash", zeitzonourwidsplashscreen)
    zeitzonowidgetswitcher.set_widget("main", zeitzonourwidmain)

    if args.no_splash:
        zeitzonowidgetswitcher.switch_widget_main()

    palette = ZeitzonoUrwidPalette(
        no_color=args.no_color, lightbg=args.bg_light
    ).get_palette()

    # we are requested to run in list-cached mode
    # print out time with city name and exit
    if args.list_cached:
        for i in zeitzonourwidmain.body_gen(nourwid=True):
            print(i)
        sys.exit(0)

    loop = urwid.MainLoop(mainframe, palette, handle_mouse=False)

    # this is kinda janky updating it here...
    # ...but it works
    zeitzonourwidmain.loop = loop
    zeitzonourwidmain.clock_update(loop)

    loop.run()


if __name__ == "__main__":
    main()
