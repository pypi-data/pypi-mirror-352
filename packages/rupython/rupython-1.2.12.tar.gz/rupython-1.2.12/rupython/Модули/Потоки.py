import threading
from rupython import __Общие_функции__

Ошибка_потока = threading.ThreadError

Словарь_параметров = {
    'цель': 'target',
    'имя': 'name',
    'аргументы': 'args',
    'именовАргументы': 'kwargs',
    'после_окончания': 'daemon',
    'время_ожидания': 'timeout',
    'количество': 'count',
    'действие': 'action',
    'блоковать': 'block',
    'обратный_вызов': 'callback',
    'аргументыОбрВыз': 'callback_args',
    'именовАргументыОбрВыз': 'callback_kwargs',
    'интервал': 'interval'
}

Словарь_склонений = {
    'поток': ['поток', 'потока', 'потоков'],
    'ресурс': ['ресурс', 'ресурса', 'ресурсов'],
    'участник': ['участник', 'участника', 'участников']
}

class Поток:
    def __init__(здесь, цель = None, имя = None, аргументы = (), именовАргументы = None, после_окончания = None):
        ИА = {}
        if цель is not None:
            ИА['target'] = цель
        if имя is not None:
            ИА['name'] = имя
        if аргументы:
            ИА['args'] = аргументы
        if именовАргументы is not None:
            ИА['kwargs'] = именовАргументы
        if после_окончания is not None:
            ИА['daemon'] = после_окончания
        здесь._thread = threading.Thread(**ИА)

    def Начать(здесь):
        здесь._thread.start()

    def Ждать(здесь, время_ожидания = None):
        ИА = {}
        if время_ожидания is not None:
            ИА['timeout'] = время_ожидания
        здесь._thread.join(**kwargs)

    def Живой(здесь):
        return здесь._thread.is_alive()

    def Получить_имя(здесь):
        return здесь._thread.getName()

    def Установить_имя(здесь, имя):
        здесь._thread.setName(имя)

    def Получить_идентификатор(здесь):
        return здесь._thread.ident

    def После_окончания(здесь):
        return здесь._thread.daemon

    def Установить_после_окончания(здесь, после_окончания):
        здесь._thread.daemon = после_окончания

    def __str__(здесь):
        return f"Поток(имя={здесь.Получить_имя()}, живой={здесь.Живой()})"

class Блокование:
    def __init__(здесь):
        здесь._lock = threading.Lock()

    def Захватить(здесь, блоковать = True, время_ожидания = None):
        ИА = {'block': блоковать}
        if время_ожидания is not None:
            ИА['timeout'] = время_ожидания
        return здесь._lock.acquire(**ИА)

    def Освободить(здесь):
        здесь._lock.release()

    def Захвачено(здесь):
        return здесь._lock.locked()

    def __enter__(здесь):
        здесь.Захватить()
        return здесь

    def __exit__(здесь, тип_исключения, значение_исключения, трассировка):
        здесь.Освободить()

    def __str__(здесь):
        return f"Блокование(захвачено={здесь.Захвачено()})"

class Повторное_блокование:
    def __init__(здесь):
        здесь._rlock = threading.RLock()

    def Захватить(здесь, блоковать = True, время_ожидания = None):
        ИА = {'block': блоковать}
        if время_ожидания is not None:
            ИА['timeout'] = время_ожидания
        return здесь._rlock.acquire(**ИА)

    def Освободить(здесь):
        здесь._rlock.release()

    def __enter__(здесь):
        здесь.Захватить()
        return здесь

    def __exit__(здесь, тип_исключения, значение_исключения, трассировка):
        здесь.Освободить()

    def __str__(здесь):
        return f"Повторное_блокование(владелец={здесь._rlock._owner}, счётчик={здесь._rlock._count})"

class Семафор:
    def __init__(здесь, количество = 1):
        ИА = {'value': количество}
        здесь._semaphore = threading.Semaphore(**ИА)

    def Захватить(здесь, блоковать = True, время_ожидания = None):
        ИА = {'block': блоковать}
        if время_ожидания is not None:
            ИА['timeout'] = время_ожидания
        return здесь._semaphore.acquire(**ИА)

    def Освободить(здесь):
        здесь._semaphore.release()

    def __enter__(здесь):
        здесь.Захватить()
        return здесь

    def __exit__(здесь, тип_исключения, значение_исключения, трассировка):
        здесь.Освободить()

    def __str__(здесь):
        return f"Семафор(ресурсов={здесь._semaphore._value})"

class Ограниченный_семафор(Семафор):
    def __init__(здесь, количество = 1):
        ИА = {'value': количество}
        здесь._semaphore = threading.BoundedSemaphore(**ИА)

class Событие:
    def __init__(здесь):
        здесь._event = threading.Event()

    def Установить(здесь):
        здесь._event.set()

    def Сбросить(здесь):
        здесь._event.clear()

    def Активно(здесь):
        return здесь._event.is_set()

    def Ждать(здесь, время_ожидания = None):
        ИА = {}
        if время_ожидания is not None:
            ИА['timeout'] = время_ожидания
        return здесь._event.wait(**ИА)

    def __str__(здесь):
        return f"Событие(активно={здесь.Активно()})"

class Условие:
    def __init__(здесь, блокование = None):
        ИА = {}
        if блокование is not None:
            ИА['lock'] = блокование._lock if isinstance(блокование, (Блокование, Повторное_блокование)) else блокование
        здесь._condition = threading.Condition(**ИА)

    def Захватить(здесь):
        return здесь._condition.acquire()

    def Освободить(здесь):
        здесь._condition.release()

    def Ждать(здесь, время_ожидания = None):
        ИА = {}
        if время_ожидания is not None:
            ИА['timeout'] = время_ожидания
        return здесь._condition.wait(**ИА)

    def Уведомить(здесь, количество = 1):
        ИА = {'n': количество}
        здесь._condition.notify(**ИА)

    def Уведомить_все(здесь):
        здесь._condition.notify_all()

    def __enter__(здесь):
        здесь.Захватить()
        return здесь

    def __exit__(здесь, тип_исключения, значение_исключения, трассировка):
        здесь.Освободить()

    def __str__(здесь):
        return f"Условие(захвачено={здесь._condition._is_owned()})"

class Барьер:
    def __init__(здесь, количество, действие = None, время_ожидания = None):
        ИА = {'parties': количество}
        if действие is not None:
            ИА['action'] = действие
        if время_ожидания is not None:
            ИА['timeout'] = время_ожидания
        здесь._barrier = threading.Barrier(**ИА)

    def Ждать(здесь, время_ожидания = None):
        ИА = {}
        if время_ожидания is not None:
            ИА['timeout'] = время_ожидания
        return здесь._barrier.wait(**ИА)

    def Сбросить(здесь):
        здесь._barrier.reset()

    def Прервать(здесь):
        здесь._barrier.abort()

    def Количество_участников(здесь):
        return здесь._barrier.parties

    def Количество_ожидающих(здесь):
        return здесь._barrier.n_waiting

    def Сломан(здесь):
        return здесь._barrier.broken

    def __str__(здесь):
        return f"Барьер({__Общие_функции__.Склонение_после_числительного(здесь.Количество_ожидающих(), Словарь_склонений['участник'])} из {здесь.Количество_участников()})"

class Таймер(Поток):
    def __init__(здесь, интервал, цель, аргументы = (), именовАргументы = None, обратный_вызов = None, аргументыОбрВыз = (), именовАргументыОбрВыз = None):
        ИА = {'interval': интервал, 'function': цель}
        if аргументы:
            ИА['args'] = аргументы
        if именовАргументы is not None:
            ИА['kwargs'] = именовАргументы
        здесь._timer = threading.Timer(**ИА)
        здесь._callback = обратный_вызов
        здесь._callback_args = аргументыОбрВыз
        здесь._callback_kwargs = именовАргументыОбрВыз or {}

    def Отменить(здесь):
        здесь._timer.cancel()

    def Завершён(здесь):
        return здесь._timer.finished.is_set()

    def __str__(здесь):
        return f"Таймер(интервал={здесь._timer.interval}, завершён={здесь.Завершён()})"

def Текущий_поток():
    return Поток(цель = lambda: None, имя = threading.current_thread().getName())

def Количество_активных_потоков():
    return threading.active_count()

def Перечислить_потоки():
    return [Поток(цель = lambda: None, имя = поток.getName()) for поток in threading.enumerate()]

def Получить_основной_поток():
    return Поток(цель = lambda: None, имя = threading.main_thread().getName())
