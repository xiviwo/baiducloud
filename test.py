from __future__ import print_function
from subprocess import PIPE, Popen
from threading  import Thread
import sys

try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty  # python 3.x

ON_POSIX = 'posix' in sys.builtin_module_names

def enqueue_output(out, queue):
	sys.stdout.flush()
	out.flush()
	for line in iter(out.readline, b''):
		
		print('--------------',line)
		line = line.decode(sys.stdout.encoding)
		queue.put(line)
	out.close()

def main():
	p = Popen(["ping","localhost"], stdout=PIPE, bufsize=0, close_fds=ON_POSIX)
	q = Queue()
	t = Thread(target=enqueue_output, args=(p.stdout, q))
	t.daemon = True # thread dies with the program
	t.start()
	
	#initially the queue is empty and stdout is open
	#stdout is closed when enqueue_output finishes
	#then continue printing until the queue is empty 
	print('here')
	while not p.stdout.closed or not q.empty():
		#print(p.stdout.closed,q.empty())
		p.stdout.flush()
		try:
		    line = q.get_nowait()
		except Empty:
		    continue
		else:
		    print('fsafsfas',line, end='')
	return 0

if __name__ == '__main__':
    sys.exit(main())
