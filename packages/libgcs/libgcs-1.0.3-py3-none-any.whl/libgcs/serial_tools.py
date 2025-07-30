import threading
import queue
import time
from abc import ABC

import serial
import serial.tools.list_ports
from serial.serialutil import PortNotOpenError, SerialException

from ._base.exception import DeviceNotFoundException
from ._base.logger import LoggerBase
from ._base.threading import ThreadBase


class SerialPort:
    def __init__(self):
        self.__device: serial.Serial | None = None
        self.__name: str | None = None
        self.__baud = 115200
        self.__port_pair = self.ports()
        self.__logger = LoggerBase(target='LOG_SERIAL')
        self.__thread_reconnect: threading.Thread | None = None
        self.__flag_reconnect = False
        self.__is_reconnecting = False

    def refresh(self):
        """
        Refresh port list

        :return:
        """
        self.__port_pair = self.ports()

    def connect(self, name: str, baud: int | str = 115200,
                auto_reconnect: bool = True, override: bool = False,
                attempt_reconnect: bool = False) -> bool:
        """
        Connect the device

        :param name: device name (directory)
        :param baud: baud rate
        :param auto_reconnect: Auto reconnect or not
        :param override: Override name checking
        :param attempt_reconnect: Is this connection attempt to reconnect? to suppress warnings
        :return: Connection successful or not
        """

        name = name.strip()
        if not override:
            try:
                if '(' in name and ')' in name:
                    if name not in self.__port_pair:
                        raise DeviceNotFoundException(f'No device named "{name}"!')
                    __name = self.__port_pair[name]
                else:
                    if name not in self.__port_pair.values():
                        raise DeviceNotFoundException(f'No device named "{name}"!')
                    __name = name
            except DeviceNotFoundException:
                if not attempt_reconnect:
                    self.__logger.warn('Device not found!')
                return False
        else:
            __name = name

        if isinstance(self.__device, serial.Serial) and not attempt_reconnect:
            self.__logger.info(f'Clearing connection from "{self.__name}" before connecting "{name}".')
            self.disconnect()

        self.__name = __name
        self.__baud = int(baud)

        try:
            self.__device = serial.Serial(self.__name,
                                          baudrate=self.__baud,
                                          bytesize=serial.EIGHTBITS,
                                          parity=serial.PARITY_NONE,
                                          stopbits=serial.STOPBITS_ONE,
                                          xonxoff=False,
                                          rtscts=False,
                                          dsrdtr=False,
                                          timeout=1,
                                          write_timeout=0)
            self.__logger.info(f'Device "{self.__name}" is successfully connected with baud rate {self.__baud}.')
            try:
                if not self.__device.is_open:
                    self.__device.open()
                if auto_reconnect:
                    self.__setup_auto_reconnect()
                return True
            except serial.SerialException:
                self.__logger.exception(
                    f'Unexpected Error! Can\'t open port "{__name}".'
                )
        except (serial.SerialException, FileNotFoundError):
            if not attempt_reconnect:
                self.__logger.exception(
                    f'Unexpected Error! Can\'t connect port "{__name}" or the port is already connected.'
                )
        self.__device = None
        return False

    def disconnect(self, *, destructor=False):
        """
        Disconnect the device

        :return:
        """
        if not destructor:
            if isinstance(self.__device, serial.Serial) and self.__device.is_open:
                self.__destroy_auto_reconnect()
                self.__device.close()
                self.__device = None
                self.__logger.info(f'"{self.__name}" has been successfully closed!')
            else:
                self.__logger.warn(f'"{self.__name}" has already been disconnected!')
        elif isinstance(self.__device, serial.Serial):
            self.__destroy_auto_reconnect()
            self.__device.close()
            self.__device = None
            self.__logger.info(f'"{self.__name}" has been successfully closed!')

    def is_connected(self) -> bool:
        """
        Check if the device is connected

        :return:
        """
        if not isinstance(self.__device, serial.Serial):
            return False
        if not self.__device.is_open:
            return False
        try:
            _ = self.__device.in_waiting
            return True
        except (OSError, serial.SerialException):
            self._drop()
            return False

    def is_reconnecting(self) -> bool:
        """
        Check if the device is being attempted to reconnect

        :return:
        """
        return self.__is_reconnecting

    def print_ports(self):
        """
        Print ports list with number

        :return:
        """
        for i, (k, v) in enumerate(self.__port_pair, start=1):
            print(f'[{i}] {v} ({k})')

    def reset(self):
        """
        Reset hardware port (clear connection and reinitializing)

        :return:
        """
        self.disconnect()
        self.__init__()

    def _drop(self):
        """
        **DANGER!** Drop the port, for internal usage. Do not use.

        :return:
        """
        self.__device = None

    def __setup_auto_reconnect(self):
        self.__flag_reconnect = True
        self.__thread_reconnect = threading.Thread(
            target=self.__try_reconnect,
            daemon=True
        )
        self.__thread_reconnect.start()

    def __destroy_auto_reconnect(self):
        if isinstance(self.__thread_reconnect, threading.Thread):
            self.__flag_reconnect = False
            self.__thread_reconnect.join()
            self.__thread_reconnect = None

    def __try_reconnect(self):
        result = True
        attempt_no = 20
        while self.__flag_reconnect:
            self.__is_reconnecting = False
            if not self.is_connected():
                self.__is_reconnecting = True
                self.__logger.warn(f'Attempting to reconnect "{self.__name}"...')
                try:
                    for i in range(1, attempt_no + 1):
                        result = self.connect(self.__name, self.__baud,
                                              auto_reconnect=False,
                                              attempt_reconnect=True)
                        if result:
                            self.__is_reconnecting = False
                            break
                        time.sleep(2.000 / attempt_no)
                except (serial.SerialException, FileNotFoundError):
                    pass
            if result:
                self.__is_reconnecting = False
                time.sleep(0.100)
            else:
                time.sleep(2.000)

    def __del__(self):
        """
        Disconnect and stop event when destructor is called.

        :return:
        """
        self.disconnect(destructor=True)

    @property
    def port_pair(self):
        return self.__port_pair

    @property
    def device(self):
        """
        Serial device object

        :return: Serial device object
        """
        return self.__device

    @property
    def name(self):
        return self.__name

    @property
    def baud(self):
        return self.__baud

    @staticmethod
    def ports():
        """
        Returns all available ports in dictionary with full name as key
        and true device name as value. Used for referencing user inputs.

        :return: Dictionary of device's full name : device true name
        """
        __port_name = dict()
        __port_infos = serial.tools.list_ports.comports()

        # Separate likely-valid and other ports
        __likely_valid = [p for p in __port_infos if p.vid or p.pid or p.manufacturer]
        __others = [p for p in __port_infos if p not in __likely_valid]

        # Sort likely-valid ports by device name
        __likely_valid_sorted = sorted(__likely_valid, key=lambda p: str(p.device))
        __others.reverse()

        # Combine lists
        __combined_ports = __likely_valid_sorted + __others

        for port_iter in __combined_ports:
            __name = f'{port_iter.device} ({port_iter.manufacturer} {port_iter.product}) {port_iter.hwid}'
            __port_name[__name] = port_iter.device

        return __port_name

    @staticmethod
    def print_verbose_ports():
        __port_infos = serial.tools.list_ports.comports()
        for port in __port_infos:
            print(port.device)
            print('    ', port.name)
            print('    ', port.description)
            print('    ', port.hwid)
            print('    ', port.vid)
            print('    ', port.pid)
            print('    ', port.serial_number)
            print('    ', port.location)
            print('    ', port.manufacturer)
            print('    ', port.product)
            print('    ', port.interface)


class SerialReader:
    def __init__(self, port: SerialPort,
                 terminator: bytes | str = b'\n',
                 encoding: str = 'ascii',
                 errors: str = 'ignore'):
        """
        SerialReader object for reading data from serial port.

        :param port: SerialPort object, not serial.Serial object!
        :param terminator: Terminator string to read each message, default is newline
        :param encoding: Encoding, default is "ascii"
        :param errors: Encoding errors handling, default is "ignore"
        """
        self.__port = port
        self.__encoding = {'encoding': encoding, 'errors': errors}
        if isinstance(terminator, str):
            self.__terminator = terminator.encode(**self.__encoding)
        else:
            self.__terminator = terminator
        self.__stream = bytearray()
        self.__logger = LoggerBase(target='LOG_READER')

    def get_message(self, terminator: str | bytes | int = None, decode: bool = False) -> bytes | str:
        if isinstance(terminator, int):
            if terminator == -1:
                __msg = self.__stream
                self.__stream = bytearray()
            elif terminator > 0:
                __msg = self.__stream[:terminator]
                self.__stream = self.__stream[len(__msg):]
            else:
                return b'' if not decode else ''

            if decode:
                return __msg.decode(**self.__encoding)
            return bytes(__msg)

        # Handle string or bytes terminator
        if terminator is None:
            terminator = self.__terminator
        elif isinstance(terminator, str):
            terminator = terminator.encode(**self.__encoding)

        __idx = self.__stream.find(terminator)
        if __idx == -1:
            return b'' if not decode else ''
        __msg = self.__stream[:__idx]
        self.__stream = self.__stream[__idx + len(terminator):]

        # Remove Carriage Return
        if terminator.endswith(b'\n'):
            __msg = __msg.replace(b'\r', b'')

        if decode:
            return __msg.decode(**self.__encoding)
        return __msg

    def read(self) -> int:
        msg = self.__read()
        self.__stream += msg
        return len(msg)

    def clear(self):
        self.__stream = bytearray()

    def __read(self) -> bytes:
        if not self.__port.is_connected():
            return b''
        try:
            return self.__port.device.read(self.__port.device.in_waiting or 1)
        except (OSError, SerialException, TypeError):
            self.__port._drop()
            return b''

    def available(self, terminator: str | bytes | int = None) -> bool:
        if isinstance(terminator, int):
            return len(self.__stream) >= terminator if terminator > 0 else len(self.__stream) > 0
        elif terminator is None:
            terminator = self.__terminator
        elif isinstance(terminator, str):
            terminator = terminator.encode(**self.__encoding)
        return len(self.__stream) > 0 and self.__stream.find(terminator) != -1

    @property
    def port(self):
        return self.__port

    @property
    def stream(self):
        return self.__stream

    @property
    def encoding(self):
        return self.__encoding


class SerialThread(ThreadBase):
    READ_INTERVAL = 0.001

    def __init__(self, reader: SerialReader, timeout: float = 1.000):
        super().__init__('LOG_SERIAL', timeout)
        self._reader = reader
        self._fifo_read: queue.Queue[bytes] = queue.Queue()

    def _task(self):
        while self._on:
            time.sleep(self.READ_INTERVAL)
            if not self._reader.read():
                continue
            _msg = self._reader.get_message(-1, decode=False)
            if not _msg:
                continue
            self._fifo_read.put(_msg)

    def size(self):
        return self.fifo.qsize()

    def get(self) -> bytes:
        acc = bytearray()
        while not self.fifo.empty():
            acc += self.fifo.get()
        return bytes(acc)

    @property
    def fifo(self) -> queue.Queue[bytes]:
        return self._fifo_read

    @property
    def queue(self) -> queue.Queue[bytes]:
        return self.fifo

    def _setup(self):
        pass

    def _loop(self):
        pass


ALL_BAUD = (110, 300, 600, 1_200, 2_400, 4_800, 9_600,
            14_400, 19_200, 38_400, 57_600, 76_800,
            115_200, 230_400, 250_000, 460_800, 500_000, 576_000, 921_600,
            1_000_000, 2_000_000)

ALL_BAUD_STR = tuple(str(e) for e in ALL_BAUD)


def __test_serial():
    import time
    port = SerialPort()
    reader = SerialReader(port)
    thread = SerialThread(reader)
    port.connect('/dev/ttyACM0', 115200)
    thread.start()
    try:
        while True:
            time.sleep(SerialThread.READ_INTERVAL)
            msg = thread.get().decode()
            if msg:
                print(msg, end='')

    except KeyboardInterrupt:
        pass
    thread.stop()
