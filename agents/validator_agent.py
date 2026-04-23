from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from ai_schema import FoodAnalysis, ValidatorFeedback

def run_validator_agent(vision_description: str, food_analysis: FoodAnalysis) -> ValidatorFeedback:
    """
    Checks if the dietitian's analysis makes sense given the visual description.
    """
    llm = ChatOpenAI(model="gpt-5.4", temperature=0)
    structured_llm = llm.with_structured_output(ValidatorFeedback)
    
    system_prompt = """Sen kıdemli bir denetici diyetisyensin. Görevin, asistan diyetisyenin yaptığı kalori ve makro hesaplamalarının mantıklı ve gerçekçi olup olmadığını kontrol etmektir. 
Sana yemeğin görsel betimlemesi ve asistanın hazırladığı analiz raporu (kalori, porsiyon ve makrolar) verilecek.
Eğer sayılar çok saçmaysa (Örneğin: Bir adet elma için 5000 kalori demişse veya küçücük bir kahveye 50 gr protein yazmışsa) 'is_valid' değerini False yap ve 'feedback' kısmına neden mantıksız olduğunu, diyetisyenin neyi düzeltmesi gerektiğini detaylıca açıkla.
Eğer hesaplamalar mantıklı sınırlardaysa 'is_valid' değerini True yap ve 'feedback' kısmını boş bırak."""

    user_prompt = f"""
Görsel Betimleme: {vision_description}

Denetlenecek Asistan Raporu:
- Yemek Adı: {food_analysis.food_name}
- Porsiyon: {food_analysis.portion}
- Kalori: {food_analysis.calories} kcal
- Makrolar: Protein {food_analysis.macros.protein}g, Karb {food_analysis.macros.carbs}g, Yağ {food_analysis.macros.fat}g
"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]
    
    result = structured_llm.invoke(messages)
    return result
