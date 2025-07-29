from random import choice

from .rolar_tabela import rolar_tabela
from .helpers.ajeita_tabela import ajeita_tabela
from .helpers.busca_index_item_tabela import busca_index_item_tabela
from .helpers.rolamento_dado import DadoRolado
from ..dado import rolar_dado_notacao


class TabelaRolavel:
    def __init__(self, tabela: list = None, dados: str | None = None, rola_subtabela: bool = False):
        """
        Cria um objeto com uma tabela vazia ou já existente (no formato de lista) para ser rolada e métodos para que busquem o
        resultado diretamente nela.

        Args:
            tabela: a tabela a ser buscada, se não passar o parâmetro, cria uma tabela vazia (que deve ser preenchida com .insere_linha_tabela()
            dados: a notação de dados a ser usado para rolar na tabela. Também pode ser passado um valor fixo (que pode ser alterado com o método .rolar())
            rola_subtabela: caso o resultado seja outra classe de TabelaRolavel, já retornar o resultado da tabela rolada. O padrão é False.
        """
        self._tabela = ajeita_tabela(tabela) if tabela else []
        self._dado_rolado = DadoRolado(rolamento=0, modificador=0)
        self._resultado = ''

        self.dados = dados
        self.rola_subtabela = rola_subtabela

        if dados:
            self.rolar()

    def __repr__(self):
        return f'<Tabela Rolável={self._tabela},\n dado usado: {self.dados}>'

    def __str__(self):
        return f'Rolamento de {self.dados}+{self.rolamento.modificador}: {self.rolamento.total}. Resultado: {self._resultado}'

    # Métodos de edição da tabela ====================================================================================
    # Usados para tabelas que podem ser mudadas conforme o resultado
    def inserir_linha_tabela(self, valor_menor: int, valor_maior: int, resultado) -> None:
        """
        Adiciona uma linha à tabela.
        :param valor_menor: o menor valor do alcance do rolamento dessa linha
        :param valor_maior: o maior valor do alcance do rolamento dessa linha
        :param resultado: o resultado do rolamento dessa linha
        """
        self._tabela.append([(valor_menor, valor_maior), resultado])

    def editar_alcance_da_linha(self, valor_da_busca: int, novo_minimo: int, novo_maximo: int) -> None:
        """
        Altera o alcance de uma linha da tabela.

        :param valor_da_busca: Um valor que esteja entre o alcance da _tabela anterior
        (exemplo, se quiser alterar (1,10) para (1, 15) o valor_da_busca pode ser qualquer número entre 1 e 10
        :param novo_minimo: O novo valor mínimo
        :param novo_maximo: O novo valor máximo
        """
        nova_tupla = (novo_minimo, novo_maximo)
        index = busca_index_item_tabela(self._tabela, valor_da_busca)

        self._tabela[index][0] = nova_tupla

    def editar_resultado_da_linha(self, valor_da_busca: int, novo_resultado) -> None:
        """
        Altera o resultado que pode ser obtido naquela linha. Exemplo: [(1, 10), **"resultado 1"**] pode virar [(1,
        10), **"tesouro 1"**]

        :param valor_da_busca: Um valor que esteja entre o alcance da tabela (exemplo,
        se quiser alterar o resultado de (1,10) o valor_da_busca pode ser qualquer número entre 1 e 10)
        :param novo_resultado: O texto a ser substituído
        """
        index = busca_index_item_tabela(self._tabela, valor_da_busca)
        self._tabela[index][1] = novo_resultado

    # Métodos de resultado da rolagem ================================================================================
    def rolar(self, valor_fixo: int | None = None, modificador_dado: int = 0, coluna: str = None) -> None:
        """
        Rola novamente a tabela e altera o resultado. Tem a opção de incluir a coluna escolhida e com isso rolar
        eventuais dados do texto (exemplo: "3d6 moedas"). Se preferir o resultado puro de texto, não passe a coluna
        como parâmetro, mas use objeto.resultado["coluna"] no lugar
        :param valor_fixo: Procura por um valor específico dentro da tabela. Se omitido vai pegar o valor passado na atribuição da classe em "dados"
        :param modificador_dado: Para o caso de haver algum modificador não básico aplicado na tabela (ex.: role na tabela X com +10)
        :param coluna: Caso o resultado tenha mais de uma coluna. Seleciona a coluna e rola dos dados dentro dela
        """
        valor_fixo = self.dados if not valor_fixo else valor_fixo
        dado = valor_fixo if type(valor_fixo) == int else rolar_dado_notacao(valor_fixo)

        self._dado_rolado = DadoRolado(dado, modificador_dado)
        self._resultado = rolar_tabela(self._tabela, self._dado_rolado.total, coluna)

    # Getters ========================================================================================================
    @property
    def tabela(self):
        return self._tabela

    @property
    def rolamento(self):
        return self._dado_rolado

    @property
    def resultado(self):
        if type(self._resultado) is TabelaRolavel and self.rola_subtabela:
            self._resultado.rolar()
            return self._resultado.resultado

        return self._resultado


class TabelaRolavelSimples:
    """
    Igual a TabelaRolavel, a diferença é que todos os itens da tabela tem a mesma chance de saírem
    Como uma tabela de 20 itens que rola o d20 para saber o resultado
    """
    def __init__(self, tabela: list = None, rola_subtabela: bool = False):
        self._tabela = tabela
        self._resultado = ''

        self.rola_subtabela = rola_subtabela

        self.rolar()

    def __repr__(self):
        return f'<Tabela Rolável Simples de {len(self._tabela)} itens={self._tabela},\n dado usado: d{len(self._tabela)}>'
    
    def __str__(self):
        return f'Rolamento na tabela ({self.rolamento}): {self._resultado}'
    
    # Métodos de edição da _tabela ====================================================================================
    # Usados para tabelas que podem ser mudadas conforme o resultado
    def inserir_linha_tabela(self, entrada_nova: str):
        self._tabela.append(entrada_nova)

    def excluir_linha_tabela(self, entrada_excluir: str):
        self._tabela.remove(entrada_excluir)

    def editar_linha_tabela(self, entrada_antiga: str, entrada_nova: str):
        indice = self._tabela.index(entrada_antiga)
        self._tabela[indice] = entrada_nova

    # Métodos de resultado da rolagem ================================================================================
    def rolar(self, valor_fixo: int = None):
        if valor_fixo:
            self._resultado = self._tabela[valor_fixo]
        else:
            self._resultado = choice(self._tabela)

    # Getters ========================================================================================================
    @property
    def tabela(self):
        return self._tabela

    @property
    def rolamento(self):
        return self._tabela.index(self._resultado)

    @property
    def resultado(self):
        if type(self._resultado) is TabelaRolavel and self.rola_subtabela:
            self._resultado.rolar()
            return self._resultado.resultado

        return self._resultado
