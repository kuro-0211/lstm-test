from pymodbus.server import StartTcpServer
from pymodbus.datastore import ModbusDeviceContext, ModbusServerContext
from pymodbus.datastore import ModbusSequentialDataBlock
import random, threading, time

def update_registers(context):
    while True:
        power_kw = int(random.uniform(0.5, 5.0) * 100)
        temp     = int(random.uniform(20.0, 35.0) * 10)
        humidity = int(random.uniform(40.0, 80.0) * 10)
        slave = context[0]
        slave.setValues(3, 0, [power_kw, temp, humidity])
        time.sleep(1)

store = ModbusDeviceContext(
    hr=ModbusSequentialDataBlock(0, [0] * 10)
)
context = ModbusServerContext(slaves=store, single=True)

t = threading.Thread(target=update_registers, args=(context,), daemon=True)
t.start()

print("[EMU] Modbus TCP 에뮬레이터 시작 - 127.0.0.1:5020")
StartTcpServer(context=context, address=("127.0.0.1", 5020))