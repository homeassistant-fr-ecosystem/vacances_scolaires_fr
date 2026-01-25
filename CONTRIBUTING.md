# Contributing

Thank you for your interest in contributing to this project!

## Development setup

```bash
# Clone the repository
git clone https://github.com/homeassistant-fr-ecosystem/vacances_scolaires_fr.git
cd vacances_scolaires_fr

# Copy to Home Assistant custom_components (for testing)
cp -r custom_components/vacances_scolaires_fr /path/to/home-assistant/custom_components/

# Run tests
pytest tests.py
```

## Testing

Make sure to test your changes against a real Home Assistant instance before submitting a PR.

## Code style

- Follow PEP 8
- Use type hints
- Add docstrings to functions and classes

## Updating vacation data

Vacation data is stored in `const.py` in the `VACANCES_SCOLAIRES` list. Update this list when new school year data is available from official sources.

Sources:
- https://www.data.gouv.fr/dataservices/api-calendrier-scolaire
- https://www.education.gouv.fr/calendrier-scolaire-de-l-annee-2024-2025
