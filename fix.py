with open('src/services/chat.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines):
    if l.strip() == '':
        lines[i] = '\n'

with open('src/services/chat.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

with open('tests/test_chat.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, l in enumerate(lines):
    if 'WHERE id=1;' in l:
        lines[i] = l.replace('SELECT SUM(amount) FROM transactions WHERE id=1', 'SELECT * FROM t WHERE id=1')
    if l.strip() == '':
        lines[i] = '\n'

with open('tests/test_chat.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)
