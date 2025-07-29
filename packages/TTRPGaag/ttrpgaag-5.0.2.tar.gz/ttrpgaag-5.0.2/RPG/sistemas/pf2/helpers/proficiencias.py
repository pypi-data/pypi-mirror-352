from dataclasses import dataclass, field
from ...pf2 import calcula_proficiencia, aumenta_proficiencia


@dataclass
class Proficiencia:
    mod_atributo: int = field(repr=False)
    proficiencia: str = field(default=None)
    nivel: int = field(repr=False, default=1)
    _modificador_item: int = field(repr=False, default=0)

    @property
    def mod(self):
        if self.proficiencia:
            return calcula_proficiencia(self.proficiencia, self.nivel) + self.mod_atributo + self.mod_item
        else:
            return None

    @property
    def mod_item(self):
        return self._modificador_item

    @mod_item.setter
    def mod_item(self, mod):
        self._modificador_item += mod

    def aumentar_proficiencia(self):
        self.proficiencia = aumenta_proficiencia(self.proficiencia)
