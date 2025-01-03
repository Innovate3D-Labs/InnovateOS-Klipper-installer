import pytest
from unittest.mock import Mock, patch
from pathlib import Path
from app.hardware.board_manager import BoardManager, Board

@pytest.fixture
def board_manager():
    return BoardManager()

@pytest.fixture
def mock_serial():
    with patch('serial.tools.list_ports.comports') as mock_comports:
        mock_port = Mock()
        mock_port.device = 'COM1'
        mock_port.vid = 0x1D50
        mock_port.pid = 0x6029
        mock_port.serial_number = 'TEST123'
        mock_port.manufacturer = 'BTT'
        mock_port.description = 'BTT Octopus'
        mock_comports.return_value = [mock_port]
        yield mock_comports

def test_detect_boards(board_manager, mock_serial):
    boards = board_manager.detect_boards()
    assert len(boards) == 1
    board = boards[0]
    assert board.port == 'COM1'
    assert board.board_type == 'BTT Octopus'
    assert board.serial_number == 'TEST123'

@pytest.mark.asyncio
async def test_test_connection(board_manager):
    with patch('serial.Serial') as mock_serial:
        mock_instance = Mock()
        mock_instance.readline.return_value = b'ok\n'
        mock_serial.return_value.__enter__.return_value = mock_instance
        
        result = await board_manager.test_connection('COM1')
        assert result is True
        
        mock_instance.write.assert_called_once_with(b'\r\n')

@pytest.mark.asyncio
async def test_prepare_for_update(board_manager):
    board = Board(
        port='COM1',
        vid=0x1D50,
        pid=0x6029,
        serial_number='TEST123',
        manufacturer='BTT',
        description='BTT Octopus',
        board_type='BTT Octopus'
    )
    
    with patch('serial.Serial') as mock_serial:
        result = await board_manager.prepare_for_update(board)
        assert result is True

@pytest.mark.asyncio
async def test_flash_firmware(board_manager):
    board = Board(
        port='COM1',
        vid=0x1D50,
        pid=0x6029,
        serial_number='TEST123',
        manufacturer='BTT',
        description='BTT Octopus',
        board_type='BTT Octopus'
    )
    firmware_path = Path('test_firmware.bin')
    
    with patch.object(board_manager, 'prepare_for_update') as mock_prepare:
        mock_prepare.return_value = True
        with patch.object(board_manager, '_flash_btt') as mock_flash:
            mock_flash.return_value = True
            
            result = await board_manager.flash_firmware(board, firmware_path)
            assert result is True
            
            mock_prepare.assert_called_once_with(board)
            mock_flash.assert_called_once_with(board, firmware_path)

def test_get_board_config(board_manager):
    config = board_manager.get_board_config('BTT Octopus')
    assert config is not None
    assert 'mcu' in config
    assert config['mcu'] == 'stm32f446'

def test_cleanup(board_manager):
    board_manager.detected_boards['COM1'] = Mock()
    board_manager.cleanup()
    assert len(board_manager.detected_boards) == 0
