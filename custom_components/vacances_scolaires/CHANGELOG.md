# Changelog

All notable changes to the Vacances Scolaires France integration will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.0] - 2026-01-27

### ✨ Initial Release

First production-ready version of the Vacances Scolaires France integration.

#### Features
- **French school holidays tracking** by zone (A, B, C) and academy
- **Calendar entity** for Home Assistant calendar view
- **Sensor entities**:
  - Current vacation name
  - Next vacation name
  - Days until next vacation
  - Days remaining in current vacation
- **Binary sensor**: In vacation / not in vacation state
- **Official data source**: data.gouv.fr API (Ministère de l'Éducation)
- **Smart caching**: 7-day local cache to reduce API calls
- **Options flow**: Reconfigure zone/academy without deleting integration

#### Documentation
- `README.md`: Complete user guide with examples
- `CHANGELOG.md`: Version history

---

## Version Numbering

- **Major version** (X.0.0): Breaking changes, major features
- **Minor version** (0.X.0): New features, improvements (backward compatible)
- **Patch version** (0.0.X): Bug fixes, security patches

---

## Links

- **Repository**: https://github.com/homeassistant-fr-ecosystem/vacances_scolaires_fr
- **Issues**: https://github.com/homeassistant-fr-ecosystem/vacances_scolaires_fr/issues
- **Documentation**: [README.md](README.md)

---

**Maintained by**: @homeassistant-fr-ecosystem
**License**: MIT
**Home Assistant Compatibility**: 2024.1+
