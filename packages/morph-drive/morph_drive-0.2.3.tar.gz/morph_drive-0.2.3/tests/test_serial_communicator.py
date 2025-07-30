import logging
import unittest
from unittest.mock import MagicMock, patch

import serial

from morph_drive.robots.serial_communicator import SerialCommunicator

logging.disable(logging.CRITICAL)


class TestSerialCommunicator(unittest.TestCase):
    def setUp(self):
        self.port = "/dev/ttyTest"
        self.baud_rate = 9600
        self.timeout = 1.0
        self.logger = logging.getLogger(__name__)
        # self.logger.setLevel(logging.DEBUG) # Enable for debugging tests

    @patch("serial.Serial")
    def test_connect_successful(self, mock_serial_class):
        mock_serial_instance = MagicMock()
        mock_serial_instance.is_open = True
        mock_serial_class.return_value = mock_serial_instance

        communicator = SerialCommunicator(
            self.port, self.baud_rate, self.timeout, self.logger
        )
        self.assertTrue(communicator.connect())
        self.assertTrue(communicator.is_open())
        mock_serial_class.assert_called_once_with(
            self.port, self.baud_rate, timeout=self.timeout
        )
        self.assertEqual(communicator.ser, mock_serial_instance)

    @patch("serial.Serial")
    @patch("morph_drive.robots.serial_communicator.sleep")  # Mock sleep
    def test_connect_failure_then_success(self, mock_sleep, mock_serial_class):
        mock_serial_instance_good = MagicMock()
        mock_serial_instance_good.is_open = True

        # Simulate failure on first attempt, success on second
        mock_serial_class.side_effect = [
            serial.SerialException("Connection failed"),
            mock_serial_instance_good,
        ]

        communicator = SerialCommunicator(
            self.port, self.baud_rate, self.timeout, self.logger
        )
        self.assertTrue(communicator.connect(retries=2, delay=0.1))
        self.assertTrue(communicator.is_open())
        self.assertEqual(mock_serial_class.call_count, 2)
        mock_sleep.assert_called_once_with(0.1)

    @patch("serial.Serial")
    @patch("morph_drive.robots.serial_communicator.sleep")  # Mock sleep
    def test_connect_persistent_failure(self, mock_sleep, mock_serial_class):
        mock_serial_class.side_effect = serial.SerialException(
            "Connection failed persistently"
        )

        communicator = SerialCommunicator(
            self.port, self.baud_rate, self.timeout, self.logger
        )
        with self.assertRaises(ConnectionError) as context:
            communicator.connect(retries=3, delay=0.1)

        self.assertIn(
            "Failed to connect to /dev/ttyTest after 3 attempts", str(context.exception)
        )
        self.assertEqual(mock_serial_class.call_count, 3)
        self.assertEqual(mock_sleep.call_count, 3)  # Sleeps after each failed attempt
        self.assertFalse(communicator.is_open())

    @patch("serial.Serial")
    def test_close_connection(self, mock_serial_class):
        mock_serial_instance = MagicMock()
        mock_serial_instance.is_open = True
        mock_serial_class.return_value = mock_serial_instance

        communicator = SerialCommunicator(
            self.port, self.baud_rate, self.timeout, self.logger
        )
        communicator.connect()

        communicator.close_connection()
        mock_serial_instance.close.assert_called_once()

    @patch("serial.Serial")
    def test_write_line_successful(self, mock_serial_class):
        mock_serial_instance = MagicMock()
        mock_serial_instance.is_open = True
        mock_serial_class.return_value = mock_serial_instance

        communicator = SerialCommunicator(
            self.port, self.baud_rate, self.timeout, self.logger
        )
        communicator.connect()

        message = "Hello\n"
        self.assertTrue(communicator.write_line(message))
        mock_serial_instance.write.assert_called_once_with(message.encode())
        mock_serial_instance.reset_input_buffer.assert_called_once()  # flush_input

    @patch("serial.Serial")
    def test_write_line_serial_exception(self, mock_serial_class):
        mock_serial_instance = MagicMock()
        mock_serial_instance.is_open = True
        mock_serial_instance.write.side_effect = serial.SerialException("Write failed")
        mock_serial_class.return_value = mock_serial_instance

        communicator = SerialCommunicator(
            self.port, self.baud_rate, self.timeout, self.logger
        )
        communicator.connect()

        self.assertFalse(communicator.write_line("Hello\n"))

    @patch("serial.Serial")
    def test_read_line_successful(self, mock_serial_class):
        mock_serial_instance = MagicMock()
        mock_serial_instance.is_open = True
        # Simulate readline returning bytes that need decoding and stripping
        mock_serial_instance.readline.return_value = b"Data from serial\r\n"
        mock_serial_class.return_value = mock_serial_instance

        communicator = SerialCommunicator(
            self.port, self.baud_rate, self.timeout, self.logger
        )
        communicator.connect()

        response = communicator.read_line()
        self.assertEqual(response, "Data from serial")
        mock_serial_instance.readline.assert_called_once()

    @patch("serial.Serial")
    def test_read_line_acknowledgement_then_data(self, mock_serial_class):
        mock_serial_instance = MagicMock()
        mock_serial_instance.is_open = True
        mock_serial_instance.readline.side_effect = [b"OK\r\n", b"Actual Data\r\n"]
        mock_serial_class.return_value = mock_serial_instance

        communicator = SerialCommunicator(
            self.port, self.baud_rate, self.timeout, self.logger
        )
        communicator.connect()

        response = communicator.read_line()
        self.assertEqual(response, "Actual Data")
        self.assertEqual(mock_serial_instance.readline.call_count, 2)

    @patch("serial.Serial")
    def test_read_line_serial_exception(self, mock_serial_class):
        mock_serial_instance = MagicMock()
        mock_serial_instance.is_open = True
        mock_serial_instance.readline.side_effect = serial.SerialException(
            "Read failed"
        )
        mock_serial_class.return_value = mock_serial_instance

        communicator = SerialCommunicator(
            self.port, self.baud_rate, self.timeout, self.logger
        )
        communicator.connect()

        self.assertIsNone(communicator.read_line())

    @patch("serial.Serial")
    def test_context_manager(self, mock_serial_class):
        mock_serial_instance = MagicMock()
        mock_serial_instance.is_open = True
        mock_serial_class.return_value = mock_serial_instance

        with SerialCommunicator(
            self.port, self.baud_rate, self.timeout, self.logger
        ) as comm:
            self.assertTrue(comm.is_open())
            mock_serial_class.assert_called_once()  # connect called

        mock_serial_instance.close.assert_called_once()  # close_connection called on exit


if __name__ == "__main__":
    unittest.main()
