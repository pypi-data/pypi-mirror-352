import heapq
from rupython import __Общие_функции__

# Словарь для перевода параметров
Словарь_параметров = {
    'перебираемое': 'iterable',
    'ключ': 'key',
    'количество': 'n',
    'элемент': 'item'
}

Словарь_склонений = {
    'элемент': ['элемент', 'элемента', 'элементов']
}

def Склонение_после_числительного(число, слова):
    return str(число) + ' ' + (
        слова[2] if число % 100 >= 5 and число % 100 <= 20 else (
            слова[0] if число % 10 == 1 else (
                слова[1] if число % 10 >= 2 and число % 10 <= 4 else слова[2]
            )
        )
    )

class Куча:
    def __init__(здесь, перебираемое=None):
        здесь._heap = list(перебираемое or [])
        heapq.heapify(здесь._heap)

    def Добавить(здесь, элемент):
        heapq.heappush(здесь._heap, элемент)

    def Извлечь(здесь):
        if not здесь._heap:
            raise IndexError("Куча пуста")
        return heapq.heappop(здесь._heap)

    def Добавить_и_извлечь(здесь, элемент):
        return heapq.heappushpop(здесь._heap, элемент)

    def Заменить(здесь, элемент):
        if not здесь._heap:
            raise IndexError("Куча пуста")
        return heapq.heapreplace(здесь._heap, элемент)

    def Наибольшие(здесь, количество, ключ=None):
        kwargs = {'n': количество}
        if ключ is not None:
            kwargs['key'] = ключ
        return heapq.nlargest(**kwargs, iterable=здесь._heap)

    def Наименьшие(здесь, количество, ключ=None):
        kwargs = {'n': количество}
        if ключ is not None:
            kwargs['key'] = ключ
        return heapq.nsmallest(**kwargs, iterable=здесь._heap)

    def Размер(здесь):
        return len(здесь._heap)

    def Пустая(здесь):
        return len(здесь._heap) == 0

    def Получить_список(здесь):
        return list(здесь._heap)

    def __len__(здесь):
        return len(здесь._heap)

    def __iter__(здесь):
        return iter(здесь._heap)

    def __contains__(здесь, элемент):
        return элемент in здесь._heap

    def __str__(здесь):
        размер = здесь.Размер()
        return f"Куча с {Склонение_после_числительного(размер, Словарь_склонений['элемент'])}: {здесь._heap}"

def Слить_кучи(*перебираемые, ключ=None):
    kwargs = {}
    if ключ is not None:
        kwargs['key'] = ключ
    return heapq.merge(*перебираемые, **kwargs)

def Создать_кучу(перебираемое):
    return Куча(перебираемое)
