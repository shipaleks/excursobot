# ExcursoBot 🤖

Telegram bot that provides interesting facts about locations using OpenAI GPT-4.

## Features

- 📍 **Location Facts**: Send your location and get surprising facts about nearby places
- 🧠 **AI-Powered**: Uses OpenAI GPT-4o-mini for intelligent fact generation  
- 🚀 **Fast Response**: Optimized for quick fact delivery (≤280 characters)
- 🔄 **Error Handling**: Robust error handling with fallback messages
- 🐳 **Containerized**: Docker-ready for easy deployment
- ⚡ **CI/CD**: Automated testing and deployment via GitHub Actions

## Quick Start

### Prerequisites

- Python 3.12+
- Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- OpenAI API Key

### Local Development

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd excursobot
   ```

2. **Set up environment:**
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Edit .env with your credentials
   nano .env
   ```

3. **Install dependencies:**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Run tests:**
   ```bash
   pytest tests/ -v
   ```

5. **Start the bot:**
   ```bash
   python -m src.main
   ```

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `TELEGRAM_TOKEN` | Your Telegram bot token | ✅ |
| `OPENAI_API_KEY` | Your OpenAI API key | ✅ |

## Docker Deployment

### Build and run locally:
```bash
docker build -t excursobot .
docker run -e TELEGRAM_TOKEN="your_token" -e OPENAI_API_KEY="your_key" excursobot
```

### Railway Deployment

1. Connect your GitHub repository to Railway
2. Set environment variables in Railway dashboard
3. Deploy automatically on push to `main` branch

## Project Structure

```
excursobot/
├── src/
│   ├── main.py              # Application entry point
│   ├── bot/
│   │   └── handlers.py      # Telegram bot handlers
│   ├── services/
│   │   └── openai_client.py # OpenAI integration
│   └── scheduler/           # (Future: live location support)
├── tests/                   # Unit tests
├── docs/                    # Documentation
├── .github/workflows/       # CI/CD configuration
├── Dockerfile              # Container configuration
├── pyproject.toml          # Dependencies and settings
└── README.md               # This file
```

## API Usage

### Commands

- `/start` - Start interaction with the bot
- `/help` - Show help message

### Location Sharing

1. Open chat with the bot
2. Tap the attachment icon (📎)
3. Select "Location"
4. Send your current location
5. Receive an interesting fact about nearby places!

## Technical Details

- **Language**: Python 3.12
- **Bot Framework**: python-telegram-bot 21.2
- **AI Model**: OpenAI GPT-4o-mini
- **Testing**: pytest + pytest-asyncio
- **Linting**: Ruff + Black
- **Deployment**: Railway + Docker
- **CI/CD**: GitHub Actions

## Development

### Code Quality

```bash
# Run linting
ruff check src/ tests/

# Format code
black src/ tests/

# Run tests with coverage
pytest tests/ -v --cov=src
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

- 📧 Issues: Use GitHub Issues
- 📖 Documentation: See `docs/` folder
- 🚀 Deployment: Railway dashboard

---

Built with ❤️ using Python and OpenAI 