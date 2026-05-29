# 1 function src/data_ingestion.py =La Brique de Chargement des données essentielle de notre RAG

Le but de ce script est simple mais crucial :
 prendre des documents d'entreprise (comme des PDF), les découper proprement en morceaux (chunks) sans perdre le contexte, et les préparer pour l'étape suivante.

# 2 function src/vector_store.py =La Base de Données Vectorielle
## objectif:
Maintenant que nos  morceaux de texte sont créés en mémoire, nous devons les transformer en "vecteurs" (en nombres) et les stocker dans notre base de données locale ChromaDB.
``python -m pip install chromadb langchain-chroma langchain-huggingface sentence-transformers`` # vectorisation

Pourquoi ChromaDB ? C'est une base de données vectorielle "embarquée". Cela signifie qu'elle ne nécessite pas d'installer un serveur lourd comme PostgreSQL ou Milvus. Elle écrit directement ses fichiers dans le dossier data/vector_db. Pour un PoC ou une PME, c'est la solution la plus économique et rapide à déployer.
### pourquoi  avoir configuré la base ainsi
1. Le modèle **BAAI/bge-m3** : C'est l'un des meilleurs modèles d'embedding open-source au monde. Sa force ? Il est multilingue (excellent en français) et prend en charge de longs textes. Il s'exécute localement sur le processeur (CPU) sans nécessiter de grosse carte graphique pour cette étape.

2. Pourquoi **ChromaDB** ? C'est une base de données vectorielle "embarquée". Cela signifie qu'elle ne nécessite pas d'installer un serveur lourd comme PostgreSQL ou Milvus. Elle écrit directement ses fichiers dans le dossier data/vector_db. Pour un PoC ou une PME, c'est la solution la plus économique et rapide à déployer.

3. La recherche par **similarité (similarity_search)** : Contrairement à une recherche par mot-clé classique (comme un Ctrl+F), si vous cherchez "impôt", le modèle comprend le sens et peut vous sortir un paragraphe qui parle de "fiscalité" ou de "taxes", même si le mot exact "impôt" n'y figure pas.

``python src/vector_store.py``
Le script va charger nos PDF (les 8 pages), le découper en 11 morceaux, calculer les vecteurs pour chacun de ces 11 morceaux, et les enregistrer définitivement dans notre base de données locale.

Ensuite, il va chercher les 2 morceaux les plus proches de votre question "Revenu imposable ou montant fiscal" et afficher le texte extrait du document. (Comme l'extraction de texte avait des caractères bizarres au début, vous risquez de voir ces caractères s'afficher, c'est normal, le processus technique, lui, est validé !).

## resultat
 -Notre script a scanné notre dossier et a trouvé d'autres documents (de  27 pages chargées, générant 173 morceaux de texte).

- La base a indexé tout cela.

La magie a opéré au Résultat #2 : nous avons cherché "Revenu imposable ou montant fiscal" et le système est allé chercher un document nommé facture_FASC04210332 (3).pdf (préparé par David N'ZASSI) parce qu'il y a détecté la section "Informations fiscales", le NIF (Numéro d'Identifiant Fiscal) et le Régime Réel.

Le système a parfaitement "compris" le sens de ma question et a extrait la bonne facture parmi mes 173 morceaux. 
**mon moteur de recherche de mon RAG est prêt et fonctionnel.**


# Ajout du "Cerveau" (Le LLM avec Ollama): moteur dinférence
## Objectif
Maintenant que notre base vectorielle est capable de sortir les morceaux de texte pertinents,
 nous pouvons donc envoyer ces morceaux à un grand modèle de langage (LLM) pour qu'il rédige une réponse intelligente et fluide à l'utilisateur, au lieu d'afficher du code brut.
 - installer ollama
 Pour que tout reste 100% local, gratuit et confidentiel sur notre machine, nous allons utiliser Ollama.
 Allez sur le site officiel : [](ollama.com) ou Gemma 3, DeepSeek-R1, Qwen3 et téléchargez l'application pour Windows
 ``ollama run llama3.2``
 (Le terminal va afficher une barre de progression pour télécharger le modèle d'environ 2 Go. Une fois le téléchargement fini, vous pourrez lui parler directement dans le terminal pour tester. Tapez **/exit** pour quitter le chat d'Ollama quand vous aurez fini).

 - 3. Installer l'outil de connexion Python
  installez la bibliothèque qui permet à LangChain de parler à Ollama :
  ``python -m pip install langchain-ollama``

  ## function src/rag_pipeline.py
  Le rôle de ce script est d'agir comme le chef d'orchestre (le pipeline RAG). Lorsqu'une question est posée, il va interroger ChromaDB pour obtenir les documents pertinents, injecter ces documents dans un "prompt sécurisé", et envoyer le tout à Ollama pour obtenir une réponse rédigée et précise

  #### explications
 - La température à 0.0 : Expliquez au client que par défaut, les IA sont créatives (température proche de 0.7). En la réglant à 0.0, vous forcez le modèle à être purement factuel et déterministe. S'il n'est pas sûr, il s'arrête au lieu d'inventer.

- Le chaînage LCEL (| prompt | llm) : C'est la syntaxe moderne de LangChain (LangChain Expression Language). Elle utilise le symbole de "pipe" (|) comme sous Linux pour faire passer la donnée d'un bloc à un autre. C'est propre, rapide et optimisé pour la production.

- Le formatage transparent (format_docs) : Le script fusionne le texte des morceaux trouvés tout en injectant de façon transparente les métadonnées (le nom du fichier et la page exacte). Cela donne au LLM tout ce qu'il faut pour être structuré.

## example de questions
1. Questions de précision (Pour valider l'extraction de données complexes)
   Ces questions vérifient si le modèle d'embedding (bge-m3) extrait les bons morceaux de texte et si le LLM restitue les chiffres exacts.Question : 
"Quel est le montant total à payer pour le renouvellement de l'assurance habitation, incluant les taxes et les frais ?"
 - Ce que l'IA doit trouver : 1 800,96 $ (répartis en 1 608,00 $de prime, 144,72$ de taxes et 48,24 $ de frais). 
 -  Question : "Quels sont les détails des prestations de catering fournies au mois d'avril 2021 ?"Ce que l'IA doit trouver : Les détails de la facture de catering de la Villa (Petit déjeuner, Déjeuner emporté, Dîner emporté, Extras).  
 -  Question : "Quelle est l'adresse de la propriété assurée par TD Assurance ?"
     Ce que l'IA doit trouver : 7400 RUE DE L'APOGEE, QUEBEC QC G3E 0K6. 
     
 2. Questions de logique et de conditions (Pour tester la compréhension du contexte)Ces questions forcent le LLM à analyser des règles ou des restrictions écrites dans les documents.Question : "À partir de quel âge l'exclusion s'applique-t-elle aux réservoirs de chauffe-eau et quel est le délai de grâce ?"Ce que l'IA doit trouver : L'exclusion s'applique aux réservoirs de 15 ans ou plus, mais il y a un délai de grâce d'un an (l'exclusion s'appliquera au renouvellement de l'année suivante).  Question : "Selon le nouvel avenant, comment sont réglées les réclamations pour des dommages causés à la toiture par le vent ou la grêle ?"Ce que l'IA doit trouver : Les réclamations sont limitées à la valeur dépréciée (selon l'âge et les matériaux) au lieu du coût de remplacement complet.  3. Questions de sécurité (Pour valider la consigne anti-hallucination)C'est le test le plus important pour un profil de consultant en IA. Vous devez poser une question sur un sujet complètement absent de vos documents pour vérifier si l'IA respecte le prompt de sécurité (votre garde-fou).Question : "Quelle est la marque de la voiture assurée dans le contrat de Serge Abaze ?"Ce que l'IA doit répondre : "Je ne trouve pas cette information dans les documents de l'entreprise." (ou une phrase similaire formulée poliment). Si elle invente une marque (ex: Toyota ou Honda), cela signifie que votre prompt ou vos paramètres de température doivent être resserrés.Question : "Quel est le nom du chef cuisinier qui a préparé le petit déjeuner en avril 2021 ?"Ce que l'IA doit répondre : Elle doit indiquer que le nom du chef n'est pas mentionné, prouvant qu'elle s'en tient strictement au contexte fourni.  