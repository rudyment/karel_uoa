#Příliš žluťoučký kůň úpěl ďábelské ó - PŘÍLIŠ ŽLUŤOUČKÝ KŮŇ ÚPĚL ĎÁBELSKÉ Ó
#U:/p5_Python/karel_uoa1/k1_classkarel/__init__.py
"""
Výchozí objektová verze knihovny Karla¤,
v níž jsou směry a barvy definovány jako objekty
a roboti jsou instancemi třídy Karel.
"""
import dbg; dbg_level=1; dbg.start_pkg(dbg_level, __name__, __doc__)
###########################################################################q
# GLOBÁLNÍ IMPORTY
###########################################################################q

from enum   import Enum
from typing import overload



###########################################################################q
# EXPORT
###########################################################################q

__all__ = ['Color', 'Dir4', 'new_world', 'show_world',
           'add_robot', 'remove_robot', 'Karel', 'RobotError'
          ]



###########################################################################q
# GLOBÁLNÍ KONSTANTY
###########################################################################q

MAX_MARKERS  = 9    # Maximální povolený počet značek na jednom políčku
DEFAULT_ROWS = 8    # Implicitní počet řádků
DEFAULT_COLS = 8    # Implicitní počet sloupců



###########################################################################q
# GLOBÁLNÍ PROMĚNNÉ
###########################################################################q

# Následující atributy jsou konstantní během života jednoho světa (dvorku)
ROWS:int = 0                    # Počet řádků dvorku
COLS:int = 0                    # Počet sloupců dvorku
WORLD:list[list[int]] = None    # Karlův svět - dvorek

# Slovník robotů přítomných ve světě (na dvorku)
ROBOTS:dict[tuple[int,int], Karel] = None



###########################################################################q
## POMOCNÉ DATOVÉ TYPY
###########################################################################q

Color = Enum('Color',
             'BLACK BLUE RED MAGENTA GREEN CYAN YELLOW WHITE')
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

Dir4.__str__ = lambda self: self.name
Dir4.__repr__= lambda self: 'Dir4.' + self.name
Dir4.values  = tuple(v for v in Dir4.__members__.values())
Dir4.DEFAULT = Dir4.EAST



###########################################################################q
# TŘÍDA ROBOTA KARLA
###########################################################################q

class Karel():
    """Třída robotů pohybujících se ve světě podle instrukcí.
    """
    count = 0   # Počitadlo vytvořených instancí

    def __init__(self, row:int=-1, col:int=0,
                 dir4:Dir4=Dir4.DEFAULT, color:Color=Color.DEFAULT):
        """Vytvoří robota se zadanými charakteristikami.
        """
        global ROBOTS
        if row < 0:   row = ROWS + row
        if col < 0:   col = COLS + col
        check_position(row, col)
        Karel.count += 1
        self._ID    = Karel.count
        self._row   = self._vrow  = row     # Real row  == visible row
        self._col   = self._vcol  = col     # Real col  == visible col
        self._dir4  = self._vdir4 = dir4    # Real dir4 == visible dir4
        self._color = color
        self._hidden= 0


    def __repr__(self):
        """Vrátí systémový podpis identifikující daného robota.
        """
        hidden = (f', hidden={self._hidden}, vrow={self._vrow}'
                  f', vcol={self._vcol}, vdir4={self._vdir4.name}'
                  if self._hidden else '')
        result = (f'{self.__class__.__name__}{self._ID}('
                  f'row={self._row}, col={self._col}, '
                  f'dir4={self._dir4.name}, color={self._color.name}'
                  f'{hidden})')
        return result


    def put(self) -> Karel:
        """Robot položí značku na políčko, na němž stojí. Přesáhne li pak celkový
        počet značek na daném políčku maximální povolený počet, ohlásí chybu.
        Vrací odkaz na svoji instanci,díky čemuž lze volání metod řetězit.
        """
        WORLD[r:=self._row][c:=self._col] += 1
        if WORLD[r][c] > MAX_MARKERS:
            raise Exception(f"Na pole lze položit maximálně"
                            f"{MAX_MARKERS} značek")
        return self


    def pick(self) -> Karel:
        """Robot zvedne značku na políčku, na němž stojí.
        Není li na něm žádná značka, ohlásí chybu.
        Vrací odkaz na svoji instanci,díky čemuž lze volání metod řetězit.
        """
        WORLD[r:=self._row][c:=self._col] -= 1
        if WORLD[r][c] < 0:
            raise Exception(f"Pokus o zvednutí neexistující značky")
        return self


    def step(self) -> Karel:
        """Přesune robota na sousední pole ve směru, do nějž je natočen.
        Je li na tomto poli zeď, ohlásí chybu.
        Vrací odkaz na svoji instanci,díky čemuž lze volání metod řetězit.
        """
        global ROBOTS
        row, col = next_position(self)
        check_position(row, col)
        del ROBOTS[(self._row,self._col)]   # Smaže informaci o původní pozici
        self._row = row
        self._col = col
        ROBOTS[(row,col)] = self    # Nastaví informaci o robotu v nové pozici
        if self._hidden == 0:
            self._vrow = row    # Visible row
            self._vcol = col    # Visible row
            show_world()
        return self


    def turn_left(self) -> Karel:
        """Otočí robota o 90° vlevo.
        Vrací odkaz na svoji instanci, díky čemuž lze volání metod řetězit.
        """
        self._dir4 = self._dir4.turn_left()
        if self._hidden == 0:
            self._vdir4 = self._dir4    # Visible dir4
            show_world()
        return self


    def is_marker(self)  ->  bool:
        """Je li pod robotem značka, vrátí True, jinak vrátí False.
        """
        return WORLD[self._row][self._col] > 0


    def is_east(self)    ->  bool:
        """Je li robot otočen na východ, vrátí True, jinak vrátí False.
        """
        return (self._dir4 == Dir4.EAST)


    def is_wall(self)  ->  bool:
        """Je li na políčku před robotem zeď, takže robot nemůže udělat krok,
        vrátí True. Jinak vrátí False. Zdí je obehnán i celý dvorek.
        """
        row, col = next_position(self)
        result = (row<0  or  col<0  or  row>=ROWS  or  col>=COLS
                         or  WORLD[row][col] < 0)
        return result


    def robot_ahead(self) -> Karel | None:
        """Je-li na políčku před robotem jiný robot, vrátí odkaz na něj,
        jinak vrátí prázdný odkaz.
        """
        return ROBOTS.get(next_position(self))


    def hide(self) -> int:
        """Zvýší úroveň skrývání robota a vrátí novou úroveň skrývání.
        Je-li tato úroveň >0, zobrazuje se robot v posledním stavu,
        kdy měl úroveň 0.
        """
        self._hidden += 1
        return self._hidden


    def unhide(self) -> int:
        """Sníží úroveň skrývání a vrátí předchozí úroveň skrývání robota.
        Je-li tato úroveň 0, překreslí robota v aktuální pozici.
        """
        self._hidden -= 1
        if self._hidden == 0:
            self._vrow  = self._row     # Visible row
            self._vcol  = self._col     # Visible col
            self._vdir4 = self._dir4    # Visible dir4
            show_world()
        return self._hidden

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
# FUNKCE PRO VYTVOŘENÍ SVĚTA ROBOTŮ A PRÁCI S NÍM
###########################################################################q

@overload
def new_world(rows:int=DEFAULT_ROWS, cols:int=DEFAULT_COLS) -> None:
    """Případnou existující aktivní instanci dvorku nejprve deaktivuje.
    Vytvoří prázdný šachovnicový dvorek se zadaným počtem řádků a sloupců.
    """

@overload
def new_world(row0:str, *rows:str) -> None:
    """Případnou existující aktivní instanci dvorku nejprve deaktivuje.
    Vytvoří svět (dvorek) zaplněný značkami, v němž jednotlivé stringy
    reprezentují řádky a jednotlivé znaky obsah jednotlivých polí.
    Číslo na políčku udává počet značek, znak # označuje zeď.
    Políčko bez značek lze zadat i jako mezeru.
    """

def new_world(*fields:int | str) -> None:
    """Případnou existující aktivní instanci dvorku nejprve deaktivuje.
    Poté vytvoří nový šachovnicový svět podle požadavků popsaných
    ve výše uvedených přetížených definicích.
    """
    global ROWS, COLS, WORLD, ROBOTS
    WORLD = []
    if len(fields)==0:
        return new_world(DEFAULT_ROWS, DEFAULT_COLS)     # Rekurzivní volání
    elif isinstance(fields[0], int):        # Prázdný svět dané velikosti
        ROWS = fields[0]
        COLS = fields[1] if len(fields)>1 else DEFAULT_COLS
        row = COLS * [0]
        WORLD = [row[:] for _ in range(ROWS)]
    elif isinstance(fields[0], str):        # Svět zadaný stringy
        WORLD = [[int(ch) if '0'<=ch<='9' else
                       (0 if ch == ' '    else -1)  for ch  in row]
                                                    for row in fields]
    ROWS   = len(WORLD)
    COLS   = len(WORLD[0])
    if any(len(row) != COLS for row in WORLD):
        raise RobotError("Všechny řádky světa musejí být stejně dlouhé")
    ROBOTS = {}


def check_position(row, col):
    """Ověří, zda je možné umístit zadaného robota požadovanou pozici."""
    if (row < 0) or (row >= ROWS) or (col < 0) or (col >= COLS):
        raise RobotError(None,
              f'Robot je umísťován mimo dvorek na [{row},{col}]')
    if (WORLD[row][col] < 0):
        raise RobotError(None, f'Robota nelze umístit na pozici '
                               f'[{row},{col}] - je na ní zeď')
    if (row, col) in ROBOTS:
        raise RobotError(None, f'Robota nelze umístit na pozici'
                               f'[{row}, {col}] - stojí tam robot:\n'
                               f'{ROBOTS[(row,col)]}')


def add_robot(row:int=-1, col:int=0, dir4:Dir4=Dir4.DEFAULT,
              color:Color=Color.DEFAULT) -> Karel:
    """Vytvoří nového robota a umístí jej do aktuálního světa
    na zadané souřadnice otočeného do zadaného směru.
    """
    check_position(row, col)
    robot = Karel(row, col, dir4, color)
    ROBOTS[(row,col)] = robot
    return robot


def remove_robot(robot:Karel) -> None:
    """Odebere robota zadaného v argumentu `robot` z aktuálního světa
    robotů. Pokud se v aktuálním světě zadaný robot nevyskytuje,
    vyvolá výjimku.
    """
    if not (robot in ROBOTS.values()):
        raise RobotError(robot, f'Zadaný robot není přítomen')
    del ROBOTS[(robot._row, robot._col)]


def next_position(robot:Karel) -> tuple[int,int]:
    """Vrátí souřadnice pozice před robotem."""
    return robot._dir4.next_position(robot._row, robot._col)



###########################################################################q
# FUNKCE PRO ZOBRAZENÍ SVĚTA
###########################################################################q

# N-tice znaků pro zobrazení robota natočeného do příslušného směru
# Znaky jsou vybrány z fontu Source Code Pro, v jiných fontech mohou
# některé znaky chybět, anebo mohou být k dispozici jiné akceptovatelné
color2char:dict[Color, str] = {
    Color.BLACK:    '>A<V',
    Color.BLUE:     '►▲◄▼',
    Color.RED:      '→↑←↓',
    Color.MAGENTA:  '⇒⇑⇐⇓',
    Color.GREEN:    '»^«v',
    Color.CYAN:     '▷△◁▽',
    Color.YELLOW:   '╠╩╣╦',
    Color.WHITE:    '├┴┤┬',
}

cWALL = '█'     # Znak reprezentující ve vykresleném dvorku zeď


def show_world() -> None:
    """Vytiskne aktuální obsah dvorku. Protože nás čas netlačí, nevadí,
    že při každém tisku budujeme příslušný string znovu.
    Kdybychom jej vybudovali spolu s dvorkem, zjednodušil by se tisk,
    ale všechny funkce měnící stav světa by museli příslušně změnit
    jak matici světa, tak string pro jeho tisk.
    Kdybychom si pamatovali jenom tento string a ne svět čísel,
    tak by se některé operace zbytečně komplikovali přepočítáváním.
    A nejhorší by na tom bylo, že bychom model světa provázali
    s modelem jeho zobrazení, což by komplikovalo budoucí úpravy.
    """
    # Při převodu zatím počítám maximálně s 9 značkami
    world = [[str(i) if i > 0 else
              cWALL  if i < 0 else " " for i in row]
             for row in WORLD ]
    for row, col in ROBOTS:     # Do světa se doplní znaky robotů
        robot = ROBOTS[(row, col)]
        vrow = robot._vrow      # Visible row
        vcol = robot._vcol      # Visible col
        world[vrow][vcol] = color2char[robot._color][robot._vdir4._n]
    col_nums = lambda:("  "
             + "".join([f'{i:>2}' for i in range(COLS)]) + '\n')
    # Funkce pro budování rámečku kolem jednotlivých polí
    top = lambda : '  ' + '╔' + (COLS-1)*('═╤') + '═╗\n'
    ins = lambda : '  ' + '╟' + (COLS-1)*('─┼') + '─╢\n'
    bot = lambda : '  ' + '╚' + (COLS-1)*('═╧') + '═╝\n'
    yard = [col_nums(), top()]      # Čísla sloupců + horní hranice
    for ir in range(ROWS):          # Přidáváme střed s obsahem polí
        rr = world[ir]              # Seznam znaků na jednotlivých polích
        yard.append(f'{ir:>2}║'     # Číslo řádku + levý okra
                  +  '│'.join(rr)   # Počty značek na jednotlivých polích
                  + f'║{ir:<2}\n')  # Pravý okraj + číslo řádku
        yard.append(ins())          # Oddělovací řádek
    yard[-1] = bot()                # Nahradí spodní oddělovač spodní hranicí
    yard.append(col_nums())         # Přidá spodní číslování
    print(*yard, sep="")



###########################################################################q
## VÝJIMKY
###########################################################################q

class RobotError(Exception):
    """Výjimka informuje o stavu robota, který ji vyvolal.
    """
    def __init__(self, robot:Karel, message:str):
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
# TESTY
###########################################################################q

TEST = 1

if TEST:

    k = r = None

    def e(cmd:str) -> None:
        """Vypíše a provede zadaný příkaz."""
        global k, r
        print(cmd)
        exec(cmd, dict(k=k, r=r))

    def check_api() -> None:
        """Prověří implementaci základních rozhraní."""
        import sys
        this_module = sys.modules[__name__]
        print('\nPrověrka API základních objektů')
        print(f'{this_module.__name__ = }')

    def check_functionality() -> None:
        # Prověří základní funkcionalitu modulu.
        global k, r
        new_world(3, 8);    k=Karel();          e("print(f'Vytvořen: {k}')")
        e("print(k.step())");                   e("print(k.is_east())")
        e("print(k.turn_left())");              e("print(k.is_east())")
        e("print(k.is_marker())")
        e("k.put().put().put()");               e("print(k.is_marker())")
        e("k.pick()");  e("k.step()");          e("print(k.is_wall())")
        e("k.step()");                          e("print(k.is_wall())")
        new_world("01234", "5678#")
        k=Karel(0, -1, Dir4.WEST)
        r=Karel(1, 1,Dir4.NORTH, color=Color.MAGENTA)
        show_world();  e('''print(f"""Vytvořeni: {k}\n{11*' '}{r}""")''')
        e('k.hide()')
        e('print(k.step().step())');e('r.step()');e('k.unhide()')
        e('print(k.robot_ahead())');            e('print(r.robot_ahead())')
        e('r.hide();print(r.turn_left().step())')
        e('r.turn_left().turn_left().unhide()');e('print(r)')
        pass;                                   e('print(r.robot_ahead())')

    def test():
        VERSION = 'k1_interface'
        print(f'{2*('\n' + 60*'#')}\nPrověrka verze {VERSION}.\n')
        check_api()
        check_functionality()
        input(f"{('\n' + 60*'#')}\nKonec prověrky verze {VERSION}.\n"
              f"Zkontroluj ji a potvrď stiskem Enter")

if __name__ == '__main__': test()



###########################################################################q
dbg.stop_pkg(dbg_level, __name__)
