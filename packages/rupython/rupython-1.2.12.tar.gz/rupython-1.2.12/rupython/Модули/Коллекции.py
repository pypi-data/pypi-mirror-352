import collections
import collections.abc
from rupython import __Общие_функции__

_Последовательность = collections.abc.Sequence
_Изменяемая_последовательность = collections.abc.MutableSequence
_Отображение = collections.abc.Mapping
_Изменяемое_отображение = collections.abc.MutableMapping
_Множество = collections.abc.Set
_Изменяемое_множество = collections.abc.MutableSet

Словарь_параметров = {
    'имя': 'name',
    'поля': 'fields',
    'перебираемый': 'iterable',
    'максимальная_длина': 'maxlen',
    'функция_по_умолчанию': 'default_factory',
    'словари': 'maps',
    'ключ': 'key',
    'значение': 'value',
    'по_умолчанию': 'default',
    'количество': 'n'
}

class Именованный_кортеж(_Последовательность):
    def __init__(здесь, имя, поля):
        здесь._namedtuple = collections.namedtuple(имя, поля)

    def __call__(здесь, *ПА, **ИА):
        return здесь._namedtuple(*ПА, **ИА)

    def __getattr__(здесь, имя):
        return getattr(здесь._namedtuple, имя)

    def __getitem__(здесь, индекс):
        return здесь._namedtuple.__getitem__(индекс)

    def __len__(здесь):
        return len(здесь._namedtuple)

    def __iter__(здесь):
        return iter(здесь._namedtuple)

    def __contains__(здесь, элемент):
        return элемент in здесь._namedtuple

    def __reversed__(здесь):
        return reversed(здесь._namedtuple)

    def __str__(здесь):
        return str(здесь._namedtuple)

class Двусторонняя_очередь(_Изменяемая_последовательность):
    def __init__(здесь, перебираемый = None, максимальная_длина = None):
        ИА = {}
        if перебираемый is not None:
            ИА['iterable'] = перебираемый
        if максимальная_длина is not None:
            ИА['maxlen'] = максимальная_длина
        здесь._deque = collections.deque(**ИА)

    def Добавить_в_начало(здесь, элемент):
        здесь._deque.appendleft(элемент)

    def Добавить_в_конец(здесь, элемент):
        здесь._deque.append(элемент)

    def Удалить_с_начала(здесь):
        if not здесь._deque:
            raise IndexError("Очередь пуста")
        return здесь._deque.popleft()

    def Удалить_с_конца(здесь):
        if not здесь._deque:
            raise IndexError("Очередь пуста")
        return здесь._deque.pop()

    def Очистить(здесь):
        здесь._deque.clear()

    def Длина(здесь):
        return len(здесь._deque)

    def Расширить_в_начало(здесь, перебираемый):
        здесь._deque.extendleft(перебираемый)

    def Расширить_в_конец(здесь, перебираемый):
        здесь._deque.extend(перебираемый)

    def Повернуть(здесь, количество):
        здесь._deque.rotate(количество)

    def Перевернуть(здесь):
        здесь._deque.reverse()

    def Количество(здесь, элемент):
        return sum(1 for x in здесь._deque if x == элемент)

    def Индекс(здесь, элемент, начало = 0, конец = None):
        if конец is None:
            конец = len(здесь._deque)
        for i, x in enumerate(здесь._deque):
            if начало <= i < конец and x == элемент:
                return i
        raise ValueError(f"{элемент} не найден в диапазоне")

    def Вставить(здесь, индекс, значение):
        здесь._deque.rotate(-индекс)
        здесь._deque.appendleft(значение)
        здесь._deque.rotate(индекс)

    def __getitem__(здесь, индекс):
        return здесь._deque[индекс]

    def __setitem__(здесь, индекс, значение):
        здесь._deque[индекс] = значение

    def __delitem__(здесь, индекс):
        del здесь._deque[индекс]

    def __len__(здесь):
        return len(здесь._deque)

    def __iter__(здесь):
        return iter(здесь._deque)

    def __contains__(здесь, элемент):
        return элемент in здесь._deque

    def __reversed__(здесь):
        return iter(reversed(здесь._deque))

    def __str__(здесь):
        элементы = ', '.join(str(x) for x in здесь._deque)
        return f"Двусторонняя_очередь([{элементы}])"

class Счётчик(_Отображение):
    def __init__(здесь, перебираемый = None):
        здесь._counter = collections.Counter(перебираемый or [])

    def Обновить(здесь, перебираемый):
        здесь._counter.update(перебираемый)

    def Вычесть(здесь, перебираемый):
        здесь._counter.subtract(перебираемый)

    def Наиболее_частые(здесь, количество = None):
        return здесь._counter.most_common(количество)

    def Элементы(здесь):
        return list(здесь._counter.elements())

    def Получить(здесь, ключ, по_умолчанию = None):
        return здесь._counter.get(ключ, по_умолчанию)

    def __getitem__(здесь, ключ):
        return здесь._counter[ключ]

    def __setitem__(здесь, ключ, значение):
        здесь._counter[ключ] = значение

    def __delitem__(здесь, ключ):
        del здесь._counter[ключ]

    def __iter__(здесь):
        return iter(здесь._counter)

    def __len__(здесь):
        return len(здесь._counter)

    def __contains__(здесь, ключ):
        return ключ in здесь._counter

    def __add__(здесь, другой):
        if isinstance(другой, Счётчик):
            return Счётчик(здесь._counter + другой._counter)
        return NotImplemented

    def __sub__(здесь, другой):
        if isinstance(другой, Счётчик):
            return Счётчик(здесь._counter - другой._counter)
        return NotImplemented

    def __str__(здесь):
        элементы = ', '.join(f"{k}: {v}" for k, v in здесь._counter.items())
        return f"Счётчик({{{элементы}}})"

    def В_строку(здесь):
        if not здесь._counter:
            return "Пустой счётчик"
        элементы = []
        for ключ, количество in здесь._counter.items():
            слово = __Общие_функции__.Склонение_после_числительного(количество, ['элемент', 'элемента', 'элементов'])
            элементы.append(f"{ключ}: {слово}")
        return ', '.join(элементы)

class Упорядоченный_словарь(_Изменяемое_отображение):
    def __init__(здесь, *ПА, **ИА):
        здесь._ordered_dict = collections.OrderedDict(*ПА, **ИА)

    def Вставить(здесь, ключ, значение):
        здесь._ordered_dict[ключ] = значение

    def Удалить(здесь, ключ, по_умолчанию = None):
        return здесь._ordered_dict.pop(ключ, по_умолчанию)

    def Удалить_последний(здесь, последний = True):
        return здесь._ordered_dict.popitem(last = последний)

    def Получить(здесь, ключ, по_умолчанию = None):
        return здесь._ordered_dict.get(ключ, по_умолчанию)

    def Установить_по_умолчанию(здесь, ключ, по_умолчанию = None):
        return здесь._ordered_dict.setdefault(ключ, по_умолчанию)

    def Ключи(здесь):
        return list(здесь._ordered_dict.keys())

    def Значения(здесь):
        return list(здесь._ordered_dict.values())

    def Элементы(здесь):
        return list(здесь._ordered_dict.items())

    def Переместить_в_конец(здесь, ключ, последний = True):
        здесь._ordered_dict.move_to_end(ключ, last = последний)

    def __getitem__(здесь, ключ):
        return здесь._ordered_dict[ключ]

    def __setitem__(здесь, ключ, значение):
        здесь._ordered_dict[ключ] = значение

    def __delitem__(здесь, ключ):
        del здесь._ordered_dict[ключ]

    def __iter__(здесь):
        return iter(здесь._ordered_dict)

    def __len__(здесь):
        return len(здесь._ordered_dict)

    def __contains__(здесь, ключ):
        return ключ in здесь._ordered_dict

    def __str__(здесь):
        элементы = ', '.join(f"{k}: {v}" for k, v in здесь._ordered_dict.items())
        return f"Упорядоченный_словарь({{{элементы}}})"

class Словарь_по_умолчанию(_Изменяемое_отображение):
    def __init__(здесь, функция_по_умолчанию = None, *ПА, **ИА):
        здесь._default_dict = collections.defaultdict(функция_по_умолчанию, *ПА, **ИА)

    def Получить(здесь, ключ, по_умолчанию = None):
        return здесь._default_dict.get(ключ, по_умолчанию)

    def Установить_по_умолчанию(здесь, ключ, по_умолчанию = None):
        return здесь._default_dict.setdefault(ключ, по_умолчанию)

    def Удалить(здесь, ключ, по_умолчанию = None):
        return здесь._default_dict.pop(ключ, по_умолчанию)

    def Удалить_последний(здесь, последний = True):
        return здесь._default_dict.popitem(last = последний)

    def __getitem__(здесь, ключ):
        return здесь._default_dict[ключ]

    def __setitem__(здесь, ключ, значение):
        здесь._default_dict[ключ] = значение

    def __delitem__(здесь, ключ):
        del здесь._default_dict[ключ]

    def __iter__(здесь):
        return iter(здесь._default_dict)

    def __len__(здесь):
        return len(здесь._default_dict)

    def __contains__(здесь, ключ):
        return ключ in здесь._default_dict

    def Ключи(здесь):
        return list(здесь._default_dict.keys())

    def Значения(здесь):
        return list(здесь._default_dict.values())

    def Элементы(здесь):
        return list(здесь._default_dict.items())

    def __str__(здесь):
        элементы = ', '.join(f"{k}: {v}" for k, v in здесь._default_dict.items())
        return f"Словарь_по_умолчанию({{{элементы}}})"

class Слоистый_словарь(_Изменяемое_отображение):
    def __init__(здесь, *словари):
        здесь._chainmap = collections.ChainMap(*словари)

    def Новый_дочерний(здесь, словарь = None):
        return Слоистый_словарь(словарь or {}, *здесь._chainmap.maps)

    def Родители(здесь):
        return Слоистый_словарь(*здесь._chainmap.maps[1:])

    def Получить(здесь, ключ, по_умолчанию = None):
        return здесь._chainmap.get(ключ, по_умолчанию)

    def Установить_по_умолчанию(здесь, ключ, по_умолчанию = None):
        return здесь._chainmap.setdefault(ключ, по_умолчанию)

    def Удалить(здесь, ключ, по_умолчанию = None):
        return здесь._chainmap.pop(ключ, по_умолчанию)

    def __getitem__(здесь, ключ):
        return здесь._chainmap[ключ]

    def __setitem__(здесь, ключ, значение):
        здесь._chainmap[ключ] = значение

    def __delitem__(здесь, ключ):
        del здесь._chainmap[ключ]

    def __iter__(здесь):
        return iter(здесь._chainmap)

    def __len__(здесь):
        return len(здесь._chainmap)

    def __contains__(здесь, ключ):
        return ключ in здесь._chainmap

    def Ключи(здесь):
        return list(здесь._chainmap.keys())

    def Значения(здесь):
        return list(здесь._chainmap.values())

    def Элементы(здесь):
        return list(здесь._chainmap.items())

    def __str__(здесь):
        элементы = ', '.join(f"{k}: {v}" for k, v in здесь._chainmap.items())
        return f"Слоистый_словарь({{{элементы}}})"

class Собственный_словарь(_Изменяемое_отображение):
    def __init__(здесь, *ПА, **ИА):
        здесь._user_dict = collections.UserDict(*ПА, **ИА)

    def Получить(здесь, ключ, по_умолчанию = None):
        return здесь._user_dict.get(ключ, по_умолчанию)

    def Установить_по_умолчанию(здесь, ключ, по_умолчанию = None):
        return здесь._user_dict.setdefault(ключ, по_умолчанию)

    def Удалить(здесь, ключ, по_умолчанию = None):
        return здесь._user_dict.pop(ключ, по_умолчанию)

    def Удалить_последний(здесь, последний = True):
        return здесь._user_dict.popitem(last = последний)

    def __getitem__(здесь, ключ):
        return здесь._user_dict[ключ]

    def __setitem__(здесь, ключ, значение):
        здесь._user_dict[ключ] = значение

    def __delitem__(здесь, ключ):
        del здесь._user_dict[ключ]

    def __iter__(здесь):
        return iter(здесь._user_dict)

    def __len__(здесь):
        return len(здесь._user_dict)

    def __contains__(здесь, ключ):
        return ключ in здесь._user_dict

    def Ключи(здесь):
        return list(здесь._user_dict.keys())

    def Значения(здесь):
        return list(здесь._user_dict.values())

    def Элементы(здесь):
        return list(здесь._user_dict.items())

    def __str__(здесь):
        элементы = ', '.join(f"{k}: {v}" for k, v in здесь._user_dict.items())
        return f"Собственный_словарь({{{элементы}}})"

class Собственный_список(_Изменяемая_последовательность):
    def __init__(здесь, перебираемый = None):
        здесь._user_list = collections.UserList(перебираемый or [])

    def Добавить(здесь, элемент):
        здесь._user_list.append(элемент)

    def Вставить(здесь, индекс, элемент):
        здесь._user_list.insert(индекс, элемент)

    def Удалить(здесь, индекс = None):
        if индекс is None:
            return здесь._user_list.pop()
        return здесь._user_list.pop(индекс)

    def Очистить(здесь):
        здесь._user_list.clear()

    def Количество(здесь, элемент):
        return здесь._user_list.count(элемент)

    def Индекс(здесь, элемент, начало = 0, конец = None):
        return здесь._user_list.index(элемент, начало, конец or len(здесь._user_list))

    def Сортировать(здесь, ключ = None, по_убыванию = False):
        здесь._user_list.sort(key = ключ, reverse = по_убыванию)

    def Перевернуть(здесь):
        здесь._user_list.reverse()

    def Расширить(здесь, перебираемый):
        здесь._user_list.extend(перебираемый)

    def __getitem__(здесь, индекс):
        return здесь._user_list[индекс]

    def __setitem__(здесь, индекс, значение):
        здесь._user_list[индекс] = значение

    def __delitem__(здесь, индекс):
        del здесь._user_list[индекс]

    def __len__(здесь):
        return len(здесь._user_list)

    def __iter__(здесь):
        return iter(здесь._user_list)

    def __contains__(здесь, элемент):
        return элемент in здесь._user_list

    def __reversed__(здесь):
        return reversed(здесь._user_list)

    def __str__(здесь):
        return f"Собственный_список({list(здесь._user_list)})"

class Собственная_строка(_Последовательность):
    def __init__(здесь, строка = ""):
        здесь._user_string = collections.UserString(строка)

    def Разделить(здесь, разделитель = None):
        return здесь._user_string.split(разделитель)

    def Соединить(здесь, перебираемый):
        return здесь._user_string.join(перебираемый)

    def В_верхний_регистр(здесь):
        return Собственная_строка(здесь._user_string.upper())

    def В_нижний_регистр(здесь):
        return Собственная_строка(здесь._user_string.lower())

    def Начинается_с(здесь, префикс):
        return здесь._user_string.startswith(префикс)

    def Заканчивается_на(здесь, суффикс):
        return здесь._user_string.endswith(суффикс)

    def __getitem__(здесь, индекс):
        return здесь._user_string[индекс]

    def __len__(здесь):
        return len(здесь._user_string)

    def __iter__(здесь):
        return iter(здесь._user_string)

    def __contains__(здесь, элемент):
        return элемент in здесь._user_string

    def __reversed__(здесь):
        return reversed(здесь._user_string)

    def __str__(здесь):
        return str(здесь._user_string)

class Собственное_множество(_Изменяемое_множество):
    def __init__(здесь, перебираемый = None):
        здесь._set = set(перебираемый or [])

    def Добавить(здесь, элемент):
        здесь._set.add(элемент)

    def Удалить(здесь, элемент):
        try:
            здесь._set.remove(элемент)
        except KeyError:
            raise KeyError(f"Элемент {элемент} не найден")

    def Отбросить(здесь, элемент):
        здесь._set.discard(элемент)

    def Очистить(здесь):
        здесь._set.clear()

    def Объединить(здесь, другой):
        if isinstance(другой, Собственное_множество):
            return Собственное_множество(здесь._set | другой._set)
        return NotImplemented

    def Пересечь(здесь, другой):
        if isinstance(другой, Собственное_множество):
            return Собственное_множество(здесь._set & другой._set)
        return NotImplemented

    def Разность(здесь, другой):
        if isinstance(другой, Собственное_множество):
            return Собственное_множество(здесь._set - другой._set)
        return NotImplemented

    def Симметрическая_разность(здесь, другой):
        if isinstance(другой, Собственное_множество):
            return Собственное_множество(здесь._set ^ другой._set)
        return NotImplemented

    def __contains__(здесь, элемент):
        return элемент in здесь._set

    def __iter__(здесь):
        return iter(здесь._set)

    def __len__(здесь):
        return len(здесь._set)

    def __or__(здесь, другой):
        return здесь.Объединить(другой)

    def __and__(здесь, другой):
        return здесь.Пересечь(другой)

    def __sub__(здесь, другой):
        return здесь.Разность(другой)

    def __xor__(здесь, другой):
        return здесь.Симметрическая_разность(другой)

    def __str__(здесь):
        элементы = ', '.join(str(x) for x in здесь._set)
        return f"Собственное_множество({{{элементы}}})"

    def В_строку(здесь):
        длина = len(здесь._set)
        if длина == 0:
            return "Пустое множество"
        return f"Множество с {__Общие_функции__.Склонение_после_числительного(длина, ['элементом', 'элементами', 'элементами'])}: {{{', '.join(str(x) for x in здесь._set)}}}"
