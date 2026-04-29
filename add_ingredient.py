with open('CalorieCalculator/app/src/main/java/com/example/caloriecalculator/MainActivity.kt', 'r', encoding='utf-8') as f:
    content = f.read()

import_pos = content.rfind('import')
end_of_imports = content.find('\n', import_pos)

content = content[:end_of_imports] + '\n\ndata class IngredientItem(val name: String, val amount: String)\n' + content[end_of_imports:]

with open('CalorieCalculator/app/src/main/java/com/example/caloriecalculator/MainActivity.kt', 'w', encoding='utf-8') as f:
    f.write(content)
print("Added IngredientItem")
