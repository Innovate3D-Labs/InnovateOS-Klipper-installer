import pytest
import asyncio
from unittest.mock import Mock, patch
from app.hardware.board_manager import BoardManager
from app.hardware.firmware_manager import FirmwareManager
from app.hardware.installation_manager import InstallationManager
from app.config.printer_profiles import ProfileManager

@pytest.fixture
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def board_manager():
    manager = BoardManager()
    yield manager
    await manager.cleanup()

@pytest.fixture
async def firmware_manager():
    manager = FirmwareManager()
    yield manager
    await manager.cleanup()

@pytest.fixture
async def installation_manager():
    manager = InstallationManager()
    yield manager
    await manager.cleanup()

@pytest.fixture
def profile_manager():
    return ProfileManager()

@pytest.mark.integration
class TestHardwareIntegration:
    @pytest.mark.asyncio
    async def test_board_detection(self, board_manager):
        """Test board detection with real hardware"""
        boards = await board_manager.detect_boards()
        assert len(boards) > 0
        for board in boards:
            assert board.port is not None
            assert board.board_type is not None

    @pytest.mark.asyncio
    async def test_board_connection(self, board_manager):
        """Test board connection and communication"""
        boards = await board_manager.detect_boards()
        if not boards:
            pytest.skip("No boards detected")
        
        board = boards[0]
        connected = await board_manager.test_connection(board.port)
        assert connected is True

    @pytest.mark.asyncio
    async def test_firmware_download(self, firmware_manager):
        """Test firmware download and verification"""
        version = "v0.11.0"
        result = await firmware_manager.download_firmware(version)
        assert result is True
        assert firmware_manager.get_firmware_path(version).exists()

    @pytest.mark.asyncio
    async def test_firmware_build(self, firmware_manager):
        """Test firmware building for specific board"""
        version = "v0.11.0"
        board_config = {
            "mcu": "stm32f103",
            "build_flags": {
                "BOARD": "generic-stm32f103",
                "MCU": "stm32f103",
                "CLOCK_FREQ": "72000000"
            }
        }
        
        result = await firmware_manager.build_firmware(version, board_config)
        assert result is True
        assert firmware_manager.get_build_path(version, board_config["mcu"]).exists()

    @pytest.mark.asyncio
    async def test_complete_installation_flow(
        self,
        board_manager,
        firmware_manager,
        installation_manager,
        profile_manager
    ):
        """Test complete installation flow with real hardware"""
        # 1. Detect board
        boards = await board_manager.detect_boards()
        if not boards:
            pytest.skip("No boards detected")
        board = boards[0]
        
        # 2. Load profile
        profile = profile_manager.get_profile("ender3")
        assert profile is not None
        
        # 3. Start installation
        installation_id = await installation_manager.start_installation(
            board=board,
            profile=profile,
            version="v0.11.0"
        )
        assert installation_id is not None
        
        # 4. Monitor progress
        status = None
        for _ in range(60):  # Wait up to 60 seconds
            status = installation_manager.get_status(installation_id)
            if status.status in ["completed", "error"]:
                break
            await asyncio.sleep(1)
        
        assert status is not None
        assert status.status == "completed"
        assert status.progress == 100

@pytest.mark.performance
class TestHardwarePerformance:
    @pytest.mark.asyncio
    async def test_board_detection_performance(self, board_manager):
        """Test board detection performance"""
        start_time = asyncio.get_event_loop().time()
        await board_manager.detect_boards()
        duration = asyncio.get_event_loop().time() - start_time
        assert duration < 2.0  # Should complete within 2 seconds

    @pytest.mark.asyncio
    async def test_firmware_build_performance(self, firmware_manager):
        """Test firmware build performance"""
        version = "v0.11.0"
        board_config = {
            "mcu": "stm32f103",
            "build_flags": {
                "BOARD": "generic-stm32f103",
                "MCU": "stm32f103",
                "CLOCK_FREQ": "72000000"
            }
        }
        
        start_time = asyncio.get_event_loop().time()
        await firmware_manager.build_firmware(version, board_config)
        duration = asyncio.get_event_loop().time() - start_time
        assert duration < 300.0  # Should complete within 5 minutes

    @pytest.mark.asyncio
    async def test_concurrent_installations(
        self,
        board_manager,
        firmware_manager,
        installation_manager,
        profile_manager
    ):
        """Test handling multiple concurrent installations"""
        boards = await board_manager.detect_boards()
        if len(boards) < 2:
            pytest.skip("Need at least 2 boards for concurrent test")
        
        profile = profile_manager.get_profile("ender3")
        assert profile is not None
        
        # Start multiple installations
        installations = []
        for board in boards[:2]:
            installation_id = await installation_manager.start_installation(
                board=board,
                profile=profile,
                version="v0.11.0"
            )
            installations.append(installation_id)
        
        # Monitor all installations
        start_time = asyncio.get_event_loop().time()
        completed = 0
        while completed < len(installations):
            completed = 0
            for installation_id in installations:
                status = installation_manager.get_status(installation_id)
                if status.status in ["completed", "error"]:
                    completed += 1
            await asyncio.sleep(1)
            
            # Check timeout
            duration = asyncio.get_event_loop().time() - start_time
            assert duration < 600.0  # Should complete within 10 minutes
        
        # Verify all completed successfully
        for installation_id in installations:
            status = installation_manager.get_status(installation_id)
            assert status.status == "completed"
            assert status.progress == 100
