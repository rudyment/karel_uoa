#Příliš žluťoučký kůň úpěl ďábelské ó - PŘÍLIŠ ŽLUŤOUČKÝ KŮŇ ÚPĚL ĎÁBELSKÉ Ó
#U:/p5_Python/dbg.py - # verze 1.18.1990_2025-08-15
"""
Pomocný modul pro nastavování hladiny kontrolních tisků,
kontrolní tisky a případné další služby spojené s laděním.¤
Protože jsou funkce spojené s laděním, nemají dlouhé
samovysvětlující názvy, ale byla dána přednost krátkým
zkratkovým názvům, přičemž v dokumentačních komentářích
funkcí je podoba názvu vždy vysvětlena.

Definované proměnné:
    DBG     - Nastavení hladiny kontrolních tisků - tiskne se pouze tehdy,
              je-li DBG >= zadaná hladina kontrolních tisků
    TST     - Indikace testovacího režimu
    PKG_DOC - Zda se bude u balíčků tisknout celý dokumentační komentář
              Uplatní se pouze u tisků na samostatný řádek
    CWD     - Zda se bude za zmínkou o importu tohoto modulu
              tisknout i current working directory
    INPUTS  - N-tice stringů s uloženými očekávanými vstupy z klávesnice
              pro ladění komunikace programu s uživatelem prostřednictvím
              funkce input()
    input_index - Index vstupu, který má být následně použit
    dbg_level   - Hladiny DBG, od níž se začnou tisknout úvodní a závěrečné
                  tisky i pro tento modul
    print_cwd   - Zda má být součástí úvodních tisků i informace
                  o aktuální pracovní složce
"""
###########################################################################q
# Nastavitelné konstanty modulu

VERSION= '1.18.1991_2025-08-15'    # Verze tohoto modulu
DBG    =  1 # Nastavení hladiny kontrolních tisků
TST    =  0 # Indikace testovacího režimu True/False pro funkci input
WRAP   = 80 # Implicitní povolená délka řádků pro funkce prIN() a prInfLim()
PKG_DOC=  1 # Zda se bude u balíčků tisknout celý dokumentační komentář
            # Uplatní se pouze u tisků na samostatný řádek

PKG_BEGIN = 'VVV_'  # První čtyři znaky zprávy o začátku načítání balíčku
PKG_END   = '^^^_'  # První čtyři znaky zprávy o konci načítání balíčku
MOD_BEGIN = '+++_'  # První čtyři znaky zprávy o začátku načítání modulu
MOD_END   = '===_'  # První čtyři znaky zprávy o konci načítání modulu
END_CHAR  = '¤'     # Znak označující konec tištěné části textu zadaného
                    # v argumentu `doc` funkce `start_pkg()`

START = ' ===== START ' # Příznak hlášky o zahájení inicializace
STOP  = ' ===== STOP '  # Příznak hlášky o ukončení inicializace

# Proměnná INPUTS slouží k uložení očekávaných vstupů z klávesnice
# Zadávané vstupy vloží testovaný program jako n-tici stringů
INPUTS:(str,...) = ()
input_index = 0

# Nastavení hladiny pro tisk kontrolních tisků tohoto modulu
dbg_level = 2   # Hladina DBG, při jejímž dosažení či překročení se tiskne
                # zpráva o vlastním zavedení
print_cwd = 1   # Zda se bude za zmínkou o zavádění tohoto modulu
                # tisknout i current working directory

# from dbg import *
if DBG >= dbg_level:
    print(f'===== Modul {__name__} ===== START - version {VERSION}')
    if print_cwd: import os; print(f'      {os.getcwd()}')



###########################################################################q

from collections.abc import Callable
from types           import FunctionType

__all__ = ['VERSION', 'DBG', 'TST', 'WRAP', 'PKG_DOC', 'now', 'reset',
           'INPUTS', 'input', 'END', 'refer_inputs', 'confirm',
           'prSEd', 'prSEdw', 'prSEda', 'prSEdaw', 'prSEdar', 'prSEdarw',
           'prSEdr', 'prSEdrw', 'prIN', 'prDB',
           'prItLn', 'prIndLim', 'prDict', 'prSeq',
           'prMatI', 'prMatO', 'prVT',
           'start_pkg', 'stop_pkg', 'start_mod', 'stop_mod',
          ]



###########################################################################q
# Funkce řešící emulovaný vstup uživatele z klávesnice

def input(prompt: str) -> str:
    """
    Náhražka zabudované funkce input() umožňující
    testování konverzace s uživatelem prostřednictvím konzole.
    :param prompt:  Vytištěná výzva
    :return:        Zadaný text
    """
    if TST:
        global input_index, INPUTS
        prDB(2, f'===== dbg: Požadován vstup z klávesnice:\n'
                f'   {input_index = }\n'
                f'   {INPUTS = }')
        print(prompt, end='')
        if input_index >= len(INPUTS):
            msg = ('Bylo zadáno málo vstupních textů - požadován text '
                  f's indexem {input_index}\n{INPUTS = }')
            raise Exception(msg)
        result = INPUTS[input_index]
        print(result)
        input_index += 1
        return result
    else:
        prDB(2, 'Spuštěn dbg.input()')
        import builtins
        return builtins.input(prompt)


def END(name: str) -> None:
    """
    Funkce volaná na závěr aplikací komunikujících s uživatelem.
    prostřednictvím klávesnice.
    :param name: Název volajícího modulu
    """
    import builtins
    return builtins.input(f'===== KONEC APLIKACE V MODULU {name} =====')


def refer_inputs() -> None:
    """
    Vytiskne načtené vstupy a aktuální index.
    """
    print(f'Aktuální stav emulátoru klávesnice: {input_index = }\n'
           f'        {INPUTS = }')


def confirm(msg:str) -> None:
    """
    Vypíše zadanou zprávu a požádá o potvrzení pokračování.
    """
    answer = input(f'{msg} - Pokračovat?')
    if answer != '':
        raise Exception('Zažádáno o ukončení')


def now() -> str:
    """
    Vrátí string s aktuálním datem vhodný pro vložení do čísla verze.
    """
    from datetime import datetime as dt
    t = dt.now()
    result = f'{t.year}-{t.month:02}-{t.day:02}_{t.hour:02}-{t.minute:02}'
    return result



###########################################################################q
# Pomocné, neveřejné funkce

def first_max(max_chars:int=70, text:str='') -> str:
    """
    Vrátí první řádek zadaného textu, ale nejvýše max znaků.
    Je-li první řádek prázdný, pracuje s druhým řádkem.
    :param max_chars: Maximální povolený počet vrácených znaků
    :param text: Text, jehož první řádek požadujeme
    :return:     Požadovaný první řádek
    """
    line_end = text.find('\n')
    if (line_end == 0) and (len(text)>1): #První řádek je prázdný
        text     = text[1:]     # Začneme od druhého
        line_end = text.find('\n')
    chars = min(max_chars, line_end if line_end>0 else len(text))
    return text[:chars]


def nsan(lst:list[str]) -> list[str]:
    """
    Očekává seznam názvů atributů a vrátí seznam těch,
    které nezačínají a nekončí dvojicí podtržítek.
    Název je zkratkou z Not System Attribute Names
    """
    l = [s for s in lst if len(s)<=4
                        or (s[:2]  != '__'  and  s[-2:] != '__')]
    return l


def prArgs(*args, **vargs):
    """
    Vrátí string se seznamem hodnot argumentů dané funkce
    standardně uzavřeným v kulatých závorkách.
    Používá se v dekorátorech.
    """
    pos = ', '.join([str(v) for v in args])
    nam = ', '.join([f'{k}={v}' for k, v in vargs.items()])
    msg =('(' + pos + (', ' if (len(pos) + len(nam) > 0)
                            else '')
              + nam + ')')
    return msg



###########################################################################q
# Exportované funkce

def prSE(level:int, se:bool, caller:str, msg:str= '') -> str:
    """
    Vytiskne oznámení o startu, resp. konci provádění funkce,
    která ji zavolala.
    Mnemonika: print at Start and End
    :param level:   Hodnota DBG, od níž se bude tisknout
    :param se:  Příznak tisku startu (True) či ukončení (False) těla metody
    :param caller:  Identifikace volajícího - většinou metody či funkce
    :param msg:     Případná zpráva za vlastním oznámením
    :return:        Doporučený odsazovací string pro následující tisky
    """
    if DBG < level:   return prSE.indent    # ==========>
    if not se:
        prSE.level -= 1  # Trasovaná metoda končí, zmenšuji odsazení
        prSE.indent = prSE.level * prSE.inc
    msg = str(msg)  # Kdyby nebyl zadán string, ale jen objekt
    print(_prIndLim(
        text   = f'{prSE.start if se else prSE.end}',
        data   = f'{caller}{ " - " + msg if len(msg)>0 else ""}',
        prefix = "", shift=0))
    if se:
        prSE.level += 1  # Zvětšuji odsazení pro nižší hladinu
        prSE.indent = prSE.level * prSE.inc
    return prSE.indent
    # Interní počitadla a další proměnné jsou na konci zdrojáku


def prSEd(level:int=1, msg:str= '', *, print_args=False, print_res=False,
          at_start: Callable[[        list, dict], str]=None,
          at_end:   Callable[[object, list, dict], str]=None,
          wait=False) -> FunctionType:
    """
    Dekorátor, který ohlásí zavolání a ukončení dekorované funkce.
    Je-li neprázdný argument `msg`, vytiskne se za úvodním ohlášením.
    Při `print_args=True' v ohlášce zavolání funkce vytiskne argumenty,
    při `print_res=True` v ohlášce ukončení funkce vytiskne výsledek.
    :param level:     Hladina kontrolních tisků, od níž se začne uplatňovat
    :param print_args:Budou se tisknout argumenty
    :param print_res: Bude se tisknout návratová hodnota
    :param msg:       Je-li neprázdný, vytiskne se za úvodním ohlášením.
    :param at_start:  Funkce přebírající argumenty volané dekorované funkce
                      a vracející string, jenž se vytiskne za řádek o startu
    :param at_end:    Funkce přebírající návratovou hodnotu a argumenty volané
                      dekorované funkce a vracející string, jenž se vytiskne
                      před řádek o ukončení volané funkce
    :param wait:      Po ukončení volané funkce se bude čekat
                      na reakci uživatele zadávanou z klávesnice
    :return: Funkce, jíž se v argumentu předá dekorovaná funkce,
             a ona vrátí dekorační obálku se zabalenou dekorovanou funkcí
    """

    def decorator(fnc:FunctionType):
        """
        Zprostředkovává předání hodnot argumentů vlastnímu dekorátoru.
        """
        def wrapper(*pargs, **nargs):
            """Vlastní dekorátor obalující dekorovanou funkci."""
            if DBG >= level:
                out = ((f'{msg}' if msg else '')
                    +  (' # ' if (msg and print_args) else '')
                    +  (f'{pargs}, {nargs}' if print_args else '')
                    +  (add if (at_start  and  (add :=
                                at_start(*pargs, **nargs))) else '')
                    )
                prSE(level, 1, fnc.__name__, out)
            #
            result = fnc(*pargs, **nargs)
            #
            if DBG >= level:
                out = ((f'result={result} ¤ ' if print_res else '')
                    +  (add if (at_end  and  (add :=
                                at_end(result, *pargs, **nargs))) else '')
                    )
                prSE(level, 0, fnc.__name__, out)
                if wait:
                    input(f'{60*"%"}\nAž vše zkontroluješ, stiskni Enter')
            return result   # Vrací návratovou hodnotu dekorované funkce

        wrapper.__name__ = '«D»' + fnc.__name__
        return wrapper

    return decorator


def prSEdw(level:int=1, msg:str='', *,
           at_start: Callable[[        list, dict], str]=None,
           at_end:   Callable[[object, list, dict], str]=None) -> 'function':
    """
    Dekorátor, který ohlásí zavolání a ukončení dekorované funkce,
    přičemž na závěr počká na reakci uživatele zadávanou z klávesnice.
    :param level:   Hladina kontrolních tisků, od níž se začne uplatňovat
    :param msg:     Je-li neprázdný, vytiskne se za úvodním ohlášením.
    """
    return prSEd(level, msg=msg, wait=True, at_start=at_start, at_end=at_end)


def prSEda(level:int=1, msg:str='', *,
           at_start: Callable[[        list, dict], str]=None,
           at_end:   Callable[[object, list, dict], str]=None) -> 'function':
    """
    Dekorátor, který ohlásí zavolání a ukončení dekorované funkce,
    přičemž v ohlášce zavolání vytiskne argumenty.
    :param level:   Hladina kontrolních tisků, od níž se začne uplatňovat
    :param msg:     Je-li neprázdný, vytiskne se za úvodním ohlášením.
    """
    return prSEd(level, msg=msg, print_args=True, print_res=False,
                 at_start=at_start, at_end=at_end)


def prSEdaw(level:int=1, msg:str='', *,
            at_start: Callable[[        list, dict], str]=None,
            at_end:   Callable[[object, list, dict], str]=None) -> 'function':
    """
    Dekorátor, který ohlásí zavolání a ukončení dekorované funkce,
    přičemž v ohlášce zavolání vytiskne argumenty
    a na závěr počká na reakci uživatele zadávanou z klávesnice.
    :param level:   Hladina kontrolních tisků, od níž se začne uplatňovat
    :param msg:     Je-li neprázdný, vytiskne se za úvodním ohlášením.
    """
    return prSEd(level, msg=msg, print_args=True, wait=True,
                 at_start=at_start, at_end=at_end)


def prSEdar(level:int=1, msg:str='', *,
            at_start: Callable[[        list, dict], str]=None,
            at_end:   Callable[[object, list, dict], str]=None) -> 'function':
    """
    Dekorátor, který ohlásí zavolání a ukončení dekorované funkce,
    přičemž v ohlášce zavolání vytiskne argumenty
    a v ohlášce ukončení výsledek.
    :param level:   Hladina kontrolních tisků, od níž se začne uplatňovat
    :param msg:     Je-li neprázdný, vytiskne se za úvodním ohlášením.
    """
    return prSEd(level, msg=msg, print_args=True, print_res=True,
                 at_start=at_start, at_end=at_end)


def prSEdarw(level:int=1, msg:str='', *,
             at_start: Callable[[        list, dict], str]=None,
             at_end:   Callable[[object, list, dict], str]=None) -> 'function':
    """
    Dekorátor, který ohlásí zavolání a ukončení dekorované funkce,
    přičemž v ohlášce zavolání vytiskne argumenty
    a v ohlášce ukončení výsledek
    a na závěr počká na reakci uživatele zadávanou z klávesnice.
    :param level:   Hladina kontrolních tisků, od níž se začne uplatňovat
    :param msg:     Je-li neprázdný, vytiskne se za úvodním ohlášením.
    """
    return prSEd(level, print_args=True, print_res=True, msg=msg, wait=True,
                 at_start=at_start, at_end=at_end)


def prSEdr(level:int=1, msg:str='', *,
           at_start: Callable[[        list, dict], str]=None,
           at_end:   Callable[[object, list, dict], str]=None) -> 'function':
    """
    Dekorátor, který ohlásí zavolání a ukončení dekorované funkce,
    přičemž v ohlášce ukončení vytiskne výsledek.
    :param level:   Hladina kontrolních tisků, od níž se začne uplatňovat
    :param msg:     Je-li neprázdný, vytiskne se za úvodním ohlášením.
    """
    return prSEd(level, print_args=False, msg=msg, print_res=True,
                 at_start=at_start, at_end=at_end)


def prSEdrw(level:int=1, msg:str='', *,
            at_start: Callable[[        list, dict], str]=None,
            at_end:   Callable[[object, list, dict], str]=None) -> 'function':
    """
    Dekorátor, který ohlásí zavolání a ukončení dekorované funkce,
    přičemž v ohlášce ukončení vytiskne výsledek
    a na závěr počká na reakci uživatele zadávanou z klávesnice.
    :param level:   Hladina kontrolních tisků, od níž se začne uplatňovat
    :param msg:     Je-li neprázdný, vytiskne se za úvodním ohlášením.
    """
    return prSEd(level, print_args=False, print_res=True, msg=msg, wait=True,
                 at_start=at_start, at_end=at_end)


def prDB(level:int, msg:str) -> None:
    """
    Rozdělí zprávu na její řádky a před každý vloží prefix prSE.indent
    nastavený funkcí prSE a funkcemi a dekorátory z ní odvozenými.
    Realizuje pomocné tisky při ladění pouze v případě,
    když je počáteční argument větší nebo roven hodnotě DBG.
    :param level: Hladina kontrolních tisků, od níž se začne uplatňovat
    :param msg:   Zobrazovaná zpráva
    """
    if DBG < level:   return   # ==========>
    if msg == None:
        msg = 'prIN: CHYBA! K TISKU BYL ZADÁN PRÁZDNÝ ODKAZ.'
    lines = msg.splitlines()
    for line in lines:
        print(prSE.indent, line, sep="")


def prD(msg:str) -> None:
    """
    Volá prDB s přednastavenou hladinou 1.
    """
    prDB(1, msg)


def prIN(level:int, msg:str='', *, msg0='', limit=WRAP, q:bool=False) -> None:
    """
    Vytiskne zadanou zprávu za prefix nastavený funkcí prSE.
    Mnemonika: print INside start and end.
    Parametr q řídí, jestli se po vytištění zprávy má zobrazit otázka,
    zda se má v programu pokračovat. (q=question)
    :param level: Hladina kontrolních tisků, od níž se začne uplatňovat
    :param msg:   Zobrazovaná zpráva
    :param msg0:  Text,  který se vytiskne před `msg` a všechny případné
                  pokračovací řádky se o jeho délku odsadí
    :param limit: Povolená délka řádku
    :param q:     Zda se po vytištění zprávy má zobrazit otázka,
                  má-li se v programu pokračovat.
    """
    if DBG < level:   return   # ==========>
    if msg == None:
        msg = 'prIN: CHYBA! K TISKU BYL ZADÁN PRÁZDNÝ ODKAZ.'
    lines = msg.splitlines()
    for line in lines:
        print(_prIndLim(msg0, line, shift=0, limit=limit))
    if q: input('\nPokračovat?')


def prItLn(source:'iterable', msg='', *, prn=True, rpr=False) -> str|None:
    """
    Vytiskne prvky iterovatelného objektu každý na samostatný řádek,
    anebo vrátí příslušný string.
    Je-li v parametru msg zadána zpráva, vytiskne ji, za ní vytiskne
    první řádek textu a další řádky odsadí o délku zprávy.
    Mnemonika: print Iterable with new lines.
    :param source:  Tištěný iterovatelný objekt
    :param msg:     Případná doprovodná zpráva
    :param prn:     Zda se bude tisknout (`True`) nebo vracet string
    :param rpr:     Zda se bude používat funkce `repr()` nebo `str()`
    :return:        Bude-li se tisknout, nevrací nic,
                    jinak vrací požadovaný string
    """
    if isinstance(source, str):
        source = source.splitlines()
    aux_lst = []
    indent  = msg if msg else ''
    indent2 = len(msg)*' '
    conv    = repr if rpr else str
    if source and (len(source)>0):
        for obj in source:
            aux_lst.append(indent + conv(obj))
            indent = indent2
        result = '\n'.join(aux_lst)
    else:
        result = msg
    if prn :
        print(result)
    else:
        return result


# @prSEda(0)
def prIndLim(text:str, data:object, *, shift=1, limit:int=80,
             end='', prefix='', prSEin=True) -> str:
    """
    Vrátí zadaný text následovaný uživatelským podpisem objektu data,
    který se pokusí zalomit na hranicích slov tak, aby délka řádku
    nepřesáhla zadaný limit, přičemž případné následující řádky podpisu
    odsazuje tak, aby byly zarovnané pod začátkem prvního.
    Mnemonika: print with indent and limit
    :param text:  Úvodní text
    :param data:  Objekt tištěný a zalamovaný za úvodním textem
    :param shift: O kolik budou následující řádky ještě odsazeny,
                  aby se text posunul např. za otevírací závorku kontejneru
    :param limit: Povolená délka řádku
    :param end:   String přidaný na závěr vygenerovaného textu
    :param prefix:Úvodní string všech řádků
    :param prSEin:Zda bude respektovat odsazení uložené v atributu
                  `prSE.indent` a zvětší o něj povolenou délku řádků
    :return:      Požadovaný string
    """
    # print(f'{30*'V'}\n%{data = }') #!#
    result = _prIndLim(text, data, shift=shift, limit=limit,
                       end=end, prefix=prefix, prSEin=prSEin)
    # print(f'{30*'A'}') #!#
    return result


def _prIndLim(text:str, data:object, *,
             shift=1, limit:int=WRAP, end='', prefix='', prSEin=True) -> str:
    """Soukromá verze, aby vylo možno funkci prIndLim dekorovat
    a zjistit tak hodnoty argumentů.
    V rámci dbg se proto používá tato soukromá verze."""
    # print(f'{60*'v'}\n_prIndLim_0: {text = }, {data = }\n'
    #       f'             {shift = }, {limit = }, {end = }, {prefix = }')

    def rest(words:list[str], start:int, length:int) -> int:
        """
        Vezme ze seznamu words postupně další prvky počínaje prvkem
        s indexem start a skládá a přidává je do seznamu lst vnější funkce.
        Zastaví s okamžiku, kdy by po přidání dalšího textu přidal více
        než length znaků. Vrátí index prvního nepřidaného prvku,
        tj. index, od nějž by se mělo příště začít.
        :param words:   seznam tištěných slov
        :param start:   index, od nějž začínáme
        :param length:  délka vytvářeného textu
        :return:        index prvního nepřidaného prvku
        """
        nonlocal lst
        sum = len(words[start]) # sum = délka prvního slova
        while True:
            lst.append(words[start])    # Přidá se dané slovo
            start += 1                  # Příště vezmeme další
            if start >= len(words):     # Je to mimo rozsah indexů?
                return start            # Vrátím index následníka
            sum += len(words[start]) +1 # Mezera + další slovo
            if sum > length:            # Přesahuje text povolenou délku?
                return start            # Ano, tímto slovem příště začneme
            lst.append(' ')             # Ne, přidej do seznamu mezeru
        # -------------------- Konec těla vnořené funkce
        # Výsledkem je seznam textů k tisknutí v proměnné lst

    # prSEind je úvodní odsazovací text v případě, že budeme respektovat
    # Vnořovaná odsazení funkce prSE() a jejích kolegů
    prSEind= prSE.indent if prSEin else ""
    indent = len(text) + shift      # Posun o otevírací závorku kontejneru
    # Počáteční text odsazující levé okraje dalších řádků
    begin  = '\n'  +  prSEind  +  prefix  +  indent * ' '
    lines = str(data).split('\n')
    result = []                        # Seznam výsledných řádků
    for ind, line in enumerate(lines):
        lst   = []    # Seznam tisknutých textů (vnořená se na něj odvolává)
        words = str(line).split()
        # Počet znaků zbývajících do konce řádku
        max   = limit - indent - len(prefix) - len(prSEind)
        # print(f'{limit=}, {indent=}, {len(prefix)=}, {len(prSEind)=}, {max=}')
        index  = 0
        while ...:
            if index >= len(words):    # Seznam je vyčerpán
                break                  # ---------->
            index = rest(words, index, max) # Přidá další řádek
            if index < len(words):     # Budeme ještě přidávat
                lst.append(begin)      # Odřádkujeme a odsadíme
        result.append(prSEind  +  prefix + text + ''.join(lst) + end)
        text = ' '*len(text)
    # print(f'_prIndLim_X:\n{60*'^'}')
    return '\n'.join(result)


def _accept(ident:str, und:int, syst:bool) -> bool:
    """Oznámí, je-li zadaná string akceptovatelný, tj. nemá-li na počátku
    více podtržítek než povoluje `und`, u systémových navíc musí být povoleno
    zobrazování systémových atributů.
    Je-li syst==True, považuje se automaticky (und >= 2)
    """
    start = 0
    for i in range(len(ident)):
        if ident[i] == '_':
            start += 1
        else:
            break
    if syst:
        und = max(2, und)
        suffix = True
    else:
        suffix = (len(ident) <= 4)  or  ('__' != ident[-2:])
    return (start <= und)  and  suffix


def prDict(d=None, *, dict=False, und=0, syst=False, msg='', mod=False,
                      prn=True, indent='', sort=False) -> str | None:
    """
    Vytiskne, resp. vrátí položky zadaného slovníku nebo jmenného prostoru
    zadaného objektu, každou na samostatný řádek.
    :param d:    Objekt, jehož atribut __dict__ se bude tisknout,
                 resp. slovník, který se bude tisknout;
                 není-li zadán, tisknou se atributy modulu __main__
    :param dict: Zda je zadán slovník (True), anebo běžný objekt (False)
    :param und:  Počet znaků podtržení povolených na počátku identifikátorů
    :param syst: Budou-li se tisknout i systémové položky, tj. dundery.
    :param msg:  Případná zpráva uvozující celý tisk
    :param mod:  Je-li zadán, bude se tisknout __dict__ modulu objektu
                 zadaného v d. Ten však musí mít atribut __module__
    :param prn:  Zda se bude vytvářený string tisknout (True) či vracet
    :return:     Podle hodnoty `prn` buďto `None` nebo vytvořený string
    """
    if not d:
        import __main__
        d = __main__
    elif mod:
        from importlib import import_module
        m = import_module(d.__module__)
        d = m
    if (dict):
        dd = d
        t  = 'Obsah slovníku'
    else:
        dd = d.__dict__
        t  = 'Atributy objektu'
        if msg=='':  msg = str(d)
    result = msg if msg else f'##### {t}:\n'
    keys   = dd.keys()
    if sort: keys = sorted(keys)
    for k in keys:
        if ((type(k) != str)  or  _accept(k, und, syst)):
            val = dd[k]
            if isinstance(val, FunctionType):
                val = f"Instance typu {type(val)}"
            result += f"{indent}{k} = {val}\n"
    if prn: print (result, end='')
    else:   return result


def prDirL(d=None, msg='', *, dict=False, sort=False, und=0, syst=False,
                              prn=True, prSEin=True ) -> str | None:
    """
    Vytiskne, resp. vrátí string se seznamem názvů atributů zadaného objektu,
    přičemž názvy jsou zobrazeny bez stringových apostrofů.
    :param d:    Objekt, jehož atributy se budou tisknout;
                 není-li zadán, tisknou se atributy modulu __main__
    :param msg:  Případná zpráva uvozující celý tisk
    :param dict: Zda je zadán slovník (True), anebo běžný objekt (False)
    :param sort: Mají-li se názvy setřídit dle abecedy
    :param und:  Počet znaků podtržení povolených na počátku identifikátorů
    :param syst: Budou-li se tisknout i systémové položky, tj. dundery.
    :param prn:  Zda se bude vytvářený string tisknout (True) či vracet
    :param prSEin:Zda bude respektovat odsazení uložené v atributu
                  `prSE.indent` a zvětší o něj povolenou délku řádků
    :return:     Podle hodnoty `prn` buďto `None` nebo vytvořený string
    """
    # accept = lambda s: (True if syst \
    #                        else (s[:1]  !=  '__'  !=  s[-2:]))
    if not d:   import __main__;   d = __main__
    src = d
    if not dict:
        src = d.__dict__
    lst = [name for name in src if _accept(name, und, syst)]
    if sort:      lst = sorted(lst)
    result = ((prSE.indent if prSEin and prn else "") + msg
             + '[' +  ', '.join(lst) + ']')
    if prn: print (result)
    else:   return result


def prDir(d=None, msg='', *, sort=False, und=0, syst=False, prn=True,
                             prSEin=True ) -> str | None:
    """
    Vytiskne, resp. vrátí string s názvy atributů zadaného objektu,
    každý na samostatný řádek.
    :param d:    Objekt, jehož atributy se budou tisknout;
                 není-li zadán, tisknou se atributy modulu __main__
    :param msg:  Případná zpráva uvozující celý tisk
    :param und:  Počet znaků podtržení povolených na počátku identifikátorů
    :param sort: Mají-li se názvy setřídit dle abecedy
    :param syst: Budou-li se tisknout i systémové položky, tj. dundery.
    :param prn:  Zda se bude vytvářený string tisknout (True) či vracet
    :param prSEin:Zda bude respektovat odsazení uložené v atributu
                  `prSE.indent` a zvětší o něj povolenou délku řádků
    :return:     Podle hodnoty `prn` buďto `None` nebo vytvořený string
    """
    # accept = lambda s: \
    #     (True if syst \
    #                        else (s[:1]  !=  '__'  !=  s[-2:]))
    if not d:   import __main__;   d = __main__
    lst = [name for name in d.__dict__ if _accept(name, und, syst)]
    if sort:  lst.sort()
    if not msg:
        obj = d.__name__ if ('__name__' in dir(d)) else str(d)
        msg = f'Názvy atributů objektu: {obj}'
    result = prSeq(lst, prn=False, prSEin=prSEin, msg=msg)
    if prn:  print (result)
    else:    return result


def prSeq(seq, prn=True, prSEin=True, msg="") -> str | None:
    """
    Vyrobí string s indexovanými položkami zadaného iterovatelného objektu
    na jednotlivých řádcích a buďto jej vytiskne nebo vrátí.
    :param seq: Tištěný iterovatelný objekt
    :param prn: Bude-li se tisknout (True), anebo vracet vytvořený string
    :param prSEin:Zda bude respektovat odsazení uložené v atributu
                  `prSE.indent` a zvětší o něj povolenou délku řádků
    :param msg: Úvodní zpráva uvozující objednaný výpis
    :return:    Podle hodnoty `prn` buďto `None` nebo vytvořený string
    """
    prSEind = prSE.indent if prSEin else ""
    result = (f'{prSEind}{msg}\n' if msg else "")  +  prSEind
    if seq: result += f'\n{prSEind}'.join(
                          [f'{i}: {item}' for i, item in enumerate(seq)])
    else:   result += (None if seq==None else '<Empty>')
    if prn: print (result)
    else:   return result


def prMatI(msg:str, mat:[[int]], pos:int=3, nl:bool=False) -> None:
    """
    Vytiskne zadaný titulek následovaný položkami zadané celočíselné
    matice, přičemž pro tisk čísla vyhradí zadaný počet pozic.
    Argument `nl` definuje, zda se má za nadpisem odřádkovat.
    Odřádkuje-li se, budou se všechny následující řádky odsazovat o 3 mezery.
    :param msg: Titulek
    :param mat: Tištěná celočíselná matice
    :param pos: Počet pozic pro jednotlivé položky
    :param nl:  Zda se má za nadpisem odřádkovat
    :return:
    """
    indent = ""
    if msg:
        print(msg, ': ', sep='', end='')
        if nl:
            print()
            indent = "   "
        else:
            indent = (len(msg) + 2)*' '
    first = 1
    for row in mat:
        if first: first = False;  print(indent if nl else '', end='')
        else:     print(indent, end='')
        print([f'{i:{pos}}' for i in row], sep=', ')


def prMatO(msg:str, mat:[[object]]) -> None:
    """
    Vytiskne zadaný titulek následovaný na dalších řádcích položkami
    zadané matice objektů, přičemž každý objekt bude vytištěn na samostatném
    řádku, na jehož počátku bude uveden index objektu v matici.
    Matice je tištěna po řádcích a před tiskem dalšího řádku je vždy
    na samostatném řádku vytištěna informace o indexu daného řádku.
    :param msg: Titulek
    :param mat: Tištěná matice objektů
    :return:    `None`
    """
    print(msg)
    for r, row in enumerate(mat):
        print(f'Řádek {r=}:')
        for c, obj in enumerate(row):
            print(f'   [{r},{c}]:  {obj}')


def prVT(expression: str) -> None:
    """
    Očekává v argumentu string reprezentující výraz;
    vytiskne tento výraz, jeho hodnoty a jeho typ.
    Mnemonika: Print Value and Type.
    :param expression: Analyzovaný výraz zadaný jako string
    """
    value = eval(expression)
    print(f'{expression} = {value} # type = {type(value)}')


def str_(lst:list[str]) -> list[str]:
    """
    Očekává seznam názvů atributů a vrátí seznam těch,
    které nezačínají a nekončí dvojicí podtržítek.
    """
    l = [s for s in lst if len(s)<=4
                        or (s[:2]  != '__'  and  s[-2:] != '__')]
    return l


# NL = '\n' + 6*' '                                                 #!#
# AT_START = lambda      *arg, **warg: f'name={arg[1]}'             #!#
# AT_STOP  = lambda ret, *arg, **warg: f'name={arg[1]}'             #!#
# @prSEd(2, at_start=AT_START, at_end=AT_STOP)                      #!#
def start_pkg(level: int, name: str, doc: str = '',
              new_line=True, end_char=END_CHAR) -> None:
    """
    Vytiskne informaci o zavádění balíčku spolu s textem zadaným
    v argumentu doc (tam se většinou zadává __doc__), přičemž je možno
    označit, kam až se zadaný text bude tisknout.
    :param level: Hladina kontrolních tisků, od níž se začne uplatňovat
    :param name:  Název zaváděného balíčku
    :param doc:   Tisknutý text, typicky dokumentační komentář
    :param new_line: Bude-li se text tisknout na samostatném řádku (True)
                     nebo hned za názvem balíčku (False)
    :param end_char: Znak označující konec tištěné části zadaného textu
                     Implicitní hodnotou je znak ¤.
    """
    def indented_lines(start:str, txt:str, end_char='¤') -> str:
        """
        Vrátí text zadaný v parametru `txt`, přičemž každý řádek bude začínat
        separátorem zadaným v parametru `start`.
        """
        index = txt.find(end_char)
        if index > 0: txt = txt[:index]
        lines = txt.splitlines()
        if lines[0].strip() == '': lines.pop(0)
        result = ''.join(start + line for line in lines)
        return result

    # prDB(+2, f'== A: {name=}{NL}{prSE.indent=}{NL}{prSE.level=}') #!#
    my_indent = "" # = prSE.indent if INDENT_PKG else ""            #!#
    # prDB(+2, f'== 1: {name=}, {my_indent=}')                      #!#
    if doc == "":
        start = START
        msg   = ""
    else:
        if new_line:
            start = START
            sep   = f'\n{my_indent}      '
            if PKG_DOC:
                msg = indented_lines(sep, doc, end_char)
            else:
                msg = f' - {first_max(72, doc)}'
            chars = 72
        else:
            start = ""
            msg = f' - {first_max(61 - len(name), doc)}'
    start_pkg.level = chr(ord(start_pkg.level)+1)
    # prDB(+2, f'== X: {name=}{NL}{my_indent=}{NL}{PKG_BEGIN=}{NL}'
    #          f'{start_pkg.level=}') #!#
    prDB(level, f'{PKG_BEGIN}{start_pkg.level} '
                f'Balíček {name}{start}{msg}')
    prSE.indent += prSE.inc
    prSE.level  += 1
    # prDB(+2, f'== Z: {name=}{NL}{prSE.indent=}{NL}{prSE.level=}') #!#
    # Interní počitadla jsou na konci zdrojáku


# @prSEd(2, at_start=AT_START, at_end=AT_STOP)                      #!#
def stop_pkg(level: int, name: str, txt:str='') -> None:
    """
    Funkce vytiskne informaci o ukončení zavádění initoru balíčku.
    """
    # prDB(+2, f'PKG_A: {name=}{NL}{prSE.indent=}{NL}{prSE.level=}') #!#
    prSE.level -= 1
    prSE.indent = prSE.level*prSE.inc
    prDB(level, f'{PKG_END}{start_pkg.level} '
                f'Balíček {name}{STOP}{txt}')
    start_pkg.level = chr(ord(start_pkg.level)-1)
    # Interní počitadla jsou na konci zdrojáku
    # prDB(+0, f'PKG_Z: {name=}{NL}{prSE.indent=}{NL}{prSE.level=}') #!#


# @prSEd(2, at_start=AT_START, at_end=AT_STOP)                      #!#
def start_mod(level:int, name:str, txt:str='') -> None:
    """
    Funkce vytiskne informaci o počátku zavádění modulu.
    """
    # prDB(+2, f'== A: {name=}{NL}{prSE.indent=}{NL}{prSE.level=}') #!#
    prSEindent = "" # = prSE.indent if INDENT_PKG else ""           #!#
    prDB(level, f'{prSEindent}{MOD_BEGIN}{start_mod.level} '
                f'Modul {name}{START}')
    start_mod.level += 1
    prSE.indent     += prSE.inc
    prSE.level      += 1
    if txt: prDB(level, txt)
    # prDB(+2, f'== Z: {name=}{NL}{prSE.indent=}{NL}{prSE.level=}') #!#
    # Interní počitadla jsou na konci zdrojáku


# @prSEd(2, at_start=AT_START, at_end=AT_STOP)                      #!#
def stop_mod(level:int, name:str, txt:str='') -> None:
    """
    Funkce vytiskne informaci o ukončení zavádění modulu.
    """
    # prDB(+2, f'== A: {name=}{NL}{prSE.indent=}{NL}{prSE.level=}') #!#
    if txt: prDB(level, txt)
    prSE.level -= 1
    prSE.indent = prSE.level*prSE.inc
    start_mod.level -= 1
    prDB(level, f'{MOD_END}{start_mod.level} '
                f'Modul {name}{STOP}{txt}')
    # Interní počitadla jsou na konci zdrojáku
    # prDB(+2, f'== Z: {name=}{NL}{prSE.indent=}{NL}{prSE.level=}') #!#



###########################################################################q
# Interní počitadla

# Definice atributů předchozí funkce
prSE.level = 0      # Hladina vnoření pro nastavení odsazení
prSE.indent= ''     # Aktuální text odsazení pro znázornění hladiny volání
prSE.inc   = '|   ' # Přírůstek odsazení pro zvětšení hloubky vnoření
prSE.start = '==> ' # Indikace volání funkce
prSE.end   = '<== ' # Indikace návratu z funkce

start_pkg.level ='@'# Hladina vnoření balíčku
start_mod.level = 0 # Hladina vnoření modulu


def reset():
    """
    Inicializuje interní počitadla modulu.
    """
    prSE.level      = 0
    prSE.indent     = ''
    start_pkg.level = '@'
    start_mod.level = 0



###########################################################################q
prDB(dbg_level, f'===== Modul {__name__} ===== STOP')
