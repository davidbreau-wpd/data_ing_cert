Contexte du projet

Novo, centre de formation spécialisé dans la montée en compétence IT souhaite formaliser sa gouvernance des données pour les raisons suivantes :

​

Conformité réglementaire

Garantir le respect des exigences du RGPD et des recommandations de la CNIL, notamment concernant la gestion des données personnelles des apprenants (noms, adresses e-mail, historiques de formation, etc.).

​

Optimisation des processus

Structurer les données internes pour faciliter leur exploitation, leur traçabilité, et leur partage au sein de l’organisation.

​

Sécurité et confidentialité

Protéger les données sensibles des apprenants et des partenaires contre tout accès non autorisé ou usage abusif.

​

Amélioration de la qualité des données

Mettre en place des processus permettant d’assurer la fiabilité, la cohérence et l’exactitude des données utilisées.

​

Votre mission consiste à expérimenter et valider une solution de gouvernance des données via un Proof of Concept (POC), ceci par la mise en place d'une infrastructure minimale pour connecter les données au catalogue de gouvernance.

​

Objectifs et étapes de mise en place du POC

​

La mise en place de l'infrastructure et du POC repose sur la création et la configuration des ressources nécessaires à la gestion des données et leur gouvernance. Voici une vue d'ensemble des étapes

​

1. Création du Resource Group

​

Créez un Resource Group personnel dédié à ce module d'apprentissage.

Nom recommandé : RG_DG_DM_votre-prenom-nom

​

​

2. Configuration des composants clés de l'infrastructure

​

NB : Les données fictives à utiliser dans cette partie se trouvent dans mocks.zip

NB : Adoptez la structuration des containers et dossier en suivant les impressions écrans dans previews.zip

​

Azure Blob Storage

​

Objectif : Stocker les fichiers non structurés (ex. : photos d'identité issues de students.zip).

​

    Créer un Blob Storage.
    Créer un container dédié.
    Importer les fichiers contenus dans students.zip.

​

Azure Data Lake Storage Gen2

​

Objectif : Stocker des lots d'assets non structurés (ex. : logs, fichiers apprenants et formateurs).

​

    Créer un Data Lake Storage Gen2.
    Créer un container pour chaque lot d’assets présent dans data_lake.zip.
    Importer les fichiers correspondants.

​

Azure SQL Database (avec Azure SQL Server)

​

Objectif : Stocker les données structurées (ex. : bases de données des clients, achats, etc...).

​

    Créer un Azure SQL Server (ressource logique).
    Créer une Azure SQL Database.
    Injecter les données du script db.sql à l'aide du Query Editor ou d'un outil comme Azure Data Studio.

​

Microsoft Purview Account

​

Objectif : Mettre en place la gouvernance des données via Microsoft Purview.

​

    Créer un Microsoft Purview Account.
    Accéder au portail Microsoft Purview : https://web.purview.azure.com.
    Lorsque l'étape suivante (key vault) sera finalisée alors vous pourrez configurer les scans afin de constituer le catalogue et effectuer la classification de méta données.

​

Azure Key Vault

​

Objectif : Sécuriser les clés d'accès aux ressources (Blob Storage, Data Lake et SQL Server).

​

    Créer un Azure Key Vault.
    Ajouter les secrets pour les différentes ressources.
    Configurer un accès pour le compte Microsoft Purview avec le rôle « Key Vault Secrets User ».

​

​

3. Collections et Classification de données avec Microsoft Purview

​

Dans cette partie de la mission, vous devez collecter (collections + scan) et classifier les données issues des ressources des stockage, précédemment mis en place, en utilisant Microsoft Purview. La classification permet d’identifier les données selon leur type ou leur sensibilité, et est essentielle pour assurer la conformité RGPD et faciliter leur utilisation dans les projets. Vous devez vous baser sur le fichier classification.txt qui décrit les catégories de classification à appliquer aux tables SQL et à certaines colonnes spécifiques.

Vous devrez également concevoir une classification similaire pour les fichiers CSV présents dans le Data Lake, en vous inspirant de la classification faîte précédemment sur les tables SQL.

Cet exercice vous permettra de maîtriser l’utilisation des outils de classification d’Azure Purview et d’enrichir un catalogue de données.

​

​

4. Mise en conformité RGPD avec la CNIL

Dans cette partie de la mission, vous allez formaliser la gestion des données en conformité avec le RGPD en remplissant un fichier de registre des traitements des données. Ce registre est un outil essentiel pour documenter l’utilisation des données personnelles, analyser les risques associés, et définir les mesures de protection adéquates.

Vous utiliserez un modèle de fichier fourni par la CNIL, que vous compléterez à partir des classifications et analyses réalisées dans la mission précédente. Ce travail vous permettra de relier la gouvernance des données techniques à leurs obligations réglementaires.
