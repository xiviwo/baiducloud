from gi.repository import Gtk
from gi.repository import Gdk
from MajorWindow import MajorWindow
from log import logger

def on_main_exit(win,gevent):
	logger.info("--------------------------Main exit---------------------")
	
	Gtk.main_quit(win,gevent)
win = MajorWindow()
win.connect("delete-event", on_main_exit)

win.show_all()

Gtk.main()
