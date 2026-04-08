# Color Studio
###### Réalisé par Charlotte Germe, Luc Telliez et Chloé Faillie

[Installation](INSTALL.md)<br><br>


Bienvenue dans la documentation de **Color Studio**, le projet de gestion de scènes lumineuses en Python.

![Logo](images/logo.png)

---
## Informations générale

ColorStudio est un logiciel de compositing d’images de synthèse permettant de combiner plusieurs rendus afin de produire une image finale cohérente.

Contrairement aux approches classiques, ColorStudio propose un compositing basé sur les sources lumineuses, offrant un contrôle fin de l’éclairage sans recalcul complet de la scène.

---

## Principe de fonctionnement

Le logiciel fonctionne à partir de séries d’images générées pour chaque lampe :

- Chaque lampe possède une trajectoire<br>
- Plusieurs images sont générées pour différentes positions<br>
- Chaque image correspond à une contribution lumineuse unique

L’image finale est obtenue par addition des contributions lumineuses

Formule utilisée :
``` I_final = somme des images de chaque lampe à une position donnée ```

## Interface utilisateur

L'interface est composé de :
 - l'image
 - la gestion des lampes
 - compositing interactif
 - les réglages globaux
 - la visualisation avancée

## Fonctionnalités principales
🔹 Gestion des lampes
Ajouter une lampe
Supprimer une lampe
Modifier ses propriétés :
Position
Couleur
Intensité

🔹 Compositing interactif
Mise à jour en temps réel de l’image
Combinaison dynamique des contributions lumineuses

🔹 Réglages globaux
Exposition automatique
Correction colorimétrique

🔹 Visualisation avancée
Analyse des couleurs en 3D


## Utilisation du logiciel


## Environnement technique

Version modernisée attendue :

Python 3.12+ <br>
PyQt6<br>

Bibliothèques :<br>

## Architecture du projet

## Qualité logicielle

## Support et maintenance

