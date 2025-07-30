<p style="text-align:center;" align="center">
  <img align="center" src="https://raw.githubusercontent.com/Malith-Rukshan/geoip-api/refs/heads/main/api/static/img/logo.png" alt="GeoIP API" width="300px" height="300px"/>
</p>
<h1 align="center">GeoIP API</h1>
<div align='center'>

[![PyPI Package](https://img.shields.io/badge/PyPI-geoip--py-4B8BBE?logo=pypi&style=flat)](https://pypi.org/project/geoip-py/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Demo-009688?logo=fastapi&style=flat)](https://geoip-api.malith.dev/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&style=flat)](https://hub.docker.com/r/malithrukshan/geoip-api)
</div>

<h4 align="center">✨ A self-hosted IP geolocation API and Python package that works completely offline! 🚀</h4>

<div align="center">
  - Deploy your own private GeoIP service with complete control over your data and infrastructure -
  <br/>
  <sup><sub>Powered by MaxMind's GeoLite2 databases ツ</sub></sup>
</div>

## ✨ Features

- 🌍 Fast and reliable IP geolocation lookups
- 🔒 Self-hosted solution with no external API dependencies
- 🛠️ Dual functionality: Python package and REST API
- 🐳 Easy deployment with Docker and cloud platforms
- 📊 Get country, city, coordinates, timezone, ISP, and ASN data
- 🎨 Beautiful, interactive demo UI for testing
- 🚀 Built with FastAPI for high performance
- 📦 Automatic GeoLite2 database downloads and updates

## 🛠️ Usage

### Python Package

#### Installation

```bash
pip install geoip-py
```

#### Basic Usage

```python
from geoip_api import GeoIPLookup

# Initialize the lookup service (downloads DB files if needed)
lookup = GeoIPLookup(download_if_missing=True)

# Look up an IP address
result = lookup.lookup('8.8.8.8')
print(result)

# Output:
# {
#   "code": "US",
#   "country": "United States",
#   "city": "Mountain View",
#   "lat": 37.4056,
#   "lon": -122.0775,
#   "tz": "America/Los_Angeles",
#   "isp": "Google LLC",
#   "asn": 15169
# }
```

### REST API

✅ Demo : https://geoip-api.malith.dev/

#### Simple Endpoints

```
# Simple path parameter
https://your-domain.com/8.8.8.8

# Query parameter
https://your-domain.com/?ip=8.8.8.8
```

#### Standard API Endpoint

```
https://your-domain.com/api/v1/geoip/lookup/8.8.8.8
```

#### Response Format

```json
{
  "ip": "8.8.8.8",
  "code": "US",
  "country": "United States",
  "city": "Mountain View",
  "lat": 37.4056,
  "lon": -122.0775,
  "tz": "America/Los_Angeles",
  "isp": "Google LLC",
  "asn": 15169
}
```

## 📦 Deployment Options

### 🚀 Cloud Deployment

One-click deployment to popular platforms:

[![Deploy with heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)
[![Deploy to Netlify](https://www.netlify.com/img/deploy/button.svg)](https://app.netlify.com/start/deploy?repository=https://github.com/Malith-Rukshan/geoip-api)

[![Deploy to Railway](https://railway.app/button.svg)](https://railway.app/template/6zn6HZ)
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/Malith-Rukshan/geoip-api)

### 🐳 Docker

The fastest way to deploy your own GeoIP API:

```bash
docker pull malithrukshan/geoip-api
docker run -p 8000:8000 malithrukshan/geoip-api
```

Your API will be available at http://localhost:8000

### Docker Compose

Create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  geoip-api:
    image: malithrukshan/geoip-api
    ports:
      - "8000:8000"
    # volumes:
    #   - ./data:/app/api/db
    environment:
      - ENVIRONMENT=production
```

Then run:

```bash
docker-compose up -d
```

### 🔨 Building Docker Image Locally

If you want to build and run the Docker image from source:

1. Clone the repository
   ```bash
   git clone https://github.com/Malith-Rukshan/geoip-api.git
   cd geoip-api
   ```
2. Build the Docker image
   ```bash
   docker build -t geoip-api .
   ```
3. Run the container
   ```bash
   docker run -p 8000:8000 geoip-api
   ```
4. Access the API at http://localhost:8000

## 💻 Local Development

### Prerequisites

- Python 3.9+
- pip

### Setup

1. Clone the repository
   ```bash
   git clone https://github.com/Malith-Rukshan/geoip-api.git
   cd geoip-api
   ```

2. Install dependencies
   ```bash
   pip install -r requirements/dev.txt
   pip install -e .
   ```

3. Download GeoIP databases (optional, will be downloaded automatically if needed)
   ```bash
   mkdir -p ~/.geoip_api
   curl -L -o ~/.geoip_api/GeoLite2-City.mmdb https://github.com/P3TERX/GeoLite.mmdb/raw/download/GeoLite2-City.mmdb
   curl -L -o ~/.geoip_api/GeoLite2-ASN.mmdb https://github.com/P3TERX/GeoLite.mmdb/raw/download/GeoLite2-ASN.mmdb
   ```

4. Run the FastAPI application
   ```bash
   uvicorn api.main:app --reload
   ```

5. Visit http://localhost:8000 to see the API in action

### Running Tests

```bash
pytest
black --check src tests api
mypy src tests api
```

## 🌐 Use Cases

- **Security & Compliance**: Enhance security systems with IP-based threat detection while maintaining data sovereignty
- **Content Localization**: Deliver region-specific content based on visitor location without sharing user data
- **Analytics**: Analyze traffic patterns and user demographics with geographic data that remains within your infrastructure
- **Fraud Prevention**: Identify suspicious login attempts based on geographic anomalies
- **Development Environment**: Use a local GeoIP service in your development environment without external API dependencies

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Database License Notice

This project uses GeoLite2 data created by MaxMind, available from [https://www.maxmind.com](https://www.maxmind.com). The GeoLite2 databases are licensed under the Creative Commons Attribution-ShareAlike 4.0 International License.

## 🔧 Acknowledgements

- GeoLite2 databases provided by [MaxMind](https://www.maxmind.com)
- Mirror of GeoLite2 databases maintained by [P3TERX](https://github.com/P3TERX/GeoLite.mmdb)
- Built with [FastAPI](https://fastapi.tiangolo.com/) and [Python](https://www.python.org/)
- Powered by [geoip2](https://github.com/maxmind/GeoIP2-python) library

### 🇺🇳 Flags By : [Animated Country Flags](https://github.com/Malith-Rukshan/animated-country-flags)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🌟 Support and Community

If you found this project helpful, please give it a ⭐ on GitHub. This helps more developers discover the project! 🫶

## 📬 Contact

If you have any questions, feedback, or just want to say hi, you can reach out to me:

- Email: [hello@malith.dev](mailto:hello@malith.dev)
- GitHub: [@Malith-Rukshan](https://github.com/Malith-Rukshan)

🧑‍💻 Built with 💖 by [Malith Rukshan](https://github.com/Malith-Rukshan)