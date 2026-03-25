# Contributing to Fam Tree Bot

Thank you for your interest in contributing to Fam Tree Bot! 🌳

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/fam-tree-bot.git`
3. Create a virtual environment: `python -m venv venv`
4. Activate it: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
5. Install dependencies: `make dev-install`

## Development Setup

```bash
# Copy environment file
cp .env.example .env

# Edit with your settings
nano .env

# Run database migrations
make migrate

# Start the bot
python src/main.py
```

## Code Style

We use:
- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

Run before committing:
```bash
make format
make lint
```

## Testing

```bash
# Run all tests
make test

# Run specific test
pytest tests/test_handlers.py -v
```

## Adding New Commands

1. Create handler in `src/handlers/`
2. Add to router in `src/handlers/router.py`
3. Add tests in `tests/`
4. Update documentation

## Pull Request Process

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make your changes
3. Run tests and linting
4. Commit with clear messages
5. Push to your fork
6. Create a Pull Request

## Commit Message Format

```
type(scope): subject

body (optional)

footer (optional)
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting
- `refactor`: Code refactoring
- `test`: Tests
- `chore`: Maintenance

## Code of Conduct

- Be respectful
- Welcome newcomers
- Focus on constructive feedback
- Help others learn

## Questions?

Join our Telegram: @famtreebot_support
