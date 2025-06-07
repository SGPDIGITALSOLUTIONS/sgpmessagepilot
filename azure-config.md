# Azure Deployment Guide for WebStudio

## 🚀 Quick Start Deployment

### Prerequisites
- Azure subscription
- Azure CLI installed
- Git repository (GitHub recommended)

### 1. Create Azure Resources

#### Option A: Azure CLI (Recommended)
```bash
# Login to Azure
az login

# Create resource group
az group create --name rg-sgp-messagepilot --location "UK South"

# Create App Service Plan (B1 or higher recommended)
az appservice plan create \
    --name plan-sgp-messagepilot \
    --resource-group rg-sgp-messagepilot \
    --sku B1 \
    --is-linux

# Create Web App
az webapp create \
    --resource-group rg-sgp-messagepilot \
    --plan plan-sgp-messagepilot \
    --name sgp-messagepilot \
    --runtime "PYTHON|3.9" \
    --deployment-local-git
```

#### Option B: Azure Portal
1. Go to Azure Portal → Create Resource → Web App
2. Fill in details:
   - **Name**: `sgp-messagepilot` (or your preferred name)
   - **Runtime**: Python 3.9
   - **OS**: Linux
   - **Region**: UK South
   - **Plan**: Basic B1 or higher

### 2. Configure Application Settings

Set these environment variables in Azure Portal → App Service → Configuration:

```bash
# Required Settings
FLASK_ENV=production
PYTHONPATH=/home/site/wwwroot
SCM_DO_BUILD_DURING_DEPLOYMENT=true
ENABLE_ORYX_BUILD=true

# Security Settings (Optional but recommended)
HTTPS_ONLY=true
MIN_TLS_VERSION=1.2

# Custom Domain (if using)
WEBSITE_HTTPLOGGING_RETENTION_DAYS=7
```

### 3. Deploy Your Code

#### Option A: GitHub Actions (Recommended)
1. Fork/clone this repository
2. Go to Azure Portal → Your App Service → Deployment Center
3. Select "GitHub" as source
4. Authorize and select your repository
5. Azure will automatically create workflow file
6. Or use the provided `.github/workflows/azure-deploy.yml`

#### Option B: Azure DevOps
1. Import repository to Azure DevOps
2. Use the provided `azure-pipelines.yml`
3. Create service connection to Azure
4. Run pipeline

#### Option C: Local Git Deployment
```bash
# Add Azure remote
git remote add azure https://<username>@sgp-messagepilot.scm.azurewebsites.net:443/sgp-messagepilot.git

# Deploy
git push azure main
```

## 🔧 Configuration Details

### App Service Configuration

#### Startup Command
Azure will automatically detect and use: `gunicorn --bind=0.0.0.0 --workers=4 startup:app`

#### File Structure Expected
```
/home/site/wwwroot/
├── app/
├── startup.py          # Main application entry
├── requirements.txt    # Python dependencies
├── web.config         # IIS configuration
├── runtime.txt        # Python version
└── .deployment       # Deployment config
```

### Environment Variables
Set in Azure Portal → Configuration → Application Settings:

| Setting | Value | Description |
|---------|-------|-------------|
| `FLASK_ENV` | `production` | Flask environment |
| `PYTHONPATH` | `/home/site/wwwroot` | Python path |
| `SCM_DO_BUILD_DURING_DEPLOYMENT` | `true` | Enable build |
| `ENABLE_ORYX_BUILD` | `true` | Use Oryx build |

### Custom Domain Setup (Optional)
1. Azure Portal → Your App Service → Custom domains
2. Add custom domain
3. Add DNS records to your domain provider
4. Configure SSL certificate (free with App Service Certificate)

## 📊 Monitoring & Logging

### Application Insights (Recommended)
```bash
# Create Application Insights
az monitor app-insights component create \
    --app sgp-messagepilot-insights \
    --location "UK South" \
    --resource-group rg-sgp-messagepilot \
    --application-type web
```

Add to your Flask app:
```python
from applicationinsights.flask.ext import AppInsights

app = Flask(__name__)
appinsights = AppInsights(app)
```

### Log Streaming
```bash
# View live logs
az webapp log tail --name sgp-messagepilot --resource-group rg-sgp-messagepilot
```

## 🔒 Security Considerations

### SSL/TLS
- Enable HTTPS Only in Azure Portal
- Set minimum TLS version to 1.2
- Use Azure's free SSL certificate or bring your own

### Access Control
```bash
# Enable authentication (optional)
az webapp auth update \
    --name sgp-messagepilot \
    --resource-group rg-sgp-messagepilot \
    --enabled true \
    --action LoginWithAzureActiveDirectory
```

### Content Security Policy
Already configured in `web.config`:
- X-Frame-Options: DENY
- X-Content-Type-Options: nosniff
- Strict-Transport-Security: enabled
- Custom CSP for Tailwind CSS

## 💰 Cost Optimization

### Recommended SKUs
- **Development**: F1 (Free tier)
- **Production**: B1 (Basic) - £13.14/month
- **High Traffic**: S1 (Standard) - £56.58/month

### Auto-scaling (S1 and above)
```bash
az monitor autoscale create \
    --resource-group rg-sgp-messagepilot \
    --resource sgp-messagepilot \
    --resource-type Microsoft.Web/sites \
    --name sgp-messagepilot-autoscale \
    --min-count 1 \
    --max-count 3 \
    --count 1
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Application Won't Start
```bash
# Check logs
az webapp log tail --name sgp-messagepilot --resource-group rg-sgp-messagepilot

# Common fixes:
# - Ensure startup.py exists and is correct
# - Check requirements.txt has all dependencies
# - Verify Python version matches runtime.txt
```

#### 2. 500 Internal Server Error
- Check Application Insights or logs
- Ensure Flask app factory pattern is correct
- Verify environment variables are set

#### 3. Static Files Not Loading
- Ensure CSS/JS files are in correct paths
- Check CSP headers in web.config
- Verify CDN resources (Tailwind CSS) are accessible

#### 4. Slow Performance
- Upgrade to higher SKU
- Enable Application Insights for performance monitoring
- Consider adding Azure CDN for static assets

### Debugging Commands
```bash
# SSH into container (Linux App Service)
az webapp ssh --name sgp-messagepilot --resource-group rg-sgp-messagepilot

# Check Python version
python --version

# Test app locally
python startup.py

# Check installed packages
pip list
```

## 🔄 Maintenance

### Regular Tasks
1. **Monitor Application Insights** for errors and performance
2. **Review logs** weekly for any issues
3. **Update dependencies** monthly for security
4. **Backup data** if you add database later
5. **Review costs** monthly

### Updates
```bash
# Update from Git
git push azure main

# Or redeploy from Azure Portal
# Portal → Deployment Center → Sync
```

## 📞 Support

### Azure Resources
- [Azure App Service Documentation](https://docs.microsoft.com/en-us/azure/app-service/)
- [Python on Azure App Service](https://docs.microsoft.com/en-us/azure/app-service/configure-language-python)
- [Azure Support Portal](https://portal.azure.com/#blade/Microsoft_Azure_Support/HelpAndSupportBlade)

### SGP Digital Solutions
For application-specific issues, contact SGP Digital Solutions support.

---

**Ready to deploy!** Follow the Quick Start section above to get your WhatsApp tool running on Azure in minutes. 