from gi.repository import Gtk
import json,os
from log import logger
from gi.repository import GdkPixbuf
import settings
import cloudapi
import utils
from subprocess import Popen, PIPE, STDOUT
import queue
import re

from Spinner import SpinnerDialog
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


class DownloadDialog(Gtk.Dialog):
	__metaclass__ = Singleton
	def __init__(self,parent,file_list=[],tokens=None):
		Gtk.Dialog.__init__(self, "Download Task", parent, 0)
		self.file_list = file_list
		self.downlink = []
		self.tokens = tokens
		#self.file_list = nlist
		#self.remove_list = file_list
		self.current_selection = None

		#self.draw_widget(file_list)
		#def draw_widget(self,file_list):
		self.set_default_size(1100, 500)
		self.set_border_width(10)


		box = self.get_content_area()

		##							   num,pix,filename,size,path,isdir,fsid,cate,spath,speed,progress,status
		#                              0   1   2        3     4    5     6    7    8     9     10       11
		self.liststore = Gtk.ListStore(int,GdkPixbuf.Pixbuf,str, str, str,int,str,int,str,str,int,str)
		self.liststore.connect("row-changed",self.row_changed)
		self.fill_liststore(self.file_list)


		#creating the treeview, making it use the filter as a model, and adding the columns
		self.treeview = Gtk.TreeView(model=self.liststore)
		for i, column_title in enumerate(["Num","Thumb","File", "Size","Status", "Saving Path","Speed","Progress"]):
			
			if column_title == "Thumb":
				
				renderer_pixbuf = Gtk.CellRendererPixbuf()
				
				column = Gtk.TreeViewColumn(column_title, renderer_pixbuf,pixbuf=i)
			elif column_title == "Saving Path":
				
				renderer = Gtk.CellRendererText()
				column = Gtk.TreeViewColumn(column_title, renderer,text=8)
			elif column_title == "Speed":
				
				renderer = Gtk.CellRendererText()
				column = Gtk.TreeViewColumn(column_title, renderer,text=9)
			elif column_title == "Status":
				
				renderer = Gtk.CellRendererText()
				column = Gtk.TreeViewColumn(column_title, renderer,text=11)
			elif column_title == "Progress":
				renderer = Gtk.CellRendererProgress()
				column = Gtk.TreeViewColumn(column_title, renderer,
				value=1)

			else:
				renderer = Gtk.CellRendererText()
				column = Gtk.TreeViewColumn(column_title, renderer,text=i)
			self.treeview.append_column(column)

		self.treeview.props.activate_on_single_click = False
		self.treeview.connect("row-activated",self.on_row_double_click)


		self.selection = self.treeview.get_selection()
		self.selection.connect("changed", self.on_tree_selection_changed)
		self.selection.set_mode(Gtk.SelectionMode.MULTIPLE)
		
 

		self.buttons = list()
		for act in ["Select All","Unselect All", "Start Task","Stop Task", "Remove Task"]:
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
	
		box.show_all()
	def row_changed(self,store,path,treeiter):
		print("rowchange:",path)
		row = tuple( i for i in store[path] )
		
		print(row)
		print(self.file_list)
		self.file_list[int(path.to_string())] = row
		print(self.file_list)
		
	def fill_liststore(self,file_list):
		if file_list:
			for i,filerow  in enumerate(file_list):

				self.liststore.append(list(filerow))

	def on_tree_selection_changed(self,selection):
		#print(selection.get_selected_rows() )
		references = []
		self.current_selection = selection.get_selected_rows()

	def on_row_double_click(self,treeview,treepath,treeviewcolumn):
		print("Double click")
	def on_select_all_button_clicked(self,*arg):
		self.selection.select_all()
	def on_unselect_all_button_clicked(self,*arg):
		self.selection.unselect_all()

	def set_value(self,num,value,pos):
		path = Gtk.TreePath(num)
		treeiter = self.liststore.get_iter(path)
		self.liststore.set_value(treeiter, pos, value)
		#self.liststore.row_changed(path,treeiter)

	def get_down_link(self,link_data,error):
		
		if not error:
			
			link,fsid,num = link_data
			logger.debug("Download Link Ready = %s"%str(link))
			
			for i,row in enumerate(self.downlink):
				if row[3] == fsid:
					listrow = list(row)
					listrow[1] = link
					self.downlink[i] = tuple(listrow)
					self.q.put(self.downlink[i])
					break
			print('----async---',self.downlink)
			
			print(self.q)
		
			status = "Download Link Ready"
			self.set_value(num,status,11)
		else:
			logger.debug("Get download link error %s"%str(error))
		self.spinn.destroy()
	def download_progress():
		while not self.q.empty():
				task = self.q.get()
				print(task)
				fn = task[0]
				link = task[1]
				spath = task[2]
				url = re.sub("http://([^/]*)/",'http://hot.baidupcs.com/',link)
				#cmd=['aria2c','-c', '-s1', '-x1','-j1', url,'-o',fn]
				cmd="cd %s && aria2c -c -s1 -x1 -j1 -o '%s' '%s'"%(spath,fn,url)
				logger.info( cmd )
				print(cmd)
				import shlex 
				#os.system("cd %s && %s"%(downpath,cmd))
				#cmd = 'ls /etc/fstab /etc/non-existent-file'
				self.downproc = Popen(shlex.split(cmd), shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
				output = self.downproc.stdout.read()
				#output,errs = self.downproc.communicate()
				#STDOUT
				output = output.decode('utf-8')
				print(output)
				speedmat = re.search("\|([^|]*\/s)\|",output)
				if speedmat:
					speed = speedmat.group(1).strip()
				else:
					spmat =  re.findall("DL:([^\s|^\]]*)",output,re.MULTILINE)
					if spmat :
						speed = spmat[len(spmat)-1]
					else:
						speed = '0B/s'
				errmat = re.search("(errorCode[^\n]*status[^\n]*)",output)
				progmat = re.findall("\(([^)]*)\)",output,re.MULTILINE)
				progress = 0
				if progmat:
						progress = int(progmat[len(progmat)-1].strip("%"))
				error = ''
				if speedmat :
					error = errmat.group(1)
					self.set_value(num,error,11)
				print(speed,progress)
				self.set_value(num,speed,9)
				self.set_value(num,progress,10)

	def on_start_task_button_clicked(self,*arg):
		if self.is_current_selection_null(): 
			return
		self.spinn = SpinnerDialog(self)
		self.spinn.show()
		store,treepaths = self.current_selection
		self.q = queue.LifoQueue()

		for tpath in treepaths:
		
			print(store[tpath][2],store[tpath][4])
			row = store[tpath]
			num = row[0]
			filename = row[2]
			path = row[4]
			isdir = row[5]
			fsid = row[6] 
			spath = row[8]
			if not self.in_list(row,self.downlink):
				print(filename,fsid)
				npath = os.path.join(path,filename)
				utils.async_call(cloudapi.get_dlink,self.tokens,fsid,npath,num,
						 callback=self.get_down_link)
				self.downlink.append((filename,None,spath,fsid))
		print('0000sync888',self.downlink)


	def on_stop_task_button_clicked(self,*arg):
		print('-------------after-------------',self.downlink)
		self.downproc.terminate()
	def on_remove_task_button_clicked(self,*arg):
		if self.is_current_selection_null(): 
			return

		store,treepaths = self.current_selection
	

		for tpath in treepaths:
			task = ()
			for i in store[tpath]:
				task = task + (i,)
		
			if task in self.file_list:
				
				self.file_list.remove(task)
		self.liststore.clear()
		self.fill_liststore(self.file_list)

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

	def remove_task_in_list(self,task,dlist):
		for row in dlist:
			
			if task[2] == row[2]:
				old_task = row
				break
		dlist.remove(old_task)

	def in_list(self,item,dlist):
		for row in dlist:
			print(item[6],row[3])
			if item[6] == row[3]:
				return True
			
		return False
