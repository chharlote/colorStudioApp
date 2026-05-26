# Color Studio

**Color Studio** est un logiciel Python pour composer des images de synthèse à partir de contributions lumineuses individuelles.

Cette documentation couvre l’installation, l’utilisation et l’architecture de l’application.

---

## Objectif du projet

Color Studio permet de :
- charger et visualiser une scène à partir d’une image de rendu,
- contrôler plusieurs sources lumineuses (lampes) en temps réel,
- ajuster l’exposition, les couleurs et la position de chaque lumière,
- obtenir un rendu final interactif sans recalculer l’intégralité de la scène.

Le principe clé est de combiner les contributions lumineuses plutôt que de recalculer la géométrie complète de la scène.

---

## Installation

### Prérequis

- Python 3.10+ (3.12 recommandé)
- Pip installé

### Dépendances principales

- PyQt6
- moderngl
- numpy
- scikit-image
- imageio

### Installation des dépendances

Depuis le répertoire racine du projet :

```powershell
py -3 -m pip install PyQt6 moderngl numpy scikit-image imageio
```


---

## Lancement de l’application

Depuis la racine du projet :

```powershell

```

Le programme ouvre la fenêtre principale en taille maximale selon la résolution de l’écran.

---

## Utilisation

### Interface principale

L’interface est organisée en trois zones :

1. **Vue de rendu principale**
   - affiche le résultat composite de toutes les lampes.
2. **Panneau de contrôle à gauche**
   - regroupe les contrôles de chaque lampe,
   - permet de modifier l’exposition, la couleur et la position des lampes.
3. **Panneau droit optionnel**
   - affiche la visualisation 3D des couleurs,
   - affiche la roue chromatique interactive.

### Contrôles de lampe

Pour chaque lampe, le panneau de contrôle contient :
- un bouton pour diminuer l’exposition,
- un bouton pour augmenter l’exposition,
- un bouton pour changer la couleur,
- un curseur de position.

Chaque contrôleur indique désormais clairement le nom de la lampe qu’il modifie.

### Options globales

- **Chargement d’image** : menu Fichier > Load Image...
- **Sauvegarde d’image** : menu Fichier > Save Image...
- **Quitter** : menu Fichier > Exit

---

## Fonctionnalités

- **Chargement et affichage d’images**
- **Redimensionnement automatique de l’image** lorsque la fenêtre est redimensionnée
- **Ouverture en plein écran** ou mode maximisé selon la résolution du moniteur
- **Contrôle individuel des lampes**
- **Affichage d’une roue chromatique** pour choisir facilement une couleur
- **Visualisation 3D des couleurs** via ModernGL
- **Exposition automatique** et réglages de saturation

---

## Architecture du projet

Le code est organisé principalement dans le dossier `src/` :

- `src/colorStudioApp.py` : point d’entrée de l’application,
-  `views/` : interface utilisateur et widgets Qt,
  - `colorStudioUIBuilder.py` : construction de l’interface principale,
  - `colorStudioWidget.py` : widgets d’affichage et contrôles personnalisés,
- `controllers/` : logique de contrôle des lampes et interactions utilisateur,
- `models/` : modèles des scènes lumineuses et post-traitement,
- `utils/` : utilitaires pour le traitement d’images et les conversions couleur.

---

## Bonnes pratiques

- Charger une image de rendu claire pour améliorer la lisibilité des contrôles d’exposition.
- Utiliser les sections pliables (`collapsible sections`) pour masquer/afficher les contrôles des lampes.
- Vérifier les couleurs de la roue chromatique avant de les appliquer pour garder un rendu cohérent.

---

## Maintenance

- Pour ajouter une nouvelle fonctionnalité, privilégier la séparation logique entre vues, contrôleurs et modèles.
- Documenter chaque nouvelle classe et chaque nouveau widget dans `docs/index.md`.
- Tester les modifications d’interface en ouvrant l’application et en redimensionnant la fenêtre.

---

## Support

Signalez les bugs en décrivant :
- le système d’exploitation utilisé,
- la version de Python,
- la séquence d’actions ayant provoqué le problème.

---

## Notes

- Ce projet a été adapté pour un environnement moderne Python/PyQt,
- certaines dépendances attendent un environnement graphique compatible.
- Le chemin d’exécution principal est `src\colorStudioApp.py`.
