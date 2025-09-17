# Fuel Tracker - Multi-Language Application

A Flask-based fuel consumption tracking application with support for multiple languages including English, Mongolian, Chinese, Russian, and Arabic.

## Features
- **Fuel Tracking**: Record fuel fill-ups with odometer readings
- **Efficiency Monitoring**: Calculate and track fuel efficiency
- **Range Prediction**: Predict driving range based on current fuel and efficiency
- **Charts & Analytics**: Visualize spending and efficiency trends
- **Vehicle Settings**: Configure tank capacity and vehicle information

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd fuel_tracker
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Database Setup**:
   
   **For Local Development (SQLite)**:
   ```bash
   python init_db.py
   ```
   
   **For Production (PostgreSQL)**:
   ```bash
   # Set environment variable
   export DATABASE_URL="postgresql://user:password@host:port/database"
   
   # Migrate to PostgreSQL
   python migrate_to_postgresql.py
   ```

5. **Test Database Connection**:
   ```bash
   python test_database.py
   ```

## Running the Application

1. **Start the application**:
   ```bash
   python run.py
   ```

2. **Open your browser** and navigate to `http://localhost:5000`

## Configuration

The application configuration is in `config.py`:

## Development

### Project Structure

```
fuel_tracker/
├── app/
│   ├── __init__.py          # Flask app initialization with Babel
│   ├── models.py            # Database models
│   ├── routes.py            # Application routes with i18n
│   ├── forms.py             # WTForms with translations
│   ├── templates/           # Jinja2 templates with gettext
│   └── translations/        # Translation files
├── config.py                # Configuration including languages
├── babel.cfg                # Babel configuration
├── requirements.txt          # Python dependencies
├── compile_translations.py  # Translation compilation script
└── run.py                   # Application entry point
```

### Key Components

- **Flask-Babel**: Handles internationalization and localization
- **gettext**: Used for string translation throughout the application
- **Session Management**: Stores user's language preference
- **RTL Support**: Special handling for Arabic text direction

## Usage Examples

### Adding Fuel Records

1. Navigate to "Add Fill-up" (or translated equivalent)
2. Fill in the form with your fuel information
3. Submit to record your fuel consumption

### Viewing Statistics

- **Home**: Overview of fuel consumption and efficiency
- **History**: Detailed list of all fuel records
- **Charts**: Visual representation of spending and efficiency trends
- **Range**: Predict driving distance based on current fuel

## Troubleshooting

### Debug Mode

To run in debug mode for development:

```python
# In run.py
app.run(debug=True)
```

## Contributing

To add new translations or improve existing ones:

1. Edit the appropriate `.po` file
2. Test the translation in the application
3. Submit a pull request with your changes

## License

This project is open source and available under the [MIT License](LICENSE).

## Support

For issues or questions about the multi-language features, please check the translation files or create an issue in the repository.
