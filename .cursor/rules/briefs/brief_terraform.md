Contexte du projet

Vous êtes alternants Data Engineer au sein de l'entreprise "DataCorp", et votre équipe souhaite valider l'utilisation de Terraform pour automatiser l'infrastructure cloud. Pour ce premier projet, votre mission est de vous exercer à déployer des ressources simples et peu coûteuses sur Azure afin de comprendre les bases de Terraform.
Votre objectif est de déployer trois ressources cloud via Terraform pour simuler un environnement basique de Data Engineering. Cette première étape permettra de valider votre maîtrise des concepts de base et de préparer le terrain pour des projets plus complexes à venir.

​

Étapes à suivre

​

1. Création d'une Machine Virtuelle (VM)

​

Utilisez Terraform pour déployer une VM Linux avec des spécifications basiques (par exemple, 1 vCPU, 1 Go de RAM). Cette VM pourrait servir pour exécuter des jobs de transformation de données, des environnements de test pour des outils comme Apache Spark, ou encore pour héberger des outils d'analyse. Elle ne nécessite aucune configuration particulière pour le moment, elle servira simplement de test pour vérifier que le provisioning de la future infrastructure cloud soit efficace et évolutif.

​

2. Créer un Azure Storage Account et un Blob Container

​

L’un des rôles critiques du Data Engineer est de gérer le stockage des données. Vous allez créer un Azure Storage Account qui sera utilisé pour stocker des fichiers de données brutes, des résultats d'analyses ou même des backups de modèles de machine learning.

Dans ce compte de stockage, vous allez également créer un Blob Container pour y déposer des objets (tout type de fichiers, csv, audio, vidéo, etc...). Ce conteneur pourrait être utilisé comme source de données pour des tâches ETL (Extract, Transform, Load) ou pour l'intégration avec des services comme Azure Data Factory ou Databricks.

​

Aucune configuration avancée n'est nécessaire pour l'instant, l'objectif étant de vérifier comment Terraform gère les services de stockage.

​

3. Déployer une Web App

​

Les Data Engineers ne se limitent pas seulement au traitement des données, mais doivent souvent être en mesure d'exposer des résultats sous forme de services. Vous allez donc déployer une Web App sur Azure à l'aide de Terraform. Cette Web App pourrait être utilisée pour exposer un endpoint API permettant d'accéder à des données transformées, des modèles de machine learning ou encore pour héberger un dashboard simplifié pour visualiser des métriques de traitement en temps réel.

La Web App, bien qu'elle soit active, ne contiendra pour l'instant aucune application, elle servira de base pour comprendre comment l'infrastructure d'hébergement peut être automatisée et incluse dans vos pipelines de données.

​

Contraintes

​

    Chaque ressource doit être indépendante et gérée via des modules Terraform pour favoriser la réutilisabilité du code.
    Utilisez un fichier variables.tf pour définir les paramètres importants comme les noms de ressources et les tailles des VM.
    Les ressources doivent être basiques et peu coûteuses pour minimiser l'impact sur votre crédit cloud Azure.

​

Cet exercice vous permettra de vous familiariser avec les concepts fondamentaux de Terraform tout en déployant des ressources cloud simples. Ce premier pas vous servira de base pour des projets plus complexes dans le futur.

​

Bonne chance ! 🦾
