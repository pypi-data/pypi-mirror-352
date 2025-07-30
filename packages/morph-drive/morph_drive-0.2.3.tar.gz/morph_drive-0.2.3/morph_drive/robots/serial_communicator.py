import logging
from time import sleep, time
from types import TracebackType
from typing import Optional, Type

import serial


class SerialCommunicator:
    def __init__(
        self, port: str, baud_rate: int, timeout: float, logger: logging.Logger
    ):
        self.port = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.logger = logger
        self.ser: Optional[serial.Serial] = None

    def connect(self, retries: int = 3, delay: float = 2) -> bool:
        for attempt in range(1, retries + 1):
            try:
                self.ser = serial.Serial(
                    self.port, self.baud_rate, timeout=self.timeout
                )
                if self.ser.is_open:
                    self.logger.info(
                        "Connected to %s at %d baud.", self.port, self.baud_rate
                    )
                    return True
            except serial.SerialException as e:
                self.logger.warning(
                    "Connection failed (port:%s, baud_rate:%d attempt:%d). Retrying...",
                    self.port,
                    self.baud_rate,
                    attempt,
                )
                self.logger.debug(str(e))
                sleep(delay)

        # Raise ConnectionError if all retries fail
        raise ConnectionError(
            f"Failed to connect to {self.port} after {retries} attempts."
        )

    def read_line(self) -> Optional[str]:
        reading = self._read_raw_line()
        # Assuming "OK" is an acknowledgement, read next line for actual data
        if reading == "OK":
            reading = self._read_raw_line()
        self.logger.debug("Received: %s", reading)
        return reading

    def write_line(self, string: str) -> bool:
        if not self.is_open() or self.ser is None:
            return False
        try:
            self.flush_input()
            self.ser.write(string.encode())
            sleep(0.1)
            self.logger.debug("<< %s", string)
            return True
        except serial.SerialException as e:
            self.logger.error("Error while writing", exc_info=e)
            return False

    def flush_input(self) -> None:
        if self.is_open() and self.ser is not None:
            self.logger.debug("Flushing input buffer...")
            self.ser.reset_input_buffer()

    def close_connection(self) -> None:
        if self.is_open() and self.ser is not None:
            self.ser.close()
            self.logger.info("Serial connection closed.")

    def _read_raw_line(self) -> Optional[str]:
        if not self.is_open() or self.ser is None:
            return None
        try:
            line = self.ser.readline().decode().strip()
            return line
        except serial.SerialException as e:
            self.logger.error("Read error", exc_info=e)
            return None
        except UnicodeDecodeError as e:
            self.logger.error("Unicode decode error on read", exc_info=e)
            return None

    def wait_for_ready(
        self, ready_signal: str = "READY", timeout_seconds: float = 10.0
    ) -> bool:
        self.flush_input()
        if not self.is_open() or self.ser is None:
            return False

        start_time = time()
        while (time() - start_time) < timeout_seconds:
            line = self._read_raw_line()
            if line == ready_signal:
                self.logger.info("Device is READY.")
                self.flush_input()
                return True
            sleep(0.1)

        self.logger.warning(f"Timeout waiting for '{ready_signal}' signal.")
        return False

    def is_open(self) -> bool:
        if not self.ser or not self.ser.is_open:
            return False
        return True

    def __enter__(self):
        self.connect()
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        self.close_connection()
