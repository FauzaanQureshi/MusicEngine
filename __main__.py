from time import monotonic as count
from msvcrt import kbhit, getch

class __Variable__(type):
    state = {}
    
    def __delattr__(cls, k, v):
        __Variable__.state.pop(k, None)
    
    def __setattr__(cls, k, v):
        __Variable__.state[k]=v
 
    def __getattribute__(cls, k):
        try:
            return __Variable__.state[k]()
        except KeyError:
            return super(__Variable__).__getattribute__(k)


class Variable(metaclass=__Variable__):
    __slots__ = ()
    pass


def radio(engine, gen_func_lambda, *, octave=4, verbose=True, **kwargs):
    while not kbhit():
        engine.play(gen_func_lambda(), octave=octave, verbose=verbose, **kwargs)
    
if __name__=="__main__":
    from rhythm.Rhythm import Rhythm
    from utils.Scale import Scale, find_scale
    from engine.Engine import Engine, StupidEngine
    from engine.Engine import seconds_to_bar, bar_to_seconds
    from random import choice, random, sample, choices
    
    Variable.low_notes = lambda : choice((True, False))
    Variable.silence_ratio = random
    Variable.inversion = lambda : choice((1, 0, 2))
    
    _chord_lambda = "lambda : (se.next_chord(silence_ratio=Variable.silence_ratio, inversion=Variable.inversion, low_notes=Variable.low_notes),)"
    _note_lambda = "lambda : (se.next_note(silence_ratio=Variable.silence_ratio),)"
    
    def random_chord_prog(scale, delay=1.5, instrument=51, mute_prev=True):
        def r(n=1, **kwargs):
            for k,v in kwargs.items():
                if hasattr(r, k):
                    setattr(r, k, v)
            scale.midi.instrument = r.instrument
            scale.chord_progression([scale.chord(i) for i in  r.pattern*n], delay=r.delay, mute_prev=r.mute_prev)
            scale.midi.play('m')
        r.delay = delay
        r.instrument = instrument
        r.mute_prev = mute_prev
        pattern = sample([1,2,3,4,5,6,7],4)
        r.pattern = pattern
        random_chord_prog.repeat = r
        scale.midi.instrument = instrument
        print("Instrument:", instrument, instrument.name)
        print("Pattern:", r.pattern)
        scale.chord_progression([scale.chord(i) for i in  pattern], delay=delay, mute_prev=mute_prev)
        scale.midi.play('m')
        return pattern
    
    def follow_rhythm(rhy, se):
        se.clear_history()
        se._delay = rhy.min_interval
        
        for r in rhy:
            if r:
                se.next_note(silence_ratio=0)
            else:
                se.note_history.append(())
    
    rhy = Rhythm()
    rhy.bpm = 40
    rhy.min_interval = 1/16
    rhy.rhythm = "---O---O-O-O-O---O---O-O-O-O---O---O-O-O-O---O-O"
    
    def rand_rhythm():
        s = []
        for _ in range(16):
            c = choices([0,1,2,3], [3/6, 1/6, 1/6, 1/6])[0]
            if not c:
                s += ["-", "-", "-"]
            else:
                x = ['-', '-', '-']
                x[c-1] = 'O'
                s += x
        return "".join(s)