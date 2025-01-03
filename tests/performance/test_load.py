import pytest
import asyncio
import aiohttp
import time
import statistics
from typing import List, Dict
import json

class LoadTest:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.results: List[Dict] = []
        self.errors: List[str] = []

    async def run_scenario(self, scenario_func, concurrent_users: int, duration: int):
        """Run a test scenario with specified number of concurrent users"""
        start_time = time.time()
        tasks = []
        
        async with aiohttp.ClientSession() as session:
            while time.time() - start_time < duration:
                while len(tasks) < concurrent_users:
                    task = asyncio.create_task(scenario_func(session))
                    tasks.append(task)
                
                done, tasks = await asyncio.wait(
                    tasks,
                    return_when=asyncio.FIRST_COMPLETED
                )
                
                for task in done:
                    try:
                        result = await task
                        self.results.append(result)
                    except Exception as e:
                        self.errors.append(str(e))

    def get_statistics(self) -> Dict:
        """Calculate test statistics"""
        if not self.results:
            return {}
        
        response_times = [r['duration'] for r in self.results]
        return {
            'min_time': min(response_times),
            'max_time': max(response_times),
            'avg_time': statistics.mean(response_times),
            'median_time': statistics.median(response_times),
            'p95_time': statistics.quantiles(response_times, n=20)[18],
            'total_requests': len(self.results),
            'error_rate': len(self.errors) / len(self.results) if self.results else 1.0,
            'requests_per_second': len(self.results) / sum(response_times)
        }

class TestPerformance:
    @pytest.fixture
    def load_test(self):
        return LoadTest("http://localhost:8000")

    async def board_detection_scenario(self, session: aiohttp.ClientSession) -> Dict:
        """Test board detection performance"""
        start_time = time.time()
        
        async with session.get("/api/hardware/detect") as response:
            data = await response.json()
            duration = time.time() - start_time
            
            return {
                'operation': 'board_detection',
                'status': response.status,
                'duration': duration,
                'boards_found': len(data['boards'])
            }

    async def config_validation_scenario(self, session: aiohttp.ClientSession) -> Dict:
        """Test config validation performance"""
        config = {
            'name': 'Test Printer',
            'dimensions': {'x': 235, 'y': 235, 'z': 250},
            'speeds': {
                'max_velocity': 300,
                'max_accel': 3000,
                'max_z_velocity': 5,
                'max_z_accel': 100
            }
        }
        
        start_time = time.time()
        
        async with session.post(
            "/api/config/validate",
            json=config
        ) as response:
            data = await response.json()
            duration = time.time() - start_time
            
            return {
                'operation': 'config_validation',
                'status': response.status,
                'duration': duration,
                'is_valid': data['valid']
            }

    async def installation_scenario(self, session: aiohttp.ClientSession) -> Dict:
        """Test complete installation flow performance"""
        start_time = time.time()
        results = []
        
        # Step 1: Board Detection
        async with session.get("/api/hardware/detect") as response:
            data = await response.json()
            results.append({
                'step': 'board_detection',
                'duration': time.time() - start_time,
                'status': response.status
            })
            
            if not data['boards']:
                raise Exception("No boards detected")
            board = data['boards'][0]
        
        # Step 2: Start Installation
        install_data = {
            'board': board,
            'config': {
                'name': 'Test Printer',
                'dimensions': {'x': 235, 'y': 235, 'z': 250}
            }
        }
        
        async with session.post(
            "/api/installation/start",
            json=install_data
        ) as response:
            data = await response.json()
            results.append({
                'step': 'installation_start',
                'duration': time.time() - start_time,
                'status': response.status
            })
            
            installation_id = data['installation_id']
        
        # Step 3: Monitor Installation
        while True:
            async with session.get(
                f"/api/installation/{installation_id}/status"
            ) as response:
                data = await response.json()
                if data['status'] in ['completed', 'error']:
                    break
                await asyncio.sleep(1)
        
        total_duration = time.time() - start_time
        
        return {
            'operation': 'complete_installation',
            'status': 'success' if data['status'] == 'completed' else 'error',
            'duration': total_duration,
            'steps': results
        }

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_board_detection_load(self, load_test):
        """Test board detection under load"""
        await load_test.run_scenario(
            self.board_detection_scenario,
            concurrent_users=10,
            duration=60
        )
        
        stats = load_test.get_statistics()
        assert stats['p95_time'] < 2.0  # 95% of requests should complete within 2 seconds
        assert stats['error_rate'] < 0.01  # Less than 1% error rate

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_config_validation_load(self, load_test):
        """Test config validation under load"""
        await load_test.run_scenario(
            self.config_validation_scenario,
            concurrent_users=50,
            duration=60
        )
        
        stats = load_test.get_statistics()
        assert stats['p95_time'] < 0.5  # 95% of requests should complete within 500ms
        assert stats['error_rate'] < 0.01  # Less than 1% error rate

    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_installation_load(self, load_test):
        """Test multiple concurrent installations"""
        await load_test.run_scenario(
            self.installation_scenario,
            concurrent_users=5,
            duration=600
        )
        
        stats = load_test.get_statistics()
        assert stats['p95_time'] < 300  # 95% of installations should complete within 5 minutes
        assert stats['error_rate'] < 0.05  # Less than 5% error rate

    def test_memory_usage(self):
        """Test memory usage during operation"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Run some operations
        asyncio.run(self.test_installation_load(LoadTest("http://localhost:8000")))
        
        final_memory = process.memory_info().rss
        memory_increase = (final_memory - initial_memory) / 1024 / 1024  # MB
        
        assert memory_increase < 500  # Should not increase by more than 500MB
