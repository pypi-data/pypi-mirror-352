from .dado import Dado
from .helpers.converter_notacao_dado import converter_notacao_dado


# ==================================================================
# Funções relacionadas
# ==================================================================

def rolar_dado_notacao(notacao: str) -> int:
    """
    Rola um conjunto de dados com base na linguagem de RPG, estilo "3d6+3" e retorna o valor total

    :param notacao: A fórmula do dado. Aceita mais de um dado, como "1d8+1d6"
    """
    # converte a notação em _dados
    notacao = converter_notacao_dado(notacao) if not notacao.isdigit() else int(notacao)

    resultado = 0

    if isinstance(notacao, int):
        return notacao

    # insere os _dados
    for dado in notacao.get("dados"):
        quantidade = dado.get("quantidade")
        faces = dado.get("faces")
        operador = dado.get("operador") if dado.get("operador") else "+"

        total_rolado = Dado(quantidade, faces).total

        resultado = eval(f'{resultado} {operador} {total_rolado}')

    # insere o modificador_dado
    operador_modificador = notacao.get("modificador_dado").get("operador")
    valor_modificador = notacao.get("modificador_dado").get("valor")

    resultado = eval(f'{resultado} {operador_modificador} {valor_modificador}')

    return resultado


if __name__ == '__main__':
    print(rolar_dado_notacao('3d6'))
