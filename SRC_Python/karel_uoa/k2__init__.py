#Příliš žluťoučký kůň úpěl ďábelské ó - PŘÍLIŠ ŽLUŤOUČKÝ KŮŇ ÚPĚL ĎÁBELSKÉ Ó
#U:/p5_Python/karel_uoa1/__init__.py
"""
Základní API s požadavky pro knihovnu robota Karla¤
realizující postupně zobecňované verze jeho světů.
Jednotlivé verze jsou definovány v samostatných modulech a podbalíčcích.
"""
import dbg; dbg_level=1; dbg.start_pkg(dbg_level, __name__, __doc__)
###########################################################################q
# GLOBÁLNÍ IMPORTY
###########################################################################q

import sys

from abc    import abstractmethod
from typing import Protocol, runtime_checkable
from enum   import Enum



###########################################################################q
# EXPORT
###########################################################################q

__all__ = (#'dbg',
    'MAX_MARKERS', 'DEFAULT_ROWS', 'DEFAULT_COLS', 'WALL_CHAR', 'RADIX',
    'Color', 'Dir4', 'IKarel', 'RobotError',
)



###########################################################################q
# GLOBÁLNÍ KONSTANTY
###########################################################################q

# Aktuální verze
VERSION = '25.01.9517_2025-11-26'

MAX_MARKERS  = 9    # Maximální povolený počet značek na jednom políčku
DEFAULT_ROWS = 8    # Implicitní počet řádků
DEFAULT_COLS = 8    # Implicitní počet sloupců

# Znak reprezentující zeď při zadávání světa stringy.
WALL_CHAR = '#'

# Základ číselné soustavy pro převod znaků na čísla představující
# počet značek na daném políčku pro případ, že by bylo povoleno
# více než 9 značek.
RADIX = 36



###########################################################################q
## POMOCNÉ DATOVÉ TYPY
###########################################################################q

Color = Enum('Color',
             'BLACK BLUE RED MAGENTA GREEN CYAN YELLOW WHITE')
# Nastaví prvky výčtového typu jako atributy modulu
# sys.modules[Color.__module__].__dict__.update(Color.__members__)
Color.__doc__ = 'Výčtový typ definující 8 základních RGB barev.'
Color.__str__ = lambda self: self.name
Color.__repr__= lambda self: 'Color.' + self.name
Color.DEFAULT = Color.BLUE  # Implicitní barva přidávaného robota



###########################################################################q

# @global_enum      # Chci jinou změnu __repr__, proto ji udělám ručně
class Dir4(Enum):
    """Výčtový typ pracující se 4 hlavními světovými stranami.
    """
    EAST      = (0,  1,  0)    # Východ       - doprava
    NORTH     = (1,  0, -1)    # Sever        - nahoru
    WEST      = (2, -1,  0)    # Západ        - doleva
    SOUTH     = (3,  0, +1)    # Jih          - dolů

    def __init__(self, n:int, dx:int, dy:int):
        self._n  = n
        self._dx = dx
        self._dy = dy

    def turn_left(self) -> 'Dir8':
        """Vrátí směr při otočení o 90° vlevo."""
        return Dir4.values[(self._n+1) & 0b_011]

    def next_position(self, row:int, col:int) -> tuple[int, int]:
        """Vrátí souřadnice sousední pozice v daném směru."""
        return (row + self._dy, col + self._dx)

# Nastaví prvky výčtového typu jako atributy modulu
# sys.modules[Dir4.__module__].__dict__.update(Dir4.__members__)
Dir4.__str__ = lambda self: self.name
Dir4.__repr__= lambda self: 'Dir4.' + self.name
Dir4.values  = tuple(v for v in Dir4.__members__.values())
Dir4.DEFAULT = Dir4.EAST



###########################################################################q
## ZÁKLADNÍ ROZHRANÍ ROBOTA KARLA
###########################################################################q

@runtime_checkable
class IKarel(Protocol):
    """Třída definuje protokol pro minimální objektovou verzi robota Karla.
    """

    def __repr__(self) -> str:
        """V podpisu robota bude jeho třída, rodné číslo (o kolikátou instanci
        dané třídy se jedná), pozice (řádek, sloupec a směr natočení) a barva.
        Nebude-li robot právě viditelný, bude přidána hloubka jeho skrytí
        a skutečná pozice, tj. ne ta, ve které je ve světě zobrazen.
        To pomůže při odhalování chyb v kódu definujícím skrytý pohyb robota.
        """

    @abstractmethod
    def pick(self) -> IKarel:           """Zvedne značku."""

    @abstractmethod
    def put(self)  -> IKarel:           """Položí značku."""

    @abstractmethod
    def step(self) -> IKarel:           """Posune se na další políčko."""

    @abstractmethod
    def turn_left(self) -> IKarel:      """Otočí se vlevo."""

    @abstractmethod
    def is_east(self) -> bool:          """Oznámí, je-li otočen na východ."""

    @abstractmethod
    def is_marker(self) -> bool:        """Oznámí, je-li pod ním značka."""

    @abstractmethod
    def is_wall(self) -> bool:          """Oznámí, je-li před ním zeď."""

    @abstractmethod
    def robot_ahead(self)->IKarel|None: """Vrátí odkaz na robota před ním."""

    @abstractmethod
    def hide(self) -> int:              """Zvýší úroveň skrývání robota 
        a vrátí novou úroveň skrývání. Dokud je tato úroveň >0, 
        zobrazuje se robot v posledním stavu, kdy měl úroveň 0."""

    @abstractmethod
    def unhide(self) -> int:            """Sníží úroveň skrývání a vrátí 
                                           předchozí úroveň skrývání robota."""


class IKarelCM(IKarel):
    """Potomek protokolu, jehož instance můžeme používat jako
    správce kontextu (context manager) v příkazu with.
    """

    def __enter__(self):
        """Nastaví kontext pro příkaz `with`, konkrétně skryje následné
        změny stavu svého robota, aby příkazy v těle `with` prováděl skrytě.
        """
        self.hide()
        return self

    def __exit__(self, exc_type:type, exc_value:BaseException, traceback):
        """Ukončí provádění příkazu `with` a robota opět zviditelní.
        Pokud byla v bloku with vyvolána výjimka, pošle ji dál.
        """
        try:
            self.unhide()   # Zmenší úroveň skrytí
        except Exception as unhide_error:
            if exc_value:   # V bloku byla vyvolána výjimka
                # Obalíme původní výjimku do kontextu té nově vzniklé,
                # aby se nic neztratilo
                raise unhide_error from exc_value
            else:   # V bloku nebyla vyvolána žádná výjimka
                raise   # Znovu vyvolej aktuálně zachycenou unhide_error
        return False    # Povolujeme vyhození případné výjimky z vnitřku bloku



###########################################################################q
## VÝJIMKY
###########################################################################q

class RobotError(Exception):
    """Výjimka informuje o stavu robota, který ji vyvolal.
    """
    def __init__(self, robot:IKarel, message:str):
        # dbg.prIN(1, f'{message = }')
        # dbg.prIN(1, f'{robot   = }')
        try:
            msg = robot.__repr__() + '\n'
            # dbg.prIN(1, f'{msg = }')
        except:
            msg = ""
        # dbg.prIN(1, f'{msg=},  {message=}')
        msg += message
        # dbg.prIN(1, f'New {msg = }')
        super().__init__(msg)



###########################################################################q
dbg.stop_pkg(dbg_level, __name__)
