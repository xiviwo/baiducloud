from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from LoginDialog import LoginDialog
from DownloadDialog import DownloadDialog
from Spinner import SpinnerDialog
from TaskDialog import TaskDialog
from VcodeDialog import VcodeDialog
from gi.repository import GdkPixbuf
import json,os
import time
import cloudapi
import auth
from log import logger

import settings
import utils
from const import *
from urllib.parse import urlparse
from weblib import fetch

#num,pix,filename,size,path,isdir,fsid,cate,spath,speed,progress,status
#0   1   2        3     4    5     6    7    8     9     10       11
class MajorWindow(Gtk.Window):

	def __init__(self):
		Gtk.Window.__init__(self, title="Cloud Disk")

		self.set_border_width(10)
		self.maximize()
		#Setting up the self.grid in which the elements are to be positionned
		self.grid = Gtk.Grid()
		self.grid.set_column_homogeneous(True)
		self.grid.set_row_homogeneous(True)
		self.add(self.grid)
		#box = Gtk.Box(spacing=6)
		#self.add(box)
		self.tokens = auth.index()

		self.bdstoken,self.sign1,self.sign3,self.timestamp = self.tokens
	
		#self.connect('activate', self.on_login_dialog_close)
		#self.connect("delete-event", Gtk.main_quit)
		if not self.bdstoken:
			dialog = LoginDialog(self)	
			#dialog.connect("close",self.on_login_dialog_close)
			response = dialog.run()
	
			dialog.destroy()
			if response == Gtk.ResponseType.DELETE_EVENT:
				print(response)
				print("quit")
				#self.close()
		
				self.destroy()
				return
			elif response == 11:
				print("login")
			else:
				return 
		self.down_list = []

		self.current_path = "/"
		self.current_selection = None
		##							   num,pix,filename,size,path,isdir,fsid,cate,spath,speed,progress,status
		#                              0   1   2        3     4    5     6    7    8     9     10       11
		self.liststore = Gtk.ListStore(int,GdkPixbuf.Pixbuf,str, str, str,int,str,int,str,str,int,str)
		self.current_list = []
		#self.loading_spin = Gtk.Spinner()
		#self.loading_spin.props.valign = Gtk.Align.CENTER
		#box.pack_start(self.loading_spin, False, False, 0)
		#self.grid.add(self.loading_spin)
		
		self.init_view(self.current_path)
		#self.spinn.hide()
		#list_json = cloudapi.list_path(self.current_path,500,settings.DRY,self.bdstoken)
		#logger.debug("list json: %s"%str(len(list_json))
		#file_list = cloudapi.get_list(list_json)
		#logger.debug("file_list: %s"%str(file_list))


		#self.populate_view(file_list)
		
		self.stop_gif = False


		#creating the treeview, making it use the filter as a model, and adding the columns
		self.treeview = Gtk.TreeView(model=self.liststore)
		for i, column_title in enumerate(["Num","Thumb","File", "Size", "Path"]):
			if column_title != "Thumb":
				renderer = Gtk.CellRendererText()
				column = Gtk.TreeViewColumn(column_title, renderer, text=i)
			else:
				renderer_pixbuf = Gtk.CellRendererPixbuf()
				
				column = Gtk.TreeViewColumn(column_title, renderer_pixbuf,pixbuf=i)
			
			#if not column_title == 'isdir' and not column_title == 'fsid' and not column_title == 'cate'  :
			self.treeview.append_column(column)

		self.treeview.props.activate_on_single_click = False
		self.treeview.connect("row-activated",self.on_row_double_click)


		self.selection = self.treeview.get_selection()
		self.selection.connect("changed", self.on_tree_selection_changed)
		self.selection.set_mode(Gtk.SelectionMode.MULTIPLE)
		#select = selection.get_selected_rows() 

		#creating buttons to filter by programming language, and setting up their events
		self.buttons = list()
		for act in ["Up level", "Refresh View", "Batch Add Task", "Remove File", "Download","CleanUp","Search"]:
			button = Gtk.Button(act)
			self.buttons.append(button)
			funcname = "on_%s_button_clicked"%act.lower().replace(" ","_")
			print(funcname)
			func = getattr(self, funcname)
			button.connect("clicked", func)


		#setting up the layout, putting the treeview in a scrollwindow, and the buttons in a row
		self.scrollable_treelist = Gtk.ScrolledWindow()
		self.scrollable_treelist.set_vexpand(True)
		#self.grid.attach(self.loading_spin, 0, 0, 10, 20)
		#self.grid.attach_next_to(self.scrollable_treelist,self.loading_spin, Gtk.PositionType.BOTTOM, 10, 23)
		self.grid.attach(self.scrollable_treelist, 0, 0, 8, 20)
		#box.pack_start(self.scrollable_treelist, True, True, 0)
		self.grid.attach_next_to(self.buttons[0], self.scrollable_treelist, Gtk.PositionType.BOTTOM, 1, 1)
		for i, button in enumerate(self.buttons[1:]):
			self.grid.attach_next_to(button, self.buttons[i], Gtk.PositionType.RIGHT, 1, 1)
			#self.add_action_widget(self.buttons[i],i+1)
			#box.pack_start(self.buttons[i], False, False, 0)
		self.scrollable_treelist.add(self.treeview)

		#box.show_all()
		self.grid.show_all()
		#self.loading_spin.start()
		#self.loading_spin.show_all()
		#self.loading_spin.hide()
		#self.hide()
	def reload_pix(self,re_data,error):
		pix = None
		if not error:
			num,thumbimg = re_data
			path = Gtk.TreePath(int(num))
			if len(self.liststore) > 0 :
				treeiter = self.liststore.get_iter(path)
				if GdkPixbuf.Pixbuf.get_file_info(thumbimg)[0]:

					pix = GdkPixbuf.Pixbuf.new_from_file(thumbimg)
				else:
					pix = None
				logger.debug("reloading pix,pix = %s"%str(pix))
				self.stop_gif = True
				self.liststore.set_value(treeiter, 1, pix)
				
		else:
			logger.debug("reload_pix error %s"%str(error))


	def get_pix_list(self,file_list):
		current_list = []
		def advance_frame(*user_data):
		
			num,pixiter = user_data
			#pass#
			if pixiter.advance() and not self.stop_gif:
			
				pix = pixiter.get_pixbuf()
			
				path = Gtk.TreePath(int(num))
			
				if len(self.liststore) > 0:
			
					treeiter = self.liststore.get_iter(path)
					self.liststore.set_value(treeiter, 1, pix)
				return True
			else:
				return False
		def down_img(num,thumbimg,link,fsid,header,path):
			logger.debug(" %s is downloading"%str(fsid))
			f=open(thumbimg,"wb")
			img = fetch(link,{},fsid,header,path)
			f.write(img)
			f.close()
			return (num,thumbimg)
		def create_img_pix(thumbimg):
			if not GdkPixbuf.Pixbuf.get_file_info(thumbimg)[0]:
				return None
			else:
				return GdkPixbuf.Pixbuf.new_from_file(thumbimg)

		for row in file_list:
			#if cate == 1:
			#(num,thumb,filename,size,path,isdir,fsid,cate)
			num = row[0]
			thumb = row[1]
			path = row[4]
			isdir =row[5]
			fsid = row[6] 
			cate = row[7]
			host = urlparse(thumb)[1]

			header = {
			'Host':host,
			'Referer':DISK_HOME,
			}
			if not os.path.exists("image"):
					os.makedirs("image")
			thumbimg = "image/" + fsid + ".jpg"

			if GdkPixbuf.Pixbuf.get_file_info(thumbimg)[0]:

				pix = GdkPixbuf.Pixbuf.new_from_file(thumbimg)

			elif thumb:
				self.stop_gif = False
				pixan = GdkPixbuf.PixbufAnimation.new_from_file("image/loading.gif")
				pixiter = pixan.get_iter()
				pix = pixiter.get_pixbuf()
				#pix.set_loop(True)
				GLib.timeout_add(pixiter.get_delay_time(),
								 advance_frame,num,pixiter)
				logger.debug("Async call download for file %s "%str(fsid))
				utils.async_call(down_img, num,thumbimg,thumb,fsid,header,path,
				     callback=self.reload_pix)
			elif isdir:
				pix = GdkPixbuf.Pixbuf.new_from_file("image/folder.png")
			else:
				pix = None
			rowlist = list(row)
			rowlist[1] = pix
			#elif cate == 6:
			#	pix = create_img_pix("image/folder.png")
			current_list.append( tuple(rowlist) + (SAVINGPATH,"0B",0,"pending"))
		return current_list

	def populate_view(self,list_json,error=None):
		if list_json:
			self.current_list = []
			file_list = cloudapi.get_list(list_json)
			logger.debug("Size of file_list: %s"%str(len(file_list)))
			pix_list = self.get_pix_list(file_list)
			self.fill_liststore(pix_list)
			#self.loading_spin.stop()
			#self.loading_spin.hide()
			#self.spinn.hide()
			self.spinn.destroy()
		
			

	def fill_liststore(self,file_list):

		self.liststore.clear()
		for i,filerow  in enumerate(file_list):
			
			#logger.info("Creating TreeView at %s"%str(i))
			
			self.liststore.append(list(filerow))
		
	def on_tree_selection_changed(self,selection):
		#print(selection.get_selected_rows() )
		references = []
		self.current_selection = selection.get_selected_rows()
			
		
	def on_login_dialog_close(self,*arg):
		print("close dialog")
		print(*arg)
		self.close()


	def init_view(self,path):
		self.current_selection = None
		self.current_path = path
		logger.debug("Current Path: %s"%self.current_path)
		#list_json = cloudapi.list_path(self.current_path,500,
		#								settings.DRY,self.bdstoken)
		utils.async_call(cloudapi.list_path, self.current_path,500,
										settings.DRY,self.bdstoken,
				     callback=self.populate_view)
		#logger.debug("Size of list json: %s"%str(len(list_json)))
		#file_list = cloudapi.get_list(list_json)
		#logger.debug("Size of file_list: %s"%str(len(file_list)))
		#self.liststore.clear()
		#self.fill_liststore(file_list)
		#self.loading_spin.start()
		#self.loading_spin.show_all()
		self.spinn = SpinnerDialog(self)
		self.spinn.show()
		file_list = []
		pix_list = self.get_pix_list(file_list)
		self.fill_liststore(pix_list)
		

	def on_row_double_click(self,treeview,treepath,treeviewcolumn):
		print("Double click")
		print(self.liststore[treepath])
		#treeiter = self.liststore.get_iter(treepath)
		#num,pix,filename,size,path,isdir,fsid,cate,spath,speed,progress = 
		row = self.liststore[treepath]
		#num = row[0]
		filename = row[2]
		#thumb = row[1]
		path = row[4]
		isdir = row[5]
		#fsid = row[6] 
		#cate = row[7]
		logger.debug("row : %s"%(','.join(str(i) for i in row )))
		if isdir:
			npath = os.path.join(path,filename)
			self.init_view(npath)

		return True
	def on_up_level_button_clicked(self,*arg):
	
		
		path = os.path.abspath(os.path.join(self.current_path,".."))
		self.init_view(path)

	def on_refresh_view_button_clicked(self,*arg):
		settings.DRY = False
		self.init_view(self.current_path)
		settings.DRY = True
	def on_batch_add_task_button_clicked(self,*arg):
		print("Click",arg)
		settings.DRY = False
		td = TaskDialog(self,self.tokens,self.current_path)
		response = td.show()
		if  response == Gtk.ResponseType.DELETE_EVENT:
		
			settings.DRY = True
			
				
		
		
	def on_remove_file_button_clicked(self,*arg):
		

		if self.is_current_selection_null(): 
			return
		store,treepaths = self.current_selection
		
		remove_list = []
		for tpath in treepaths:
			row = store[tpath]
			filename = row[2]
			path = row[4]
			isdir = row[5]
			remove_list.append(os.path.join(path,filename))
		fl = '["' + '","'.join(str(i) for i in remove_list) + '"]'
		logger.debug("Flist: %s"%fl)
		if not self.agree_to_action(fl,"remove"):
			return

		cloudapi.delete_file(self.bdstoken,fl)
		settings.DRY = False
		self.init_view(self.current_path)
		settings.DRY = True

	def task_in_list(self,task,dlist):
		for row in dlist:
			#num,pix,filename,size,path,isdir,fsid,cate,spath,speed,progress = row
			if task[6] == row[6]:
				return True
			
		return False

	def on_download_button_clicked(self,*arg):
		#if self.is_current_selection_null(): 
		#	return
		
		if self.current_selection and self.current_selection[1]:
			store,treepaths = self.current_selection
	

			for tpath in treepaths:
				
				task = store[tpath]
				num = task[0]
				filename = task[2]
				thumb = task[1]
				path = task[4]
				isdir = task[5]
				fsid = task[6] 
				cate = task[7]

				if not isdir and not self.task_in_list(task,self.down_list):
					self.down_list.append(task)
				else:
					tasks = self.recursive_selected([task])
				
					for task in tasks:

						if not self.task_in_list(task,self.down_list):
						
							self.down_list.append(task)
		print(self.down_list)
		self.downdialog = DownloadDialog(self,self.down_list,self.tokens)
		#self.downdialog.connect("delete-event",self.hide_down_dialog)
		#self.downdialog.hide()
		#self.downdialog.liststore.clear()
		
		#self.downdialog.fill_liststore(self.down_list)
		response = self.downdialog.show()
		
		if response == Gtk.ResponseType.DELETE_EVENT:
			print(response)
			self.downdialog.hide()
		self.selection.unselect_all()

	def on_cleanup_button_clicked(self,*arg):
		print("Click",arg)
	def on_search_button_clicked(self,button):
		print("Click",button)
		url = 'http://pan.baidu.com/genimage?33324238656332346361663334656637323237633636373637643239666664336662343932343631383931303030303030303030303030303031343335353131313938D9224DC2E75F22A923706D077C0CD5B2'
		vd = VcodeDialog(self,url)
		response = vd.run()
		print(response)
		if response == 22:
			print("The OK button was clicked")
			vcode = vd.get_user_input()
			vd.destroy()
		elif  response == Gtk.ResponseType.DELETE_EVENT:
			vd.destroy()
	def is_current_selection_null(self):
		if not self.current_selection or not self.current_selection[1] :
			dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO,
            Gtk.ButtonsType.OK, "Attention.......")
			dialog.format_secondary_text("NO File is selected.!")
			dialog.run()
			dialog.destroy()
			return True
		else:	
			return False
	def agree_to_action(self,fl,action):
		dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.QUESTION,
			Gtk.ButtonsType.YES_NO, "%s Confirmation"%action.title())
		dialog.format_secondary_text(
			"Are you sure to %s file(s) : %s"%(action,fl))
		response = dialog.run()
		dialog.destroy()
		if response == Gtk.ResponseType.YES:	
			return True
		elif response == Gtk.ResponseType.NO:
			return False
	def hide_down_dialog(self,*arg):
		self.downdialog.hide()
	def recursive_selected(self,lists):	
		task_list = []
		folder = []
		
		for row in lists:
			filename = row[2]
			path = row[4]
			isdir = row[5]
			if not isdir:
				
				task_list.append(row)
				
			else:
				folder.append((path,filename))

		
		for path,filename in folder:
			npath = os.path.join(path,filename)
			
			list_json = cloudapi.list_path(npath,300,True,self.bdstoken)
			nlists = []
			for row in self.get_pix_list(cloudapi.get_list(list_json )):
				
				nlists.append(row)
			
			task_list += self.recursive_selected(nlists)
		return task_list
