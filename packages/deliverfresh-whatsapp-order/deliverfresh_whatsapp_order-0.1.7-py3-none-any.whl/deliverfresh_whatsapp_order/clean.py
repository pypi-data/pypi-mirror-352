import re

def normalize(text):
    text = text.lower().strip()
    text = re.sub(r"[.,:;!?]+$", "", text)
    text = re.sub(r"\b(1g|lg|kgs?|kg|250gram|500gram|600gram|11g|1lg|no|./)\b", "", text)
    text = re.sub(r"\bof red tomato\b", "tomato", text)

    replacements = {
        r"\bpotatoes\b": "potato",
        r"\btomatoes\b": "tomato",
        r"\bcarrots\b": "carrot",
        r"\bonions\b": "onion",
        r"\bcabbages\b": "cabbage",
        r"\bcauliflowers\b": "cauliflower",
        r"\bspring onions\b": "spring onion",
        r"\bchillies\b": "chilli",
        r"\bbags?\b": "bag",
        r"\bbunches\b": "bunch",
        r"\bboxe?s\b": "box",
        r"\bbhajji\b": "bhaji",
        r"\braddish\b": "radish",
        r"\bpeeld garlic\b": "peeled garlic",
        r"\blemons\b": "lemon"
    }

    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text)

    text = re.sub(r"\d+", "", text)  # remove numbers
    text = re.sub(r"deliverfresh( customer care| team)?", "", text)
    text = text.replace("www.deliverfresh.au", "")
    text = text.replace("-", "")
    return text.strip()

def clean_chat_file(input_file, output_file):
    with open(input_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    date_pattern = re.compile(r"^\d{1,2}/\d{1,2}/\d{2,4},\s+\d{1,2}:\d{2}")
    quantity_pattern = re.compile(r"\b\d+\s*(kg|g|gm|bunch|box|bag|pcs?|pieces?)\b", re.IGNORECASE)
    number_pattern = re.compile(r"\b\d+\b")
    exclude_starts = ["thank", "thanks"]
    exclude_contains = [
        "@", "??", "doing well", "i hope", "warm regards", "please", "sorry",
        "all good", "appreciate", "delivery", "today", "<this message was edited>",
        "or", "we hope you're well", "you need"
    ]

    cleaned_lines = []
    seen = set()

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if date_pattern.match(line):
            continue
        if any(line.lower().startswith(kw) for kw in exclude_starts):
            continue
        if any(phrase in line.lower() for phrase in exclude_contains):
            continue
        if len(line.split()) > 8:
            continue

        line = quantity_pattern.sub("", line)
        line = number_pattern.sub("", line)
        line = line.replace("$", "").replace("/kg", "").replace(":", "").strip()
        line = normalize(line)

        if line and line not in seen:
            cleaned_lines.append(line)
            seen.add(line)

    cleaned_lines = sorted(cleaned_lines)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(cleaned_lines))
