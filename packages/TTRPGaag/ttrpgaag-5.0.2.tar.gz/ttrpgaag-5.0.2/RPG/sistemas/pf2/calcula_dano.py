from .helpers.base_calcula_dano import CalculaDanoBase
from ...dado import Dado


class CalculaDanoAtaque(CalculaDanoBase):
    tipo = "Ataque"

    def __init__(self,
                 nome: str,
                 ataque: int,
                 ac: int,
                 dano: tuple,
                 numero_acoes: int = 1,
                 multiplicador_critico: int = 2,
                 valor_fixo_falha: int = 0,
                 multiplicador_falha: float = 0,
                 multiplicador_falha_critica: float = 0,
                 fatal: int | None = None,
                 deadly: int | None = None,
                 qtd_dados_deadly: int | None = None
                 ):
        """
        Calcula o dano médio do ataque e o dano por ação do mesmo. Considera a chance de acertar, o dano crítico
        :param nome: O nome do ataque
        :param ataque: Modificador para acertar o ataque
        :param ac: A AC do alvo
        :param dano: Uma tupla representando o dano: o primeiro valor da tupla é a quantidade de dados rolados, o segundo valor o número de faces e o último o modificador do dado
        :param numero_acoes: O número de ações que o ataque custa (padrão 1)
        :param multiplicador_critico: Por quanto o dano é multiplicado no crítico (padrão 2)
        :param valor_fixo_falha: Caso errar tenha um valor fixo (como no feat Advantageous Assault), insira aqui
        :param multiplicador_falha: O valor com o qual a falha é multiplicada. Padrão é 0, mas caso cause metade do dano, coloque 0.5
        :param multiplicador_falha_critica: O mesmo que acima, mas para o caso de falhas críticas (normalmente 0)
        :param fatal: O valor do dado da Arma fatal, caso tenha
        :param deadly: O valor do dado da arma deadly, caso tenha
        :param qtd_dados_deadly: A quantidade de dados da arma deadly caso seja diferente da quantidade rolada pelo dano normal (padrão). Use em casos de ataque como Vicious Swing que tem um valor de dano diferente do padrão.
        """
        super().__init__(
            nome,
            modificador_rolamento=ataque,
            numero_alvo=ac,
            dano=dano,
            numero_acoes=numero_acoes,
            multiplicador_critico=multiplicador_critico,
            multiplicador_falha=multiplicador_falha,
            valor_fixo_falha=valor_fixo_falha,
            multiplicador_falha_critica=multiplicador_falha_critica,
        )

        self._fatal_dado = fatal if fatal else None
        self._deadly_dado = deadly if deadly else None
        self._deadly_qtd_dado = qtd_dados_deadly if qtd_dados_deadly else self._qtd_dados

        self._fatal = Dado(1, self._fatal_dado).media + self._mod_dano if fatal else None
        self._deadly = Dado(self._deadly_qtd_dado, self._deadly_dado).media if deadly else None

    def __str__(self):
        fatal = f' (fatal d{self._fatal_dado})' if self._fatal_dado else ''
        deadly = f' (deadly d{self._deadly_dado})' if self._deadly_dado else ''

        extra = fatal + deadly

        return f"""{self.nome}: +{self._modificador_rolamento} vs. AC {self._numero_alvo}, {self.dano_em_dados}{extra} = {self.dano_medio} ({self.dano_por_acao} por ação)"""

    @property
    def ataque(self):
        return self._modificador_rolamento


class CalculaDanoSave(CalculaDanoBase):
    tipo = "Save"

    def __init__(self,
                 nome: str,
                 dc: int,
                 save: int,
                 dano: tuple,
                 numero_acoes: int = 2,
                 multiplicador_falha_critica: int = 2,
                 multiplicador_sucesso: float = 0.5,
                 valor_fixo_sucesso: int = 0,
                 multiplicador_sucesso_critica: float = 0,
                 ):
        """
        Calcula o dano médio de efeito de save (como magia) e o dano por ação do mesmo. Considera o dano por sucesso no save, o dano por falha crítica no save
        :param nome: O nome da habilidade
        :param dc: O DC da habilidade
        :param save: O valor do save do oponente
        :param dano: Uma tupla representando o dano: o primeiro valor da tupla é a quantidade de dados rolados, o segundo valor o número de faces e o último o modificador do dado
        :param numero_acoes: O número de ações que a habilidade custa (padrão 2, que é o mais comum nas magias)
        :param multiplicador_falha_critica: Por quanto o dano é multiplicado na falha crítica do alvo (padrão 2)
        :param multiplicador_sucesso: O multiplicador de dano que a habilidade causa no caso do alvo passar no save (padrão 0.5)
        :param valor_fixo_sucesso: Caso a habilidade cause um dano fixo se o oponente passar no teste
        :param multiplicador_sucesso_critica: O mesmo que multiplicador_sucesso, mas para o caso de sucesso crítico (normalmente 0)
        """
        super().__init__(
            nome,
            modificador_rolamento=dc-10,
            numero_alvo=save+10,
            dano=dano,
            numero_acoes=numero_acoes,
            multiplicador_critico=multiplicador_falha_critica,
            multiplicador_falha=multiplicador_sucesso,
            valor_fixo_falha=valor_fixo_sucesso,
            multiplicador_falha_critica=multiplicador_sucesso_critica,
        )

    def __str__(self):
        return f"""{self.nome}: {self.dano_em_dados}. DC {self._modificador_rolamento+10} vs. +{self._numero_alvo-10} = {self.dano_medio} ({self.dano_por_acao} por ação)"""


class CalculaPersistent:
    flat_dc = 15

    def __init__(self, dano: int):
        self._dano = dano

    def __eq__(self, other):
        return self.dano_medio == other.dano_medio

    def __lt__(self, other):
        return self.dano_medio < other.dano_medio

    def __repr__(self):
        return f"""<Persistent Damage: {self._dano}>"""

    def __str__(self):
        return f"""{self._dano} persistent damage, média de {self.dano_medio}"""

    @property
    def dano_medio(self):
        # https://rpg.stackexchange.com/questions/185445/how-many-rounds-is-persistent-damage-expected-to-last
        chance = 20 / (21 - self.flat_dc)
        return round(self._dano * chance, 4)