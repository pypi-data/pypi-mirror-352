import re
from ...dado.helpers.monta_dado import monta_dado


def converter_notacao_dado(notacao: str) -> dict:
    """
    Converte a notação de _dados de RPG em um objeto para ser manipulado posteriormente

    :param notacao: a notação de dado usada. Exemplo: "3d6+1d4+3"
    :return: um dicionário: { "dados": [...dado], "modificador_dado": { "modificador_dado": numero, "operador": string }
        "dado": { "quantidade": numero, "faces": numero, "operador": string }
        No exemplo acima: {
            "dados": [ { "quantidade": 3, "faces": 6 }, { "quantidade": 1, "faces": 4", "operador": "+" } ],
            "modificador_dado": { "numero": 3, "operador": "+" }
        }
    """

    # Separa a fórmula em partes
    partes = re.split(r"([+\-*/])", notacao)

    # Separa o modificador_dado numérico
    if "d" in partes[-1]:
        modificador = {
            "valor": 0,
            "operador": "+"
        }
    else:
        modificador = {
            "valor": int(partes.pop(-1)),
            "operador": partes.pop(-1)
        }

    # Converte o primeiro dado na variável
    dados = [monta_dado(partes.pop(0))]

    # Insere as demais partes
    while partes:
        operador = partes.pop(0)
        print(type(operador))
        notacao_dado = partes.pop(0)

        dado = monta_dado(notacao_dado)
        dado["operador"] = operador

        dados.append(dado)

    resultado = {
        "dados": dados,
        "modificador_dado": modificador
    }

    return resultado
