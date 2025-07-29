import random


class Baralho:
    def __init__(self, cartas: list):
        """
        Manipula uma lista de cartas_aplicadas, embaralhando seus elementos e permite sacar, resetar para seu status original

        :param cartas: a lista de cartas_aplicadas a ser usada
        """

        self._cartas = cartas
        self._original = tuple(cartas)

        self.descarte = list()
        self.em_jogo = list()

        self.reiniciar_baralho()

    def __str__(self):
        return f'{len(self._cartas)} cartas disponíveis para saque: {self._cartas}'

    def __repr__(self):
        return f'<Baralho com as cartas {self._original}>'

    def __len__(self):
        return len(self._cartas)

    def __getitem__(self, item):
        return self._cartas[item]

    # GETTERS ==============================================================
    @property
    def pilha_saque(self):
        return self._cartas

    # MÉTODOS DO BARALHO ===================================================
    # Esses métodos são relacionados somente com o baralho e não cartas
    def reiniciar_baralho(self) -> None:
        """
        Começa um novo baralho com todas as cartas embaralhadas e esvazia a pilha de descartes
        """

        self._cartas = list(self._original)
        self.embaralhar()
        self.descarte.clear()
        self.em_jogo.clear()

    def embaralhar(self) -> None:
        """
        Embaralha as cartas disponíveis no baralho
        """
        random.shuffle(self._cartas)

    # MÉTODOS DA PILHA ======================================================
    # Métodos que manipulam a pilha de cartas básica
    def ver_cartas(self, qtd: int) -> list:
        """
        Revela a quantidade selecionada de cartas do topo da pilha de saque
        :param qtd: a quantidade de cartas a serem vistas
        :return: lista com as cartas
        """
        return self._cartas[:qtd]

    def sacar(self, do_topo: bool = True) -> list | None:
        """
        Saca uma carta do topo do baralho, removendo-a do mesmo
        :param do_topo: se marcado como falsa, pega aleatoriamente
        :return: a carta sacada, None se não tiver o que sacar
        """

        if len(self._cartas) > 0:
            sacada = self._cartas[0] if do_topo else random.choice(self._cartas)
            self.em_jogo.append(sacada)
            return self._cartas.pop(self._cartas.index(sacada))

        return None

    def descer_carta(self, carta, aleatorio: bool = False, embaralha: bool = False):
        """
        Coloca uma carta em jogo na pilha de saques
        :param carta: a carta a ser devolvida
        :param aleatorio: devolve aleatoriamente para a pilha, mas nunca como primeira carta. Se Falso, devolve para o final
        :param embaralha: reembaralha a pilha de saques ao devolver a carta
        """

        index = random.randint(1, len(self._cartas)) if aleatorio else len(self._cartas)
        self._cartas.insert(index, carta)
        self.em_jogo.pop(self.em_jogo.index(carta))

        if embaralha:
            self.embaralhar()

    def mover_cartas(self, qtd: int = 1, aleatorio: bool = True):
        """
        Move uma quantidade de cartas do início da pilha
        :param qtd: A quantidade de cartas a serem movidas
        :param aleatorio: Coloca aleatoriamente no baralho, se falso, coloca no final
        """
        a_mover = list(self._cartas[:qtd])
        self._cartas = self._cartas[qtd:len(self._cartas)]

        for carta in a_mover:
            index = random.randint(1, len(self._cartas)) if aleatorio else len(self._cartas)
            self._cartas.insert(index, carta)

    # MÉTODOS DO DESCARTE ====================================================
    # Métodos que manipulam a pilha de descarte
    def descartar(self, carta):
        """
        Joga a carta selecionada na pilha de descartes
        :param carta: a carta a ser descartada
        """

        self.descarte.append(carta)
        self.descarte = list(reversed(self.descarte))
        self.em_jogo.pop(self.em_jogo.index(carta))

    def pegar_do_descarte(self, carta=None):
        """
        Pega uma carta da pilha de descartes. Se não escolher a carta, pega uma aleatória
        :param carta: qual a carta escolhida do descarte
        :return: a carta sacada, None se não tiver o que sacar do descarte
        """

        if len(self.descarte) > 0:
            sacada = carta if carta else random.choice(self.descarte)
            self.em_jogo.append(sacada)
            return self.descarte.pop(self.descarte.index(sacada))

        return None

    def ver_descarte(self, qtd: int = None) -> list | None:
        """
        Revela a quantidade selecionada de cartas do topo da pilha de descarte
        :param qtd: a quantidade de cartas a exibir, se omitido exibe a lista inteira
        :return: lista com as cartas
        """
        if not self.descarte:
            return None

        if not qtd:
            return self.descarte

        return self.descarte[0:qtd]

    # MÉTODOS DA PILHA E DO DESCARTE ========================================
    # Métodos que envolvem tanto a pilha de cartas e a pilha de descartes
    def recuperar_carta(self, carta_descartada, aleatorio: bool = False, embaralha: bool = True):
        """
        Coloca a carta selecionadaa da pilha de descartes de volta para a pilha de saque
        :param carta_descartada: qual a carta a ser devolvida da pilha de descarte
        :param aleatorio: se coloca aleatoriamente (True) ou no final da pilha (False - Padrão)
        :param embaralha: se embaralha a pilha de saques depois disso
        """
        sacada = self.pegar_do_descarte(carta_descartada)

        self.descer_carta(sacada, aleatorio, embaralha)



if __name__ == "__main__":
    baralho_teste = Baralho(list(range(1, 11)))
    print(baralho_teste)
    mao_extra = [baralho_teste.sacar() for _ in range(5)]
    print("Mão com 5 cartas_aplicadas:", mao_extra)
    print(baralho_teste)
    print("---------------------------------------------------------------------")
    print("Descartando as duas menores cartas da mão:")

    for i in range(2):
        sacado = min(mao_extra)
        baralho_teste.descartar(sacado)
        mao_extra.pop(mao_extra.index(sacado))

    print("Mão atual:", mao_extra)
    print("Pilha de descartes", baralho_teste.descarte)
    print(baralho_teste)
