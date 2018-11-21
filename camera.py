import os.path, time, optparse
import threading, queue, signal
import requests
from debug import Debug


def ticks2Secs(x):
    coeff = 1 / 10000000.0 # from MSDN
    return x * coeff



class CaptureThread(threading.Thread):

    TIMEOUT_S = 2

    def __init__(self):
        super().__init__()
        self.q = queue.Queue()

    def quit(self):
        self.q.put('asdasds')

    def run(self):
        Debug()
        while True:
            try:
                msg = self.q.get(block=True, timeout=self.TIMEOUT_S)
            except queue.Empty:
                pass
            else:
                Debug('quitting...')
                break

            GET_URL = 'http://dbs.digiscura.com/PiCamArray/'
            Debug(GET_URL)
            startTime = time.time()
            r = requests.get(GET_URL)
            endTime = time.time()
            httpDuration = endTime - startTime
            
            if r.status_code != 200:
                Debug('Error on', GET_URL, ':', r.status_code)
                break
            
            a, b, c = r.text.split(':')
            nowTicks, shotTimeTicks, shotIndex = int(a), int(b), int(c)
            if shotTimeTicks < nowTicks:
                continue
            
            Debug('Now:', nowTicks, 'ShotTime:', shotTimeTicks, 'ShotIndex:', shotIndex)
            nowSecs = ticks2Secs(nowTicks)
            shotTimeSecs = ticks2Secs(shotTimeTicks)

            sleepSecs = shotTimeSecs - (nowSecs + (httpDuration/2))
            Debug('sleeping %f seconds...' % sleepSecs)
            time.sleep(sleepSecs)

            Debug('Taking photo...')
            PHOTO_PATH = '/Users/patrick/Desktop/2018-04-07_20-07-08.jpg'
            with open(PHOTO_PATH, 'rb') as f:
                bdata = f.read()
                POST_URL = 'http://dbs.digiscura.com/PiCamArray/SubmitShot'
                Debug('Posting %i bytes to %s:' % (len(bdata), POST_URL))
                r = requests.post(POST_URL, params={
                    'piId': 0,
                    'shotId': shotIndex
                }, data={
                    '_filedata': bdata
                })
                Debug('POST response:', r.status_code)

                
from optparse import OptionParser
parser = OptionParser()
parser.add_option("-q", "--quit", dest="quit",
                  help="Quit running server", action='store_true', default=False)
parser.add_option("-c", "--capture", dest="capture",
                  help="Trigger photo capture on server", action='store_true', default=False)
parser.add_option("-p", "--pidfile", dest="pidfile",
                  help="Quit running server", action='store_true',
                  default=os.path.join(os.getcwd(), 'camera.pid'))
options, args = parser.parse_args()

def main():
    if options.quit:
        if os.path.isfile(options.pidfile):
            with open(options.pidfile, 'r') as f:
                pid = int(f.read())
                Debug('Sending quit signal...')
                os.kill(pid, signal.SIGQUIT)
        else:
            Debug('No server process running.')
    elif options.capture:
        Debug('Schedule shot')
        r = requests.get('http://dbs.digiscura.com/PiCamArray/ScheduleShot')
        if r.status_code != 200:
            Debug('Error on', 'ScheduleShot', ':', r.status_code)        
    else:

        # check for existing server process
        if os.path.isfile(options.pidfile):
            with open(options.pidfile, 'r') as f:
                try:
                    pid = int(f.read())
                    Debug(pid)
                    os.kill(pid, 0)
                except: # ProcessLookupError: process not running, ValueError: contents not an integer
                    Debug('removing pid file', options.pidfile)
                    os.remove(options.pidfile) # process is not running anymore, must have errored out
                else:
                    Debug('Server already running; quitting....')
                    return
                    
        Debug(options.pidfile, os.getpid())
        pidFile = open(options.pidfile, 'w')
        Debug()
        pidFile.write(str(os.getpid()))
        pidFile.flush()
        Debug()
        pidFile = None
        thread = CaptureThread()
        Debug()
        thread.start()
        Debug()
        
        def handle_signal(x, y):
            if x == signal.SIGQUIT:
                thread.quit()
                thread.join()
                os.remove(options.pidfile)
                # app exits
        signal.signal(signal.SIGQUIT, handle_signal)

        # main thread automatically waits for capture thread to finish

main()
