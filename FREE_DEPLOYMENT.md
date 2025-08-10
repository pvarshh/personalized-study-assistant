# 🚀 Free Deployment Guide

## Option 1: Streamlit Cloud (Recommended - 100% Free)

### Prerequisites
- GitHub account
- Google Gemini API key

### Step-by-Step Deployment

#### 1. Push to GitHub
```bash
# Create a new repository on GitHub (public or private)
# Then push your code:
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

#### 2. Deploy on Streamlit Cloud
1. **Visit**: [share.streamlit.io](https://share.streamlit.io)
2. **Sign in** with your GitHub account
3. **Click "New app"**
4. **Select your repository** and branch (main)
5. **Set main file path**: `app.py`
6. **Advanced settings**:
   - Python version: `3.10`
   - Requirements file: `requirements.txt`

#### 3. Configure Secrets
In the Streamlit Cloud dashboard:
1. **Go to your app settings**
2. **Navigate to "Secrets"**
3. **Add the following**:
   ```toml
   GEMINI_API_KEY = "your_actual_api_key_here"
   ```

#### 4. Deploy!
- **Click "Deploy"**
- **Wait 2-5 minutes** for initial deployment
- **Your app will be live** at: `https://your-repo-name.streamlit.app`

### ✅ Benefits of Streamlit Cloud
- **100% Free** for public repos
- **Automatic deployments** on git push
- **Custom domain** available
- **Built-in secrets management**
- **Community support**

---

## Option 2: Hugging Face Spaces (Free)

### Step-by-Step
1. **Create account** at [huggingface.co](https://huggingface.co)
2. **Create new Space**:
   - SDK: Streamlit
   - Hardware: CPU Basic (free)
3. **Upload your files** or connect GitHub
4. **Add secrets** in Space settings:
   ```
   GEMINI_API_KEY=your_api_key
   ```
5. **Space automatically deploys**

---

## Option 3: Railway (Free Tier)

### Step-by-Step
1. **Visit**: [railway.app](https://railway.app)
2. **Connect GitHub** account
3. **Deploy from GitHub** repo
4. **Add environment variables**:
   - `GEMINI_API_KEY=your_key`
5. **App deploys automatically**

### Free Tier Limits
- **$5/month credit** (usually sufficient)
- **Sleep after 1 hour** of inactivity
- **Custom domain** available

---

## Option 4: Render (Free)

### Step-by-Step
1. **Visit**: [render.com](https://render.com)
2. **Connect GitHub** account
3. **Create Web Service**:
   - Build: `pip install -r requirements.txt`
   - Start: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`
4. **Add environment variables**
5. **Deploy**

### Free Tier Limits
- **750 hours/month** free
- **Sleep after 15 minutes** of inactivity
- **Spins up in ~30 seconds**

---

## 🎯 Recommended: Streamlit Cloud

**Why Streamlit Cloud?**
- ✅ **Purpose-built** for Streamlit apps
- ✅ **No sleep/wake delays**
- ✅ **Easiest deployment**
- ✅ **Best performance**
- ✅ **Community showcase**

## 🔑 Getting Your Google Gemini API Key

1. **Visit**: [Google AI Studio](https://makersuite.google.com/app/apikey)
2. **Sign in** with Google account
3. **Create API key**
4. **Copy the key** (keep it secure!)

## 🚨 Important Notes

### Security
- **Never commit API keys** to git
- **Use secrets management** in deployment platform
- **Keep your API key private**

### Performance
- **Free tiers have limitations**
- **Streamlit Cloud is most reliable**
- **Consider upgrading for production use**

## ✅ Quick Checklist

- [ ] Code committed to git
- [ ] GitHub repository created
- [ ] Google Gemini API key obtained
- [ ] Streamlit Cloud account created
- [ ] App deployed and tested
- [ ] Secrets configured
- [ ] App is accessible online

## 🆘 Troubleshooting

### Common Issues
1. **Import errors**: Check requirements.txt
2. **API errors**: Verify API key in secrets
3. **Memory issues**: Use free tier limits wisely
4. **Slow startup**: Normal for free tiers

### Support
- **Streamlit Community**: [discuss.streamlit.io](https://discuss.streamlit.io)
- **Documentation**: [docs.streamlit.io](https://docs.streamlit.io)

---

**Ready to deploy your AI Study Assistant for free! 🎓🚀**
