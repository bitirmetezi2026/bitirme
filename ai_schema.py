from pydantic import BaseModel, Field

class Macros(BaseModel):
    protein: float = Field(description="Tahmini protein miktari (gram bazinda)")
    carbs: float = Field(description="Tahmini karbonhidrat miktari (gram bazinda)")
    fat: float = Field(description="Tahmini yag miktari (gram bazinda)")

class FoodAnalysis(BaseModel):
    food_name: str = Field(description="Yemegin tahmini adi ve genel tanimi")
    portion: str = Field(description="Porsiyon bilgisi (orn: 1 tabak, 2 dilim, 150 gram vb.)")
    calories: float = Field(description="Tahmini toplam kalori degeri")
    macros: Macros = Field(description="Besin ögesi makro degerleri")

class ValidatorFeedback(BaseModel):
    is_valid: bool = Field(description="Diyetisyenin hesapladigi porsiyon ve kalori/makro verileri mantikliysa True, aksi halde False")
    feedback: str = Field(description="Eger is_valid False ise, diyetisyene neyin yanlis oldugunu aciklayan geri bildirim metni. (Orn: 'Bir elma 5000 kalori olamaz, lutfen daha dusuk ve gercekci hesapla'). Eger gecerliyse bos. ")
