# Brief : Découverte du Data Lake Azure

## Contexte

Dans ce brief, vous allez apprendre à configurer un **Azure Data Lake** **Storage Gen2** et à gérer l’ingestion de données depuis diverses sources, locales et cloud, pour centraliser des données et permettre leur analyse. À travers les étapes proposées, vous manipulerez différentes sources de données, créerez des pipelines de données et apprendrez à automatiser des processus d’ingestion pour optimiser la gestion de flux de données à grande échelle.

---

## Ressources

1. **Données Fictives** :
    - [images](https://drive.google.com/file/d/1FGvy6QY8QM243vpO3l6gnQtISPd6ibSr/view)
    - [sample_data](https://drive.google.com/drive/folders/1ap7hgoXF_eNkEYZ2ENVAoMOGvlvon6_m?usp=drive_link)
    - Une BDD AdventureWorks a été déployé sur Azure
    - Créez des données fictives à l’aide de [Mockaroo](https://www.mockaroo.com/).

## Notes

**Nommage des Ressources** :

- Nommez les ressources en respectant le format suivant : `RG_[PREMIERE LETTRE DE VOTRE PRENOM][NOM_DE_FAMILLE]`
- Exemple : Pour Jérémy Vangansberg ⇒ `RG_JVANGANSBERG`.
- Data lake gen2 (storage account): adls`[nomdefamille]`
- Blob storage :blob`[nomdefamille]`
- Data Factory : df`[nomdefamille]`

---

## Étape 1 : Création d'un Azure Data Lake Gen2

1. **Objectif** : Créer un **compte de stockage Azure Data Lake Gen2** dans votre abonnement Azure, qui servira de cible pour centraliser les données. 

---

## Étape 2 : Ingestion de Données par batch Unique

### A. Ingestion de Données On-Premise

### 1. Utilisation du Portail Azure

- **Objectif** : Transférez des données on-premise vers le Data Lake via le portail Azure.
- **Étapes** :
    - Téléchargez le dossier `sample_data` sur votre machine.
    - Créez un conteneur nommé `datastorage` dans votre Data lake.
    - À l'intérieur, créez un dossier `input_data_portal` pour organiser les données.
    - Après le transfert effectuez les modifications suivantes :
        - **fichier sample.json** : Changez le *tier* du fichier en **cold tier** pour optimiser les coûts.
        - **fichier sample.txt** : Ajoutez un bail sur ce fichier.
        - **fichier sample.xml** : Renommez `sample.xml` en `to_delete.xml` et supprimez-le.
    - **Images** : Appliquez la même procédure pour les images téléchargées dans le Google Drive et stocker dans un dossier dans `input_data_portal_images`.

### 2. Utilisation de l’Outil AzCopy

- **Objectif** : Automatiser l’ingestion de données on-premise avec AzCopy.
- **Étapes** :
    - Créez un dossier `input_data_azcopy` dans le Data Lake.
    - Regardez la documentation de [Azcopy](https://learn.microsoft.com/en-us/azure/storage/common/storage-use-azcopy-v10?tabs=dnf)
    - Écrivez un script bash avec **AzCopy** pour transférer les données `sample_data` de votre machine vers le data lake.
    - Vous devrez choisir une méthode d’authentification : utilisez un **SAS (Shared Access Signature)** pour l'authentification.

### B. Ingestion de Données Cloud

1. Effectuer une **veille** sur les différents types de format : Parquet, Avro, XML, ORC
2. **Création d’un Azure Data Factory** : Créez un service Data Factory (sans Git) pour orchestrer l’ingestion et la transformation des données.
3. **Source : Azure Blob Storage**
    - **Ingestion avec Data Factory** :
        - Créer un Azure Blob Storage (faites la différence entre ça et votre data lake) et mettez y les `sample_data`
        - Configurez un pipeline avec Data Factory pour ingérer les données depuis **Azure Blob Storage** vers le Data Lake.
        - Importez les fichiers du dossier `sample_data` dans un dossier `input_df_abs` sur le data lake.
        - **Recommencez avec les images** : Uploadez les images sur Blob Storage et configurez une ingestion depuis le blob storage vers le data lake. Ajoutez une étape de compression des données dans le data lake.
4. **Source : Azure SQL Database**
    - **Base de données disponible** :
        - **Serveur** : `adventure-works-server-de-hdf`
        - **Nom de la BDD** : `adventure_works`
        - **Identifiants** :
            - Utilisateur : `adminawdehdf`
            - Mot de passe : `k*uIe1034^ReF~`
    - **Transfert des Données** :
        - Transférez toutes les tables vers le Data Lake vers un dossier `input_df_sql`.
        - **Étapes** :
            - Sauvegardez une copie initiale en fichier texte. Inspecter les données sur le data lake.
            - Modifiez le pipeline pour sauvegarder ensuite les données en format **Parquet**. Inspecter les données sur le data lake.

---

### C. Ingestion avec choix libre de technologies

Dans ce cas de figure, aucune technologie est imposée. Vous pouvez vous aider du Data Migration tool pour sélectionner l'outil le plus adapté selon les scénarios d'ingestion.

1. **Base Sakila avec PostgreSQL** :
    - Générez une base **Sakila** en local sur PostgreSQL en suivant ce [dépôt GitHub](https://github.com/jOOQ/sakila/tree/main/postgres-sakila-db).
    - Ingérer vers un dossier `input_sakila`
2. **Weather API** (Attention besoin de 24h pour que la clé ssoit activé):
    - Connectez-vous à l’API météo de [OpenWeather](https://openweathermap.org/api) pour ingérer des données climatiques sur un historique (1 an, 10 ans, etc.).
    - Ingérer vers un dossier `input_openweather`
    - Alternative API : [jsonplaceholder.typicode.com](http://jsonplaceholder.typicode.com/)
3. **[Bonus] Données du BOFIP** :
    - **Télécharger les données de stock** depuis le BOFIP (Bulletin officiel des finances publiques).
    - **Définir un Pipeline** : Créez un pipeline pour appeler l’API, et sauvegardez les données sur le Data Lake.
    - Ingérer vers un dossier `input_bofip`

## Étape 3 : Ingestion avancée : déclencheurs, récurrence, incrémentielle (Data Factory)

### A. Déclencheurs Programmés (Scheduled)

1. **Ingestion Programmée dans Azure Blob Storage** :
    - Planifiez une ingestion à une date et heure spécifique dans la semaine depuis le blob storage qui va copier toutes les données (`sample_data` depuis votre blob storage)vers le data lake. Configurer également une option de récurrence (toutes les heures pour tester)
    - Ajoutez de nouvelles données fictives (avec Mockaroo) pour tester.
2. **Ingestion incrémentielle programmée**
    - Planifiez une ingestion qui va uniquement ajouter que les informations nouvelles (sur `sample_data` ou les `images`). (Vous devrez éditer le pipeline précédent)
- Indice : Comment faire une ingestion incrémentielle ?
    
    Vous devrez créer un pipeline personnalisé dans Data Factory. Exemple : 
    
    - approche qui nécessite une **table de contrôle,** l’idée c’est de faire un pipeline personnalisé en enchaînant plusieurs **activités** :
        - **Get Metadata** – Récupère les métadonnées du fichier récemment ajouté (nom, date de modification, etc.), associé cette activité avec un trigger event.
        - **Lookup/Select** – Vérifie dans la table de contrôle si le fichier existe déjà.
        - **If Condition** – Vérifie si le fichier est nouveau ou déjà transféré :
            - **Vrai (nouveau fichier)** : Passe à l'étape suivante.
            - **Faux (fichier déjà transféré)** : Terminer le pipeline.
        - **Copy Data** – Transfère le fichier vers le Data Lake si la condition est remplie.
        - **Insert into Control Table** – Met à jour la table de contrôle avec les informations sur le fichier transféré.
1. **[Bonus]** Modifier le pipeline précédent afin qu’il détecte comme nouveau des modifications sur un fichier qui n’a pas changé de nom.
2. **[Bonus] Ingestion Quotidienne depuis l'API OpenWeatherMap** :
    - Programmez un pipeline d’ingestion quotidienne pour collecter des données météo.

### B. Déclencheurs Basés sur des Événements (Event-based)

1. Lancement d’un pipeline en cas d’ajout d’un fichier
    
    Dans votre blob storage, où se trouve les `sample_data` , appliqué la règle suivante :
    
    Quand un fichier est ajouté sur ce blob storage, effectuer le transfert tous les fichiers vers le data lake.
    
2. **Ajout des nouveaux éléments dans Blob Storage** :
    - Configurez un trigger pour détecter et ajouter UNIQUEMENT les nouveaux éléments. (*événementiel* + *incrementiel*). Utiliser le blob storage qui contient les images. Votre objectif est de lancer le pipeline quand une nouvelle image est upload sur le blob storage et transférer uniquement cette nouvelle image vers le Data Lake.
3. **[Bonus] Détection de Nouvelles Entrées dans la BDD On-Premise** :
    - Créez un pipeline qui surveille les mises à jour dans une base de données locale et déclenche l’ingestion dès qu’une nouvelle entrée est ajoutée.
4. **[Bonus] Intégration des Données du BOFIP (Flux)**
    - **Objectif** : Configurer un pipeline qui analyse automatiquement le calendrier des mises à jour du BOFIP et récupère les nouvelles données.
    - **Automatisation** : Programmez le pipeline pour déclencher l'ingestion des données dès qu'une mise à jour est détectée.