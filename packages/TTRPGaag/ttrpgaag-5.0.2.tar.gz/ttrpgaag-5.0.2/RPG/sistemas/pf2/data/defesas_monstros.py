from dataclasses import dataclass, InitVar
from typing import Optional


@dataclass
class Defesa:
    extreme: int
    high: int
    moderate: int
    low: int
    terrible: InitVar[Optional[int]] = None


ac_base = [
    Defesa(19, 16, 15, 13),
    Defesa(19, 16, 15, 13),
    Defesa(21, 18, 17, 15),
    Defesa(22, 19, 18, 16),
    Defesa(24, 21, 20, 18),
    Defesa(25, 22, 21, 18),
    Defesa(27, 24, 23, 21),
    Defesa(28, 25, 24, 22),
    Defesa(30, 27, 26, 24),
    Defesa(31, 28, 27, 25),
    Defesa(33, 30, 29, 27),
    Defesa(34, 31, 30, 28),
    Defesa(36, 34, 33, 31),
    Defesa(37, 34, 33, 31),
    Defesa(39, 36, 35, 33),
    Defesa(40, 37, 36, 34),
    Defesa(42, 39, 38, 36),
    Defesa(43, 40, 39, 37),
    Defesa(45, 42, 41, 39),
    Defesa(46, 43, 42, 40),
    Defesa(48, 45, 44, 42),
    Defesa(49, 46, 45, 43),
    Defesa(51, 48, 47, 45),
    Defesa(52, 49, 48, 46),
    Defesa(54, 51, 50, 48),
    Defesa(18, 15, 14, 12)
]

saving_throws_base = [
    Defesa(10, 9, 6, 3, 1),
    Defesa(11, 10, 7, 4, 2),
    Defesa(12, 11, 8, 5, 3),
    Defesa(14, 12, 9, 6, 4),
    Defesa(15, 14, 11, 8, 6),
    Defesa(17, 15, 12, 9, 7),
    Defesa(18, 17, 14, 11, 8),
    Defesa(20, 18, 15, 12, 10),
    Defesa(21, 19, 16, 13, 11),
    Defesa(23, 21, 18, 15, 12),
    Defesa(24, 22, 19, 16, 14),
    Defesa(26, 24, 21, 28, 15),
    Defesa(27, 25, 22, 19, 16),
    Defesa(29, 26, 23, 20, 18),
    Defesa(30, 28, 25, 22, 19),
    Defesa(32, 29, 26, 23, 20),
    Defesa(33, 30, 28, 25, 22),
    Defesa(35, 32, 29, 26, 23),
    Defesa(36, 33, 30, 27, 24),
    Defesa(38, 35, 32, 29, 26),
    Defesa(39, 36, 33, 30, 27),
    Defesa(41, 38, 35, 32, 28),
    Defesa(43, 39, 36, 33, 30),
    Defesa(44, 40, 37, 34, 31),
    Defesa(46, 42, 38, 36, 32),
    Defesa(9, 8, 5, 2, 0)
]

defesa_base = []
for i in range(len(ac_base)):
    defesa_base.append(
        {
            "AC": ac_base[i],
            "Fort": saving_throws_base[i],
            "Ref": saving_throws_base[i],
            "Will": saving_throws_base[i]
        }
    )


defesas_monstro_nao_oficial = [
    {"AC": 13, "Fort": 3, "Ref": 2, "Will": 0},
    {"AC": 15, "Fort": 4, "Ref": 4, "Will": 3},
    {"AC": 16, "Fort": 6, "Ref": 5, "Will": 3},
    {"AC": 18, "Fort": 7, "Ref": 6, "Will": 6},
    {"AC": 19, "Fort": 7, "Ref": 9, "Will": 6},
    {"AC": 20, "Fort": 11, "Ref": 9, "Will": 8},
    {"AC": 21, "Fort": 13, "Ref": 10, "Will": 11},
    {"AC": 21, "Fort": 13, "Ref": 10, "Will": 10},
    {"AC": 25, "Fort": 14, "Ref": 13, "Will": 12},
    {"AC": 27, "Fort": 15, "Ref": 15, "Will": 14},
    {"AC": 26, "Fort": 18, "Ref": 16, "Will": 15},
    {"AC": 30, "Fort": 19, "Ref": 16, "Will": 16},
    {"AC": 31, "Fort": 21, "Ref": 19, "Will": 21},
    {"AC": 33, "Fort": 24, "Ref": 21, "Will": 22},
    {"AC": 33, "Fort": 24, "Ref": 19, "Will": 24},
    {"AC": 35, "Fort": 26, "Ref": 26, "Will": 23},
    {"AC": 38, "Fort": 29, "Ref": 24, "Will": 26},
    {"AC": 39, "Fort": 29, "Ref": 26, "Will": 28},
    {"AC": 40, "Fort": 31, "Ref": 25, "Will": 27},
    {"AC": 43, "Fort": 34, "Ref": 30, "Will": 29},
    {"AC": 44, "Fort": 32, "Ref": 31, "Will": 33},
    {"AC": 45, "Fort": 36, "Ref": 33, "Will": 35},
    {"AC": 47, "Fort": 37, "Ref": 34, "Will": 37},
    {"AC": 49, "Fort": 43, "Ref": 38, "Will": 39},
]
