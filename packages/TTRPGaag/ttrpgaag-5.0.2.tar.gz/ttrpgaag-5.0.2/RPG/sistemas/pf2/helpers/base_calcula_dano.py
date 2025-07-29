from ....dado import Dado


class CalculaDanoBase:
    tipo: str = "Base"

    def __init__(self,
                 nome: str,
                 modificador_rolamento: int,
                 numero_alvo: int,
                 dano: tuple,
                 numero_acoes: int = 1,
                 multiplicador_critico: int = 2,
                 multiplicador_falha: float = 0,
                 valor_fixo_falha: int = 0,
                 multiplicador_falha_critica: float = 0,
                 ):
        self.nome = nome

        self._qtd_dados = dano[0]
        self._face_dados = dano[1]
        self._mod_dano = dano[2] if len(dano) == 3 else 0

        self._modificador_rolamento = modificador_rolamento
        self._numero_alvo = numero_alvo
        self._dano = Dado(self._qtd_dados, self._face_dados).media + self._mod_dano

        self._acoes = numero_acoes

        self._multiplicador_critico = multiplicador_critico
        self._multiplicador_falha = multiplicador_falha
        self._valor_fixo_falha = valor_fixo_falha
        self._multiplicador_falha_critica = multiplicador_falha_critica

        self._fatal = None
        self._deadly = None

        self._chance_critico = (21 - self._calcula_numero_critico())
        self._chance_acerto = (21 - self._calcula_numero_acerto() - self._chance_critico)
        self._chance_falha_critica = self._calcula_numero_falha_critica()
        self._chance_falha = 20 - self._chance_critico - self._chance_acerto - self._chance_falha_critica

    # FUNÇÕES DE CLASSE
    def __eq__(self, other):
        return self.dano_por_acao == other.dano_por_acao

    def __lt__(self, other):
        return self.dano_por_acao < other.dano_por_acao

    def __add__(self, other):
        return self.dano_medio + other.dano_medio

    def __repr__(self):
        return self.__str__()

    # MÉTODOS BASE
    def _calcula_dano_critico(self):
        critico_basico = self._dano * self._multiplicador_critico

        if self._deadly:
            return self._deadly + critico_basico

        if self._fatal:
            return (self._fatal * self._multiplicador_critico) + self._fatal

        return critico_basico

    def _calcula_dano_falha(self):
        return (self._dano * self._multiplicador_falha) + self._valor_fixo_falha

    def _calcula_dano_falha_critica(self):
        return self._dano * self._multiplicador_falha_critica

    def _calcula_numero_acerto(self):
        resultado = self._numero_alvo - self._modificador_rolamento

        if resultado in range(1, 21):
            return resultado

        if resultado < 0:
            return 1

        if resultado > 20:
            return 20

    def _calcula_numero_critico(self):
        critico = self._calcula_numero_acerto() + 10
        return critico if critico < 21 else 20

    def _calcula_numero_falha_critica(self):
        falha_critica = self._calcula_numero_acerto() - 10
        return falha_critica if falha_critica > 1 else 1

    def _calcula_dano_medio(self):
        dano_falha_critica = self._calcula_dano_falha_critica() * self._chance_falha_critica
        dano_falha = self._calcula_dano_falha() * self._chance_falha
        dano = self._dano * self._chance_acerto
        dano_critico = self._calcula_dano_critico() * self._chance_critico

        return round((dano_falha_critica + dano_falha + dano + dano_critico) / 20, 4)

    # GETTERS
    @property
    def dano_acerto(self) -> float:
        return self._dano

    @property
    def dano_critico(self) -> float:
        return self._calcula_dano_critico()

    @property
    def dano_falha(self) -> float:
        return self._calcula_dano_falha()

    @property
    def dano_falha_critica(self) -> float:
        return self._calcula_dano_falha_critica()

    @property
    def chance_acerto(self) -> str:
        """
        :return: Representação textual da chance de acertar a ação (inclui crítico)
        """
        return f'{(self._chance_acerto + self._chance_critico) * 5}%'

    @property
    def chance_critico(self) -> str:
        """
        :return: Representação textual da chance de causar um crítico
        """
        return f'{self._chance_critico * 5}%'

    @property
    def chance_falha_critica(self) -> str:
        """
        :return: Representação textual da chance de falhar criticamente
        """
        return f'{self._calcula_numero_falha_critica() * 5}%'

    @property
    def chance_falha(self) -> str:
        """
        :return: Representação textual da chance de falhar na ação (incluindo falha crítica)
        """
        return f'{(self._chance_falha + self._chance_falha_critica) * 5}%'

    @property
    def dano_medio(self) -> float:
        """
        :return: Dano médio causado pela habilidade, incluindo as chances de erro e de crítico
        """
        return self._calcula_dano_medio()

    @property
    def dano_por_acao(self) -> float:
        """
        :return: Dano médio causado pela habilidade, incluindo as chances de erro e de crítico, por ponto de ação gasto
        """
        return round(self._calcula_dano_medio() / self._acoes, 4)

    @property
    def acoes(self) -> int:
        return self._acoes

    @property
    def dano_em_dados(self) -> str:
        mod = '' if self._mod_dano == 0 else f'+{self._mod_dano}' if self._mod_dano > 0 else self._mod_dano
        return f'{self._qtd_dados}d{self._face_dados}{mod}'