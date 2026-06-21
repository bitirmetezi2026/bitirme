# graph/graph.py

from dotenv import load_dotenv
load_dotenv()

from langgraph.graph import END, StateGraph

# Zincir (Chains) ve Yönlendirici (Router) importları
from .chains.answer_grader import answer_grader
from .chains.hallucination_grader import hallucination_grader
from .chains.router import question_router, RouteQuery

# Düğüm sabitleri ve Durum (State) importları
from .node_constants import RETRIEVE, GRADE_DOCUMENTS, GENERATE, WEBSEARCH
from .state import GraphState

# Düğüm (Node) fonksiyonlarının import edilmesi
# DİKKAT: get_user_profile importunu SİLDİK.
from .nodes.generate import generate
from .nodes.grade_documents import grade_documents
from .nodes.out_of_domain import out_of_domain
from .nodes.retrieve import retrieve
from .nodes.web_search import web_search

# --- Karar ve Yönlendirme Fonksiyonları ---
OUT_OF_DOMAIN = "out_of_domain"

def decide_to_generate(state: GraphState) -> str:
    print("--- DEĞERLENDİRME: Alınan Belgeler İnceleniyor ---")
    filtered_documents = state.get("documents", [])

    if not filtered_documents:
        print("--- KARAR: Alakalı belge bulunamadı. Web araması başlatılıyor. ---")
        return WEBSEARCH
    else:
        print("--- KARAR: Alakalı belgeler bulundu. Cevap üretme aşamasına geçiliyor. ---")
        return GENERATE


def grade_generation_grounded_in_documents_and_question(state: GraphState) -> str:
    print("--- DEĞERLENDİRME: Cevap Halüsinasyon Kontrolü ---")
    question = state["question"]
    documents = state["documents"]
    generation = state["generation"]

    # Selamlama ve basit sohbetler için halüsinasyon kontrolünü atla
    q_lower = question.lower().strip()
    greetings = ["selam", "merhaba", "naber", "nasılsın", "günaydın", "iyi akşamlar", "hey", "hi", "kimsin", "kendinden bahset"]
    if any(word in q_lower for word in greetings) or len(q_lower) < 20:
        print("--- KARAR: Basit sohbet/selamlama algılandı. Doğrudan bitiş. ---")
        return "useful"

    score = hallucination_grader.invoke(
        {"documents": documents, "generation": generation}
    )

    if score.binary_score:
        print("--- KARAR: Cevap belgelere dayanıyor. ---")
        print("--- DEĞERLENDİRME: Cevap Soruyu Yanıtlıyor mu? ---")

        score = answer_grader.invoke({"question": question, "generation": generation})
        if score.binary_score:
            print("--- KARAR: Cevap soruyu başarılı bir şekilde yanıtlıyor. Bitiş. ---")
            return "useful"
        else:
            print("--- KARAR: Cevap soruyu yanıtlamıyor. Web araması denenmeli. ---")
            return "not useful"
    else:
        print("--- KARAR: Cevap belgelere dayanmıyor. Tekrar üretme denenmeli. ---")
        return "not supported"


def route_question(state: GraphState) -> str:
    print("--- YÖNLENDİRME: Gelen Soru Analiz Ediliyor ---")
    question = state["question"]
    source: RouteQuery = question_router.invoke({"question": question})

    if source.datasource == WEBSEARCH:
        print(f"--- KARAR: Soru '{source.datasource}'e yönlendirildi. ---")
        return WEBSEARCH
    elif source.datasource == "vectorstore":
        print(f"--- KARAR: Soru '{source.datasource}'e (RAG) yönlendirildi. ---")
        return RETRIEVE
    else:
        print("--- KARAR: Kapsam dışı soru tespit edildi. ---")
        return OUT_OF_DOMAIN


# --- GRAFİK (WORKFLOW) OLUŞTURMA ---

workflow = StateGraph(GraphState)

# 1. Adım: Düğümleri (Nodes) Ekle (get_user_profile siliyoruz)
workflow.add_node(RETRIEVE, retrieve)
workflow.add_node(GRADE_DOCUMENTS, grade_documents)
workflow.add_node(GENERATE, generate)
workflow.add_node(WEBSEARCH, web_search)
workflow.add_node(OUT_OF_DOMAIN, out_of_domain)



# 2. Adım: Grafiğin Başlangıç Noktasını Belirle
# DİKKAT: Artık veritabanı beklemediğimiz için grafiğe direkt "Şartlı Giriş" yapıyoruz.
workflow.set_conditional_entry_point(
    route_question,
    {
        WEBSEARCH: WEBSEARCH,
        RETRIEVE: RETRIEVE,
        OUT_OF_DOMAIN: OUT_OF_DOMAIN,
    },
)

# 3. Adım: Kenarları (Edges) ve Akışı Tanımla
workflow.add_edge(RETRIEVE, GRADE_DOCUMENTS)

workflow.add_conditional_edges(
    GRADE_DOCUMENTS,
    decide_to_generate,
    {
        WEBSEARCH: WEBSEARCH,
        GENERATE: GENERATE,
    },
)

workflow.add_edge(WEBSEARCH, GENERATE)
workflow.add_edge(OUT_OF_DOMAIN, END)

workflow.add_conditional_edges(
    GENERATE,
    grade_generation_grounded_in_documents_and_question,
    {
        "not supported": GENERATE,
        "useful": END,
        "not useful": WEBSEARCH,
    },
)

# 4. Adım: Grafiği Derle
app = workflow.compile()