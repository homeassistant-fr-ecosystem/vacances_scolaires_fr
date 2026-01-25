# Vacances Scolaires FR

Intégration Home Assistant pour les vacances scolaires françaises par zone (A, B, C).

## Fonctionnalités

- 📅 **Entité Calendar** : Affichage des périodes de vacances
- 🎒 **Sensors exploitables** :
  - `sensor.vacances_en_cours` : Vacances actuelles (on/off)
  - `sensor.prochaines_vacances` : Prochaines vacances (date de début)
  - `sensor.jours_avant_vacances` : Jours avant les prochaines vacances
  - `sensor.zone_scolaire` : Zone scolaire configurée
- 🤖 **Automatisable** : Notifications, modes maison, adaptation du chauffage, etc.
- 📍 **Sans dépendance externe** : Données embarquées, pas d'ICS fragile

## Installation

1. Créez le dossier `custom_components/vacances_scolaires_fr` dans votre répertoire Home Assistant
2. Copiez tous les fichiers du composant
3. Redémarrez Home Assistant
4. Allez dans **Paramètres > Appareils et services > Créer une automatisation**
5. Sélectionnez **Vacances scolaires FR**
6. Choisissez votre zone (A, B, ou C)

## Entités

### Calendar
- `calendar.vacances_scolaires` : Calendrier avec tous les événements de vacances

### Sensors
- `sensor.vacances_en_cours` : État actuel (on si en vacances, off sinon)
  - Attributs : nom, début, fin, zone, jours_restants
- `sensor.prochaines_vacances` : Date de début des prochaines vacances
  - Attributs : nom, début, fin, zone, jours_avant
- `sensor.jours_avant_vacances` : Nombre de jours avant les prochaines vacances
- `sensor.zone_scolaire` : Zone configurée (A, B, C)

## Cas d'usage

### Notification au début des vacances
```yaml
automation:
  - alias: "Notification vacances"
    trigger:
      platform: time
      at: "07:00:00"
    condition:
      - condition: state
        entity_id: sensor.vacances_en_cours
        state: "on"
    action:
      service: notify.mobile_app_phone
      data:
        message: "Bienvenue en vacances ! 🎒"
```

### Activer un mode "vacances" dans la maison
```yaml
automation:
  - alias: "Mode vacances activé"
    trigger:
      platform: state
      entity_id: sensor.vacances_en_cours
      to: "on"
    action:
      service: input_boolean.turn_on
      data:
        entity_id: input_boolean.enfants_en_vacances
```

### Rappel J-7 avant vacances
```yaml
automation:
  - alias: "Rappel vacances dans 7 jours"
    trigger:
      platform: numeric_state
      entity_id: sensor.jours_avant_vacances
      below: 8
    action:
      service: notify.mobile_app_phone
      data:
        message: "Les vacances commencent dans {{ state_attr('sensor.prochaines_vacances', 'jours_avant') }} jours ! 📚"
```

## Support

- Repository : https://github.com/homeassistant-fr-ecosystem/vacances_scolaires_fr
- Issues : https://github.com/homeassistant-fr-ecosystem/vacances_scolaires_fr/issues

