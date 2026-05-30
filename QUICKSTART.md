# 🚀 Quick Start Guide

Get your AI Lead Finder running in 5 minutes!

## Step 1: Install Python

Make sure you have Python 3.10 or higher:

```bash
python --version
```

If not installed, download from [python.org](https://www.python.org/downloads/)

## Step 2: Get API Keys

### Bright Data (Required)
1. Go to [brightdata.com](https://brightdata.com)
2. Sign up for free trial
3. Navigate to Dashboard → API Access
4. Copy your API key
5. Go to Web Unlocker → Get proxy URL

### Google Gemini (Required - Free)
1. Visit [ai.google.dev](https://ai.google.dev)
2. Click "Get API Key"
3. Create new project
4. Copy API key

### OpenAI (Optional - Backup)
1. Visit [platform.openai.com](https://platform.openai.com)
2. Sign up and add payment method
3. Create API key

## Step 3: Setup Project

```bash
# Clone or download the project
cd ai-lead-finder

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Step 4: Configure API Keys

Create `.env` file:

```bash
# Windows
copy .env.example .env

# Mac/Linux
cp .env.example .env
```

Edit `.env` and add your keys:

```env
BRIGHT_DATA_API_KEY=your_bright_data_key_here
WEB_UNLOCKER_PROXY=http://brd-customer-xxx.zproxy.lum-superproxy.io:22225
GEMINI_API_KEY=your_gemini_key_here
```

## Step 5: Run the App

```bash
streamlit run app.py
```

Browser will open automatically at `http://localhost:8501`

## Step 6: Generate Your First Leads

1. Select **Real Estate** as niche
2. Enter **Islamabad** as city
3. Select **AI Chatbot** as service
4. Set lead count to **10**
5. Click **"Find Leads"**
6. Wait 2-3 minutes
7. Download CSV with results!

## 🎉 That's It!

You now have a working lead generation system!

## Next Steps

- Try different niches (Schools, Clinics, E-commerce)
- Increase lead count to 50-100
- Use the pitch messages to contact clients
- Track your outreach in the CSV file

## Need Help?

Check `lead_finder.log` for errors or see the full README.md

## Docker Quick Start (Alternative)

If you prefer Docker:

```bash
# Build image
docker-compose build

# Run container
docker-compose up

# Access at http://localhost:8501
```

## Common Issues

### "Configuration Error"
- Check your `.env` file exists
- Verify API keys are correct
- No spaces around `=` in `.env`

### "Module not found"
- Make sure virtual environment is activated
- Run `pip install -r requirements.txt` again

### "Connection timeout"
- Check internet connection
- Verify Bright Data proxy URL is correct
- Try increasing timeout in `.env`

## Cost Warning

- First 10-20 leads: ~$0.10-0.50
- 100 leads/day: ~$10-25/month
- Monitor your Bright Data usage dashboard

## Ready to Scale?

Once you get your first client, you can:
- Increase lead count to 100-500
- Run daily for fresh leads
- Target multiple cities
- Expand to more niches

**Happy Lead Hunting! 🎯**
