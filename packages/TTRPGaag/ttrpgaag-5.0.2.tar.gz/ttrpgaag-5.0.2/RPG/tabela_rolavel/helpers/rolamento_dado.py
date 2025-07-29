from dataclasses import dataclass


@dataclass
class DadoRolado:
    """
    Retorna uma dataclass composto pelo rolamento, o dado rolado e seu valor e o valor total
    """
    rolamento: int
    modificador: int = 0
    total: int = 0

    def __post_init__(self):
        self.total = self.rolamento + self.modificador
