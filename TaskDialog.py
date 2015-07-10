from gi.repository import Gtk
import json,os
from log import logger
import settings
import cloudapi
import utils
import re
from Spinner import SpinnerDialog
from VcodeDialog import VcodeDialog
import urllib.parse
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


class TaskDialog(Gtk.Dialog):
	__metaclass__ = Singleton
	def __init__(self,parent,tokens,save_path):
		Gtk.Dialog.__init__(self, "Download Task", parent, 0)
		self.file_list = []
		#self.downlink = []
		self.tokens = tokens
		
		self.bdstoken,sign1,sign3,timestamp = self.tokens
		#self.file_list = nlist
		#self.remove_list = file_list
		self.current_selection = None
		self.save_path = save_path
		#self.draw_widget(file_list)
		#def draw_widget(self,file_list):
		self.set_default_size(800, 500)
		self.set_border_width(10)


		box = self.get_content_area()

		##							   num,filename,size,status,path,
		#                              0   1       2        3     4    
		self.liststore = Gtk.ListStore(int,str, str, str,str,str)
		#self.liststore.connect("row-changed",self.row_changed)
		self.spinn = SpinnerDialog(self)
		self.spinn.show()
		self.init_view(self.bdstoken)


		#creating the treeview, making it use the filter as a model, and adding the columns
		self.treeview = Gtk.TreeView(model=self.liststore)
		for i, column_title in enumerate(["Num","File", "Size","Status", "Path"]):
						
			renderer = Gtk.CellRendererText()
			column = Gtk.TreeViewColumn(column_title, renderer,text=i)
			self.treeview.append_column(column)

		self.treeview.props.activate_on_single_click = False
		self.treeview.connect("row-activated",self.on_row_double_click)


		self.selection = self.treeview.get_selection()
		self.selection.connect("changed", self.on_tree_selection_changed)
		self.selection.set_mode(Gtk.SelectionMode.MULTIPLE)


		self.buttons = list()
		for act in ["Add Magnet or Ed2k Link File","Select All","Unselect All", "Remove Task"]:
			button = Gtk.Button(act)
			self.buttons.append(button)
			funcname = "on_%s_button_clicked"%act.lower().replace(" ","_")
			
			func = getattr(self, funcname)
			button.connect("clicked", func)


		self.scrollable_treelist = Gtk.ScrolledWindow()
		self.scrollable_treelist.set_vexpand(True)

		box.pack_start(self.scrollable_treelist, True, True, 0)


		for i, button in enumerate(self.buttons):
			#box.pack_start(self.buttons[i], False,False, 0)
			self.add_action_widget(self.buttons[i],i+1)
		self.scrollable_treelist.add(self.treeview)
	

		self.infobar = Gtk.InfoBar()
		self.infobar.set_message_type(Gtk.MessageType.ERROR)
		#box.pack_end(self.infobar, False, False, 0)
		#grid.attach_next_to(self.infobar,lbutton,Gtk.PositionType.BOTTOM,13,1)
		box.add(self.infobar)
		info_content = self.infobar.get_content_area()
		self.info_label = Gtk.Label.new("Add magnet/ed2k file to add offline download task")
		info_content.pack_start(self.info_label, False, False, 0)

		
		self.infobar.hide()
		box.show_all()


	def on_tree_selection_changed(self,*arg):
		self.current_selection = self.selection.get_selected_rows()

	def populate_view(self,*arg):
		listjson,error = arg
		print(listjson)
		if 'task_info' in list(listjson.keys()):
			task_list = listjson['task_info']
		
			file_list = []
			for i,row in enumerate(task_list):
				if int(row['status']) == 0:
					status = "Success"
				else:
					status = "Not Finised"
				nrow = (i,row['task_name'],'0B',status,row['save_path'],row['task_id'])
				file_list.append(nrow)
		
			self.fill_liststore(file_list)
		
		elif 'error_msg' in list(listjson.keys()):
			info =listjson['error_msg']
			logger.info(info)
			self.info_label.set_text(info)
		self.spinn.destroy()
		
	def init_view(self,bdstoken):
		
		utils.async_call(cloudapi.list_task, bdstoken,
				     callback=self.populate_view)

		self.fill_liststore([])

	def fill_liststore(self,file_list):
		if file_list:
			self.liststore.clear()
			for i,filerow  in enumerate(file_list):

				self.liststore.append(list(filerow))


	def on_select_all_button_clicked(self,*arg):
		self.selection.select_all()
	def on_unselect_all_button_clicked(self,*arg):
		self.selection.unselect_all()
	def on_remove_task_button_clicked(self,*arg):
		def is_current_selection_null():
			if not self.current_selection or not self.current_selection[1] :
				dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.INFO,
		        Gtk.ButtonsType.OK, "Attention.......")
				dialog.format_secondary_text("NO File is selected.!")
				dialog.run()
				dialog.destroy()
				return True
			else:	
				return False
		def after_delete_task(data,error):
			self.info_label.set_text("Deletion is done")
			self.init_view(self.bdstoken)
			self.spinn.destroy()

		if is_current_selection_null(): 
			return
		store,treepaths = self.current_selection
	

		for tpath in treepaths:
			task = ()
			for i in store[tpath]:
				task = task + (i,)
				
			task_id = task[5]
			self.spinn = SpinnerDialog(self)
			self.spinn.show()
			self.info_label.set_text("Deleting task %s "%task[1])
			utils.async_call(cloudapi.delete_task, self.bdstoken,task_id ,
						 callback=after_delete_task)
		#self.liststore.clear()
		#self.fill_liststore(file_list)


	def on_row_double_click(self,*arg):
		pass
	def after_cancel_task(self,*arg):
		
		taskdata,error = arg
		canceljson,task_id,task_name = taskdata
		logger.debug("canceljson: %s "%canceljson)
		info ="Task:%s,id:%s is cancelled."%(task_name,task_id)
		logger.info(info)
		self.info_label.set_text(info)
		self.init_view(self.bdstoken)
		self.spinn.destroy()

	def after_query_task(self,*arg):
		taskdata,error = arg
		taskjson,task_id = taskdata
		#self.init_view(self.bdstoken)
		#taskjson = cloudapi.query_task(task_id)
		logger.debug("taskjson: %s "%taskjson)
		#if task_json:
		file_size = int(taskjson['task_info'][task_id]['file_size'])
		finished_size = int(taskjson['task_info'][task_id]['finished_size'])
		task_name  = taskjson['task_info'][task_id]['task_name']
		logger.debug("file_size: %s "%file_size)
		logger.debug("finished_size: %s "%finished_size)


		if finished_size/file_size < 1 :
			info = "%s : Finished rate is less than 0.6, canceling."%task_name
			logger.info(info)
			self.info_label.set_text(info)
			utils.async_call(cloudapi.cancel_task, self.bdstoken,task_id,task_name,
					 callback=self.after_cancel_task)

		else:
			info = "Task:%s,id:%s is successfully created."%(task_name,task_id)
			logger.info(info)
			self.info_label.set_text(info)
			#self.init_view(self.bdstoken)
			self.spinn.destroy()
			

	def after_add_task(self,*arg):
		taskjson,error = arg
		logger.debug("taskjson: %s "%taskjson)
		if 'task_id' in taskjson.keys():
			task_id = str(taskjson['task_id'])
			utils.async_call(cloudapi.query_task, self.bdstoken,task_id,
				     callback=self.after_query_task)

		else:
			error = taskjson['error_msg']
			logger.info(error)
			self.info_label.set_text(error)
			#self.init_view(self.bdstoken)
			self.spinn.destroy()

		#self.spinn.destroy()

	def on_add_magnet_or_ed2k_link_file_button_clicked(self,*arg):
		dialog = Gtk.FileChooserDialog("Please choose a file", self,
			Gtk.FileChooserAction.OPEN,
			(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
			 Gtk.STOCK_OPEN, Gtk.ResponseType.OK))

		response = dialog.run()
		if response == Gtk.ResponseType.OK:
			#linkfile = dialog.get_file().read()
			filename = dialog.get_filename()
			
			print("Open clicked")
			print("File selected: " + dialog.get_filename())
		elif response == Gtk.ResponseType.CANCEL:
			return
		
		dialog.destroy()
		
		link_list = open(filename).read()
		task_list = []
		invalid_list = []
		for line in link_list.split("\n"):
			line = line.strip()
			if line and ( line.startswith("magnet:?xt=urn") or \
				 line.startswith("ed2k://") ):
				task_list.append(line)
				
			elif line:
				invalid_list.append(line)
		if invalid_list:
				dialog = Gtk.MessageDialog(self, 0, Gtk.MessageType.QUESTION,
						Gtk.ButtonsType.OK, "Attention")
				dialog.format_secondary_text(
						"Only magnet or ed2k protocal is support! Invalid lines :%s"%str(invalid_list))
				response = dialog.run()
				dialog.destroy()
				return 
		print(self.save_path)
		
		maglist = [ i['source_url'] for i in self.task_list   if "magnet:?xt=urn:" in i['source_url'] ]
		logger.debug("maglist: %s "%str(maglist))
		
		for i,l in enumerate(task_list):
			mag = re.search('(&.*$)',l).group(1)
			task_name = dict(urllib.parse.parse_qsl(mag))['dn']
			txt = "%s out of %s | %s is running."%(str(i),len(task_list),str(task_name))
			logger.info(txt)
			self.info_label.set_text(txt)
			maglink = re.search("(magnet[^&]*)",l).group(1)
			logger.debug("maglink: %s "%maglink)
			self.spinn = SpinnerDialog(self)
			self.spinn.show()
			if maglink not in maglist:
				
				self.info_label.set_text("Adding task: %s "%task_name)
				taskjson = cloudapi.add_task(self.bdstoken, l,self.save_path,self)
				self.init_view(self.bdstoken)
				self.spinn.destroy()

				#taskjson = cloudapi.add_task(l,self.save_path)
				logger.debug("taskjson: %s "%taskjson)
				if 'task_id' in taskjson.keys():
					self.spinn = SpinnerDialog(self)
					self.spinn.show()
					self.info_label.set_text("Querying task: %s "%task_name)
					task_id = str(taskjson['task_id'])
					utils.async_call(cloudapi.query_task, self.bdstoken,task_id,
							 callback=self.after_query_task)
					self.spinn.destroy()
				else:
					error = taskjson['error_msg']
					logger.info(error)
					self.info_label.set_text(error)
					#self.spinn.destroy()
				
			else:
				info = "Already existed,pass"
				logger.info(info)
				self.info_label.set_text(info)
			
				self.spinn.destroy()
				
