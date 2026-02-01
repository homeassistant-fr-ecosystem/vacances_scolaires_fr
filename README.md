# Vacances Scolaires FR

Intégration Home Assistant pour les vacances scolaires françaises par zone (A, B, C) et DOM-TOM.

## Fonctionnalités

- 📅 **Entité Calendar** : Affichage des périodes de vacances
- 🎒 **Sensors exploitables** :
  - `binary_sensor.school_holidays_on` : Vacances actuelles (on/off)
  - `sensor.next_school_holidays` : Prochaines vacances (date de début)
  - `sensor.days_until_holidays` : Jours avant les prochaines vacances
  - `sensor.school_zone` : Zone scolaire configurée
- 🤖 **Automatisable** : Notifications, modes maison, adaptation du chauffage, etc.
- 📍 **Sans dépendance externe** : Données embarquées, pas d'ICS fragile

## Installation

1. Créez le dossier `custom_components/vacances_scolaires_fr` dans votre répertoire Home Assistant
2. Copiez tous les fichiers du composant
3. Redémarrez Home Assistant
4. Allez dans **Paramètres > Appareils et services > Créer une automatisation**
5. Sélectionnez **Vacances scolaires FR**
6. Choisissez votre zone :
   - **Métropole** : Zone A, B ou C et votre académie
   - **DOM-TOM** : Guadeloupe, Martinique, Guyane, La Réunion, Mayotte, Nouvelle-Calédonie, Polynésie française, Wallis-et-Futuna, ou Saint-Pierre-et-Miquelon
7. Configurez les options avancées (optionnel) :
   - **Fuseau horaire** : Automatiquement configuré selon votre zone
   - **Intervalle de mise à jour** : 1-30 jours (défaut: 7 jours)
   - **Vérification SSL** : Activer/désactiver la vérification SSL pour l'API (défaut: activé)
   - **Créer calendrier** : Activer/désactiver l'entité calendrier (défaut: activé)

## Zones supportées

### Métropole
- **Zone A** : Besançon, Bordeaux, Clermont-Ferrand, Dijon, Grenoble, Limoges, Lyon, Poitiers
- **Zone B** : Aix-Marseille, Amiens, Caen, Lille, Nancy-Metz, Nantes, Nice, Orléans-Tours, Reims, Rennes, Rouen, Strasbourg
- **Zone C** : Créteil, Montpellier, Paris, Toulouse, Versailles, Corse

### DOM-TOM
- **Guadeloupe** (UTC-4 - America/Guadeloupe)
- **Martinique** (UTC-4 - America/Martinique)
- **Guyane** (UTC-3 - America/Cayenne)
- **La Réunion** (UTC+4 - Indian/Reunion)
- **Mayotte** (UTC+3 - Indian/Mayotte)
- **Nouvelle-Calédonie** (UTC+11 - Pacific/Noumea)
- **Polynésie française** (UTC-10 - Pacific/Tahiti)
- **Wallis-et-Futuna** (UTC+12 - Pacific/Wallis)
- **Saint-Pierre-et-Miquelon** (UTC-3 - America/Miquelon)

**Note** : Les calendriers scolaires DOM-TOM sont automatiquement synchronisés avec les fuseaux horaires locaux. Les calculs de dates (jours avant vacances, jours restants) utilisent l'heure locale du territoire.

## Entités

### Calendar
- `calendar.school_holidays_calendar_{zone}_{academy}` : Calendrier avec tous les événements de vacances

### Binary Sensor
- `binary_sensor.school_holidays_on_{zone}_{academy}` : État actuel (on si en vacances, off sinon)
  - Attributs : nom, début, fin, zone, jours_restants

### Sensors
- `sensor.next_school_holidays_{zone}_{academy}` : Date de début des prochaines vacances
  - Attributs : nom, début, fin, zone, jours_avant
- `sensor.days_until_holidays_{zone}_{academy}` : Nombre de jours avant les prochaines vacances
- `sensor.school_zone_{zone}_{academy}` : Zone configurée (A, B, C)

**Note :** `{zone}` et `{academy}` sont remplacés par votre configuration (ex: `a_lyon`)

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
        entity_id: binary_sensor.school_holidays_on_a_lyon
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
      entity_id: binary_sensor.school_holidays_on_a_lyon
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
      entity_id: sensor.days_until_holidays_a_lyon
      below: 8
    action:
      service: notify.mobile_app_phone
      data:
        message: "Les vacances commencent dans {{ state_attr('sensor.next_school_holidays_a_lyon', 'jours_avant') }} jours ! 📚"
```

## Configuration

### Options avancées

Après l'installation, vous pouvez reconfigurer l'intégration via **Paramètres > Appareils et services > Vacances scolaires FR > Configurer** :

- **Zone et Académie** : Modifier votre zone et académie
- **Options avancées** :
  - **Intervalle de mise à jour** : Fréquence de mise à jour des données (1-30 jours)
  - **Vérification SSL** : Activer/désactiver la vérification des certificats SSL
  - **Créer calendrier** : Activer/désactiver l'entité calendrier

**Note** : Toute modification des options nécessite un rechargement automatique de l'intégration.

## Support

- Repository : https://github.com/homeassistant-fr-ecosystem/vacances_scolaires_fr
- Issues : https://github.com/homeassistant-fr-ecosystem/vacances_scolaires_fr/issues

