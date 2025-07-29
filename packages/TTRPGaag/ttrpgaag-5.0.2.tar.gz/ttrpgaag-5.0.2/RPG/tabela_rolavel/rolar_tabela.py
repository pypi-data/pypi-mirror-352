from .helpers.ajeita_tabela import ordena_dicionario, converte_lista_para_dicionario
from .helpers.ajusta_resultados import rola_dados_resultado

def rolar_tabela(tabela: list | dict, valor: int, coluna: str | int | None=None, rolar_dados: bool=True) -> str:
    """Busca o resultado em uma tabela de RPG retornando a linha e a eventual 
    coluna, caso tenha. Se o texto possuir notação de dados (exemplo: 1d6)
    também já rola o resultado.

    A tabela pode ser um dicionário ou uma lista.
    Como dicionário, cada chave é o número mais alto (exemplo: de 3 até 6, seria 6).
    Por exemplo: {2: 'resultado 1', 4: 'resultado 2'}

    Como lista o padrão de cada linha é ((inicio, fim), resultado da busca).
    É possível colocar apenas um valor na primeira tupla caso esse item só tenha
    um valor.
    
    O resultado da tabela pode ser uma string como "1d6 gp" ou um dicionário com
    o formato { "col 1": "resultado col 1", "col2": "valor col2" } para tabelas
    com colunas

    Args:
        tabela (list | dict): a tabela a ser buscado, pode aparecer em dois formatos: dicionário ou lista.
        valor (int): o valor a ser buscado
        coluna (str, int, optional): qual a coluna a ser buscada pelo resultado, se não tiver colunas, ignore. Defaults to None.
        rolar_dados (bool, optional): booleano para indicar se o resultado que contenha dados a ser rolado (ex.: "1d10 gp"). Se não quiser que já retorne o dado rolado, marque False. Defaults to True.

    Returns:
        str: O resultado da tabela
    """
    # Converte a lista para dicionário
    tabela = tabela if type(tabela) is dict else converte_lista_para_dicionario(tabela)
    # Ordena o dicionário em ordem numérica, caso esteja fora de ordem
    tabela = ordena_dicionario(tabela)

    # Converte o dicionário em duas listas para realizar a busca
    # e gera o índice do item rolado
    chaves, valores = list(tabela.keys()), list(tabela.values())
    indice = next((chave[0] for chave in enumerate(chaves) if chave[1] >= valor), -1)

    # Gera o resultado da busca
    resultado = valores[indice]
    resultado = resultado[coluna] if coluna else resultado

    resultado = rola_dados_resultado(rolar_dados, resultado)
    
    return resultado
    


if __name__ == "__main__":
    # Exemplo de uso
    exemplo_tabela = [
        ((1, 6), {"coluna 1": "2d6 moedas de ouro", "coluna 2": "2d10+1d6 moedas de ouro e 1d6 de prata",
                  "coluna 3": "d8*2 moedas de ouro"}),
        ((7, 9), {"coluna 1": "2d6 moedas de ouro", "coluna 2": "2d10+1d6 moedas de ouro e 1d6 de prata",
                  "coluna 3": "d8*2 moedas de ouro"}),
        (10, {"coluna 1": "2d6 moedas de ouro", "coluna 2": "2d10+1d6+100 moedas de ouro e 1d6 de prata",
              "coluna 3": "d8*2 moedas de ouro"})
    ]

    print('-------------------------------------------------------------------------')
    print("Tabela:")
    print(*exemplo_tabela, sep='\n')
    print('-------------------------------------------------------------------------')
    print(f"O resultado foi: {rolar_tabela(exemplo_tabela, 3, 'coluna 2')}")
    print('-------------------------------------------------------------------------')