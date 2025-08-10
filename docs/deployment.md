# Deployment Guide

This guide covers various deployment options for the Personalized Study Assistant.

## 🚀 Quick Deployment Options

### 1. Local Development

**Requirements**: Python 3.8+, Google Gemini API key

```bash
# Clone and setup
git clone <repository-url>
cd ai-trials
make install

# Configure environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# Run application
make run
```

Access at: `http://localhost:8501`

### 2. Docker Deployment

**Requirements**: Docker, Docker Compose

```bash
# Build and run with Docker Compose
docker-compose up -d

# Or build manually
docker build -t study-assistant .
docker run -p 8501:8501 -e GEMINI_API_KEY=your_key study-assistant
```

### 3. Streamlit Cloud

**Requirements**: GitHub repository, Streamlit Cloud account

1. Push code to GitHub
2. Connect repository to Streamlit Cloud
3. Set environment variables in Streamlit Cloud dashboard
4. Deploy automatically

## 🔧 Environment Configuration

### Required Environment Variables

```env
GEMINI_API_KEY=your_google_gemini_api_key
```

### Optional Configuration

```env
# Model Settings
GEMINI_MODEL=gemini-2.5-pro
TEMPERATURE=0.1
MAX_TOKENS=8192

# Vector Store
CHUNK_SIZE=1000
CHUNK_OVERLAP=100
VECTOR_STORE_PATH=./chroma_db

# Application
LOG_LEVEL=INFO
```

## ☁️ Cloud Platform Deployment

### Heroku

1. **Prepare for Heroku**:
   ```bash
   # Create Procfile
   echo "web: streamlit run app.py --server.port=\$PORT --server.address=0.0.0.0" > Procfile
   
   # Create runtime.txt
   echo "python-3.10.12" > runtime.txt
   ```

2. **Deploy**:
   ```bash
   heroku create your-app-name
   heroku config:set GEMINI_API_KEY=your_key
   git push heroku main
   ```

### AWS EC2

1. **Launch EC2 instance** (Ubuntu 20.04+)
2. **Setup environment**:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-venv git
   git clone <your-repo>
   cd ai-trials
   make install
   ```

3. **Configure systemd service**:
   ```bash
   sudo nano /etc/systemd/system/study-assistant.service
   ```
   
   ```ini
   [Unit]
   Description=Study Assistant
   After=network.target
   
   [Service]
   Type=exec
   User=ubuntu
   WorkingDirectory=/home/ubuntu/ai-trials
   Environment=PATH=/home/ubuntu/ai-trials/env/bin
   EnvironmentFile=/home/ubuntu/ai-trials/.env
   ExecStart=/home/ubuntu/ai-trials/env/bin/streamlit run app.py --server.port=8501
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```

4. **Start service**:
   ```bash
   sudo systemctl enable study-assistant
   sudo systemctl start study-assistant
   ```

### Google Cloud Platform

1. **Create App Engine app**:
   ```yaml
   # app.yaml
   runtime: python310
   
   env_variables:
     GEMINI_API_KEY: "your_key"
   
   automatic_scaling:
     min_instances: 1
     max_instances: 10
   ```

2. **Deploy**:
   ```bash
   gcloud app deploy
   ```

### Azure Container Instances

```bash
# Build and push to Azure Container Registry
az acr build --registry myregistry --image study-assistant .

# Deploy to Container Instances
az container create \
  --resource-group myResourceGroup \
  --name study-assistant \
  --image myregistry.azurecr.io/study-assistant \
  --port 8501 \
  --environment-variables GEMINI_API_KEY=your_key
```

## 🔒 Security Considerations

### Production Security

1. **Environment Variables**: Never commit API keys to version control
2. **HTTPS**: Use SSL/TLS certificates in production
3. **Authentication**: Implement user authentication if needed
4. **Rate Limiting**: Configure rate limiting for API calls
5. **Input Validation**: Ensure robust input sanitization

### Example Nginx Configuration

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## 📊 Monitoring and Logging

### Application Logs

Configure logging levels:
```env
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
```

### Health Checks

The application includes built-in health checks:
- Docker: `/_stcore/health`
- Custom endpoint: Monitor ChromaDB and API connectivity

### Monitoring Setup

```bash
# Install monitoring tools
pip install prometheus-client grafana-dashboard

# Add to requirements.txt
echo "prometheus-client>=0.17.0" >> requirements.txt
```

## 🔄 Continuous Deployment

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Streamlit Cloud
        run: |
          # Streamlit Cloud auto-deploys on push
          echo "Deployment triggered"
```

### GitLab CI/CD

```yaml
# .gitlab-ci.yml
stages:
  - test
  - deploy

test:
  stage: test
  script:
    - pip install -r requirements.txt
    - python -m pytest tests/

deploy:
  stage: deploy
  script:
    - docker build -t study-assistant .
    - docker push $CI_REGISTRY_IMAGE
  only:
    - main
```

## 🚨 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure `src/` directory is in Python path
2. **API Key Issues**: Verify GEMINI_API_KEY is set correctly
3. **Memory Issues**: Monitor ChromaDB disk usage
4. **Port Conflicts**: Change port with `--server.port=8502`

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
streamlit run app.py
```

### Performance Optimization

1. **Resource Limits**: Set appropriate memory/CPU limits
2. **Caching**: Enable Streamlit caching for better performance
3. **Database**: Optimize ChromaDB collection settings
4. **Load Balancing**: Use multiple instances for high traffic

## 📋 Deployment Checklist

- [ ] Environment variables configured
- [ ] API keys secured
- [ ] Database initialized
- [ ] SSL certificates installed (production)
- [ ] Monitoring setup
- [ ] Backup strategy implemented
- [ ] Health checks configured
- [ ] Documentation updated
- [ ] Testing completed

## 🆘 Support

For deployment issues:
1. Check application logs
2. Verify environment configuration
3. Test API connectivity
4. Review resource usage
5. Contact support if needed

---

**Happy Deploying! 🚀**
