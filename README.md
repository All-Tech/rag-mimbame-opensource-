# rag-mimbame-opensource-
## A. Titre d'impact et Description orientée "Business"
Titre : Assistant IA Souverain et Sécurisé pour l'Analyse de Documents d'Entreprise (RAG Open-Source)
Description : Ce PoC démontre comment une entreprise peut déployer un chatbot intelligent connecté à ses données internes (RH, fiches techniques, procédures) de manière 100% locale et sécurisée, sans envoyer aucune donnée à des tiers (OpenAI, Anthropic).

## B. Choix de la Stack Technique (Justifié !)

 - LLM Local : Mistral-7B-Instruct-v0.3 (quantifié en Q4_K_M via Ollama) pour un équilibre parfait entre performance en français et faible empreinte matérielle (exécutable sur un GPU de 8 Go à 12 Go de VRAM).

- Framework d'orchestration : LangChain ou LlamaIndex pour la flexibilité du pipeline.

- Base Vectorielle : ChromaDB (moteur local, évite l'abonnement à un service cloud managé).

- Interface : Streamlit ou Chainlit pour offrir une interface utilisateur intuitive en moins de 100 lignes de code.

## C Architecture du repo 
rag-entreprise-opensource/
│
├── .github/workflows/       # Optionnel : pour l'automatisation (CI/CD)
│
├── data/                    # DOSSIER TRÈS IMPORTANT
│   ├── raw/                 # Fichiers PDF/Docx d'exemples de l'entreprise
│   └── vector_db/           # Stockage local de votre base vectorielle (ex: ChromaDB)
│
├── src/                     # Code source de l'application
│   ├── __init__.py
│   ├── config.py            # Gestion des variables d'environnement, choix du LLM
│   ├── data_ingestion.py    # Extraction du texte et Chunking des documents
│   ├── vector_store.py      # Génération des Embeddings et stockage
│   └── rag_pipeline.py      # Gestion de la mémoire, du Prompt et de la requête au LLM
│
├── app.py                   # Interface utilisateur (Streamlit ou Chainlit)
├── Dockerfile               # Pour l'isolation et le déploiement en entreprise
├── requirements.txt         # Liste des dépendances Python (LangChain, Ollama, etc.)
├── .env.example             # Exemple de configuration (sans clés secrètes)
└── README.md                # LA VITRINE de votre projet (voir section suivante)

## D. Guide d'installation rapide (Le "Quick Start")
Un utilisateur doit pouvoir cloner votre projet et le lancer en 3 lignes de commande :
``git clone https://github.com/votre-nom/rag-entreprise-opensource.git
cd rag-entreprise-opensource
docker-compose up --build``

python -m pip install langchain langchain-community langchain-text-splitters pypdf



# exécuter 
python src/data_ingestion.py


## config postgres
python -m pip install psycopg2-binary langchain-postgres
choco install postgresql-pgvector
