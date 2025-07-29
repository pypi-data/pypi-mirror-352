from abc import ABC, abstractmethod
import datetime


class SoftStateMixin:
    """
    Хранит программное состояние входов/выходов.
    Позволяет обновлять состояния и получать их по ключу.
    """
    spec_addr = {}      # переназначение адресов (если физический != логическому)
    map_keys_amount = 0
    starts_with = 0

    def __init__(self, map_keys_amount=None, starts_with=None, spec_addr=None):
        self.map_keys_amount = map_keys_amount if map_keys_amount is not None else getattr(self.__class__, 'map_keys_amount', 0)
        self.starts_with = starts_with if starts_with is not None else getattr(self.__class__, 'starts_with', 0)
        self.spec_addr = spec_addr if spec_addr is not None else getattr(self.__class__, 'spec_addr', {})
        self.state = self._init_state()


    def _init_state(self):
        points = {}
        for i in range(self.map_keys_amount):
            logical_ch = self.starts_with + i
            addr = self.spec_addr.get(logical_ch, logical_ch)
            points[logical_ch] = {"state": None, "changed": None, "addr": addr}
        return points

    def update_state(self, addr, value, mark_time=True):
        now = datetime.datetime.now() if mark_time else None
        for logical_ch, info in self.state.items():
            if info["addr"] == addr:
                info["state"] = value
                info["changed"] = now

    def get_state(self):
        return self.state

    def get_point(self, num):
        return self.state.get(num, {"error": f"channel {num} not found"})


class BasePhysInterface(ABC):
    """
    Абстрактный интерфейс работы с железом.
    Потомки реализуют конкретную работу с DI или Relay.
    """
    @abstractmethod
    def get_phys_dict(self) -> dict:
        """
        Вернуть словарь {канал: значение} с физического устройства.
        """
        pass


class RelayPhysInterface(BasePhysInterface):
    @abstractmethod
    def change_phys_relay_state(self, addr: int, state: bool):
        """
        Изменить состояние реле на физическом устройстве.
        """
        pass

class DIInterface(SoftStateMixin, BasePhysInterface):
    def __init__(self, map_keys_amount=None, starts_with=None, spec_addr=None):
        super().__init__(map_keys_amount, starts_with, spec_addr)
        self.update_from_device()

    def update_from_device(self):
        values = self.get_phys_dict()
        for addr, value in values.items():
            self.update_state(addr, value, mark_time=False)


class RelayInterface(SoftStateMixin, RelayPhysInterface):
    def __init__(self, map_keys_amount=None, starts_with=None, spec_addr=None):
        super().__init__(map_keys_amount, starts_with, spec_addr)
        self.update_from_device()

    def update_from_device(self):
        values = self.get_phys_dict()
        for addr, value in values.items():
            self.update_state(addr, value, mark_time=False)

    def change_relay_state(self, logical_ch: int, state: bool):
        self.update_state(logical_ch, state)
        addr = self.state[logical_ch]["addr"]
        return self.change_phys_relay_state(addr, state)


class ControllerInterface:
    """
    Комбинирует доступ к DI и Relay интерфейсам.
    """
    def __init__(self, di_interface=None, relay_interface=None):
        self.di_interface = di_interface
        self.relay_interface = relay_interface

    def update_all(self):
        if self.di_interface:
            self.di_interface.update_from_device()
        if self.relay_interface:
            self.relay_interface.update_from_device()

    def get_all_states(self):
        return {
            "di": self.di_interface.get_state() if self.di_interface else {},
            "relays": self.relay_interface.get_state() if self.relay_interface else {}
        }
