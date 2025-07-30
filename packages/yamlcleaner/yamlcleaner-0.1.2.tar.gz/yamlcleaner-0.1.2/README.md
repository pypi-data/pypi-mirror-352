# yamlcleaner

**yamlcleaner** est un outil en ligne de commande (CLI) pour nettoyer les fichiers YAML en supprimant tous les commentaires.

## Installation

Assurez-vous d'avoir Python 3.7 ou supérieur installé.

Installez les dépendances :

```bash
pip install -r requirements.txt
# ou, si installé via pyproject.toml :
pip install .
```

## Utilisation

Pour nettoyer un fichier YAML :

```bash
yamlcleaner chemin/vers/fichier.yaml
```

Pour nettoyer tous les fichiers d’un dossier (récursivement) :

```bash
yamlcleaner chemin/vers/dossier
```

Par défaut, les fichiers nettoyés sont enregistrés dans le dossier `./cleaned`.  
Vous pouvez spécifier un dossier de sortie avec l’option `-o` :

```bash
yamlcleaner chemin/vers/dossier -o dossier_sortie
```

## Exemple

Avant :

```yaml
# Ceci est un commentaire
nom: Alice # commentaire en ligne
age: 30
```

Après nettoyage :

```yaml
nom: Alice
age: 30
```

## Licence

Voir le fichier [LICENSE.MD](LICENSE.MD).