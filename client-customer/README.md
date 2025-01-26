# Bodhi Bookstore - Customer Portal

A Streamlit-based web application for Bodhi Bookstore's customer-facing online store.

## Features

- Browse and search books
- View book details
- Shopping cart functionality
- Secure checkout process
- Real-time inventory tracking
- Responsive design

## Project Structure

```
├── .streamlit/          # Streamlit configuration
│   └── config.toml      # Theme and settings
├── components/          # UI components
│   ├── book_details.py  # Book details view
│   ├── book_grid.py     # Main book grid
│   ├── checkout_form.py # Checkout process
│   └── shopping_cart.py # Cart sidebar
├── pages/              # Additional pages
│   └── 1_📚_About.py   # About page
├── services/           # External services
│   └── api.py         # API calls
├── styles/            # Styling
│   └── custom_styles.py # Custom CSS
├── utils/             # Utility functions
│   ├── cart.py       # Cart operations
│   ├── helpers.py    # General helpers
│   └── session.py    # Session management
├── Home.py           # Main application file
└── requirements.txt  # Dependencies
```

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file with your configuration:
   ```
   API_BASE_URL=http://your-api-url
   ```

4. Run the application:
   ```bash
   streamlit run Home.py
   ```

## Development

- Follow PEP 8 style guide
- Use type hints
- Add docstrings to functions
- Keep components modular
- Test thoroughly before committing

## Dependencies

- Python >= 3.8
- Streamlit >= 1.31.0
- Requests >= 2.31.0
- Pandas >= 2.2.0
- python-dotenv >= 1.0.0

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

Copyright © 2024 Bodhi Bookstore. All rights reserved. 