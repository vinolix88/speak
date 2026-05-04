import os
import re

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    modified = False
    # Добавляем пустую строку в конец, если её нет
    if lines and not lines[-1].endswith('\n'):
        lines.append('\n')
        modified = True
    # Добавляем две пустые строки перед функциями/классами (кроме первого)
    new_lines = []
    prev_blank = 0
    for i, line in enumerate(lines):
        if re.match(r'^(async\s+)?def\s+\w+\(|^class\s+\w+', line) and i > 0:
            # Считаем количество пустых строк перед этой строкой
            blank_count = 0
            j = i-1
            while j >= 0 and lines[j].strip() == '':
                blank_count += 1
                j -= 1
            if blank_count < 2:
                # Добавляем недостающие пустые строки
                for _ in range(2 - blank_count):
                    new_lines.append('\n')
                    modified = True
        new_lines.append(line)
    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f"Fixed: {filepath}")
    else:
        print(f"OK: {filepath}")

def main():
    base_dir = "app"
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.py'):
                fix_file(os.path.join(root, file))
    # Дополнительно исправим главные файлы
    for file in ["app/main.py", "app/schemas/chat.py", "app/schemas/message.py"]:
        if os.path.exists(file):
            fix_file(file)

if __name__ == "__main__":
    main()