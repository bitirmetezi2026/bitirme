from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from schema import FoodAnalysis

def run_dietitian_agent(vision_description: str, feedback: str = None) -> FoodAnalysis:
    """
    Takes the detailed textual description from the vision agent and predicts portion, calories and macros.
    If there is validator feedback, uses it to improve the prediction.
    """
    llm = ChatOpenAI(model="gpt-4o", temperature=0.2)
    structured_llm = llm.with_structured_output(FoodAnalysis)
    
    system_prompt = """Sen uzman bir diyetisyensin. Görevin, sana verilen detaylı yemek görseli betimlemesini okuyup, yemeğin adını, porsiyon miktarını, toplam kalorisini ve makro değerlerini (protein, karbonhidrat, yağ gramajı) çok hassas ve en tutarlı şekilde tahmin etmektir. Dönüşünü JSON olarak istenilen yapıda yapmalısın. Eğer sana bir 'Geri Bildirim (Feedback)' verildiyse, önceki tahminin yanlış demektir, bu geri bildirime göre değerlerini düzelt!"""
    
    user_prompt = f"Yemek Betimlemesi: {vision_description}"
    
    if feedback:
        user_prompt += f"\n\nUYARI - Denetmen Ajanından Geri Bildirim: {feedback}\nLütfen bu eleştiriyi dikkate alarak hesaplamalarını revize et."
        
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]
    
    result = structured_llm.invoke(messages)
    return result
