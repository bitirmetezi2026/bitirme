import os
import base64
from typing import TypedDict, List
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

# Define Pydantic models for structured output
class Recipe(BaseModel):
    name: str = Field(description="Yemeğin adı")
    description: str = Field(description="Yemeğin kısa bir açıklaması ve neden sağlıklı olduğu")
    ingredients: List[str] = Field(description="Kullanılacak malzemelerin listesi")
    steps: List[str] = Field(description="Adım adım hazırlanış tarifi")
    calories: str = Field(description="Tahmini kalori miktarı")

class RecipeRecommendations(BaseModel):
    recipes: List[Recipe] = Field(description="Önerilen 2-3 sağlıklı tarifin listesi")

class IngredientsList(BaseModel):
    ingredients: List[str] = Field(description="Görselde tespit edilen tüm yiyecek malzemelerinin listesi")

# Define the Agent State
class AgentState(TypedDict):
    image_base64: str
    ingredients: List[str]
    recipes: dict
    kalan_kalori: str
    kisitlamalar: str

def extract_ingredients_node(state: AgentState):
    """
    Node that takes the image and uses GPT-4o to identify ingredients.
    """
    image_base64 = state["image_base64"]
    
    # Initialize the vision model
    llm = ChatOpenAI(model="gpt-4o", temperature=0.0)
    # We use with_structured_output to force the model to output a JSON matching our schema
    structured_llm = llm.with_structured_output(IngredientsList)
    
    # Base64 encoded image formatting for OpenAI
    image_url = f"data:image/jpeg;base64,{image_base64}"
    
    messages = [
        SystemMessage(content="Sen uzman bir aşçı yardımcısısın. Sana verilen fotoğraftaki tüm yiyecek ve malzemeleri tespit edip listelemelisin. Sonucu Türkçe hazırlamalısın."),
        HumanMessage(
            content=[
                 {"type": "text", "text": "Bu fotoğrafta hangi malzemeler var?"},
                 {
                     "type": "image_url",
                     "image_url": {
                         "url": image_url
                     }
                 }
            ]
        )
    ]
    
    # Invoke model
    response = structured_llm.invoke(messages)
    
    return {"ingredients": response.ingredients}

def recipe_generator_node(state: AgentState):
    """
    Node that takes the extracted ingredients and generates diet-friendly recipes.
    """
    ingredients = state["ingredients"]
    
    llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
    structured_llm = llm.with_structured_output(RecipeRecommendations)
    
    ingredients_str = "\n- ".join(ingredients)
    
    diet_info = ""
    if state.get("kisitlamalar"):
        diet_info += f"\nKullanıcının diyet kısıtlamaları ve rahatsızlıkları: {state['kisitlamalar']}. DİKKAT: Gösterilen veya listelenen malzemeler arasında bu yasaklı listeye girenler varsa ASLA tarifine dahil etme (örneğin laktoz intoleransı varsa asla sütlü/peynirli bir tarif önerme)."
    
    if state.get("kalan_kalori") and state.get("kalan_kalori") != "0":
        diet_info += f"\nDİKKAT! Kullanıcının bugünkü KALAN KALORİ HAKKI: {state['kalan_kalori']} kcal. Lütfen önereceğin yemek tarifinin porsiyon kalorisi bu kalori miktarına olabildiğince uygun olsun. Eğer fotoğraftaki malzemeler bu enerjiye yetmiyorsa ve çok düşük kalorili kalıyorsa, tarifin yanına ek olarak sağlıklı atıştırmalıklar (örneğin X adet kaloriye denk gelecek ceviz, badem, yoğurt vb.) önererek kaloriyi kullanıcının kalan hedefine yaklaştır."

    system_prompt = f"""
Sen usta bir şef ve uzman bir diyetisyensin. Kullanıcının elindeki malzemelerle yapabileceği 2 veya 3 tane sağlıklı, dengeli ve lezzetli yemek tarifi önermeni istiyorum.
Tarifleri tamamen TÜRKÇE dilinde detaylı olarak vermelisin.
{diet_info}

Kullanıcının elindeki malzemeler:
- {ingredients_str}

Lütfen sadece bu malzemeleri ağırlıklı kullanarak (yağ, tuz, baharat gibi temel mutfak ürünlerini dahil edebilirsin) yaratıcı ve kısıtlamaları ihlal etmeyen tarifler üret.
    """
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content="Bana bu malzemelerle yapabileceğim sağlıklı tarifler öner.")
    ]
    
    # Invoke model
    response = structured_llm.invoke(messages)
    
    # Return as dict for the state
    recipes_dict = response.model_dump() if hasattr(response, "model_dump") else response.dict()
    return {"recipes": recipes_dict}

# Build the LangGraph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("extract_ingredients", extract_ingredients_node)
workflow.add_node("generate_recipes", recipe_generator_node)

# Add edges
workflow.set_entry_point("extract_ingredients")
workflow.add_edge("extract_ingredients", "generate_recipes")
workflow.add_edge("generate_recipes", END)

# Compile graph
app_graph = workflow.compile()

def process_fridge_image(image_bytes: bytes, kalan_kalori: str = None, kisitlamalar: str = None) -> dict:
    """
    Main entry point function to process an image and return recipe recommendations.
    """
    image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    
    # Run the graph
    initial_state = {
        "image_base64": image_base64,
        "ingredients": [],
        "recipes": {},
        "kalan_kalori": kalan_kalori or "",
        "kisitlamalar": kisitlamalar or ""
    }
    
    final_state = app_graph.invoke(initial_state)
    return final_state
