import os
from typing import List
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

def load_documents_from_folder(folder_path: str) -> List[Document]:
    """
    Charge tous les fichiers PDF présents dans un dossier spécifique.
    """
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Le dossier spécifié n'existe pas : {folder_path}")
    
    print(f"📂 Chargement des PDF depuis le dossier : {folder_path}...")
    loader = PyPDFDirectoryLoader(folder_path)
    documents = loader.load()
    print(f"✅ {len(documents)} pages chargées avec succès.")
    return documents

def split_documents(documents: List[Document], chunk_size: int = 500, chunk_overlap: int = 50) -> List[Document]:
    """
    Découpe les documents en morceaux (chunks) optimisés pour le RAG.
    """
    print(f"✂️ Découpe des documents en blocs (Taille : {chunk_size}, Chevauchement : {chunk_overlap})...")
    
    # Utilisation du splitter recommandé pour le texte général
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", " ", ""]  # Découpe intelligemment aux paragraphes, puis phrases
    )
    
    chunks = text_splitter.split_documents(documents)
    print(f"🧠 Création de {len(chunks)} morceaux (chunks) prêts pour la vectorisation.")
    return chunks

# Bloc de test pour valider le script de manière autonome
if __name__ == "__main__":
    # On définit des chemins relatifs propres à notre architecture de projet
    RAW_DATA_DIR = os.path.join(os.path.dirname(__file__), "../data/raw")
    
    # Créer le dossier s'il n'existe pas pour éviter les erreurs au premier lancement
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    
    print("--- TEST DU MODULE D'INGESTION ---")
    try:
        raw_docs = load_documents_from_folder(RAW_DATA_DIR)
        if len(raw_docs) == 0:
            print(f"⚠️ Le dossier '{RAW_DATA_DIR}' est vide. Ajoutez-y un fichier PDF pour tester.")
        else:
            final_chunks = split_documents(raw_docs)
            # Affichage d'un exemple pour vérifier visuellement la structure
            print("\n🔍 Aperçu du premier chunk :")
            print(final_chunks[0].page_content[:200] + "...")
            print(f"Metadata associées : {final_chunks[0].metadata}")
    except Exception as e:
        print(f"❌ Une erreur est survenue : {e}")