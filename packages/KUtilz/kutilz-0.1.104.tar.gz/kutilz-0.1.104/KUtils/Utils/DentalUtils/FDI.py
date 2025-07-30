from KUtils.Typing import *
from enum import Enum

class ToothType(str, Enum):
    INCISOR = 'incisor'
    CANINE = 'canine'
    PREMOLAR = 'pre-molar'
    MOLAR = 'molar'

    @classmethod
    def FromFDI(cls, fdi: int):
        tid = int(fdi)
        a, b = tid // 10, tid % 10
        if b in [1, 2]:
            k = ToothType.INCISOR
        elif b in [3]:
            k = ToothType.CANINE
        elif b in [4, 5]:
            k = ToothType.PREMOLAR
        elif b in [6, 7, 8]:
            k = ToothType.MOLAR
        else:
            raise ValueError(f'Invalid FDI designation: {tid}')
        return k

def _teeth_upto(qudrant: int, upto: int)->List[int]:
    return [qudrant*10 + tooth_num for tooth_num in range(1, upto+1)]

def get_all(permanent=True,
            deciduous=False,
            supernumerary=False,
            dtype: Type[T] = int)->List[T]:
    fdis = []
    if permanent:
        for quadrant in range(1, 4 + 1):
            fdis.extend(_teeth_upto(quadrant, 8))

    if deciduous:
        for quadrant in range(5, 8 + 1):
            fdis.extend(_teeth_upto(quadrant, 5))

    fdis = [dtype(i) for i in fdis]

    return fdis
