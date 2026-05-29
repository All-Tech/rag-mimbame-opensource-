import os
from typing import List
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

# Définition des chemins locaux
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_DIR = os.path.join(BASE_DIR, "data", "vector_db")
from langchain_postgres import PGVector

# Lien de connexion vers votre base Postgres (local ou cloud)
CONNECTION_STRING = "postgresql+psycopg://utilisateur:devadmin@localhost:5432/ma_base_ia"
COLLECTION_NAME = "documents_entreprise"

def create_vector_store_postgres(chunks, embeddings):
    print("💾 Stockage des vecteurs dans PostgreSQL...")
    
    vector_store = PGVector.from_documents(
        documents=chunks,
        embedding=embeddings,
        connection=CONNECTION_STRING,
        collection_name=COLLECTION_NAME,
        use_jsonb=True # Permet de stocker les metadata proprement en JSON
    )
    return vector_store

def get_embedding_model():
    """
    Initialise le modèle d'embedding. 
    Nous utilisons un modèle léger, très performant en français et 100% gratuit.
    """
    print("🧠 Chargement du modèle d'embedding (bge-m3)...")
    model_name = "BAAI/bge-m3"
    # we run it on CPU by default, change to 'cuda' if you have an Nvidia GPU
    model_kwargs = {'device': 'cpu'}
    encode_kwargs = {'normalize_embeddings': True}
    
    return HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )

def create_vector_store(chunks: List[Document], embeddings) -> Chroma:
    """
    Prend les morceaux de texte, les vectorise et les stocke dans la base ChromaDB.
    """
    print(f"💾 Initialisation de ChromaDB dans : {DB_DIR}...")
    
    # Création et sauvegarde locale de la base de données vectorielle
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=DB_DIR
    )
    
    print("✅ Base de données vectorielle créée et sauvegardée localement avec succès !")
    return vector_store

def query_vector_store(query: str, embeddings, k: int = 3):
    """
    Permet de tester la base en faisant une recherche par similarité.
    """
    # Connexion à la base existante
    db = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)
    
    print(f"🔍 Recherche des {k} morceaux les plus pertinents pour : '{query}'...")
    results = db.similarity_search(query, k=k)
    
    for i, doc in enumerate(results):
        print(f"\n📄 Résultat #{i+1} (Source: {doc.metadata.get('source', 'Inconnue')}) :")
        print(doc.page_content[:300] + "...")
    
    return results

if __name__ == "__main__":
    import sys
    # On permet à Python de trouver le module data_ingestion situé dans le même dossier
    from data_ingestion import load_documents_from_folder, split_documents

    print("--- PIPELINE CONFIGURATION: DU PDF À CHROMADB ---")
    
    # 1. Chemins des dossiers
    RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
    
    # 2. Étape d'ingestion (Étape 1)
    try:
        raw_docs = load_documents_from_folder(RAW_DATA_DIR)
        if len(raw_docs) == 0:
            print("⚠️ Aucun PDF trouvé dans data/raw. Fin du processus.")
            sys.exit()
            
        real_chunks = split_documents(raw_docs)
        
        # 3. Récupération du modèle d'embedding
        embeddings = get_embedding_model()
        
        # 4. Sauvegarde des VRAIS morceaux dans la base vectorielle (Étape 2)
        db = create_vector_store(real_chunks, embeddings)
        
        print("\n--- TEST DE RECHERCHE SUR VOS VRAIS DOCUMENTS ---")
        # 5. On fait une recherche test sur vos vrais documents
        # Modifiez cette phrase en fonction de ce qui se trouve dans votre PDF !
        query_vector_store("Revenu imposable ou montant fiscal", embeddings, k=2)
        
    except Exception as e:
        print(f"❌ Une erreur est survenue dans le pipeline : {e}")