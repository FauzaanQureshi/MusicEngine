'''
Defines Engine classes that 
Returns note (sequence) / chord (sequence)
'''


from utils.Scale import Scale
from typing import Iterator, List, Tuple, Text
from functools import wraps
from random import choices, choice
from math import ceil
from time import sleep


def seconds_to_bar(sec:float, bpm:int):
    '''
    Convert Seconds to Bar.
    
    @params:
        sec: float
        bpm: int
    '''
    return sec*(bpm/60)
    

def bar_to_seconds(bar:int, bpm:int):
    '''
    Convert Bar to Seconds.
    
    @params:
        bar: int
        bpm: int
    '''
    return bar/(bpm/60)


class Engine:

    def __init__(self, scale:Scale=None):
        class Iterable:
            '''
            Wrapper for get_<X>_sequence methods to add 'generator' property.
            '''
            def __init__(self, func):
                self.__f = func
            
            def __call__(self, *args, **kwargs)->List:
                return self.__f(*args, **kwargs)
            
            def generator(self, *args, **kwargs)->Iterator:
                '''
                Returns Iterator from get_<X>_sequence method.
                '''
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
        '''
        Scale object. Raises ValueError if no Scale is specified.
        '''
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
        '''
        List object.
        next_chord method adds new entry. 
        Each entry a Tuple containing 
        < Tuple(note_number, octave), Tuple(note_number, octave), ... >
        
        get_chord_sequence method empties exisiting List
        before entering new entries.
        '''
        return self.__chord_history
        
    @chord_history.setter
    def chord_history(self, history:List):
        if not isinstance(history, List):
            raise TypeError("Expected type 'List'")
        self.__chord_history = history
    
    @property
    def note_history(self)->List:
        '''
        List object.
        next_note method adds new entry. 
        Each entry a Tuple containing 
        < Tuple(note_number, octave) >
        
        get_note_sequence method empties exisiting List
        before entering new entries.
        '''
        return self.__note_history
        
    @note_history.setter
    def note_history(self, history:List):
        if not isinstance(history, List):
            raise TypeError("Expected type 'List'")
        self.__note_history = history
    
    def clear_history(self):
        self.chord_history = []
        self.note_history = []
    
    def next_chord(self, *args, **kwargs)->Tuple:
        '''
        Returns a chord and Inserts it to the chord_history
        '''
        raise NotImplementedError
    
    def next_note(self, *args, **kwargs)->Tuple:
        '''
        Returns a note and Inserts it to the note_history
        '''
        raise NotImplementedError
    
    def get_chord_sequence(self, *args, **kwargs)->List:
        '''
        Empties chord_history. 
        Returns a sequence of chords and Inserts it to the chord_history
        '''
        raise NotImplementedError
    
    def get_note_sequence(self, *args, **kwargs)->List:
        '''
        Empties note_history. 
        Returns a sequence of notes and Inserts it to the note_history
        '''
        raise NotImplementedError
        
    def play(self, blob:List[Tuple], *, verbose=True, sustain=True, octave=3):
        '''
        Invokes MidiPlayer in Scale to play given sequence.
        
        @params:
            blob: List[Tuple]. Acceptable forms:
                [((midi_note_number, octave), (midi_note_number, octave), ...), (), ...]
                [((midi_note_number, octave),), ((midi_note_number, octave),), (), ...]
                [(LetterNoteNameOctave, LetterNoteNameOctave, ...), (), ...]
                [(LetterNoteNameOctave,), (LetterNoteNameOctave,), (), ...]
            verbose (Optional): bool - Show/Hide Notes being played.
            sustain (Optional): bool - False: sends 'mute' signal before playing next item in blob
            octave  (Optional): int - If blob items contain midi-number, Translates them to note in
                    specified octave. If blob items contain LetterNotes, has no effect.
        '''
        def _check_if_midi_(_):
            raise Exception(_)
        midi:bool
        try:    # Loop through blob to find first non-empty item and check if it's midi. Raise exception to exit loop.
            [_check_if_midi_(False) if isinstance(_[0], str) else _check_if_midi_(True) for _ in blob if len(_)>0]
        except Exception as e:
            midi = e.args[0]
            
        for b in blob:
            if len(b) == 0:
                if verbose:
                    print(f"---{self._delay}---")
                sleep(self._delay)
                continue
            if midi:
                _ = ("" if sustain else "m") + "".join(self.scale.semitones_to_letter_notes(b, octave=octave))
            else:
                _ = ("" if sustain else "m") + "".join(b)
            if verbose:
                print(_)
            self.scale.midi.play(_)
            sleep(self._delay)
    
    def rhythm(self, rhy):
        _instrument = self.scale.midi.instrument
        self.scale.midi.instrument = 115
        for __ in range(4):
            _ = True
            for r in rhy:
                if r:
                    print("O", end="")
                    self.scale.midi.play("mG4" if _ else "mC#5")
                    _ = False
                else:
                    print("-", end="")
                    sleep(rhy.min_interval)
            print()
        self.scale.midi.instrument = _instrument
    
    def __repr__(self):
        return self.__class__.__name__


class StupidEngine(Engine):
    '''
    Stupid because generates chord/note (sequence) by random pooling.
    '''
    def next_chord(self, silence_ratio=0.25, inversion=0, low_notes=True):
        '''
        Returns a random chord and Inserts it to the chord_history
        
        @params:
            silence_ratio: float - Ratio of Silence:Notes. Ex.: 1:4
            inversion: int - To be Implemented
            low_notes: bool - True: Adds 1st and 5th Note from 1 octave lower in a chord
        '''
        if len(self.chord_history)>128:
            self.chord_history.clear()
        oct = [0, 1, 2]
        choi = [0,1,2,3,4,5,6,7]
        wts = [silence_ratio]+[(1-silence_ratio)/7]*7
        self.chord_history.append((lambda x: self.scale.chord(choice(oct)+x, inversion=inversion, low_notes=low_notes) if x>0 else () )(choices(choi, wts)[0]))
        return self.chord_history[-1]
    
    def next_note(self, silence_ratio=0.25):
        '''
        Returns a random note and Inserts it to the note_history
        
        @params:
            silence_ratio: float - Ratio of Silence:Notes. Ex.: 1:4
        '''
        if len(self.note_history)>128:
            self.note_history.clear()
        oct = [0, 1, 2]
        choi = [0,1,2,3,4,5,6,7]
        wts = [silence_ratio]+[(1-silence_ratio)/7]*7
        self.note_history.append((lambda x: self.scale.intervals[choice(oct)+x,] if x>0 else () )(choices(choi, wts)[0]))
        return self.note_history[-1]
    
    def get_chord_sequence(self, *, duration=4.0, low_notes=True, octave=3, silence_ratio=0.25, midi=False, **kwargs):
        '''
        Empties chord_history. Repeatedly calls next_chord to generate a sequence.
        Returns a sequence of chords and Inserts it to the chord_history
        
        @params: Optional
            duration: float - Total playtime of sequence, in seconds
            silence_ratio: float - Ratio of Silence:Notes. Ex.: 1:4
            low_notes: bool - True: Adds 1st and 5th Note from 1 octave lower in a chord
            midi: bool - True: Returns chord containing LetterNotes
                         False: Returns chord containing midi-number-notes
            octave: int - If midi is False, Translates them to note in specified octave
        '''
        self.chord_history = []
        _len = ceil(duration/self._delay)
        for _ in range(_len):
            self.next_chord(silence_ratio=silence_ratio, low_notes=low_notes, **kwargs)
            
        if not midi:
            return [
                self.scale.semitones_to_letter_notes(_, octave=octave)
                for _ in self.chord_history
            ]
        return self.chord_history
        
    def get_note_sequence(self, *, duration=4.0, octave=3, silence_ratio=0.25, midi=False):
        '''
        Empties note_history. Repeatedly calls next_note to generate a sequence.
        Returns a sequence of notes and Inserts it to the note_history
        
        @params: Optional
            duration: float - Total playtime of sequence, in seconds
            silence_ratio: float - Ratio of Silence:Notes. Ex.: 1:4
            midi: bool - True: Returns sequence containing LetterNotes
                         False: Returns sequence containing midi-number-notes
            octave: int - If midi is False, Translates them to note in specified octave
        '''
        self.note_history = []
        _len = ceil(duration/self._delay)
        for _ in range(_len):
            self.next_note(silence_ratio=silence_ratio)
            
        if not midi:
            return [
                self.scale.semitones_to_letter_notes(_, octave=octave)
                for _ in self.note_history
            ]
        return self.note_history
