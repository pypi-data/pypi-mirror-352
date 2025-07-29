from gravity_controller_operator.controllers_super import DIInterface, RelayInterface, ControllerInterface
from pyModbusTCP.client import ModbusClient


class ARMK210ControllerDI(DIInterface):
    map_keys_amount = 8
    starts_with = 0

    def __init__(self, client):
        self.client = client
        super().__init__()

    def get_phys_dict(self):
        response = self.client.read_input_registers(self.starts_with, self.map_keys_amount)
        while not response:
            response = self.client.read_input_registers(self.starts_with, self.map_keys_amount)
        return {i: val for i, val in enumerate(response)}


class ARMK210ControllerRelay(RelayInterface):
    map_keys_amount = 8
    starts_with = 0

    def __init__(self, client):
        self.client = client
        super().__init__()

    def get_phys_dict(self):
        response = self.client.read_holding_registers(self.starts_with, self.map_keys_amount)
        while not response:
            response = self.client.read_holding_registers(self.starts_with, self.map_keys_amount)
        return {i: val for i, val in enumerate(response)}

    def change_phys_relay_state(self, addr, state: bool):
        result = self.client.write_single_coil(addr, state)
        while not result:
            result = self.client.write_single_coil(addr, state)


class ARMK210Controller:
    model = "arm_k210"

    def __init__(self, ip: str, port: int = 8234, name="ARM_K210_Controller", *args, **kwargs):
        client = ModbusClient(host=ip, port=port)
        di = ARMK210ControllerDI(client)
        relay = ARMK210ControllerRelay(client)
        self.interface = ControllerInterface(di_interface=di, relay_interface=relay)
