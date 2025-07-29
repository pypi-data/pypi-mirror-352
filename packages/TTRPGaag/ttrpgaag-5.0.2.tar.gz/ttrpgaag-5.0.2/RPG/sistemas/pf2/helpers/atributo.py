from dataclasses import dataclass
import math


@dataclass
class Atributo:
    base: int

    def aumentar(self):
        self.base += 1 if self.base < 4 else + 0.5

    def flaw(self):
        self.base -= 1

    @property
    def mod(self):
        return math.floor(self.base)
