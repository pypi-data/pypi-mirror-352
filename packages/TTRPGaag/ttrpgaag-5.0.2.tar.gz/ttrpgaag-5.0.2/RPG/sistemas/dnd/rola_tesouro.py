from dataclasses import dataclass
from ... import rolar_dado_notacao, TabelaRolavel

from .data import tesouro, mecanicas


@dataclass
class Tesouro:
    _cr: int = 1

    def __post_init__(self):
        self._inicia_param()

    def _inicia_param(self):
        self.moedas = {'cp': 0, 'sp': 0, 'ep': 0, 'gp': 0, 'pp': 0}
        self.bens = None
        self.itens = None

    def _rola_moedas(self, tabela):
        moedas = [rolar_dado_notacao(moeda) if type(moeda) == str else moeda for moeda in tabela]

        for i in range(len(moedas)):
            self.moedas[mecanicas.tipos_moedas[i]] += moedas[i]


@dataclass
class TesouroIndividual(Tesouro):
    def __post_init__(self):
        super().__post_init__()
        self._rolar()

    def _rolar(self):
        self._inicia_param()

        tabela_individual = TabelaRolavel(tesouro.individual, self._cr).resultado
        tabela_moedas = TabelaRolavel(tabela_individual, 'd100').resultado

        self._rola_moedas(tabela_moedas)


@dataclass
class TesouroHoard(Tesouro):
    pass