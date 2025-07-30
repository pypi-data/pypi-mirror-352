class ZeitzonoUrwidPalette:
    palette = """
        main_zeitzono,          light red,              default
        main_version,           light cyan,             default
        main_base_time,         yellow,                 default
        main_base_time_current, light magenta,          default
        main_basezc,            yellow,                 default
        main_helpline,          light green,            default
        main_index,             light red,              default

        search_prompt,          light red,              default

        splash_url,             yellow,                 default
        splash_main,            light red,              default
        splash_main_clock,      dark green,             default
        splash_version,         light cyan,             default
        splash_presskey,        white,                  default
        splash_author,          light blue,             default

        numresults_str,         yellow,                 default
        numresults_num,         light magenta,          default
    """

    palette_lightbg = """
        main_zeitzono,          dark red,               default
        main_version,           dark cyan,              default
        main_base_time,         brown,                  default
        main_base_time_current, dark magenta,           default
        main_basezc,            brown,                  default
        main_helpline,          dark green,             default
        main_index,             dark red,               default

        search_prompt,          dark red,               default

        splash_url,             brown,                  default
        splash_main,            dark red,               default
        splash_main_clock,      brown,                  default
        splash_version,         dark cyan,              default
        splash_presskey,        black,                  default
        splash_author,          dark blue,              default

        numresults_str,         brown,                  default
        numresults_num,         dark magenta,           default
    """

    palette_nocolor = """
        main_zeitzono,          default,                default
        main_version,           default,                default
        main_base_time_current, default,                default
        main_base_time,         default,                default
        main_basezc,            default,                default
        main_helpline,          default,                default
        main_index,             default,                default

        search_prompt,          default,                default

        splash_url,             default,                default
        splash_main,            default,                default
        splash_main_clock,      default,                default
        splash_version,         default,                default
        splash_presskey,        default,                default
        splash_author,          default,                default

        numresults_str,         default,                default
        numresults_num,         default,                default
    """

    def __init__(self, no_color=False, lightbg=False):
        palette = self.palette

        if lightbg:
            palette = self.palette_lightbg

        if no_color:
            palette = self.palette_nocolor

        mypalette = palette.strip().splitlines()
        mypalette = [p.strip() for p in mypalette if p.strip()]
        mypalette = [p.split(",") for p in mypalette]
        mypalette = [[i.strip() for i in p] for p in mypalette]
        self.palette = mypalette

    def get_palette(self):
        return self.palette
