from collections.abc import Iterable
from typing import Tuple


class CircularOctave:
    """
        Ring Tuple for Notes / MIDI Notes / Semitones / Keys / Scale.
    """
    
    def __init__(self, *args):
        if len(args) == 1 and isinstance(args[0], Iterable):
            self._elems = tuple(args[0])
        else:
            self._elems = args
            
        self._cur = min(0, len(self._elems)-1)
    

    def __next__(self) -> Tuple:
        """
            Returns Tuple(next element, octave of next element relative to root)
            Moves the root to the next element.
        """
        if self._cur == -1:
            raise StopIteration("No elements to iterate")
            
        self._cur, oct = divmod(self._cur, len(self))[::-1]
        self._cur, oct = divmod(self._cur + 1, len(self))[::-1]
        
        return self._elems[self._cur], oct
        
        
    def __getitem__(self, index) -> Tuple:
        """
            Overrides Index [] operators.
            
            Usage:
            
            obj[i] : returns Tuple(ith element, octave of ith element)
                
            obj[i, j, ...] : returns Tuple(
                           Tuple(ith element, octave of ith element),
                           Tuple(jth element, octave of jth element),
                           ...
                       )
        """
        if self._cur == -1:
            raise IndexError("Empty")
            
        if isinstance(index, int):
            index, oct = divmod(self._cur+index, len(self))[::-1]
            return (self._elems[index], oct)
            
        if isinstance(index, tuple):
            res = []
            for i in index:
                i, oct = divmod(self._cur+i, len(self))[::-1]
                res.append((self._elems[i], oct))
            return tuple(res)


    @property
    def root(self) -> int:
        """
            Property: Current element.
            type <int>
        """
        return self._elems[self._cur]


    @property
    def root_idx(self) -> int:
        """
            Property: Current element index.
            type <int>
        """
        return self._cur


    @root_idx.setter
    def root_idx(self, val:int):
        if not isinstance(val, int):
            raise ValueError(f"Root index expected of type 'int', not {type(val)}")
        self._cur = val


    def __iter__(self):
        for elem in (self._elems[self._cur:] + self._elems[:self._cur]):
            yield elem


    def __len__(self):
        return len(self._elems)
        

    def __repr__(self):
        return f"CircularOctave({repr(self._elems)})"
    

    def __str__(self):
        return str(self._elems[self._cur:] + self._elems[:self._cur])
