# Fuel Tracker - Multi-Language Application

A Flask-based fuel consumption tracking application with support for multiple languages including English, Mongolian, Chinese, Russian, and Arabic.

## Features

- **Multi-language Support**: Available in 5 languages
  - English (en)
  - Mongolian (Монгол) - mn
  - Chinese (中文) - zh
  - Russian (Русский) - ru
  - Arabic (العربية) - ar
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

4. **Initialize the database**:
   ```bash
   python init_db.py
   ```

## Running the Application

1. **Start the application**:
   ```bash
   python run.py
   ```

2. **Open your browser** and navigate to `http://localhost:5000`

3. **Change language** using the language selector in the top-right corner of the application

## Language Support

### Supported Languages

| Language | Code | Native Name |
|----------|------|-------------|
| English | en | English |
| Mongolian | mn | Монгол |
| Chinese | zh | 中文 |
| Russian | ru | Русский |
| Arabic | ar | العربية |

### Language Features

- **RTL Support**: Arabic language includes right-to-left text direction support
- **Localized Content**: All user interface elements are translated
- **Session Persistence**: Language selection is remembered during the session
- **Fallback**: Falls back to English if a translation is missing

## Translation Management

### Adding New Languages

1. Create a new directory structure:
   ```
   app/translations/[language_code]/LC_MESSAGES/
   ```

2. Create a `messages.po` file with translations

3. Compile translations:
   ```bash
   python compile_translations.py
   ```

### Updating Translations

1. Edit the `.po` files in the `app/translations/[lang]/LC_MESSAGES/` directory
2. Run the compilation script:
   ```bash
   python compile_translations.py
   ```

### Translation File Structure

```
app/translations/
├── en/LC_MESSAGES/messages.po
├── mn/LC_MESSAGES/messages.po
├── zh/LC_MESSAGES/messages.po
├── ru/LC_MESSAGES/messages.po
└── ar/LC_MESSAGES/messages.po
```

## Configuration

The application configuration is in `config.py`:

```python
LANGUAGES = {
    'en': 'English',
    'mn': 'Монгол',
    'zh': '中文',
    'ru': 'Русский',
    'ar': 'العربية'
}
```

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

### Changing Language

1. Use the language dropdown in the top-right corner
2. Select your preferred language
3. The application will reload with the new language

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

### Common Issues

1. **Translations not working**: Ensure you've compiled the translation files
2. **Language not changing**: Check that the language code is supported in `config.py`
3. **Missing translations**: Some strings may not be translated yet

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
