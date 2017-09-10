import npyscreen
import core
import config
import actionhook
from mylogger import logger
import navigationpane
import assignpane
import actionpane
import sys
import curses
import theme

class NavigationForm(npyscreen.FormMuttActiveTraditional):
    MAIN_WIDGET_CLASS = navigationpane.NavigationPane

    def __init__(self, *args, **keywords):
        super(NavigationForm, self).__init__(*args, **keywords)
        self.handlers = {
                "=":                    self.h_enter_assign_mode,
                curses.ascii.ESC:       self.h_exit, 
                }
        return

    def h_exit(self, input):
        sys.exit(0)

    def h_enter_assign_mode(self, input):
        self.parentApp.switchForm('ASSIGN')


    def set_title_to_cwd(self):
        self.set_title(self.parentApp.core.current_entry.get_absolute_path())

    def set_title(self, title):
        self.wStatus1.value = " " + title 
        self.wStatus1.display()

    def beforeEditing(self):
        self.wMain.redraw()

class AssignForm(npyscreen.FormMuttActiveTraditional):
    MAIN_WIDGET_CLASS = assignpane.AssignPane

    def __init__(self, *args, **keywords):
        super(AssignForm, self).__init__(*args, **keywords)
        self.wStatus1.value = "assign key: choose entry"
        self.wStatus1.display()

        self.handlers = {
                "=":     self.h_exit_assign_mode
                }
        return

    def h_exit_assign_mode(self, input):
        self.parentApp.switchForm('MAIN')
        return

    def beforeEditing(self):
        self.wMain.values = self.parentApp.core.current_entry.children
        self.wMain.mode = 'choose-entry'

class ActionForm(npyscreen.FormMuttActiveTraditional):
    MAIN_WIDGET_CLASS = actionpane.ActionPane

    def __init__(self, *args, **keywords):
        super(ActionForm, self).__init__(*args, **keywords)
        self.handlers = {
                curses.ascii.ESC:       self.h_exit, 
                }
        return

    def h_exit(self, input):
        sys.exit(0)

    def beforeEditing(self):
        self.wStatus1.value = "{} - choose action:".format(self.parentApp.core.current_entry.name)
        self.wMain.redraw()



class Frame(npyscreen.NPSAppManaged):
    def onStart(self):
        npyscreen.setTheme(theme.Theme)
        self.core = core.Core()
        self.config = config.Config()
        self.action_engine = actionhook.ActionEngine( self.config )
        self.addForm("MAIN", NavigationForm)
        self.addForm("ASSIGN", AssignForm)
        self.addForm("ACTION", ActionForm)

    def onCleanExit(self):
        self.core.shutdown()


if __name__ == "__main__":
    logger.info('starting sodalite')
    app = Frame()
    try:
        app.run()
    except KeyboardInterrupt:
        app.core.shutdown()
        logger.info('bye')

