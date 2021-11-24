from utils.Scale import Scale
from typing import Iterator, List, Tuple, Text
from functools import wraps
from random import choices, choice
from math import ceil
from time import sleep


class Engine:

    def __init__(self, scale:Scale=None):
        class Iterable:
            def __init__(self, func):
                self.__f = func
            
            def __call__(self, *args, **kwargs)->List:
                return self.__f(*args, **kwargs)
            
            def generator(self, *args, **kwargs)->Iterator:
                return iter(self.__f(*args, **kwargs))
        
        self.__scale: Scale
        if scale:
            self.__scale = scale
        self.__chord_history: List = []
        self.__note_history: List = []
        self._delay = 0.25
        
        self.get_chord_sequence = Iterable(self.get_chord_sequence)
        self.get_note_sequence = Iterable(self.get_note_sequence)
        
        
    @property
    def scale(self)->Scale:
        try:
            return self.__scale
        except AttributeError:
            raise ValueError(f"No value associated with property {repr(self)}.scale")
    
    @scale.setter
    def scale(self, s:Scale):
        if not isinstance(s, Scale):
            raise TypeError("Expected type 'Scale'")
        self.__scale = s
    
    @property
    def chord_history(self)->List:
            return self.__chord_history
        
    @chord_history.setter
    def chord_history(self, history:List):
        if not isinstance(history, List):
            raise TypeError("Expected type 'List'")
        self.__chord_history = history
    
    @property
    def note_history(self)->List:
        return self.__note_history
        
    @note_history.setter
    def note_history(self, history:List):
        if not isinstance(history, List):
            raise TypeError("Expected type 'List'")
        self.__note_history = history
    
    def clear_history(self):
        self.chord_history = []
        self.note_history = []
    
    def next_chord(self, *args, **kwargs):
        raise NotImplementedError
    
    def next_note(self, *args, **kwargs):
        raise NotImplementedError
    
    def get_chord_sequence(self, *args, **kwargs):
        self.get_chord_sequence.__func__.generator: Generator
        raise NotImplementedError
    
    def get_note_sequence(self, *args, **kwargs):
        self.get_note_sequence.__func__.generator: Generator
        raise NotImplementedError
        
    def play_chord(self, chords:List[Tuple], *, verbose=True, sustain=True):
        def _check_if_midi_(_):
            raise Exception(_)
        midi:bool
        try:
            [_check_if_midi_(False) if isinstance(chord[0], str) else _check_if_midi_(True) for chord in chords if len(chord)>0]
        except Exception as e:
            midi = e.args[0]
            
        for chord in chords:
            if len(chord) == 0:
                if verbose:
                    print(f"---{self._delay}---")
                sleep(self._delay)
                continue
            if midi:
                _ = ("" if sustain else "m") + "".join(self.scale.semitones_to_letter_notes(chord))
            else:
                _ = ("" if sustain else "m") + "".join(chord)
            if verbose:
                print(_)
            self.scale.midi.play(_)
            sleep(self._delay)
    
    def __repr__(self):
        return self.__class__.__name__


class StupidEngine(Engine):
    def next_chord(self, silence_ratio=0.25, inversion=0, low_notes=True):
        oct = [0, 1, 2]
        choi = [0,1,2,3,4,5,6,7]
        wts = [silence_ratio]+[(1-silence_ratio)/7]*7
        self.chord_history.append((lambda x: self.scale.chord(choice(oct)+x, inversion=inversion, low_notes=low_notes) if x>0 else () )(choices(choi, wts)[0]))
        return self.chord_history[-1]
    
    def next_note(self, *args, **kwargs):
        oct = [0, 1, 2]
        choi = [0,1,2,3,4,5,6,7]
        wts = [silence_ratio]+[(1-silence_ratio)/7]*7
        self.note_history.append((lambda x: self.scale.intervals[choice(oct)+x,] if x>0 else () )(choices(choi, wts)[0]))
        return self.note_history
    
    def get_chord_sequence(self, *, duration=4.0, low_notes=True, octave=3, silence_ratio=0.25, midi=False):
        self.chord_history = []
        _len = ceil(duration/self._delay)
        for _ in range(_len):
            self.chord_history.append(self.next_chord(silence_ratio=silence_ratio, low_notes=low_notes))
            
        if not midi:
            return [
                self.scale.semitones_to_letter_notes(_)
                for _ in self.chord_history
            ]
        return self.chord_history
        
    def get_note_sequence(self, *args, **kwargs):
        raise NotImplementedError
