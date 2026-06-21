from typing import Any, Dict
from ..state import GraphState

def out_of_domain(state: GraphState) -> Dict[str, Any]:
    """
    Diyet dışı soruları reddeder.
    """
    print("---OUT OF DOMAIN---")
    question = state["question"]
    
    # Reddetme mesajını direkt `generation` içine atıyoruz
    generation = "Ben bir Diyetisyen Asistanıyım. Sadece sağlık, beslenme, kalori ve diyetinizle ilgili sorularınıza yanıt verebilirim. Lütfen bu kapsamda bir soru sorunuz."
    
    return {"generation": generation, "question": question, "documents": []}
