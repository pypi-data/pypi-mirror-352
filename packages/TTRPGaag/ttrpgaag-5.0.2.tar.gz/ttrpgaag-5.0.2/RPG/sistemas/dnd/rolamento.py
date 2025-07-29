from ...dado import d20
from .helpers.checa_testes import checa_teste, checa_ataque


class Rolamento:
    def __init__(self, modificador=0, dc=10, vantagem=False, desvantagem=False):
        """
        Define o teste para uma habilidade
        :param modificador: o modificador no rolamento
        :param dc: qual o DC do teste
        :param vantagem: se o personagem tem vantagem na rolagem
        :param desvantagem: se o personagem tem desvantagem na rolagem
        """
        self._modificador: int = modificador
        self._dc: int = dc
        self._vantagem: bool = vantagem
        self._desvantagem: bool = desvantagem
        self._rolamento = []

        self._corrige_vantagem_desvantagem()
        self.dado = self._rolamento_inicial()

    def __str__(self):
        string_dado = 'dado rolado' if len(self._rolamento) == 1 else 'dados rolados'
        string_modificador = self._define_str_modificador()

        return f'{string_dado.capitalize()}: {", ".join(str(d) for d in self._rolamento)}' \
               f'. Modificador: {string_modificador}{self._define_str_vantagem_desvantagem()}.' \
               f' Total: {self.total} vs DC {self._dc}.' \
               f' {self.resultado.capitalize()}.'

    def __repr__(self):
        return f'<Teste{self._define_str_vantagem_desvantagem()},' \
               f' dc: {self._dc}, rolamento={self._rolamento},' \
               f' modificador: {self._define_str_modificador()}>'

    # INICIALIZADORES E AUXILIARES=====================================================
    def _rolamento_inicial(self):
        self._rolamento.append(d20())

        if self._vantagem or self._desvantagem:
            self._rolamento.append(d20())
            return max(self._rolamento) if self._vantagem else min(self._rolamento)

        return self._rolamento[0]

    def _corrige_vantagem_desvantagem(self):
        if self._vantagem and self._desvantagem:
            self._vantagem = False
            self._desvantagem = False

    def _define_str_vantagem_desvantagem(self) -> str:
        return '' if not (self._vantagem or self._desvantagem) else \
            ' com vantagem' if self._vantagem else ' com desvantagem'

    def _define_str_modificador(self) -> str:
        return f'+{self._modificador}' if self._modificador > - 1 else self._modificador

    # MÉTODOS =========================================================================
    def rerolar(self, modificador=None, dc=None, vantagem=None, desvantagem=None) -> None:
        self._modificador = modificador if modificador else self._modificador
        self._dc = dc if dc else self._dc
        self._vantagem = vantagem if vantagem else self._vantagem
        self._desvantagem = desvantagem if desvantagem else self._desvantagem

        self._rolamento.clear()
        self.dado = self._rolamento_inicial()

    # PROPRIEDADES ====================================================================
    @property
    def total(self) -> int:
        dado = self.dado
        resultado = dado + self._modificador

        return resultado

    @property
    def resultado(self) -> str:
        return checa_teste(self.total, self._dc)

    @property
    def dado_minimo(self) -> int:
        """
        Calcula o valor mínimo que precisa ser tirado no d20 para conseguir um sucesso
        :return: Um valor entre 1 a 20. Se o resultado for None, não é possível passar nesse teste
        """
        rolamento_min = self._dc - self._modificador
        return rolamento_min if rolamento_min in range(1, 21) else 1 if rolamento_min <= 0 else None

    @property
    def chance_sucesso(self) -> str:
        dado = self.dado_minimo if self.dado_minimo else 0
        return str((21 - dado) * 5) + '%'


class Ataque(Rolamento):
    def __init__(self, modificador=0, ac=10, vantagem=None, desvantagem=None):
        super().__init__(modificador, dc=ac, vantagem=vantagem, desvantagem=desvantagem)
        self._ac = self._dc

    def __str__(self):
        string_dado = 'dado rolado' if len(self._rolamento) == 1 else 'dados rolados'
        string_modificador = self._define_str_modificador()

        return f'{string_dado.capitalize()}: {", ".join(str(d) for d in self._rolamento)}' \
               f'. Modificador: {string_modificador}{self._define_str_vantagem_desvantagem()}.' \
               f' Total: {self.total} vs AC {self._ac}.' \
               f' {self.resultado.capitalize()}.'

    def __repr__(self):
        return f'<Ataque{self._define_str_vantagem_desvantagem()},' \
               f' ac: {self._ac}, rolamento={self._rolamento},' \
               f' modificador: {self._define_str_modificador()}>'

    # PROPRIEDADES ====================================================================
    @property
    def resultado(self) -> str:
        return checa_ataque(self.dado, self.total, self._ac)

    @property
    def dado_minimo(self) -> int:
        """
        Calcula o valor mínimo que precisa ser tirado no d20 para conseguir um sucesso
        :return: Um valor entre 1 a 20. Se o resultado for None, não é possível passar nesse teste
        """
        rolamento_min = self._dc - self._modificador
        return rolamento_min if rolamento_min in range(1, 21) else 1 if rolamento_min <= 0 else 20
