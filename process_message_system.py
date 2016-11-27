#
# Name: Logan Finlayson
# ID:   2969317
# UPI:  lfin100
#
# Assignment: CompSci 340 A1 S2 2016
#


import os
import pickle
import sys
import atexit
import time
import threading
ANY = "any"


class MessageProc:

    def start(self, *args):
        pid = os.fork()
        if pid == 0:
            self.main(*args)
            sys.exit()
        else:
            return pid


    def main(self):
        atexit.register(self.exit_handler)
        self.pipeName = ('/tmp/pipe' + str(os.getpid()))
        os.mkfifo(self.pipeName)
        self.pipeDict = {}
        self.pipeReceiver = Receiver(self.pipeName)
        self.pipeReceiver.setDaemon(True)
        self.pipeReceiver.start()


    def give(self, pid, label, *values):

        while os.path.exists('/tmp/pipe'+str(pid)) == False:

            if ('/tmp/pipe'+str(pid)) in self.pipeDict:
                return

            time.sleep(0.01)

        if ('/tmp/pipe' + str(pid)) not in self.pipeDict:
            self.pipeDict['/tmp/pipe' + str(pid)] = 1

        fifo = open('/tmp/pipe'+str(pid),'wb')
        dictionary = {'label':label, 'values':values}
        pickle.dump(dictionary, fifo)
        fifo.close()


    def receive(self, *messages):
        timeout = next((x for x in messages if isinstance(x, TimeOut)), None)

        self.pipeReceiver.lock.acquire()
        qlength = len(self.pipeReceiver.queue)
        self.pipeReceiver.lock.release()

        if qlength == 0:

            with self.pipeReceiver.condition:

                if timeout != None:
                    self.pipeReceiver.interrupt = False
                    self.pipeReceiver.condition.wait(timeout.time)

                    if self.pipeReceiver.interrupt == False:
                        return timeout.action()

                else:
                    self.pipeReceiver.condition.wait()

        while True:
            self.pipeReceiver.lock.acquire()
            qlength = len(self.pipeReceiver.queue)
            self.pipeReceiver.lock.release()

            for i in range(qlength):

                self.pipeReceiver.lock.acquire()
                label = self.pipeReceiver.queue[i]['label']
                self.pipeReceiver.lock.release()

                for message in messages:

                    if isinstance(message, Message):

                        if message.label == label and message.guard():
                            self.pipeReceiver.lock.acquire()
                            value = message.action(*self.pipeReceiver.queue.pop(i)['values'])
                            self.pipeReceiver.lock.release()
                            return value

                        elif message.label == ANY and message.guard():

                            self.pipeReceiver.lock.acquire()
                            value = message.action(*self.pipeReceiver.queue.pop(i)['values'])
                            self.pipeReceiver.lock.release()
                            return value

            if timeout != None:
                with self.pipeReceiver.condition:
                    self.pipeReceiver.interrupt = False
                    self.pipeReceiver.condition.wait(timeout.time)

                    if self.pipeReceiver.interrupt == False:
                        return timeout.action()

            time.sleep(0.01)


    def exit_handler(self):
        try:
            os.remove('/tmp/pipe' + str(os.getpid()))
        except FileNotFoundError:
            pass



class Receiver(threading.Thread):

    def __init__(self, pipeName):
        super().__init__()
        self.pipeName = pipeName
        self.queue = []
        self.lock = threading.RLock()
        self.condition = threading.Condition()
        self.interrupt = False

    def run(self):
        fifo = open(self.pipeName, 'rb')

        while True:
            try:
                recDictionary = pickle.load(fifo)
                with self.condition:

                    self.lock.acquire()
                    self.queue.append(recDictionary)
                    self.lock.release()

                    self.interrupt = True
                    self.condition.notify()

            except EOFError:
                time.sleep(0.01)

        fifo.close()



class Message:
    def __init__(self, label, guard = lambda: True, action=lambda: None):
        self.label = label
        self.guard = guard
        self.action = action



class TimeOut:
    def __init__(self, time, action=lambda: None):
        self.time = time
        self.action = action

