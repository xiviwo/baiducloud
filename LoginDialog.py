#!/usr/bin/python
from gi.repository import Gtk, GObject
import auth
from log import logger
import settings
from Spinner import SpinnerDialog
import utils
from VcodeDialog import VcodeDialog
class LoginDialog(Gtk.Dialog):

	def __init__(self, parent):
		Gtk.Dialog.__init__(self, "Login...", parent, 0)

		self.set_default_size(350, 200)
		self.set_border_width(15)
		grid = Gtk.Grid()
		grid.set_row_spacing(10)
		#grid.set_row_baseline_position(1,Gtk.BaselinePosition.CENTER )
		#labelu = Gtk.Label("User Name:")
		#labelu.set_markup("<span style=\"oblique\">%s</span>")
		#labelp = Gtk.Label("Password:")
		self.uentry = Gtk.Entry()
		self.pentry = Gtk.Entry()
		self.uentry.set_text("xivhwo2002")
		self.pentry.set_text("mnja12")
		self.pentry.set_visibility(False)
		lbutton = self.add_button("Login...",11) #Gtk.Button("Login...")
		lbutton.props.xalign  = 0.5
		lbutton.connect("clicked",self.on_click_login)
		offline = Gtk.CheckButton("Offline Mode")
		offline.connect("toggled",self.on_toggle_offline)
		verbose = Gtk.CheckButton("Verbose Mode")
		verbose.connect("toggled",self.on_toggle_verbose)
		box = self.get_content_area()
		box.set_spacing(8)
		#box.add(grid)
		box.add(self.uentry)
		box.add(self.pentry)
		box.add(offline)
		box.add(verbose)
		#grid.add(labelu)
		#grid.attach_next_to(self.uentry,labelu,Gtk.PositionType.RIGHT,13,1)
		#grid.attach(labelp,0, 2, 1, 1)
		#grid.attach_next_to(self.pentry,labelp,Gtk.PositionType.RIGHT,13,1)
		#grid.attach_next_to(lbutton,self.pentry,Gtk.PositionType.BOTTOM,13,1)

		self.infobar = Gtk.InfoBar()
		self.infobar.set_message_type(Gtk.MessageType.ERROR)
		#box.pack_end(self.infobar, False, False, 0)
		#grid.attach_next_to(self.infobar,lbutton,Gtk.PositionType.BOTTOM,13,1)
		box.add(self.infobar)
		info_content = self.infobar.get_content_area()
		self.info_label = Gtk.Label.new("Input username/password to log in..")
		info_content.pack_start(self.info_label, False, False, 0)

		
		self.infobar.hide()

		self.show_all()

	def on_click_login(self,button):
		self.username = self.uentry.get_text()
		self.password = self.pentry.get_text()
		if not self.username or not self.password:
			self.info_label.set_text("Username or Password is blank.")
			return
		self.info_label.set_text("Going to index")
		logger.info("Username|Password %s %s"%(self.username,self.password))
		self.spinn = SpinnerDialog(self)
		self.spinn.show()
		utils.async_call(auth.index,
							 callback=self.after_goto_index)
		#bdstoken,sign1,sign3,timestamp = auth.index()


		print("click")
		#self.destroy()
	def after_goto_index(self,data,error):
		print(data)
		bdstoken,sign1,sign3,timestamp = data
		if not bdstoken:

			self.info_label.set_text("Geting token")
			
			#token = auth.get_token()
			utils.async_call(auth.get_token, 
							 callback=self.after_get_token)

		else:
			info = "bdstoken %s existing,no need to login again!"%bdstoken
			logger.info(info)
			self.info_label.set_text(info)
			self.spinn.destroy()

	def after_get_token(self,token,error):

			self.token = token
			self.info_label.set_text("Geting public key")
			utils.async_call(auth.get_public_key,self.token,
							 callback=self.after_get_public_key)
			#rsakey,pubkey = auth.get_public_key(token)
	def after_get_public_key(self,data,error):
		rsakey,pubkey = data
		
		self.info_label.set_text("Loging in now")
		#xml = auth.login(rsakey,pubkey,self.username,self.password,self.token)
		utils.async_call(auth.login,rsakey,pubkey,self.username,self.password,self.token,
							 callback=self.after_login)
	def after_login(self,data,error):
		xml,errdict = data
		if errdict['err_no']  == 257 : #Need verification Code
			codestring = errdict['codeString'] 
			url = 'https://passport.baidu.com/cgi-bin/genimage?' + codestring
			
			vd = VcodeDialog(self,url)
			vd.run()
			vf = vd.get_user_input()
			if not vf or len(vf) != 4:
				self.info_label.set_text("Verification Code missing or incorrect!")
				return
			else:
				vd.destory()
			utils.async_call(auth.relogin,rsakey,pubkey,self.username,self.password,vf,codeString,
							 callback=self.after_login)

		elif errdict['err_no']  == 0: 
			self.info_label.set_text("Login Successfully!")
			self.hide()
		self.spinn.destroy()

	def on_toggle_offline(self,button):
		if button.get_active():
			settings.DRY = True
		else:
			settings.DRY = False
		logger.info("Flag DRY toggled to %s"%settings.DRY)
	def on_toggle_verbose(self,button):
		if button.get_active():
			settings.VERBOSE = True
		else:
			settings.VERBOSE = False
		logger.info("Flag VERBOSE toggled to %s"%settings.VERBOSE)
