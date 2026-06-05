from pymodbus.client import ModbusTcpClient


class ModbusWrapper:
    def __init__(self, host="127.0.0.1", port=502):
        self.client = ModbusTcpClient(host, port=port)
        self.connected = self.client.connect()

        print(f"[Modbus] Connected: {self.connected}")

    def write_register(self, address, value):
        if not self.connected:
            print(f"[Modbus] Not connected. Skipping write {address}={value}")
            return

        try:
            # Newer pymodbus versions
            self.client.write_register(
                address=address,
                value=value,
                slave=1
            )
        except TypeError:
            try:
                # Older pymodbus versions
                self.client.write_register(
                    address=address,
                    value=value,
                    unit=1
                )
            except TypeError:
                # Some versions use no slave/unit argument
                self.client.write_register(
                    address=address,
                    value=value
                )

    def read_registers(self, address, count):
        if not self.connected:
            return [0] * count

        try:
            # Newer pymodbus versions
            result = self.client.read_holding_registers(
                address=address,
                count=count,
                slave=1
            )
        except TypeError:
            try:
                # Older pymodbus versions
                result = self.client.read_holding_registers(
                    address=address,
                    count=count,
                    unit=1
                )
            except TypeError:
                # Some versions use no slave/unit argument
                result = self.client.read_holding_registers(
                    address=address,
                    count=count
                )

        if result.isError():
            return [0] * count

        return result.registers

    def close(self):
        self.client.close()


modbus = ModbusWrapper()