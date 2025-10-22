#Příliš žluťoučký kůň úpěl ďábelské ó - PŘÍLIŠ ŽLUŤOUČKÝ KŮŇ ÚPĚL ĎÁBELSKÉ Ó
#U:/p5_Python/karel_uoa2/k2_irobotworld/__init__.py
"""
Balíček k2_irobotworld přidává definici světa robotů jako třídy.

Nové vlastnosti:
- Světy robotů jsou instancemi třídy implementující protokol IRobotWorld
  definovaný v rodičovském balíčku.
- Initor balíčku se chová jako správce světa robotů implementující protokol
  IRobotWorldManager definovaný v rodičovském balíčku.
"""
import dbg; dbg_level=1; dbg.start_pkg(dbg_level, __name__, __doc__)
###########################################################################q
# IMPORTY
###########################################################################q

from typing import overload, Sequence

# Atributy společného rodičovského balíčku všech verzí
from .. import (MAX_MARKERS, DEFAULT_ROWS, DEFAULT_COLS,
                Color,  Dir4,
                IKarel, IKarelCM,
                IRobotWorld, IRobotWorldManager,
                RobotError)



###########################################################################q
# EXPORT
###########################################################################q

__all__ = ['new_world', 'show_world', 'Karel',
          ]



###########################################################################q
# GLOBÁLNÍ KONSTANTY
###########################################################################q

MAX_MARKERS  = 9    # Maximální povolený počet značek na jednom políčku
DEFAULT_ROWS = 8    # Implicitní počet řádků
DEFAULT_COLS = 8    # Implicitní počet sloupců

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



###########################################################################q
# GLOBÁLNÍ PROMĚNNÉ
###########################################################################q

# Odkaz na aktuální (a jediný funkční) svět robotů
_active_world:RobotWorld = None

# Odkaz na aktuální třídu světů robotů
_world_class: type = None



###########################################################################q
# TŘÍDA ROBOTA KARLA
###########################################################################q

class Karel(IKarelCM):
    """Třída robotů pohybujících se ve světě podle instrukcí.
    """
    count = 0   # Počitadlo vytvořených instancí

    def __init__(self, row=-1, col=0, dir4:Dir4=Dir4.DEFAULT,
                 color:Color=Color.DEFAULT):
        """Vytvoří robota se zadanými charakteristikami.
        """
        Karel.count += 1
        self.ID      = Karel.count
        if not _active_world:
            raise RobotError(self, f'Robota č. {self.ID} není kam zařadit - '
                                   f'žádný svět není aktivní')
        world = _active_world._world
        rows = len(world)
        cols = len(world[0])

        if row < 0:   row = rows + row
        if col < 0:   col = cols + col

        self._row   = row
        self._col   = col
        self._dir4  = dir4
        self._color = color
        self._world = _active_world
        self._hidden= 0

        _active_world.add_robot(self, row, col, dir4, color)
        show_world()


    def __repr__(self) ->str:
        """Vrátí systémový podpis robota.
        """
        # if self not in _active_world._robots:
        #     raise RobotError(self, f'Robot č. {self.ID} není v aktuálním světě\n'
        #                            f'a nemůže se proto podepsat')
        result = (f'{self.__class__.__name__}_{self.ID}(row={self._row}, '
                  f'col={self._col}, dir4={self._dir4.name}, '
                  f'color={self._color.name}'
               + (f', hidden={self._hidden})' if self._hidden else ')'))
        return result


    def _show(self, world_too:bool=True) -> str:
        """Je-li robot viditelný, zobrazí aktuální stav světa.
        Je-li world_too==False, zobrazí jenom počty značek pod roboty,
        je-li True, zobrazí před nimi i celý svět.
        """
        if not self._hidden:
            if world_too:
                show_world()
            else:
                message = show_hidden_markers()
                if message: print(message)


    def _check_is_active(self) -> None:
        """Ověří, že daný robot je přítomen v aktivním světě.
        """
        if _active_world != self._world:
            raise RobotError(self, 'Svět daného robot již není aktivní')
        if self not in self._world._robots:
            raise RobotError(self,
                            f'Robot č. {self.ID} není součásti aktivního světa')



    #######################################################################q
    # METODY PRO OVLÁDÁNÍ ROBOTA

    def pick(self) -> IKarel:
        """Robot zvedne značku z políčka, na němž stojí.
        Není li na něm žádná značka, ohlásí chybu.
        Vrátí odkaz na svého robota, aby bylo možno příkazy řetězit.
        """
        _active_world.change_markers_under(self, -1)
        if not self._hidden:
            self._show(0)
        return self


    def put(self) -> IKarel:
        """Položí značku na políčko, na němž robot stojí. Přesáhne-li pak počet
        značek na daném políčku maximální povolený počet, ohlásí chybu.
        Vrátí odkaz na svého robota, aby bylo možno příkazy řetězit.
        """
        _active_world.change_markers_under(self, +1)
        if not self._hidden:
            self._show(0)
        return self


    def step(self) -> None:
        """Přesune robota na sousední pole ve směru, do nějž je natočen.
        Je li na tomto poli zeď nebo jiný robot, ohlásí chybu.
        Vrátí odkaz na svého robota, aby bylo možno příkazy řetězit.
        """
        self._row += self._dir4.dy  # Destination row
        self._col += self._dir4.dx  # Destination column
        _active_world.move_robot_to(self, self._row, self._col, self._dir4)
        if not self._hidden:
            self._show(1)
        return self


    def turn_left(self) -> IKarel:
        """Otočí robota o 90° vlevo.
        Vrátí odkaz na svého robota, aby bylo možno příkazy řetězit.
        """
        self._dir4 = self._dir4.turn_left()
        _active_world.move_robot_to(self, self._row, self._col, self._dir4)
        if not self._hidden:
            self._show(1)
        return self



    #######################################################################q
    # METODY PRO ZJIŠŤOVÁNÍ AKTUÁLNÍHO STAVU

    def is_marker(self)  ->  bool:
        """Je li pod robotem značka, vrátí True, jinak vrátí False.
        """
        self._check_is_active()
        return _active_world._world[self._row][self._col] > 0


    def is_east(self)    ->  bool:
        """Je li robot otočen na východ, vrátí True, jinak vrátí False.
        """
        self._check_is_active()
        return self._dir4 == Dir4.EAST


    def is_wall(self)  ->  bool:
        """Je li na políčku před robotem zeď, takže robot nemůže udělat krok,
        vrátí True. Jinak vrátí False. Zdí je obehnán i celý dvorek.
        """
        self._check_is_active()
        wrow   = self._row + self._dir4.dy  # Wall row
        wcol   = self._col + self._dir4.dx  # Wall column
        world  = _active_world
        result = (wrow<0  or  wrow>=world._rows
              or  wcol<0  or  wcol>=world._cols
              or  world._world[wrow][wcol] < 0)
        return result


    def robot_ahead(self)  ->  None:
        """Vrátí odkaz na robota na políčku před sebou.
        Není-li tam žádný robot, vrátí None.
        """
        self._check_is_active()
        rrow   = self._row + self._dir4.dy  # Robot row
        rcol   = self._col + self._dir4.dx  # Robot column
        for robot in _active_world._robots:
            if (rrow == robot._row)  and   (rcol == robot._col):
                return robot
        return None



    #######################################################################q
    # METODY PRO ZAPÍNÁNÍ A VYPÍNÁNÍ SKRYTÉHO PROVÁDĚNÍ AKCI

    def hide(self) -> True:
        """Přestane robota zobrazovat, čímž jeho činnost výrazně zrychlí,
        a vrátí hodnotu True, aby jej bylo možno použít jako podmínku
        v podmíněném příkazu iniciujícím odsazení.
        """
        self._check_is_active()
        if self._hidden == 0:
            self.drow = self._row
            self.dcol = self._col
            self.ddir = self._dir4
        self._hidden += 1
        return True


    def unhide(self) -> int:
        """Vrátí úroveň zobrazování do stavy před posledním skrytím.
        Byl-li proto již tehdy skrytý (a tím pádem i zrychlený),
        zůstane skrytý (a zrychlený) i po tomto částečném odkrytí.
        Byl-li tehdy zobrazovaný a je-li `self._hidden==0`,
        začne se opět zobrazovat a začne zobrazením aktuálního stavu.
        Vrátí aktuální hloubku potlačování zobrazení.
        """
        self._check_is_active()
        self._hidden -= 1
        if self._hidden < 0:
            raise RobotError(self, f'Robot byl vícekrát odkryt než zakryt')
        if self._hidden == 0:
            show_world()        return self._hidden



###########################################################################q
# SVĚT ROBOTŮ A FUNKCE PRO JEHO VYTVOŘENÍ
###########################################################################q

class RobotWorld(IRobotWorld):
    """Instance třídy reprezentují svět robotů."""

    count = 0

    def __init__(self, world:[[int]]):
        """Inicializuje instanci šachovnicového světa robotů.
        """
        RobotWorld.count += 1
        self.ID      = RobotWorld.count
        self._world  = world
        self._rows   = len(world)
        self._cols   = len(world[0])
        self._robots = []  # Na počátku je svět bez robotů


    def __repr__(self):
        return (f'{self.__class__.__name__}_{self.ID}('
                f'rows={self._rows}, cols={self._cols}), '
                f'robots={len(self._robots)}')


    def _check_is_active(self):
        if _active_world == self: return
        raise RobotError(self, 'Zadaný svět již není aktivní')


    def add_robot(self, robot:IKarel, row:int, col:int, dir4:Dir4,
                  color:Color) -> IKarel:
        """Přidá na dvorek robota se zadanými vlastnostmi."""
        self._check_is_active()
        if robot in self._robots:
            raise RobotError(robot, f'Zadaný robot je již přítomen')
        self.check_position(robot, row, col)
        self._robots.append(robot)


    def remove_robot(self, robot:IKarel) -> None:
        """Odebere robota zadaného v argumentu `robot` z aktuálního světa
        robotů. Pokud se v aktuálním světě zadaný robot nevyskytuje,
        vyvolá výjimku.
        """
        if not robot in self._robots:
            raise RobotError(robot, f'Zadaný robot není přítomen')
        self._robots.remove(robot)


    def check_position(self, robot, row, col):
        """Ověří, zda je možné umístit zadaného robota požadovanou pozici."""
        self._check_is_active()
        if (row < 0) or (row >= self._rows) or (col < 0) or (col >= self._cols):
            raise RobotError(robot,
                  f'Robot je umísťován mimo dvorek na [{row},{col}]')
        if (self._world[row][col] < 0):
            raise RobotError(robot, f'Robota nelze umístit na pozici '
                                    f'[{row},{col}] - je na ní zeď')
        for r in self._robots:
            if r is robot:  continue
            if (row, col) == (r._row, r._col):
                raise RobotError(robot, f'Robota nelze umístit na pozici'
                                 f'[{row}{col}] - stojí nan ní robot:\n{r}')


    def move_robot_to(self, robot:IKarel, row:int, col:int, dir4:Dir4):
        """Nastaví zadanému robotu zadanou pozici."""
        self._check_is_active()
        if not robot in self._robots:
            raise RobotError(robot, f'Zadaný robot není ve světě přítomen')
        self.check_position(robot, row, col)
        robot._row, robot._col, robot._dir4 = row, col, dir4


    def change_markers_under(self, robot:IKarel, change:int):
        """Změní počet značek pod zadaným robotem o zadaný počet.
        Přitom zkontroluje, zda je výsledný počet akceptovatelný."""
        self._check_is_active()
        if not robot in self._robots:
            raise RobotError(robot, f'Zadaný robot není ve světě přítomen')
        self._world[robot._row][robot._col] += change



###########################################################################q
# FUNKCE SPRÁVCE SVĚTA ROBOTŮ
###########################################################################q

def new_world(*fields:[int | str]) -> IRobotWorld:
    """Případnou existující aktivní instanci dvorku nejprve deaktivuje.
    Poté vytvoří nový šachovnicový dvorek.
    Jsou-li zadány dva celočíselné argumenty, je vytvořen prázdný dvorek
    se zadaným počtem řádků (první argument) a sloupců (druhý argument).
    Jsou-li zadány stringy, teré musejí být všechny stejně dlouhé,
    reprezentují jejich znaky jednotlivá políčka.
    Číslo na políčku udává počet značek, znak # označuje zeď.
    Není-li zadán žádný argument, chová se jako po zavolání new_world(10,10).
    """
    global _active_world
    _active_world = None
    world = []
    if not fields:  fields = (10, 10)
    if isinstance(fields[0], int):          # Prázdný svět dané velikosti
        row = fields[1] * [0]
        world = [row[:] for _ in range(fields[0])]
    elif isinstance(fields[0], str):        # Svět zadaný stringy
        world = [[int(chr) if '0'<=chr<='9' else
                        (0 if chr == ' '    else -1)  for chr in row]
                                                      for row in fields]
    _active_world = RobotWorld(world)
    return _active_world


def active_world() -> IRobotWorld:
    """Vrací odkaz na aktuální aktivní svět; není-li takový, vrátí None.
    """
    return _active_world


def set_world_class(self, RobotClass:type) -> None:
    """Nastaví třídu, její instance bude vytvářet new_world()."""
    global _world_class
    _world_class = RobotClass


def get_world_class(self) -> type:
    """Vrátí aktuální třídu vytvářených světů."""
    return _world_class



###########################################################################q
# Funkce pro zobrazení světa
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
    if not _active_world:
        raise RobotError(None, 'Žádný svět není aktivní')
    world    = _active_world._world
    rows     = len(world)
    cols     = len(world[0])
    col_nums = lambda:("  "
             + "".join([f'{i:>2}' for i in range(cols)]) + '\n')
    # Funkce pro budování rámečku kolem jednotlivých polí
    # (potřebují zjišťovat počet sloupců až v okamžiku použití)
    top = lambda : '  ' + '╔' + (cols-1)*('═╤') + '═╗\n'
    ins = lambda : '  ' + '╟' + (cols-1)*('─┼') + '─╢\n'
    bot = lambda : '  ' + '╚' + (cols-1)*('═╧') + '═╝\n'

    # Příprava obrazu dvorku bez robotů
    yard = [col_nums(), top()]  # Čísla sloupců + horní hranice
    for ir in range(rows):      # Přidáváme střed s obsahem polí
        rr = []                 # Seznam počtů značek na polích
        for x in world[ir]:                 # Obsah řádku
            rr.append(cWALL if x < 0        # Na poli je zeď
                else str(x) if x else ' ')  # 0 značek = mezera
        yard.append(f'{ir:>2}║'     # Číslo řádku + levý okra
                  +  '│'.join(rr)   # Počty značek na jednotlivých polích
                  + f'║{ir:<2}\n')  # Pravý okraj + číslo řádku
        yard.append(ins())                      # Oddělovací řádek
    yard[-1] = bot()    # Nahradí spodní oddělovač spodní hranicí
    yard.append(col_nums())         # Přidá spodní číslování

    # Na polích s roboty nahradí počet značek zobrazením robota
    robots = _active_world._robots
    for r in robots:
        rrow, rcol, rdir = ((r.drow, r.dcol, r.ddir) if r._hidden
                       else (r._row, r._col, r._dir4))
        row = yard[index := 2*rrow+2]      # String řádku s robotem
        dbg.prDB(1, '')
        yard[index] = (row[:2*rcol+3]      # Počátek řádku
                       + color2char[r._color][rdir.value[0]//2]  # Znak robota
                       + row[2*rcol+4:])   # Zbytek řádku
    print(*yard, sep="", end="")
    result = show_hidden_markers()
    if result:  print(result)


def show_hidden_markers() -> str:
    """|Podívá se, kolik značek je pod jednotlivými roboty
    a vypíše jejich počty.
    """
    aw  = _active_world
    aww = _active_world._world
    result = []
    for r in aw._robots:
        result.append(f"Značek na poli [{r._row},{r._col}] = "
                                  f"{aww[r._row] [r._col]}")
    result = '\n'.join(result)
    return result



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
        from karel_uoa import IKarel, IRobotWorld, IRobotWorldManager
        import sys
        this_module = sys.modules[__name__]
        print('\nPrověrka API základních objektů')
        print(f'{this_module.__name__ = }')
        print(f'{isinstance(this_module, IRobotWorldManager) = }')
        print(f'{issubclass(RobotWorld,  IRobotWorld)        = }')
        print(f'{issubclass(Karel,       IKarel)             = }')

    def check_functionality() -> None:
        # Prověří základní funkcionalitu modulu.
        global k, r
        new_world(3, 8);    k=Karel()
        e("k.step()");        e("print(k.is_east())")
        e("k.turn_left()");   e("print(k.is_east())")
        e("print(k.is_marker())")
        e("k.put()");   e("k.put()");   e("k.put()")
        e("print(k.is_marker())")
        e("k.pick()");  e("k.step()");  e("print(k.is_wall())")
        e("k.step()");                  e("print(k.is_wall())")
        new_world("01234", "5678#");
        k=Karel(0, -1, Dir4.WEST)
        r=Karel(1, 1,Dir4.NORTH, color=Color.MAGENTA)
        show_world()
        e('k.hide()')
        print(k)
        e('k.step().step()')
        e('r.step()')
        e('k.unhide()')
        e('print(k.robot_ahead())')
        e('print(r.robot_ahead())')
        e('r.hide();print(r.turn_left().turn_left().turn_left().unhide())')
        e('print(r.robot_ahead())')

    def test():
        VERSION = 'k1_interface'
        print(f'{2*('\n' + 60*'#')}\nPrověrka verze {VERSION}.\n')
        check_api()
        check_functionality()
        input(f"{('\n' + 60*'#')}\nKonec prověrky verze {VERSION}.\n"
              f"Zkontroluj ji a potvrď stiskem Enter")



###########################################################################q
dbg.stop_pkg(dbg_level, __name__)
