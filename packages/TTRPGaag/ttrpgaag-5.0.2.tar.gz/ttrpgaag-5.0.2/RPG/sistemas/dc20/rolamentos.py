from ...dado import Dado


class RolamentoBase:
    def __init__(self,
                 modificador: int = 0,
                 dificuldade: int = 10,
                 vantagens: int = 0,
                 desvantagens: int = 0) -> None:
        self.modificador = modificador
        self.vantagens = vantagens
        self.desvantagens = desvantagens
        self._dificuldade = dificuldade

        self._qtd_dados = self._calcular_dados()
        self._vantagem = self._calcular_vantagem()
        self._desvantagem = self._calcular_desvantagem()

        self._rolar_dados()


    def __str__(self) -> str:
        return f'Rolamento: {self.modificador} vs DC {self._dificuldade}. Vant: {self.vantagens}, DesVant: {self.desvantagens}. Resultado: {self.total}. {self.resultado}'


    def __repr__(self) -> str:
        return f'<Rolamento {self.modificador} vs DC {self._dificuldade}, {self.vantagens} Vant, {self.desvantagens} DesVant. Rolamento: {self.dados}>'


    # Métodos privados =========================================================
    def _calcular_dados(self):
        return 1 + abs(self.vantagens - self.desvantagens)


    def _calcular_vantagem(self):
        return self.vantagens > self.desvantagens


    def _calcular_desvantagem(self):
        return self.desvantagens > self.vantagens


    def _rolar_dados(self):
        self._dados = Dado(self._qtd_dados, 20)


    def _escolher_dado(self):
        if self._vantagem:
            return self._dados.maior

        if self._desvantagem:
            return self._dados.menor

        return self._dados[0]


    # Métodos ==================================================================
    def rerolar(self):
        self._dados.rerolar


    # Propriedades =============================================================
    @property
    def dados(self):
        return self._dados.rolamento


    @property
    def dado(self):
        return self._escolher_dado()


    @property
    def total(self):
        return self.dado + self.modificador


    @property
    def sucesso(self):
        return self.total >= self._dificuldade


    @property
    def critico(self):
        return self.dado == 1 or self.dado == 20


    @property
    def diferenca(self):
        return abs(self.total - self._dificuldade)


    @property
    def gradacao(self):
        return int(self.diferenca / 5)


    @property
    def resultado(self):
        texto = 'Sucesso' if self.sucesso else 'Falha'

        if self.critico:
            texto += ' crítico' if self.sucesso else ' crítica'

        texto += f'. Diferença: {self.diferenca}'

        return texto
    

class Rolamento(RolamentoBase):
    def __init__(self, 
                 modificador: int = 0, 
                 dc: int = 10, 
                 vantagens: int = 0, 
                 desvantagens: int = 0) -> None:
        super().__init__(modificador, dc, vantagens, desvantagens)
        """
        Gera um rolamento para determinada habilidade ou ataque

        rolamento = Rolamento(modificador: 4, dc: 15, vantagens: 1)

        print(rolamento) -> Rolamento: 0 vs DC 10. Vant: 0, DesVant: 0. Total: 10 # valor aleatório

        * modificador: o modificador no rolamento dos dados (valor da habilidade). Padrão: 0
        * dc: o número alvo para o rolamento. Padrão: 10
        * vantagens: a quantidade de vantagens no rolamento. Padrão 0
        * desvantagens: a quantidade de desvantagens no rolamento. Padrão 0
        """
    # PROPRIEDADES =============================================================
    @property
    def dc(self):
        return self._dificuldade
    
    @dc.setter
    def dc(self, dc):
        self._dificuldade = dc


class RolamentoAtaque(RolamentoBase):
    def __init__(self,
                 modificador: int = 4,
                 pd: int = 12,
                 dano: int = 1,
                 vantagens: int = 0,
                 desvantagens: int = 0):
        super().__init__(modificador, pd, vantagens, desvantagens)
        self.dano_base = dano
        self.pd = self._dificuldade


    def __str__(self) -> str:
        return f'Rolamento de Ataque: {self.modificador} vs PD {self._dificuldade}. Vant: {self.vantagens}, DesVant: {self.desvantagens}. Resultado: {self.total}. {self.resultado}'


    def __repr__(self) -> str:
        return f'<Rolamento de Ataque {self.modificador} vs PD {self._dificuldade}, {self.vantagens} Vant, {self.desvantagens} DesVant, {self.dano_base} dano. Rolamento: {self.dados}>'


    # MÉTODOS PRIVADOS =========================================================
    def _calcular_dano_final(self):
        base = self.dano_base + self.gradacao

        if self.critico:
            base += 2

        if not self.sucesso:
            base = 0

        return base
    
    # Propriedades =============================================================
    @property
    def dano_causado(self):
        return self._calcular_dano_final()
    
    @property
    def resultado(self):
        texto = super().resultado

        if self.gradacao == 1:
            texto += ', heavy hit'

        if self.gradacao == 2:
            texto += ', brutal hit'

        return texto
