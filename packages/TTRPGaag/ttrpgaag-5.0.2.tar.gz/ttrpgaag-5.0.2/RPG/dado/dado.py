import random


class Dado:
    def __init__(self, quantidade: int = 1, faces: int = 6):
        """
        Gera uma lista dos dados rolados

        rolamento = Dado(quantidade=2, faces=6)

        print(rolamento) -> "[3, 5]"  # valor aleatório

        Caso use algum método para alterar o resultado da lista, é possível acessar
        com o atributo '.rolamento_original'

        :param quantidade: a quantidade de dados rolados, padrão: 1
        :param faces: o número de faces do dado, padrão: 6
        """
        self._quantidade = quantidade
        self._faces = faces
        self._rolamento = self._rolagem_de_dados()
        self.rolamento_original = tuple(self.rolamento)
        self.retirado = None

    def __str__(self):
        retirado = f' (dado retirado: {self.retirado})' if self.retirado else ''
        return f'{self._quantidade}d{self._faces}, dados: {self._rolamento}{retirado}, total: {self.total}'

    def __repr__(self):
        return f'<Dado quantidade={self._quantidade} faces={self._faces}>'

    def __len__(self):
        return len(self._rolamento)

    def __getitem__(self, index):
        return self._rolamento[index]

    def __setitem__(self, index, value):
        self._rolamento[index] = value

    def __lt__(self, other):
        return self.total < other.total

    # Funções de abertura ======================================================
    def _rolagem_de_dados(self):
        """
        Retorna uma lista com os _dados rolados
        """
        return [random.randint(1, self._faces) for _ in range(self._quantidade)]
    
    def _reiniciar(self):
        """
        Reinicia a classe, rolando novamente e resetando também os valores originais
        Use para casos que os valores de dados e rolamentos podem ser alterados
        """
        self.rerolar()
        self.rolamento_original = tuple(self.rolamento)

    # Métodos para alterar o resultado =========================================
    def rolar(self):
        """
        Rola os dados novamente, com a quantidade e face originais
        """
        self._reiniciar()


    def rerolar(self):
        """
        Rerola os dados, com a quantidade e face originais
        """
        self._rolamento.clear()
        self._rolamento.extend(self._rolagem_de_dados())

    def retirar_menor(self):
        """
        Retira o menor dado rolado da lista
        """
        self._rolamento.remove(min(self._rolamento))

    def explodir(self, explode_em: int | None = None):
        """
        :param explode_em: intenger, explode acima ou igual a esse valor. Por padrão é o número de faces do dado
        """
        if explode_em is None:
            explode_em = self._faces

        for i in self._rolamento:
            if i >= explode_em:
                self._rolamento.append(random.randint(1, self._faces))

    # getters ==================================================================
    @property
    def rolamento(self):
        return self._rolamento

    @property
    def media(self):
        base = (1 + self._faces) / 2
        return int(base * self._quantidade)

    @property
    def total(self):
        return sum(self.rolamento)

    @property
    def maior(self):
        return max(self.rolamento)

    @property
    def menor(self):
        return min(self.rolamento)


if __name__ == "__main__":
    # Exemplo de uso
    print(Dado(5, 6))
    print("A média de 5d6 é:", Dado(5, 6).media)

    print("------------------------------------------------------------")
    print(f"Rolando 3d4, mas explosivo:")
    print(Dado(3, 4).explodir())

    print("------------------------------------------------------------")
    print("Rolando 4d6, 6 vezes e tirando o menor dado:")
    atributos_dnd = [Dado(4, 6) for _ in range(6)]
    atributos_final = []

    for dado in atributos_dnd:
        dado.retirar_menor()
        atributos_final.append(dado.total)

    print(atributos_final)
