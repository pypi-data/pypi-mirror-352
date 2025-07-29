from dataclasses import dataclass, field

from .data import Data
from .helpers.atributo import Atributo
from .helpers.proficiencias import Proficiencia


@dataclass
class PC:
    nome: str = field(compare=False)
    classe: str
    background: str = field(compare=False)
    ancestry: str = field(compare=False)
    heritage: str = field(compare=False)

    _nivel: int = field(default=1, repr=False)
    _atributos: dict[str, str | Atributo] = field(
        default_factory=lambda: {'str': 0, 'dex': 0, 'con': 0, 'int': 0, 'wis': 0, 'cha': 0}, repr=False)
    _hp_ancestry: int = field(default=6, repr=False)
    _hp_classe: int = field(default=6, repr=False)
    _hp_extra: dict[str, int] = field(default_factory=lambda: {}, repr=False)
    _perception: str | Proficiencia = field(default='trained', repr=False)
    saves: dict[str, str | Proficiencia] = field(
        default_factory=lambda: {'Fortitude': 'trained', 'Reflex': 'trained', 'Will': 'trained'}, repr=False)
    _skills: list[str] | dict[str, Proficiencia] = field(default=None, repr=False)
    _ataques: list[str] | dict[str, Proficiencia] = field(default=None, repr=False)
    _atributo_magia: str = field(default='cha', repr=False)
    _atributo_dc: str | Proficiencia = field(default='str', repr=False)
    _defesas: list[str | Proficiencia] = field(default=None, repr=False)
    feats: dict[str, str] = field(default_factory=lambda: {'ancestry': [], 'skill': [], 'general': [], 'classe': []},
                                  repr=False)
    speed: int = field(default=25, repr=False)

    def __post_init__(self):
        self._iniciar_atributos()
        self._iniciar_hp()
        self._iniciar_skills()
        self._iniciar_ataques()
        self._iniciar_defesas()
        self._iniciar_magia()
        self._iniciar_dc()

        self._atualizar_tudo()

    # INICIALIZADORES
    def _iniciar_atributos(self):
        self._atributos = {atributo: Atributo(valor) for atributo, valor in self._atributos.items()}

    def _iniciar_hp(self):
        chaves = ['fixo', 'por nível']
        for chave in chaves:
            self._hp_extra[chave] = self._hp_extra[chave] if chave in self._hp_extra.keys() else 0

    def _iniciar_skills(self):
        self.skills = {}

        for skill in Data.skills:
            mod = self._atributos[Data.skills[skill]].mod
            self.skills[skill] = Proficiencia(mod, 'untrained', self.nivel)

        if self._skills:
            self.aumentar_skills(*self._skills)

    def _iniciar_ataques(self):
        self.ataques = {}

        for ataque in Data.tipos_ataques:
            self.ataques[ataque] = Proficiencia(0, 'untrained', self.nivel)

        if self._ataques:
            self.aumentar_ataques(*self._ataques)

    def _iniciar_defesas(self):
        self.defesas = {}

        for defesa in Data.tipos_defesas:
            self.defesas[defesa] = Proficiencia(0, 'untrained', self.nivel)

        if self._defesas:
            self.aumentar_defesas(*self._defesas)

    def _iniciar_magia(self):
        mod_magia = self.ataques['spell'].mod + self._atributos[self._atributo_magia].mod
        self.magias = {'ataque': mod_magia, 'dc': 10 + mod_magia}

    def _iniciar_dc(self):
        self._dc = Proficiencia(self._atributos[self._atributo_dc].mod, 'trained', self.nivel)


    # ATUALIZADORES AUTOMÁTICOS
    def _atualizar_tudo(self):
        self._atualizar_atributos()
        self._atualizar_percepcao()
        self._atualizar_saves()
        self._atualizar_skills()
        self._atualizar_ataques()
        self._atualizar_defesas()
        self._atualizar_magias()
        self._atualizar_dc()

    def _atualizar_atributos(self):
        for atributo in self._atributos:
            self._atributos[atributo] = Atributo(self._atributos[atributo].base)

    def _atualizar_percepcao(self):
        if type(self._perception) is str:
            self._perception = Proficiencia(self.wisdom, self._perception, self.nivel)
        else:
            self._perception = Proficiencia(self.wisdom, self._perception.proficiencia, self.nivel)

    def _atualizar_saves(self):
        for save in Data.saves:
            valor_atributo = self._atributos[Data.saves[save]].mod

            for save in self.saves:
                if type(self.saves[save]) is str:
                    self.saves[save] = Proficiencia(valor_atributo, self.saves[save], self.nivel)
                else:
                    proficiencia = self.saves[save].proficiencia
                    self.saves[save] = Proficiencia(valor_atributo, proficiencia, self.nivel)

    def _atualizar_skills(self):
        for skill in self.skills:
            mod = self._atributos[Data.skills[skill]].mod if skill in Data.skills else self._atributos['int'].mod
            self.skills[skill] = Proficiencia(mod, self.skills[skill].proficiencia, self.nivel)

    def _atualizar_ataques(self):
        for ataque in self.ataques:
            self.ataques[ataque] = Proficiencia(0, self.ataques[ataque].proficiencia, self.nivel)

    def _atualizar_magias(self):
        mod_magia = self.ataques['spell'].mod + self._atributos[self._atributo_magia].mod
        self.magias = {'ataque': mod_magia, 'dc': 10 + mod_magia}

    def _atualizar_defesas(self):
        for defesa in self.defesas:
            self.defesas[defesa] = Proficiencia(0, self.defesas[defesa].proficiencia, self.nivel)

    def _atualizar_dc(self):
        self._dc = Proficiencia(self._atributos[self._atributo_dc].mod, self._dc.proficiencia, self.nivel)

    # INICIALIZADORES E ATUALIZADORES DE USUÁRIO
    def reduzir_atributos(self, *args):
        for atributo in args:
            self._atributos[atributo].flaw()
        self._atualizar_tudo()

    def aumentar_atributos(self, *args):
        for atributo in args:
            self._atributos[atributo].aumentar()
        self._atualizar_tudo()

    def aumentar_percepcao(self):
        self._perception.aumentar_proficiencia()
        self._atualizar_percepcao()

    def hp_ancestry(self, valor: int):
        self._hp_ancestry = valor

    def hp_classe(self, valor: int):
        self._hp_classe = valor

    def hp_extra(self, fixo: int = 0, por_nivel: int = 0):
        self._hp_extra['fixo'] += fixo
        self._hp_extra['por nível'] += por_nivel

    def aumentar_skills(self, *args):
        for skill in args:
            if skill not in self.skills:
                self.skills[skill] = Proficiencia(self.intelligence, 'trained', self.nivel)
            else:
                self.skills[skill].aumentar_proficiencia()

        self._atualizar_skills()

    def aumentar_ataques(self, *args):
        for ataque in args:
            self.ataques[ataque].aumentar_proficiencia()
        self._atualizar_ataques()

    def aumentar_defesas(self, *args):
        for defesa in args:
            self.defesas[defesa].aumentar_proficiencia()
        self._atualizar_defesas()

    def atributo_magia(self, atributo: str = 'cha'):
        self._atributo_magia = atributo
        self._atualizar_magias()

    def atributo_dc(self, atributo: str):
        self._atributo_dc = atributo
        self._atualizar_dc()

    def aumentar_dc(self):
        self._dc.aumentar_proficiencia()
        self._atualizar_dc()

    def acrescentar_feat(self, feat: str, categoria: str):
        self.feats[categoria.lower()].append(feat)

    # ATRIBUTOS DA CLASSE (não confundir com atributo básico de personagem)
    @property
    def nivel(self):
        return self._nivel

    @nivel.setter
    def nivel(self, nivel):
        self._nivel = nivel
        self._atualizar_tudo()

    @property
    def strength(self):
        return self._atributos['str'].mod

    @property
    def dexterity(self):
        return self._atributos['dex'].mod

    @property
    def constitution(self):
        return self._atributos['con'].mod

    @property
    def intelligence(self):
        return self._atributos['int'].mod

    @property
    def wisdom(self):
        return self._atributos['wis'].mod

    @property
    def charisma(self):
        return self._atributos['cha'].mod

    @property
    def hp(self):
        fixo = self._hp_ancestry + self._hp_extra['fixo']
        por_nivel = (self._hp_classe + self._hp_extra['por nível'] + self.constitution) * self.nivel

        return fixo + por_nivel

    @property
    def perception(self):
        return self._perception.mod

    @property
    def fortitude(self):
        return self.saves['Fortitude'].mod

    @property
    def reflex(self):
        return self.saves['Reflex'].mod

    @property
    def will(self):
        return self.saves['Will'].mod

    @property
    def dc(self):
        return 10 + self._dc.mod
