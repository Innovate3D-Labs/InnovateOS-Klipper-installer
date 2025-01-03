import pytest
import asyncio
import subprocess
from unittest.mock import patch, MagicMock, AsyncMock
from backend.installer import KlipperInstaller

@pytest.fixture
def installer():
    """Erstellt eine Testinstanz des KlipperInstallers"""
    return KlipperInstaller()

@pytest.mark.asyncio
async def test_install_dependencies_success(installer):
    """
    Test ob die Installation der Abhängigkeiten erfolgreich durchgeführt wird
    """
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        
        result = await installer.install_dependencies()
        
        assert result == True
        assert mock_run.call_count == 2

@pytest.mark.asyncio
async def test_install_dependencies_failure(installer):
    """
    Test ob Fehler bei der Installation der Abhängigkeiten korrekt behandelt werden
    """
    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(1, ['apt-get'])
        
        result = await installer.install_dependencies()
        
        assert result == False

@pytest.mark.asyncio
async def test_install_interface_fluidd(installer):
    """
    Test ob die Fluidd-Installation korrekt durchgeführt wird
    """
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(returncode=0)
        
        result = await installer.install_interface('fluidd')
        
        assert result == True
        assert mock_run.call_count == 2
        
        # Überprüfen ob der Download-Befehl korrekt ist
        first_call = mock_run.call_args_list[0][0][0]
        assert 'curl' == first_call[0]
        assert 'fluidd.zip' in first_call[2]  # URL enthält fluidd.zip

@pytest.mark.asyncio
async def test_configure_printer(installer):
    """
    Test ob die Druckerkonfiguration korrekt eingerichtet wird
    """
    with patch('subprocess.run') as mock_run, \
         patch('os.path.exists') as mock_exists, \
         patch('os.makedirs') as mock_makedirs:
        
        mock_exists.return_value = False
        
        result = await installer.configure_printer(
            'ender3',
            'config/ender3/printer.cfg'
        )
        
        assert result == True
        mock_makedirs.assert_called_once()
        mock_run.assert_called_once()

@pytest.mark.asyncio
async def test_websocket_callback():
    """
    Test ob der WebSocket-Callback korrekt funktioniert
    """
    mock_callback = AsyncMock()  # AsyncMock statt MagicMock
    installer = KlipperInstaller(websocket_callback=mock_callback)
    
    await installer.send_status("Test-Nachricht", 50)
    
    mock_callback.assert_called_once_with({
        "message": "Test-Nachricht",
        "progress": 50
    })
