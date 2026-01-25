# Vacances Scolaires France - Home Assistant Integration

[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](CHANGELOG.md)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2024.1+-blue.svg)](https://www.home-assistant.io/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> Intégration Home Assistant pour suivre les vacances scolaires françaises par zone et académie, avec données officielles du Ministère de l'Éducation.

---

## 📋 Table des matières

- [Présentation](#-présentation)
- [Fonctionnalités](#-fonctionnalités)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Entités créées](#-entités-créées)
- [Services](#-services)
- [Exemples d'utilisation](#-exemples-dutilisation)
- [Dépannage](#-dépannage)
- [Contribuer](#-contribuer)
- [Changelog](#-changelog)

---

## 📖 Présentation

Cette intégration permet de suivre les vacances scolaires françaises directement dans Home Assistant. Elle récupère les données officielles du [calendrier scolaire](https://data.education.gouv.fr/explore/dataset/fr-en-calendrier-scolaire/) publié par le Ministère de l'Éducation nationale.

### Caractéristiques principales

- ✅ **Données officielles** : Utilise l'API data.gouv.fr
- ✅ **Multi-zones** : Support des zones A, B et C
- ✅ **Par académie** : Filtrage par académie pour plus de précision
- ✅ **Cache intelligent** : Mise en cache locale pour réduire les appels API
- ✅ **Optimisé** : Recherche binaire pour des performances maximales
- ✅ **Sécurisé** : Protection contre les injections et permissions restrictives
- ✅ **Configurable** : Interface de configuration intuitive

---

## 🎯 Fonctionnalités

### Entités disponibles

#### 📅 Calendrier
- Vue complète des vacances scolaires
- Compatible avec le calendrier Home Assistant
- Affichage des événements à venir

#### 📊 Capteurs
- **Vacances en cours** : Nom des vacances actuelles (si applicable)
- **Prochaines vacances** : Nom des prochaines vacances
- **Jours avant vacances** : Nombre de jours avant les prochaines vacances
- **Jours restants** : Nombre de jours restants dans les vacances en cours

#### 🔘 Capteur binaire
- **En vacances** : État ON/OFF indiquant si nous sommes en période de vacances

### Caractéristiques avancées

- **Mise à jour automatique** : Rafraîchissement quotidien des données
- **Cache local** : Validité de 7 jours pour limiter les appels API
- **Fallback intelligent** : Utilise le cache en cas d'échec de l'API
- **Performance optimisée** : Recherche binaire O(log n) au lieu de O(n)
- **Reconfiguration facile** : Changez de zone/académie sans supprimer l'intégration

---

## 📥 Installation

### Méthode 1 : HACS (Recommandé)

_Cette intégration n'est pas encore dans le store HACS par défaut._

1. Ouvrez HACS dans Home Assistant
2. Cliquez sur les 3 points en haut à droite
3. Sélectionnez "Dépôts personnalisés"
4. Ajoutez l'URL du dépôt
5. Recherchez "Vacances Scolaires France"
6. Cliquez sur "Installer"
7. Redémarrez Home Assistant

### Méthode 2 : Installation manuelle

1. Copiez le dossier `custom_components/vacances_scolaires` vers votre dossier `custom_components`
2. Redémarrez Home Assistant
3. Allez dans Configuration → Intégrations
4. Cliquez sur "+ Ajouter une intégration"
5. Recherchez "Vacances Scolaires France"

---

## ⚙️ Configuration

### Configuration initiale

1. **Allez dans** : Configuration → Intégrations → Ajouter une intégration
2. **Recherchez** : "Vacances Scolaires France"
3. **Sélectionnez votre zone** :
   - Zone A (8 académies)
   - Zone B (12 académies)
   - Zone C (5 académies)
4. **Sélectionnez votre académie** parmi la liste proposée
5. **C'est terminé** ! L'intégration créera automatiquement les entités

### Zones et académies

#### Zone A
Besançon, Bordeaux, Clermont-Ferrand, Dijon, Grenoble, Limoges, Lyon, Poitiers

#### Zone B
Aix-Marseille, Amiens, Caen, Lille, Nancy-Metz, Nantes, Nice, Orléans-Tours, Reims, Rennes, Rouen, Strasbourg

#### Zone C
Créteil, Île-de-France, Montpellier, Toulouse, Corse

### Reconfiguration

Pour changer de zone ou d'académie :

1. **Allez dans** : Configuration → Intégrations
2. **Trouvez** : "Vacances scolaires - Zone X (Académie)"
3. **Cliquez sur** : "Configurer"
4. **Sélectionnez** : Nouvelle zone et/ou académie
5. **Validez** : L'intégration se recharge automatiquement

---

## 🔌 Entités créées

Toutes les entités sont préfixées par `sensor.vacances_scolaires_` ou `calendar.vacances_scolaires`.

### Calendrier

**Entity ID** : `calendar.vacances_scolaires`

- **État** : Prochain événement
- **Attributs** :
  - `message` : Nom de la vacation
  - `start_time` : Date de début
  - `end_time` : Date de fin
  - `location` : Zone et académie
  - `description` : Description de l'événement

### Capteurs

#### Vacances en cours
**Entity ID** : `sensor.vacances_scolaires_en_cours`

- **État** : Nom des vacances (ex: "Vacances de Noël") ou "Aucune"
- **Attributs** :
  - `nom` : Nom des vacances
  - `debut` : Date de début (YYYY-MM-DD)
  - `fin` : Date de fin (YYYY-MM-DD)
  - `zone` : Zone concernée
  - `academie` : Académie concernée
  - `jours_restants` : Nombre de jours restants

#### Prochaines vacances
**Entity ID** : `sensor.vacances_scolaires_prochaines`

- **État** : Nom des prochaines vacances
- **Attributs** :
  - `nom` : Nom des vacances
  - `debut` : Date de début
  - `fin` : Date de fin
  - `zone` : Zone concernée
  - `academie` : Académie concernée
  - `jours_avant` : Nombre de jours avant le début

#### Jours avant vacances
**Entity ID** : `sensor.vacances_scolaires_jours_avant`

- **État** : Nombre de jours (entier)
- **Unité** : `days`

#### Jours restants
**Entity ID** : `sensor.vacances_scolaires_jours_restants`

- **État** : Nombre de jours (entier)
- **Unité** : `days`

### Capteur binaire

**Entity ID** : `binary_sensor.vacances_scolaires`

- **État** : `on` pendant les vacances, `off` hors vacances
- **Device class** : `presence`

---


## 💡 Exemples d'utilisation

### Automatisation : Notification avant les vacances

```yaml
automation:
  - alias: "Notification 7 jours avant les vacances"
    trigger:
      - platform: numeric_state
        entity_id: sensor.vacances_scolaires_jours_avant
        below: 8
        above: 6
    action:
      - service: notify.mobile_app
        data:
          title: "Vacances scolaires bientôt !"
          message: >
            Les {{ states('sensor.vacances_scolaires_prochaines') }}
            commencent dans {{ states('sensor.vacances_scolaires_jours_avant') }} jours !
```

### Automatisation : Mode vacances

```yaml
automation:
  - alias: "Activer mode vacances"
    trigger:
      - platform: state
        entity_id: binary_sensor.vacances_scolaires
        to: 'on'
    action:
      - service: input_boolean.turn_on
        target:
          entity_id: input_boolean.mode_vacances
```

### Carte Lovelace : Affichage des vacances

```yaml
type: entities
title: Vacances scolaires
entities:
  - entity: binary_sensor.vacances_scolaires
    name: En vacances
  - entity: sensor.vacances_scolaires_en_cours
    name: Vacances actuelles
  - entity: sensor.vacances_scolaires_jours_restants
    name: Jours restants
  - entity: sensor.vacances_scolaires_prochaines
    name: Prochaines vacances
  - entity: sensor.vacances_scolaires_jours_avant
    name: Dans
```

### Template : Compteur avant vacances

```yaml
sensor:
  - platform: template
    sensors:
      vacances_countdown:
        friendly_name: "Compte à rebours vacances"
        value_template: >
          {% if states('sensor.vacances_scolaires_jours_avant') | int > 0 %}
            Plus que {{ states('sensor.vacances_scolaires_jours_avant') }} jours !
          {% elif is_state('binary_sensor.vacances_scolaires', 'on') %}
            En vacances ! ({{ states('sensor.vacances_scolaires_jours_restants') }} jours restants)
          {% else %}
            Pas de vacances prévues
          {% endif %}
```

---

## 🐛 Dépannage

### L'intégration ne charge pas les données

**Vérifications** :
1. Vérifiez les logs : Configuration → Logs
2. Recherchez : `vacances_scolaires` ou `Vacances`
3. Erreurs courantes :
   - Problème d'accès à l'API data.gouv.fr
   - Cache corrompu
   - Configuration invalide

**Solutions** :
```bash
# Supprimer le cache
rm -rf .storage/vacances_scolaires/

# Redémarrer Home Assistant
```

### Les capteurs affichent "Inconnu" ou "Unavailable"

**Causes possibles** :
- API data.gouv.fr inaccessible
- Cache expiré et API en erreur
- Pas de données pour la zone/académie sélectionnée

**Solution** :
1. Vérifiez la connectivité internet
2. Attendez quelques minutes (retry automatique)
3. Reconfigurez l'intégration si nécessaire

### Erreur "Invalid zone" lors de la configuration

**Cause** : Zone non reconnue

**Solution** : Utilisez uniquement A, B ou C (majuscules)

### Performance lente

**Cause** : Rare avec la version 2.0 (recherche binaire)

**Vérification** :
- Nombre de périodes de vacances dans les logs
- Version de l'intégration (doit être ≥ 2.0)

---

## 📊 Architecture technique

### Source des données

- **API officielle** : [data.education.gouv.fr](https://data.education.gouv.fr/api/explore/v2.1/catalog/datasets/fr-en-calendrier-scolaire/records)
- **Format** : JSON via OpenDataSoft API
- **Filtres** : Zone, académie, population (élèves uniquement)
- **Période** : Année en cours + année suivante

### Cache et performances

- **Localisation** : `.storage/vacances_scolaires/`
- **Nom fichier** : `vacances_{zone}_{academie}.json`
- **Validité** : 7 jours
- **Permissions** : 0700 (propriétaire uniquement)
- **Algorithme** : Recherche binaire O(log n)

---

## 🔄 Mises à jour

### Mise à jour manuelle

1. Téléchargez la dernière version
2. Remplacez le dossier `custom_components/vacances_scolaires`
3. Redémarrez Home Assistant
4. Vérifiez les logs pour confirmer la nouvelle version

### Mise à jour via HACS

1. HACS → Intégrations
2. Recherchez "Vacances Scolaires France"
3. Cliquez sur "Mettre à jour"
4. Redémarrez Home Assistant

---

## 🤝 Contribuer

Les contributions sont les bienvenues !

### Comment contribuer

1. **Forkez** le projet
2. **Créez** une branche (`git checkout -b feature/amazing-feature`)
3. **Committez** (`git commit -m 'Add amazing feature'`)
4. **Pushez** (`git push origin feature/amazing-feature`)
5. **Ouvrez** une Pull Request

### Guidelines

- Suivez le style de code existant
- Ajoutez des tests si possible
- Mettez à jour la documentation
- Vérifiez que tout fonctionne avant de soumettre

---

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

---

## 👏 Remerciements

- **Ministère de l'Éducation nationale** : Pour les données officielles
- **data.gouv.fr** : Pour l'API OpenDataSoft
- **Home Assistant Community** : Pour le support et les retours

---

## 📚 Documentation complémentaire

- [CHANGELOG.md](CHANGELOG.md) : Historique des versions

---

## 🆘 Support

- **Issues** : [GitHub Issues](https://github.com/homeassistant-fr-ecosystem/vacances_scolaires_fr/issues)
- **Discussions** : [GitHub Discussions](hhttps://github.com/homeassistant-fr-ecosystem/vacances_scolaires_fr/discussions)
- **Forum HA** : [Community Forum](https://community.home-assistant.io/)

---

**Version** : 0.1.0
**Dernière mise à jour** : 2026-01-27
**Auteur** : @homeassistant-fr-ecosystem
**Home Assistant** : 2024.1+
