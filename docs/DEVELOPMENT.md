# InnovateOS Klipper Installer - Developer Guide

## Project Structure

```
klipper-installer/
├── backend/
│   ├── app/
│   │   ├── routers/       # API endpoints
│   │   ├── services/      # Business logic
│   │   ├── models/        # Data models
│   │   └── utils/         # Helper functions
│   ├── tests/             # Backend tests
│   └── requirements.txt   # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/    # Vue components
│   │   ├── views/         # Page components
│   │   ├── store/         # Pinia stores
│   │   ├── router/        # Vue Router config
│   │   └── services/      # API clients
│   ├── tests/             # Frontend tests
│   └── package.json       # Node.js dependencies
└── docs/                  # Documentation
```

## Development Setup

### Prerequisites

1. Install development tools:
```bash
# Python tools
pip install black isort mypy pytest

# Node.js tools
npm install -g @vue/cli typescript
```

2. Configure IDE (VSCode recommended):
```json
{
  "editor.formatOnSave": true,
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.mypyEnabled": true,
  "typescript.updateImportsOnFileMove.enabled": "always",
  "vetur.format.defaultFormatter.html": "prettier"
}
```

### Development Workflow

1. Create a feature branch:
```bash
git checkout -b feature/your-feature
```

2. Run tests during development:
```bash
# Backend tests
cd backend
pytest -v --cov=app

# Frontend tests
cd frontend
npm run test:unit
```

3. Format code before committing:
```bash
# Backend
black app tests
isort app tests

# Frontend
npm run lint
```

4. Create pull request with:
   - Clear description of changes
   - Test coverage
   - Documentation updates
   - Migration steps if needed

## Architecture

### Backend

1. **FastAPI Application**
   - Modular router structure
   - Dependency injection
   - Pydantic models for validation
   - Async/await for I/O operations

2. **WebSocket Service**
   ```python
   class WebSocketManager:
       async def connect(self, websocket: WebSocket):
           await websocket.accept()
           self.active_connections.append(websocket)

       async def broadcast(self, message: dict):
           for connection in self.active_connections:
               await connection.send_json(message)
   ```

3. **Hardware Integration**
   ```python
   class HardwareManager:
       def detect_boards(self) -> List[Board]:
           # Board detection logic
           pass

       async def update_firmware(self, board: Board, firmware: Path):
           # Firmware update logic
           pass
   ```

### Frontend

1. **Vue Components**
   - Composition API
   - TypeScript support
   - Props validation
   - Event handling

2. **State Management**
   ```typescript
   export const useInstallationStore = defineStore('installation', {
     state: () => ({
       status: 'not_started',
       progress: 0
     }),
     actions: {
       async startInstallation() {
         // Installation logic
       }
     }
   })
   ```

3. **Router Guards**
   ```typescript
   router.beforeEach(async (to, from) => {
     const store = useInstallationStore()
     if (to.meta.requiresBoard && !store.selectedBoard) {
       return { name: 'select-board' }
     }
   })
   ```

## Testing

### Backend Tests

1. **Unit Tests**
   ```python
   def test_board_detection():
       manager = HardwareManager()
       boards = manager.detect_boards()
       assert len(boards) > 0
       assert all(isinstance(b, Board) for b in boards)
   ```

2. **Integration Tests**
   ```python
   async def test_websocket_connection():
       client = TestClient(app)
       with client.websocket_connect("/ws") as websocket:
           data = websocket.receive_json()
           assert data["type"] == "connection_established"
   ```

### Frontend Tests

1. **Component Tests**
   ```typescript
   describe('BoardSelector', () => {
     it('displays available boards', async () => {
       const wrapper = mount(BoardSelector)
       await flushPromises()
       expect(wrapper.findAll('.board-item')).toHaveLength(3)
     })
   })
   ```

2. **Store Tests**
   ```typescript
   describe('installationStore', () => {
     it('updates installation progress', () => {
       const store = useInstallationStore()
       store.updateProgress(50)
       expect(store.progress).toBe(50)
     })
   })
   ```

## API Integration

1. **API Client**
   ```typescript
   class APIClient {
     async detectBoards(): Promise<Board[]> {
       const response = await this.client.get('/api/boards/detect')
       return response.data
     }

     async startInstallation(config: InstallationConfig): Promise<string> {
       const response = await this.client.post('/api/install/start', config)
       return response.data.installation_id
     }
   }
   ```

2. **WebSocket Integration**
   ```typescript
   class WebSocketService {
     connect(): void {
       this.ws = new WebSocket(WS_URL)
       this.ws.onmessage = (event) => {
         const data = JSON.parse(event.data)
         this.handleMessage(data)
       }
     }

     private handleMessage(data: WebSocketMessage): void {
       switch (data.type) {
         case 'installation_progress':
           this.store.updateProgress(data.progress)
           break
       }
     }
   }
   ```

## Contributing

1. Follow coding standards:
   - PEP 8 for Python
   - Vue Style Guide
   - TypeScript best practices

2. Document your code:
   - Function docstrings
   - Component documentation
   - API documentation updates

3. Write tests:
   - Unit tests for new features
   - Integration tests for API endpoints
   - E2E tests for critical paths

4. Review process:
   - Code review by team members
   - CI/CD pipeline checks
   - Documentation review

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Vue 3 Documentation](https://v3.vuejs.org/)
- [Pinia Documentation](https://pinia.vuejs.org/)
- [TypeScript Documentation](https://www.typescriptlang.org/docs/)
