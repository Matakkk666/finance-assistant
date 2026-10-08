with open('src/services/llm.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

lines[17] = '    prompt = (\n        "Ты умный финансовый ассистент. "\n        "Твоя задача — категоризировать список транзакций.\\n\\n"\n    )\n'

with open('src/services/llm.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
