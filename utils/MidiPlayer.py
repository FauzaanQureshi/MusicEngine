from os import chdir, getpid, remove
from subprocess import Popen, PIPE
from multiprocessing import Process, Pipe
from utils.config import CONFIG


def util(conn):
    chdir(CONFIG.get('java_path', '..'))
    print("Child Process: ", getpid(), PIPE)
    with open("../Error.log", 'w+') as err:
        p = Popen(['java', 'JavaProg.MusicSheetReader', 'p'], stdin=PIPE, stdout=PIPE, stderr=err)
        while p.poll() is None:
            p.stdin.write(conn.recv().encode())
            p.stdin.flush()
    #err.close()
    #remove("../Error.log")
    

class MidiPlayer:

    class UninitializedError(Exception):
        def __init__(self):
            self.message = "Initialize MIDI Player by calling start()"
            super().__init__(self.message)
    
    
    class MIDIError(Exception):
        def __init__(self):
            self.message = "Error occurred in MIDI Player subprocess\n"
            super().__init__(self.message)
    
    
    class InvalidInstrument(Exception):
        def __init__(self):
            self.message = "Instrument code must be between (0-127)\n"
            super().__init__(self.message)
    

    def __init__(self, file=None, fileno=4):
        self.__reader__, self.__writer__ = Pipe(False)
        self._process = Process(target=util, args=(self.__reader__,))
        print("INIT MidiPlayer", getpid())
        self._running = False
    
    def change_instrument(self, instrument):
        if isinstance(instrument, str):
            if instrument.isdigit():
                self.__writer__.send(f"I<{int(instrument)%128}>")
            else:
                __ = []
                for _ in instrument:
                    if _.isdigit():
                        __.append(_)
                
                self.__writer__.send(f"I<{int(''.join(__))%128}>")
        elif isinstance(instrument, int):
            self.__writer__.send(f"I<{instrument%128}>")
        else:
            raise MidiPlayer.InvalidInstrument()
        
    
    def listen(function):
        def _wrapper(*args, **kwargs):
            function(*args, **kwargs)
            print("MIDI ERROR Poll", args[0].rc.poll())
            if args[0].rc.poll():#MidiPlayer.errorListener and MidiPlayer.errorListner.file.tell()!=0:
                print(args[0].rc.recv())
                args[0].rc.close()
                raise MidiPlayer.MIDIError()
        
        return _wrapper
        
    #@listen
    def play(self, notes):
        if not self._running:
            raise self.UninitializedError()

        self.__writer__.send(notes)
        
        #if self.rc.poll():
        #    raise self.MIDIError()

    def start(self):
        self._process.start()
        print("start process alive ", self._process.is_alive())
        self._running = True

    def stop(self):
        self.play('q')
        self._process.terminate()
        self._running = False
    
    @property
    def running(self):
        return self._running
        
    def refresh(self):
        self.play('q')
        self._process._popen.kill()
        self._process.terminate()
        self._process = Process(target=util, args=(self.__reader__,))
        self.start()
        
    def __del__(self):
        self._process.terminate()
