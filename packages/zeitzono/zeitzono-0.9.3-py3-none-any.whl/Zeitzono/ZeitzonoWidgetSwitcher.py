class ZeitzonoWidgetSwitcher:
    def __init__(self, mainframe=None):
        self.widgets = {}
        self.mainframe = mainframe

    def set_mainframe(self, mainframe):
        self.mainframe = mainframe

    def set_time(self, zeitzonotime):
        self.zeitzonotime = zeitzonotime

    def set_widget(self, name, widget):
        self.widgets[name] = widget

    def set_widget_help_main(self, widget):
        self.set_widget("helpmain", widget)

    def set_widget_help_search(self, widget):
        self.set_widget("helpsearch", widget)

    def switch_widget_help_main(self):
        self._switch_widget("helpmain")

    def switch_widget_help_search(self):
        self._switch_widget("helpsearch")

    def switch_widget_main(self):
        self.widgets["main"].body_render()
        self._switch_widget("main")

    def switch_widget_search(self):
        self._switch_widget("search")

    def _switch_widget(self, name):
        self.mainframe.contents["body"] = (self.widgets[name], None)
