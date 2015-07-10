from gi.repository import Gtk
import utils
import re
from Spinner import SpinnerDialog
from gi.repository import GdkPixbuf
from weblib import fetch
class Singleton(type):  
	def __init__(cls, name, bases, dict):  
		super(Singleton, cls).__init__(name, bases, dict)  
		cls._instance = None  
	def __call__(cls, *args, **kw):  
		if cls._instance is None:  
		    cls._instance = super(Singleton2, cls).__call__(*args, **kw)  
		return cls._instance  
	def __new__(cls, name, bases, dct):
		
		return type.__new__(cls, name, bases, dct)


class VcodeDialog(Gtk.Dialog):
	__metaclass__ = Singleton
	def __init__(self,parent,url):
		Gtk.Dialog.__init__(self, "Verification Code", parent, 0,)
		self.file_list = []
		#self.downlink = []
		#self.tokens = tokens
		self.url = url
		#self.bdstoken,sign1,sign3,timestamp = self.tokens
		self.vcodefile = "image/vcode.jpeg"
		self.set_default_size(300, 200)
		self.set_border_width(10)
		label = Gtk.Label("Please input verification code above to proceed.")
		self.spinn = SpinnerDialog(self)
		self.spinn.show()
		self.vcodeimg = Gtk.Image.new()

		self.box = self.get_content_area()
		self.entry = Gtk.Entry()
		self.entry.connect("activate",self.on_enter_entry)
		self.entry.set_can_focus(True)
		self.entry.grab_focus()
		self.liststore = Gtk.ListStore(GdkPixbuf.Pixbuf)
		pix = GdkPixbuf.Pixbuf.new_from_file("image/loading.gif")
		self.liststore.append([pix])
		iconview = Gtk.IconView.new()
		iconview.set_model(self.liststore)
		iconview.set_pixbuf_column(0)
		#self.liststore.append([pix])
		self.show_vcode("image/loading.gif",None)#"image/loading.gif",
	
		self.box.add(iconview)
		#pix = GdkPixbuf.Pixbuf.new_from_file("image/loading.gif")
		 #Gtk.Image.new_from_pixbuf(pix)
		button = Gtk.Button("Refresh Code")
		button.connect("clicked", self.on_click_refresh_clicked)
		self.on_click_refresh_clicked(button)

	
		#self.entry.set_text("Input vcode above")

		self.okbtn = self.add_button("OK", 22)
		self.okbtn.connect("clicked", self.on_click_OK_clicked)
		self.box.set_child_packing(button,False,False,1,Gtk.PackType.START)

		self.box.set_spacing(8)
		self.box.add(label)
		
		self.box.add(self.entry)
		self.box.add(button)
		#self.box.add(okbtn)
		
		self.box.show_all()

	def on_enter_entry(self,*arg):
		self.okbtn.clicked()
	def on_click_refresh_clicked(self,*arg):
		utils.async_call(self.download_vcodeimg,self.url,self.vcodefile,
						 callback=self.show_vcode)
	def new_url(self,url):
		self.url = url
	def on_click_OK_clicked(self,*arg):
		if not self.entry.get_text().strip():
			dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO,
            Gtk.ButtonsType.OK, "Attention.......")
			dialog.format_secondary_text("Nothing is input!")
			dialog.run()
			dialog.destroy()
			return
		
	def get_user_input(self,*arg):
		print(arg)
		inputtxt = self.entry.get_text().strip()

		return inputtxt
	def download_vcodeimg(self,imgurl,vcodeimg):
		f=open(vcodeimg,"wb")
		fp = fetch(imgurl,{},"GetVcode")
		f.write(fp)
		f.close()
		return vcodeimg
	def show_vcode(self,imgfile,error):
		print('filename:',imgfile,error)
		pix = GdkPixbuf.Pixbuf.new_from_file(imgfile)
		fmat = GdkPixbuf.Pixbuf.get_file_info(imgfile)
		print(fmat[0].get_description(),fmat[0].get_extensions(),fmat[0].get_mime_types())
		print(pix)
		#if not self.vcodeimg:
		#self.vcodeimg.clear()
		#self.vcodeimg = Gtk.Image.new_from_pixbuf(pix)
		path = Gtk.TreePath(0)
		#self.liststore.append([pix])
		treeiter = self.liststore.get_iter(path)
		self.liststore.set_value(treeiter, 0, pix)
		#else:
		#	self.vcodeimg = Gtk.Image.set_from_pixbuf(pix)
		#self.vcodeimg.show()
		
		self.spinn.destroy()
