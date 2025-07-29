from ...tabela_rolavel import TabelaRolavel
from .data.criticos import criticos

tabela_criticos = {chave: TabelaRolavel(criticos[chave], 'd100') for chave in criticos.keys()}
intensidades = 'ABCDE'


def consulta_critico(tipo_critico: str, intensidade_critico: str, valor_rolado: int) -> str:
    """
    Faz uma consulta na tabela de críticos com um valor rodado externamente e retornar o resultado
    :param tipo_critico: qual o crítico procurado, como chave da tabela de críticos
    :param intensidade_critico: qual a letra do crítico
    :param valor_rolado: qual o valor rolado nos dados
    :return: uma string com o resultado do crítico
    """
    intensidade_critico = intensidade_critico.upper()
    valor_rolado = 100 if valor_rolado == 0 else valor_rolado

    if tipo_critico not in criticos.keys():
        print(f'{tipo_critico} não é um tipo de crítico válido. Tipos aceitáveis: {", ".join(list(criticos.keys()))}.')
        return ''

    if intensidade_critico not in intensidades:
        print(f'{intensidade_critico} não é uma intensidade de crítico válida. Valores aceitáveis: {", ".join(list(intensidades))}')
        return ''

    critico = tabela_criticos[tipo_critico]
    critico.rolar(valor_fixo=valor_rolado, coluna=intensidade_critico)

    return critico.resultado
