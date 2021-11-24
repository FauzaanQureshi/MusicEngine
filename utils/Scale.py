from utils.MidiPlayer import MidiPlayer
from utils.CircularOctave import CircularOctave
from time import sleep


class Scale:
    note_name = ('C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B')
    semitones = CircularOctave(*range(1,13))
    rules = dict(
        major_scale = (1,1,0,1,1,1,0),
        minor_scale = (1,0,1,1,0,1,1),
        harmonic_scale = (1,0,1,1,0,2,1),
        melodic_minor = (1,0,1,1,1,1,0),
    )
    
    def __init__(self, key, name=None):
        
        if isinstance(key, str):
            try:
                self._key = self.note_name.index(key.strip().upper())+1
            except ValueError:
                raise ValueError(f"Invalid key.\nValid keys:\n{self.note_name}\n{tuple(range(1, 13))}")
        elif isinstance(key, int) and 0<key<13:
            self._key = key
        else:
            raise TypeError(f"Invalid key type.\nValid keys:\n{self.note_name}\n{tuple(range(1, 13))}")
        
        self._name = name
        self._initialize()
        self.midi = MidiPlayer()
        self.__play_wrappers__()


    def _initialize(self):
        self.semitones.root_idx = self.key-1
        self.rule = self.rules.get(self.name, None)
        self.intervals = self.get_intervals()
        print(self.intervals)
        self.notes = {_:self.note_name[_-1] for _ in self.intervals}
    
    
    def __play_wrappers__(self):
        def _phrase(_obj, func):
            def _wrapper(*args, **kwargs):
                _obj.midi.play(func(*args, **kwargs))
            return _wrapper
        
        def _chord(_obj, func):
            def _wrapper(*args, **kwargs):
                _obj.midi.play(
                    "".join(
                        _obj.semitones_to_letter_notes(func(*args, **kwargs))
                    )
                )
            return _wrapper
        
        self.phrase.__func__.play = _phrase(self, self.phrase)
        self.chord.__func__.play = _chord(self, self.chord)
        

    def get_intervals(self):
        if not self.rule:
            raise NotImplementedError
        
        notes = [self.key]
        for step in self.rule[:-1]:
            for _ in range(step+1):
                n, o = next(self.semitones)
            notes.append(n)
        
        for _ in range(self.rule[-1]+1):
            next(self.semitones)
            
        return CircularOctave(notes)


    def chord(self, num, inversion=0, low_notes=True):
        _keys = (0, 2, 4)
        if low_notes:
            _keys = (-7, -3) + _keys
            
        self.intervals.root_idx = num-1
        chord = self.intervals[_keys]
        self.intervals.root_idx = self.key-1
        return chord
        

    def chord_progression(self, chords, delay=0.5, mute_prev=False):
        for chord in chords:
            notes = ''.join(self.semitones_to_letter_notes(chord))
            print(notes)
            self.midi.play(('m' if mute_prev else '') + notes+'--')
            sleep(delay)


    def phrase(self, phrase, root=4):
        mod_notes = {i:v for i,v in enumerate(self.notes.values(), 1)}
        invalid_note = lambda s: print(f"Invalid note '{s}'. Notes must be in scale. Playing 'C' note instead.") or 'C'
        get_note = lambda s: mod_notes.get(s, False) or invalid_note(s)
        
        oct_flag = True
        oct = 0
        notes = []
        special_cmd_stack = []
        
        for s in phrase:
            if s=='q' or s=='Q':
                print("Press 0 to Quit")
                break
            
            if s.isnumeric():
                if not oct_flag:
                    notes.append(f"{min(max(root+oct, 0), 7)}")
                notes.append(get_note(int(s)))
                oct_flag = False
                oct = 0
            elif s=='-':
                oct -= 1
            elif s=='+':
                oct += 1
            elif s==' ':
                notes.append(f"{min(max(root+oct, 0), 7)}-" if not oct_flag else "-")
                oct = 0
                oct_flag = True
            else:
                notes.append(f"{min(max(root+oct, 0), 7)}"+s if not oct_flag else s)
                oct = 0
                oct_flag = True
        
        if not oct_flag:
            notes.append(f"{min(max(root+oct, 0), 7)}")
        
        notes = ''.join(notes)
        print(f"Playing: {notes}")
        return notes


    def init_midi(self):
        self.midi.start()
        self.midi.play('C7---')
        sleep(3)


    def close_midi(self):
        self.midi.stop()
    
    
    @property
    def key(self):
        return self._key


    @key.setter
    def key(self, key):
        if isinstance(key, str):
            try:
                self._key = self.note_name.index(key.strip().upper())+1
            except ValueError:
                raise ValueError(f"Invalid key.\nValid keys:\n{self.note_name}\n{tuple(range(1, 13))}")
        elif isinstance(key, int) and 0<key<13:
            self._key = key
        else:
            raise TypeError(f"Invalid key type.\nValid keys:\n{self.note_name}\n{tuple(range(1, 13))}")
        
        self._initialize()


    @property
    def name(self):
        return self._name


    @name.setter
    def name(self, val):
        self._name = val
        self._initialize()


    @staticmethod
    def console():
        def change_scale():
            print("\n\nScales:")
            print(*[f"{i}. {k} " for i,k in enumerate(Scale.rules.keys(), 1)], sep='\n')
            name = int(input("\nSelect Scale: "))
            return tuple(Scale.rules.keys())[name-1]
            
        def menu():
            print("\n\n\n\n")
            print("1. Change Key")
            print("2. Change Scale")
            print("3. Show Notes")
            print("4. Show Chords")
            print("5. Play Phrase")
            print("6. Play Chords")
            print("7. Play Chord Progression")
            print("\n0. Exit\n\n")
        
        def play_chord():
            cin = -1
            print("\n\nPlay Chords <0 to exit>")
            while cin != 0:
                try:
                    if cin>0:
                        notes = scale.semitones_to_letter_notes(
                                    scale.chord(cin)
                                )
                        print(' '.join(notes))
                        scale.midi.play(
                            ''.join(notes)
                        )
                    cin = int(input('Chord>'))
                except ValueError:
                    continue
            print('\n\n')

        def play_chord_progression():
            print("\n\nPlay Chord Progressions <0 to exit>\n<Sample input: '1 2 3 2 1'>\n")
            delay=0.5
            while True:
                try:
                    cin = *map(int, input("\nProgression> ").split()),
                    if cin.count(0)>0:
                        break
                    else:
                        scale.chord_progression(
                            [
                                scale.chord(i)
                                for i in cin
                            ],
                            delay
                        )
                except ValueError:
                    try:
                        delay=float(input("\nDelay>"))
                    except ValueError:
                        continue
            print('\n\n')
        
        def play_phrase():
            print("\n\nPlay phrase. Valid chars: 'note numbers', ' ' for 1 note, '_' for ½ note, '.' for ¼ note\n0 to Exit\nNotes:")
            print({i:v for i,v in enumerate(scale.notes.values(), 1)})
            while True:
                try:
                    cin = input("Phrase>")
                    if cin.count('0')>0:
                        break
                    scale.phrase.play(cin)
                except Exception as e:
                    print(e)
            print('\n\n')
            
        key = input("Key: ").strip().upper()
        name = change_scale()
        scale = Scale(key, name)
        scale.init_midi()
        
        choice = {
            '1' : lambda : scale.__setattr__('key', input(f"Current Key: {key}\nNew Key: ")),
            '2' : lambda : scale.__setattr__('name', change_scale()),
            '3' : lambda : print('\n\n', scale.notes, '\n'),
            '4' : lambda : print(
                '\n\nChords:',
                *[
                    f"{i}: {' '.join(Scale.semitones_to_letter_notes(scale.chord(i)))}"
                    for i in range(1, 8)
                ],
                sep='\n',
                end='\n\n'
            ),
            '5' : play_phrase,
            '6' : play_chord,
            '7' : play_chord_progression,
        }
        menu()
        while True:
            try:
                cin = input(">")
                if cin == '\t':
                    menu()
                elif cin.lower() in ('0', 'bye', 'exit', 'q'):
                    raise KeyboardInterrupt
                else:
                    choice.get(cin, lambda: None)()
            except KeyboardInterrupt:
                print("Exiting...")
                scale.close_midi()
                break


    def __str__(self):
        return f"{self.name} in Key of {self.note_name[self.key-1]} - {tuple(self.note_name[i-1] for i in self.intervals)}"

        
    @staticmethod
    def midi_to_letter_notes(*midi):
        res = []
        for m in midi:
            n, oct = divmod(m, 12)[::-1]
            res.append(f"{Scale.note_name[n]}{oct-1}")
        return tuple(res)


    @staticmethod
    def semitones_to_letter_notes(*t, root_octave=4):
        res = []
        for _ in t[0]:
            n, oct = _
            res.append(f"{Scale.note_name[n-1]}{root_octave+oct}")
        return tuple(res)

