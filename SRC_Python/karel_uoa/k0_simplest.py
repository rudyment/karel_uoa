#Příliš žluťoučký kůň úpěl ďábelské ó - PŘÍLIŠ ŽLUŤOUČKÝ KŮŇ ÚPĚL ĎÁBELSKÉ Ó
#U:/p5_Python/karel_uoa1/k0_simplest/__init__.py
"""
Výchozí, prozatím neobjektová verze knihovny funkcí pro robota Karla¤,
kterou by bylo možno využít pro zadávání úloh na procvičení konstrukcí
ze základů algoritmizace.
"""
import dbg; dbg_level=1; dbg.start_pkg(dbg_level, __name__, __doc__)
###########################################################################q
# GLOBÁLNÍ IMPORTY
###########################################################################q

from typing import overload     # Pouze pro typovou kontrolu



###########################################################################q
# EXPORT
###########################################################################q

__all__ = ['new_world', 'add_robot', 'show_world',
           'EAST', 'NORTH', 'WEST', 'SOUTH',
           'step', 'turn_left', 'put', 'pick',
           'is_wall', 'is_marker', 'is_east', ]



###########################################################################q
# GLOBÁLNÍ KONSTANTY
###########################################################################q

MAX_MARKERS  = 9    # Maximální povolený počet značek na jednom políčku
DEFAULT_ROWS = 8    # Implicitní počet řádků
DEFAULT_COLS = 8    # Implicitní počet sloupců

cE:str = '>'    # Znak zobrazující robota otočeného na východ   > ► → ▷ »
cN:str = 'A'    # Znak zobrazující robota otočeného na sever    A ▲ ↑ △ ^
cW:str = '<'    # Znak zobrazující robota otočeného na západ    < ◄ ← ◁ «
cS:str = 'V'    # Znak zobrazující robota otočeného na jih      V ▼ ↓ ▽ v
cWALL  = '█'    # Znak reprezentující ve vykresleném dvorku zeď # █ ▓ ▒ ░

# N-tice znaků pro zobrazení robota natočeného do příslušného směru
cDIR:tuple[str] = (cE, cN, cW, cS)

EAST  = 0   # Východ       - doprava
NORTH = 1   # Sever        - nahoru
WEST  = 2   # Západ        - doleva
SOUTH = 3   # Jih          - dolů

dx = [1,  0, -1, 0]     # Vodorovný posun při natočení do daného směru
dy = [0, -1,  0, 1]     # Svislý    posun při natočení do daného směru

ROW:int  = 0    # Index řádku   v seznamu souřadnic robota
COL:int  = 1    # Index sloupce v seznamu souřadnic robota
DIR4:int = 2    # Index směru   v seznamu souřadnic robota



###########################################################################q
# GLOBÁLNÍ PROMĚNNÉ
###########################################################################q

# Následující atributy jsou konstantní během života jednoho světa (dvorku)
ROWS:int = 0                    # Počet řádků dvorku
COLS:int = 0                    # Počet sloupců dvorku
WORLD:list[list[int]] = None    # Karlův svět - dvorek

KAREL:list[int] = None          # Souřadnice robota [řádek, sloupec, směr]



###########################################################################q
# FUNKCE PRO OVLÁDÁNÍ ROBOTA
###########################################################################q

def put() -> None:
    """Robot položí značku na políčko, na němž stojí. Přesáhne li pak celkový
    počet značek na daném políčku maximální povolený počet, ohlásí chybu.
    """
    WORLD[r:=KAREL[ROW]][c:=KAREL[COL]] += 1
    if WORLD[r][c] > MAX_MARKERS:
        raise Exception(f"Na pole lze položit maximálně"
                        f"{MAX_MARKERS} značek")


def pick() -> None:
    """Robot zvedne značku na políčku, na němž stojí.
    Není li na něm žádná značka, ohlásí chybu.
    """
    WORLD[r:=KAREL[ROW]][c:=KAREL[COL]] -= 1
    if WORLD[r][c] < 0:
        raise Exception(f"Pokus o zvednutí neexistující značky")


def step() -> None:
    """Přesune robota na sousední pole ve směru, do nějž je natočen.
    Je li na tomto poli zeď, ohlásí chybu.
    """
    if is_wall():
        raise Exception('Robot narazil do zdi')
    KAREL[ROW] += dy[KAREL[DIR4]]
    KAREL[COL] += dx[KAREL[DIR4]]
    show_world()


def turn_left() -> None:
    """Otočí robota o 90° vlevo."""
    KAREL[DIR4] = (KAREL[DIR4] + 1)  %  4
    show_world()


def is_marker()  ->  bool:
    """Je li pod robotem značka, vrátí True, jinak vrátí False.
    """
    return WORLD[KAREL[ROW]][KAREL[COL]] > 0


def is_east()    ->  bool:
    """Je li robot otočen na východ, vrátí True, jinak vrátí False.
    """
    return (KAREL[DIR4] == EAST)


def is_wall()  ->  bool:
    """Je li na políčku před robotem zeď, takže robot nemůže udělat krok,
    vrátí True. Jinak vrátí False. Zdí je obehnán i celý dvorek.
    """
    drow   = KAREL[ROW] + dy[KAREL[DIR4]]  # Destination row
    dcol   = KAREL[COL] + dx[KAREL[DIR4]]
    result = (drow<0  or  dcol<0  or  drow>=ROWS  or  dcol>=COLS
                      or  WORLD[drow][dcol] < 0)
    return result



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
    global ROWS, COLS, WORLD, KAREL
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
    else:
        raise Exception("Špatně zadané argumenty pro vytváření světa")
    ROWS  = len(WORLD)
    COLS  = len(WORLD[0])
    KAREL = None


def add_robot(row:int=-1, col:int=0, dir4:int=EAST):
    """Umístí na zadané souřadnice robota otočeného do zadaného směru.
    Byl-li na dvorku nějaký robot, odstraní ho a nahradí přidaným.
    """
    if row < 0:   row = ROWS + row
    if col < 0:   col = COLS + col
    if ((row < 0) or (col < 0) or (row >= ROWS) or (col >= COLS)
                  or (dir4< 0) or (dir4 > 3)):
        raise Exception("Špatně zadané argumenty pro vytváření robota\n"
              f"{row=}, {col=}, {dir4=}")
    global KAREL
    KAREL = [row, col, dir4]



###########################################################################q
# FUNKCE PRO ZOBRAZENÍ SVĚTA
###########################################################################q

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
    if KAREL:
        world[KAREL[ROW]][KAREL[COL]] = cDIR[KAREL[DIR4]]
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
# TESTY
###########################################################################q

TEST = 1
if TEST:
    def e(cmd:str) -> None:
        """Vypíše a provede zadaný příkaz."""
        print(cmd)
        exec(cmd)

    def test():
        """Prověří základní funkcionalitu modulu."""
        VERSION = 'k0_simplest'
        print(f'{2*('\n' + 60*'#')}\nPrověrka verze {VERSION}.\n')
        e("new_world(3, 8);    add_robot();    show_world()")
        e("step()");                            e("print(is_east())")
        e("turn_left()");                       e("print(is_east())")
        pass;                                   e("print(is_marker())")
        e("put()"); e("put()"); e("put()");     e("print(is_marker())")
        e("pick()");  e("step()");              e("print(is_wall())")
        e("step()");                            e("print(is_wall())")
        e('new_world("01234", "5678#");   add_robot(0, -1, WEST)')
        e("show_world()")
        input(f"{('\n' + 60*'#')}\nKonec prověrky verze {VERSION}.\n"
              f"Zkontroluj ji a potvrď stiskem Enter")

if __name__ == '__main__': test()



###########################################################################q
dbg.stop_pkg(dbg_level, __name__)
