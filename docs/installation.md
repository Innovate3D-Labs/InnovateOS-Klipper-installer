# InnovateOS Klipper Installer - Installation Guide

## System Requirements

- Linux (Debian/Ubuntu recommended)
- Docker and Docker Compose
- Git
- USB port for printer connection

## Installation Methods

### Option 1: Using Docker (Recommended)

1. Install Docker and Docker Compose (if not already installed):
```bash
sudo apt-get update
sudo apt-get install docker.io docker-compose
```

2. Clone the repository:
```bash
git clone https://github.com/Innovate3D-Labs/InnovateOS-Klipper-installer.git
cd InnovateOS-Klipper-installer
```

3. Start the application:
```bash
sudo docker-compose up -d
```

4. Access the application:
- Web Interface: `http://localhost:3000`
- Backend API: `http://localhost:8000`

5. View logs (optional):
```bash
# All container logs
sudo docker-compose logs -f

# Backend logs only
sudo docker-compose logs -f backend

# Frontend logs only
sudo docker-compose logs -f frontend
```

6. Stop the application:
```bash
sudo docker-compose down
```

### Option 2: Development Mode

1. Clone the repository:
```bash
git clone https://github.com/Innovate3D-Labs/InnovateOS-Klipper-installer.git
cd InnovateOS-Klipper-installer
```

2. Start the backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

3. Start the frontend (in a new terminal):
```bash
cd frontend
npm install
npm run dev
```

4. Access the application:
- Web Interface: `http://localhost:3000`
- Backend API: `http://localhost:8000`

## Configuration

### Environment Variables

Backend (`.env`):
```bash
ENVIRONMENT=production
LOG_LEVEL=info
ALLOW_ORIGINS=http://localhost:3000
```

Frontend (`.env`):
```bash
VITE_API_BASE_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000/ws
```

## Troubleshooting

### Common Issues

1. Permission Denied
```bash
# Fix USB permissions
sudo usermod -a -G dialout $USER
sudo udevadm control --reload-rules
# Log out and back in for changes to take effect
```

2. Docker Issues
```bash
# Check Docker service
sudo systemctl status docker

# Restart Docker
sudo systemctl restart docker

# Check container status
sudo docker-compose ps
```

3. Port Conflicts
```bash
# Check if ports are in use
sudo lsof -i :3000
sudo lsof -i :8000

# Change ports in docker-compose.yml if needed
```

### Getting Help

- Open an issue on [GitHub](https://github.com/Innovate3D-Labs/InnovateOS-Klipper-installer/issues)
- Check the logs for detailed error messages
- Refer to the [FAQ](./faq.md)

## Security Notes

- Keep Docker and system packages updated
- Use strong passwords for web interface access
- Consider using HTTPS in production
- Regularly backup your configuration files

## Updating

1. Pull latest changes:
```bash
git pull origin main
```

2. Rebuild and restart containers:
```bash
sudo docker-compose down
sudo docker-compose build
sudo docker-compose up -d
```

## Uninstallation

1. Stop and remove containers:
```bash
sudo docker-compose down -v
```

2. Remove repository (optional):
```bash
cd ..
rm -rf InnovateOS-Klipper-installer
```
