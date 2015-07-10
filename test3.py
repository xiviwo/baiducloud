import sys,os
import datetime
import fcntl
import subprocess
from threading import Thread


def log_worker(stdout):
    ''' needs to be in a thread so we can read the stdout w/o blocking '''
    #username, hostname = os.environ.get('USER'), socket.gethostname()
    #log_file = 'log.txt'
    #log = open(log_file, 'a')
    while True:
        output = non_block_read(stdout).strip()
        if output:
            ''' [Tue Oct 30 22:13:13 2012 cseibert@host1]> '''
            prompt = '[%(timestamp)s ] \n' % dict(
                    timestamp=datetime.datetime.now().strftime('%a %b %d %H:%M:%S %Y'))
            print prompt + output
            #log.write(prompt + output + '\n')
    #log.close()


def non_block_read(output):
    ''' even in a thread, a normal read with block until the buffer is full '''
    fd = output.fileno()
    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
    try:
        return output.read()
    except:
        return ''


if __name__ == '__main__':
	timestamp=datetime.datetime.now().strftime('%a %b %d %H:%M:%S %Y')
	print(timestamp)
	mysql_process = subprocess.Popen(
		["ping","localhost"],
		stdin=sys.stdin,
		stdout=subprocess.PIPE,
		stderr=subprocess.PIPE)

	thread = Thread(target=log_worker, args=[mysql_process.stdout])
	thread.daemon = True
	thread.start()

	mysql_process.wait()
	thread.join(timeout=1)


