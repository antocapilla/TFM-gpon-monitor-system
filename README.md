# GPON Management System for Hospitality Environments

## Overview

This project is an advanced management and monitoring system for Gigabit Passive Optical Networks (GPON) tailored for hospitality environments. It provides a comprehensive solution for visualizing network topology, real-time monitoring, historical analysis, and network simulation, significantly improving operational efficiency and service quality in hotel settings.

## Key Features

- **Visual Space Management**: Intuitive interface for managing hotel buildings, floors, and ONT devices.
- **Real-time Monitoring**: Live dashboard showing key performance metrics of the GPON network.
- **Historical Data Analysis**: Detailed historical data views with customizable date ranges and metrics.
- **Connectivity Monitoring**: Specialized monitoring for WAN services and WLAN networks.
- **Network Simulation**: Tools for optimizing ONT placement and WiFi channel allocation.
- **Integration with Hotel Management Systems**: Seamless integration with existing hotel management software (SWH).

## Technologies Used

- **Frontend**: React.js
- **Backend**: FastAPI (Python)
- **Database**: MongoDB
- **Containerization**: Docker
- **API Documentation**: OpenAPI (Swagger)

## Prerequisites

- Docker and Docker Compose
- Node.js (for local development)
- Python 3.8+ (for local development)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/antocapilla/TFM.git
   cd gpon-management-system
   ```

2. Build and run the Docker containers:
   ```
   docker-compose up -d
   ```

3. Access the application:
   - Frontend: `http://localhost:3000`
   - Backend API: `http://localhost:8000`
   - API Documentation: `http://localhost:8000/docs`

## Development Setup

For local development without Docker:

1. Set up the backend:
   ```
   cd backend
   pip install -r requirements.txt
   uvicorn main:app --reload
   ```

2. Set up the frontend:
   ```
   cd frontend
   npm install
   npm start
   ```

## Configuration

- Environment variables can be set in the `.env` file for both backend and frontend configurations.
- Modify `docker-compose.yml` for container-specific settings.

## Usage

Refer to the user manual in the `docs` folder for detailed usage instructions.

## Contributing

Contributions are welcome! Please read our contributing guidelines and code of conduct before submitting pull requests.

## License

This project is licensed under the [MIT License](LICENSE).

## Acknowledgments

- Ekselans by ITS for their collaboration and SWH integration support.
- The open-source community for the various libraries and tools used in this project.