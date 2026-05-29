import os
from langchain_chroma import Chroma
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from vector_store import get_embedding_model, DB_DIR

def format_docs(docs):
    """
    Formate les documents récupérés pour les intégrer proprement dans le prompt.
    """
    formatted = []
    for doc in docs:
        source_name = os.path.basename(doc.metadata.get('source', 'Inconnue'))
        page_num = doc.metadata.get('page', 0) + 1
        formatted.append(f"--- Extrait de {source_name} (Page {page_num}) ---\n{doc.page_content}")
    return "\n\n".join(formatted)

def create_rag_chain():
    """
    Construit la chaîne de traitement RAG complète avec LangChain.
    """
    print("🤖 Configuration du modèle de langage Ollama (Llama 3.2)...")
    # Initialisation du LLM local via Ollama
    llm = ChatOllama(
        model="llama3.2",
        temperature=0.0  # Température à 0 pour éviter au maximum les hallucinations
    )
    
    # Récupération du modèle d'embedding pour se connecter à la base
    embeddings = get_embedding_model()
    
    if not os.path.exists(DB_DIR):
        raise FileNotFoundError(f"La base vectorielle n'existe pas dans {DB_DIR}. Lancez d'abord vector_store.py")
        
    db = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)
    # Configuration du chercheur (retriever) pour extraire les 3 morceaux les plus proches
    retriever = db.as_retriever(search_kwargs={"k": 3})
    
    # Structure du prompt de sécurité pour l'entreprise
    template = """Tu es un assistant IA professionnel et rigoureux pour une entreprise. 
Tu dois répondre à la question posée en te basant UNIQUEMENT sur le contexte fourni ci-dessous.
Si la réponse ne se trouve pas dans le contexte, dis clairement et poliment que tu ne trouves pas l'information dans les documents de l'entreprise. 
N'invente rien et ne fais pas de suppositions.

Contexte des documents internes :
{context}

Question de l'utilisateur : {question}

Réponse professionnelle détaillée :"""
    
    prompt = ChatPromptTemplate.from_template(template)
    
    # Assemblage de la chaîne avec le langage d'expression LangChain (LCEL)
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return rag_chain

if __name__ == "__main__":
    print("--- LANCEMENT DE L'ASSISTANT IA ENTREPRISE (RAG) ---")
    try:
        # Initialisation de la chaîne
        chain = create_rag_chain()
        
        # Exemple de question. Modifiez-la selon vos documents (ex: sur une facture de David N'ZASSI ou le relevé de Sonia)
        #ma_question = "Quel est le montant total à payer pour le renouvellement de l'assurance habitation, incluant les taxes et les frais ?"
        #ma_question = "Quel est le montant total HT de la facture de catering d'avril 2021 et quel est le taux de TVA ?"
        ma_question = "Quelle est la prime pour le terme de l'assurance habitation, avant les frais et les taxes ?"
        print(f"\n❓ Question posée : {ma_question}")
        print("⏳ L'IA analyse les documents et rédige la réponse...")
        
        reponse = chain.invoke(ma_question)
        
        print("\n💡 Réponse de l'IA :")
        print(reponse)
        
    except Exception as e:
        print(f"❌ Une erreur est survenue dans le pipeline RAG : {e}")