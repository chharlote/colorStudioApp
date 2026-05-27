# Accueil - ColorStudio

Bienvenue dans la documentation officielle de **ColorStudio**.

## Présentation du projet
**ColorStudio** est un logiciel Python dédié au compositing d'images de synthèse, conçu pour composer une image finale à partir de contributions lumineuses individuelles.

## Objectif principal
Son objectif est de fusionner plusieurs images issues de rendus distincts afin de produire un éclairage cohérent et contrôlable en temps interactif. Le principe clé est d'éviter le recalcul de la géométrie 3D complète de la scène : vous ajustez l'exposition, la couleur et la position de chaque lumière, et le rendu composite se met à jour instantanément.

## Structure de la documentation
Cette documentation est divisée en deux grandes sections pour vous accompagner au mieux :

* **Guide Utilisateur** : Tout ce qu'il faut savoir pour installer l'application, comprendre ses concepts clés (compositing par sources lumineuses), et maîtriser son interface (chargement de scènes, réglages des lampes, visualisation 3D des couleurs).
* **Documentation Technique** : Détails destinés aux développeurs souhaitant comprendre, maintenir ou faire évoluer l'application (architecture logicielle MVC, fondements théoriques de l'additivité de la lumière, etc.).