import subprocess, time, sys,datetime
class FlushFile(object):
	"""Write-only flushing wrapper for file-type objects."""
	def __init__(self, f):
		self.f = f
	def write(self, x):
		self.f.write(x)
		#self.f.flush()
	def flush(self):
		self.f.flush()
# Replace stdout with an automatically flushing version
sys.stdout = FlushFile(sys.__stdout__)

def execute(command):
	process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

	# Poll process for new output until finished
	while True:
		sys.stdout.flush()
		nextline = process.stdout.readline()
		if nextline == '' and process.poll() != None:
			break
		print(datetime.datetime.now().strftime('%a %b %d %H:%M:%S %Y'))
		sys.stdout.write(nextline)
		sys.stdout.flush()

	output = process.communicate()[0]
	exitCode = process.returncode

	if (exitCode == 0):
		return output
	else:
		raise ProcessException(command, exitCode, output)

print(datetime.datetime.now().strftime('%a %b %d %H:%M:%S %Y'))
execute("ping localhost")
