from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI

def run_vision_agent(image_data: str) -> str:
    """
    Takes base64 image or url, calls GPT-4o, and returns a detailed textual description of the food.
    """
    llm = ChatOpenAI(model="gpt-5.4", temperature=0.1)
    
    prompt = "Bu görseldeki yemeği çok detaylı şekilde analiz et. Tabaktaki yiyeceklerin türü, tahmini pişirme yöntemi, porsiyon boyutu hakkında gördüklerini aktar. Sadece gördüklerini söyle, kalori hesaplamaya çalışma, onu bir sonraki ajan yapacak."
    
    message = HumanMessage(
        content=[
            {"type": "text", "text": prompt},
            {
                "type": "image_url",
                "image_url": {
                    "url": image_data
                }
            }
        ]
    )
    
    response = llm.invoke([message])
    return response.content
