import pytest
from playwright.sync_api import Page, expect
from typing import Generator
import time

@pytest.fixture(scope="function")
def setup_installation(page: Page) -> Generator:
    # Navigate to home page
    page.goto("/")
    
    # Wait for initial load
    page.wait_for_selector("text=Welcome to InnovateOS")
    
    yield
    
    # Cleanup after test
    page.evaluate("window.localStorage.clear()")

def test_complete_installation_flow(page: Page, setup_installation):
    """Test complete installation flow from start to finish"""
    
    # Step 1: Board Selection
    page.click("text=Get Started")
    expect(page).to_have_url("/board-selection")
    
    # Wait for board detection
    page.wait_for_selector(".board-list")
    
    # Select first available board
    page.click(".board-item >> nth=0")
    page.click("text=Continue")
    
    # Step 2: Configuration
    expect(page).to_have_url("/configuration")
    
    # Select printer profile
    page.click("select[name='profile']")
    page.click("text=Ender 3")
    
    # Fill basic settings
    page.fill("#printerName", "My Ender 3")
    
    # Fill dimensions
    page.fill("#bedSizeX", "235")
    page.fill("#bedSizeY", "235")
    page.fill("#bedSizeZ", "250")
    
    # Fill speeds
    page.fill("#maxVelocity", "300")
    page.fill("#maxAccel", "3000")
    page.fill("#maxZVelocity", "5")
    page.fill("#maxZAccel", "100")
    
    # Enable features
    page.check("#bedMesh")
    page.check("#inputShaping")
    
    # Preview config
    page.click("text=Preview")
    page.wait_for_selector(".config-preview")
    
    # Save configuration
    page.click("text=Save Configuration")
    
    # Step 3: Installation
    expect(page).to_have_url("/installation")
    
    # Wait for installation to complete (with timeout)
    success = False
    start_time = time.time()
    timeout = 600  # 10 minutes
    
    while time.time() - start_time < timeout:
        if page.query_selector("text=Installation Complete"):
            success = True
            break
        if page.query_selector("text=Installation Error"):
            raise Exception("Installation failed")
        time.sleep(1)
    
    assert success, "Installation did not complete within timeout"
    
    # Step 4: Complete
    page.click("text=Continue")
    expect(page).to_have_url("/complete")
    
    # Verify success message
    expect(page.locator("text=Your printer is ready")).to_be_visible()

def test_error_recovery_flow(page: Page, setup_installation):
    """Test error recovery during installation"""
    
    # Setup: Get to installation page
    page.goto("/board-selection")
    page.click(".board-item >> nth=0")
    page.click("text=Continue")
    
    # Fill minimum required config
    page.fill("#printerName", "Test Printer")
    page.click("text=Save Configuration")
    
    expect(page).to_have_url("/installation")
    
    # Wait for error (simulated by backend)
    page.wait_for_selector("text=Installation Error", timeout=30000)
    
    # Verify error display
    error_message = page.locator(".error-message")
    expect(error_message).to_be_visible()
    
    # Test retry functionality
    page.click("text=Retry")
    
    # Verify installation restarts
    expect(page.locator("text=Installing Klipper")).to_be_visible()
    
    # Test cancel functionality
    page.click("text=Cancel")
    expect(page).to_have_url("/board-selection")

def test_config_backup_restore(page: Page, setup_installation):
    """Test configuration backup and restore"""
    
    # Setup: Create initial config
    page.goto("/configuration")
    
    # Fill configuration
    page.fill("#printerName", "Backup Test")
    page.fill("#bedSizeX", "235")
    page.fill("#bedSizeY", "235")
    page.fill("#bedSizeZ", "250")
    
    # Save configuration
    page.click("text=Save Configuration")
    
    # Backup configuration
    page.click("text=Backup Configuration")
    
    # Download should trigger automatically
    page.wait_for_download()
    
    # Clear configuration
    page.click("text=Reset")
    
    # Restore configuration
    with page.expect_file_chooser() as fc_info:
        page.click("text=Restore from Backup")
    file_chooser = fc_info.value
    
    # Select backup file (need to implement file selection in test environment)
    # file_chooser.set_files("path/to/backup.json")
    
    # Verify restored values
    expect(page.locator("#printerName")).to_have_value("Backup Test")
    expect(page.locator("#bedSizeX")).to_have_value("235")
    expect(page.locator("#bedSizeY")).to_have_value("235")
    expect(page.locator("#bedSizeZ")).to_have_value("250")

def test_performance_metrics(page: Page, setup_installation):
    """Test performance metrics during installation"""
    
    # Setup: Get to installation page
    page.goto("/installation")
    
    # Start performance measurement
    metrics = []
    
    def handle_metrics(route, request):
        metrics.append({
            'timestamp': time.time(),
            'url': request.url,
            'method': request.method,
            'resource_type': request.resource_type
        })
        route.continue_()
    
    page.route("**/*", handle_metrics)
    
    # Run installation
    page.click("text=Start Installation")
    
    # Wait for completion
    page.wait_for_selector("text=Installation Complete", timeout=600000)
    
    # Analyze metrics
    api_calls = [m for m in metrics if m['resource_type'] == 'fetch']
    websocket_messages = [m for m in metrics if m['resource_type'] == 'websocket']
    
    # Verify performance requirements
    assert len(api_calls) < 100, "Too many API calls"
    assert len(websocket_messages) < 1000, "Too many WebSocket messages"
    
    # Verify timing requirements
    start_time = metrics[0]['timestamp']
    end_time = metrics[-1]['timestamp']
    total_duration = end_time - start_time
    
    assert total_duration < 600, "Installation took too long"
