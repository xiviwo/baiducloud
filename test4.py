from gi.repository import Gtk,Gdk
import cairo
class DialogExample(Gtk.Dialog):

	def __init__(self, parent):
		Gtk.Dialog.__init__(self, "Spinner", parent, 0)
		self.set_position(Gtk.WindowPosition.CENTER)

		box = self.get_content_area()

		self.spinner = Gtk.Spinner()

		grid = Gtk.Grid()
		grid.set_column_homogeneous(True)
		grid.set_row_homogeneous(True)
		grid.set_row_spacing(5)
		grid.set_column_spacing(5)

		grid.attach(self.spinner, 0, 0, 8, 8)

		box.add(grid)
		self.spinner.start()
		self.spinner.show_all()
		self.set_app_paintable(True)
		self.connect("draw", self.area_draw)
		self.show_all()
		self.get_window().set_decorations(Gdk.WMDecoration.BORDER)

	def area_draw(self, widget, cr):
		cr.set_source_rgba(1.0, 1.0, 1.0, 0.0)
		cr.set_operator(cairo.OPERATOR_SOURCE)
		cr.paint()
		cr.set_operator(cairo.OPERATOR_OVER)

class SpinnerAnimation(Gtk.Window):

	def __init__(self):

		Gtk.Window.__init__(self, title="Spinner")
		self.set_border_width(3)
		self.connect("delete-event", Gtk.main_quit)

		self.button = Gtk.ToggleButton("Start Spinning")
		self.button.connect("toggled", self.on_button_toggled)
		self.button.set_active(False)

		dialog = DialogExample(self)
		response = dialog.show()

		self.table = Gtk.Table(3, 2, True)
		self.table.attach(self.button, 0, 2, 0, 1)
		#self.table.attach(self.spinner, 0, 2, 2, 3)

		self.add(self.table)
		self.show_all()

	def on_button_toggled(self, button):
		

		#dialog.destroy()


		if button.get_active():
			dialog.spinner.start()
			self.button.set_label("Stop Spinning")

		else:
			dialog.spinner.stop()
			self.button.set_label("Start Spinning")


myspinner = SpinnerAnimation()

Gtk.main()
