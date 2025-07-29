from ...dado.rolar_dado_notacao import rolar_dado_notacao
import re


def rola_dados_resultado(rolar_dados: bool, resultado: str) -> str:
    """
    Transforma o texto que contenha notação de dados em texto com resultado
    :param rolar_dados:
    :param resultado:
    :return:
    """
    if rolar_dados and type(resultado) == str:
        palavras = resultado.split()
        texto_regex = []

        for palavra in palavras:
            if re.match(r'\d*d\d+(?:[-+*/]\d+)?', palavra):
                rolado = rolar_dado_notacao(palavra)
                texto_regex.append(str(rolado))
            else:
                texto_regex.append(palavra)

        resultado = ' '.join(texto_regex)

    return resultado
