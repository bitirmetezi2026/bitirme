import os
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

from agents.vision_agent import run_vision_agent
from agents.dietitian_agent import run_dietitian_agent
from agents.validator_agent import run_validator_agent
from ai_schema import FoodAnalysis, ValidatorFeedback
from ai_utils import get_image_data

from dotenv import load_dotenv
load_dotenv()

class AgentState(TypedDict):
    image_source: str
    image_data: str
    vision_description: str
    food_analysis: FoodAnalysis
    validator_feedback: ValidatorFeedback
    revision_count: int

def init_node(state: AgentState):
    print("\n[Aşama 1] Sistem Hazırlanıyor...")
    source = state["image_source"]
    img_data = get_image_data(source)
    return {"image_data": img_data, "revision_count": 0}

def vision_node(state: AgentState):
    print("[Aşama 2] Vision Agent (Görüntü Analizi) çalışıyor...")
    desc = run_vision_agent(state["image_data"])
    print(f"    > Gözlem: {desc[:100]}...")
    return {"vision_description": desc}

def dietitian_node(state: AgentState):
    rev = state.get('revision_count', 0)
    print(f"[Aşama 3] Diyetisyen Agent ({rev + 1}. Hesaplama) devrede...")
    
    feedback_str = None
    if state.get("validator_feedback") and not state["validator_feedback"].is_valid:
        feedback_str = state["validator_feedback"].feedback
        
    analysis = run_dietitian_agent(state["vision_description"], feedback=feedback_str)
    print(f"    > Tahmin: {analysis.food_name} / {analysis.calories} kcal")
    return {"food_analysis": analysis}

def validator_node(state: AgentState):
    print("[Aşama 4] Denetmen Agent (Doğrulama) başlatıldı...")
    feedback = run_validator_agent(state["vision_description"], state["food_analysis"])
    
    new_rev_count = state.get("revision_count", 0) + 1
    
    if feedback.is_valid:
        print("    > Denetmen Onayı: BAŞARILI! Mantıklı hesaplama.")
    else:
        print(f"    > Denetmen Onayı: REDDEDİLDİ! Gerekçe: {feedback.feedback}")
        
    return {"validator_feedback": feedback, "revision_count": new_rev_count}

def should_loop(state: AgentState):
    if state["validator_feedback"].is_valid:
        return "end"
    if state["revision_count"] >= 3:
        print("\n[Uyarı] Maksimum düzeltme denemesine ulaşıldı. Mevcut sonuç döndürülüyor.")
        return "end"
    
    print("\n[Bilgi] Diyetisyen yeniden çalışması için geri gönderildi...")
    return "dietitian"

workflow = StateGraph(AgentState)

workflow.add_node("init", init_node)
workflow.add_node("vision", vision_node)
workflow.add_node("dietitian", dietitian_node)
workflow.add_node("validator", validator_node)

workflow.add_edge(START, "init")
workflow.add_edge("init", "vision")
workflow.add_edge("vision", "dietitian")
workflow.add_edge("dietitian", "validator")
workflow.add_conditional_edges(
    "validator",
    should_loop,
    {"end": END, "dietitian": "dietitian"}
)

app = workflow.compile()
