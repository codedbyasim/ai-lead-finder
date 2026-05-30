# 🤖 AI Freelance Lead Finder System

A powerful lead generation system for AI and web development freelancers to discover potential clients who need services like AI chatbots, web scraping, automation, and dashboards.

## 🎯 Features

- **Automated Lead Discovery**: Search Google/Bing for businesses using Bright Data SERP API
- **Contact Extraction**: Automatically extract emails, phones, and WhatsApp numbers
- **AI-Powered Scoring**: Score leads (0-100) using Google Gemini or GPT-4o Mini
- **Problem Detection**: AI identifies what services each business needs
- **Personalized Pitches**: Auto-generate pitch messages in Urdu and English
- **CSV Export**: Export all leads with complete details
- **User-Friendly UI**: Beautiful Streamlit interface

## 🎯 Target Niches

- Real Estate Agencies (Islamabad, Rawalpindi, Lahore, Karachi)
- Private Schools & Academies
- Clinics & Hospitals
- E-commerce Stores
- Software Houses & Digital Agencies

## 🛠️ Tech Stack

- **Backend**: Python 3.10+, FastAPI
- **Frontend**: Streamlit
- **Data Collection**: Bright Data SERP API + Web Unlocker
- **AI**: Google Gemini 1.5 Flash (primary) / GPT-4o Mini (fallback)
- **Data Processing**: Pandas, BeautifulSoup4
- **Output**: CSV export

## 📋 Prerequisites

- Python 3.10 or higher
- Bright Data account with API access
- Google Gemini API key OR OpenAI API key
- Internet connection

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/codedbyasim/ai-lead-finder
cd ai-lead-finder
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Copy example file
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac
```

Edit `.env` and add your API keys:

```env
# Bright Data API Configuration
BRIGHT_DATA_API_KEY=your_bright_data_api_key_here
SERP_ENDPOINT=https://api.brightdata.com/serp
WEB_UNLOCKER_PROXY=http://brd-customer-xxx.zproxy.lum-superproxy.io:22225

# AI API Keys (at least one required)
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# System Configuration (optional)
REQUEST_TIMEOUT=30
MAX_CONCURRENT_REQUESTS=5
MAX_RETRIES=3
LOG_LEVEL=INFO
```

### 5. Get API Keys

#### Bright Data
1. Sign up at [brightdata.com](https://brightdata.com)
2. Get your API key from the dashboard
3. Set up Web Unlocker proxy credentials

#### Google Gemini
1. Visit [ai.google.dev](https://ai.google.dev)
2. Create an API key
3. Free tier available

#### OpenAI (Optional)
1. Visit [platform.openai.com](https://platform.openai.com)
2. Create an API key
3. Pay-per-use pricing

## 🎮 Usage

### Run the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

### Using the Interface

1. **Select Business Niche**: Choose from Real Estate, Schools, Clinics, E-commerce, or Software Houses
2. **Enter City**: Target city (e.g., Islamabad, Lahore, Karachi)
3. **Select Services**: Choose services you offer (AI Chatbot, Web Scraping, etc.)
4. **Set Lead Count**: How many leads to generate (10-100)
5. **Choose Language**: Urdu or English for pitch messages
6. **Click "Find Leads"**: System will search, extract, and analyze
7. **Review Results**: See scored leads with contact info and pitch messages
8. **Download CSV**: Export all leads for tracking

### CSV Output Format

The exported CSV includes:

| Column | Description |
|--------|-------------|
| business_name | Business name |
| website_url | Website URL |
| niche | Business category |
| city | Location |
| email | Email address |
| phone | Phone number |
| whatsapp | WhatsApp number |
| has_chatbot | Chatbot detected (True/False) |
| problem_detected | AI-identified problem |
| suggested_service | Recommended service |
| pitch_message | Personalized pitch |
| lead_score | AI score (0-100) |
| score_category | High/Medium/Low |
| technologies | Detected technologies |
| services | Business services |

## 📊 How It Works

### Pipeline Flow

```
User Input → Search Queries → SERP API → Business URLs
    ↓
Web Unlocker → HTML Content → Contact Extraction
    ↓
AI Analysis → Lead Scoring → Pitch Generation
    ↓
CSV Export → Download
```

### Scoring Criteria

The AI scores leads based on:
- **Chatbot Presence**: +20 points if missing
- **Online Booking**: +15 points if missing
- **Contact Visibility**: +10 points if poor
- **Technology Stack**: +15 points if outdated
- **Niche Match**: +20 points for strong match
- **Website Quality**: +10 points for active site
- **Service Diversity**: +10 points for multiple services

### Score Categories

- **High (70-100)**: Priority leads, high conversion potential
- **Medium (40-69)**: Good leads, worth contacting
- **Low (0-39)**: Lower priority, may not need services

## 🐳 Docker Deployment

### Build Docker Image

```bash
docker build -t ai-lead-finder .
```

### Run Container

```bash
docker run -p 8501:8501 --env-file .env ai-lead-finder
```

Access at `http://localhost:8501`

## 📁 Project Structure

```
ai-lead-finder/
├── app.py                  # Streamlit UI
├── pipeline.py             # Main orchestrator
├── serp_collector.py       # SERP API integration
├── web_scraper.py          # Web scraping
├── ai_scorer.py            # AI scoring
├── exporter.py             # CSV export
├── config.py               # Configuration
├── utils.py                # Utilities
├── requirements.txt        # Dependencies
├── .env.example            # Environment template
├── .gitignore              # Git ignore rules
├── Dockerfile              # Docker config
└── README.md               # This file
```

## 🔧 Configuration

### Adjust Concurrent Requests

Edit `.env`:
```env
MAX_CONCURRENT_REQUESTS=5  # Increase for faster processing
```

### Change Timeout

```env
REQUEST_TIMEOUT=30  # Seconds per request
```

### Retry Attempts

```env
MAX_RETRIES=3  # Number of retry attempts
```

## 🐛 Troubleshooting

### "Configuration Error: API key missing"
- Ensure `.env` file exists
- Check API keys are correctly set
- Restart the application

### "Timeout fetching URL"
- Increase `REQUEST_TIMEOUT` in `.env`
- Check internet connection
- Verify Web Unlocker proxy is correct

### "No leads found"
- Try different search terms
- Increase lead count
- Check different cities
- Verify SERP API is working

### "AI scoring failed"
- Check Gemini/OpenAI API keys
- Verify API quota/credits
- Check API key permissions

## 💰 Cost Estimates

### Monthly Costs (100 leads/day)

| Service | Cost |
|---------|------|
| Bright Data SERP API | $3-5 |
| Bright Data Web Unlocker | $5-10 |
| Google Gemini API | Free - $7 |
| **Total** | **$10-25/month** |

**Note**: Bright Data offers free trials and startup discounts. One client can recover these costs.

## 📈 Performance

- **50 leads**: ~10 minutes
- **100 leads**: ~20 minutes
- **Concurrent processing**: 5 URLs simultaneously
- **Success rate**: 70-85% (depends on website accessibility)

## 🔒 Security & Ethics

- ✅ Only collects public data
- ✅ Respects robots.txt (via Web Unlocker)
- ✅ API keys stored securely in `.env`
- ✅ No login bypass attempts
- ✅ Complies with Bright Data ToS
- ✅ Data for manual outreach only (no spam)

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

This project is for educational and commercial use by freelancers.

## 📞 Support

For issues or questions:
- Check the troubleshooting section
- Review logs in `lead_finder.log`
- Open an issue on GitHub

## 🎓 Learning Resources

- [Bright Data Documentation](https://docs.brightdata.com)
- [Google Gemini API](https://ai.google.dev/docs)
- [Streamlit Documentation](https://docs.streamlit.io)
- [BeautifulSoup Guide](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)

## 🚀 Future Enhancements

### Phase 2
- Lead score filtering
- Bulk processing (500+ leads)
- Enhanced error recovery
- Progress persistence

### Phase 3
- MCP agent integration
- Dataset Marketplace integration
- Lead history database (SQLite)
- WhatsApp bulk sender
- Multi-user support
- Advanced analytics dashboard

## ⭐ Acknowledgments

- Bright Data for powerful web data APIs
- Google for Gemini AI
- Streamlit for amazing UI framework
- BeautifulSoup for HTML parsing

---

**Made with ❤️ for Freelancers**

Start finding your next clients today! 🚀
