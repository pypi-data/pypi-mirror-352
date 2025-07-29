import tempfile
import os
from deliverfresh_whatsapp_order import clean_chat_file

def test_clean_chat_file_basic():
    raw_input = """2kg tomatoes
1 box carrots
Thanks
We hope you're well
of red tomato
bhajji"""

    expected_lines = sorted([
        "bhaji",
        "carrot",
        "tomato"
    ])

    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as input_file:
        input_file.write(raw_input)
        input_path = input_file.name

    with tempfile.NamedTemporaryFile(mode="r+", delete=False) as output_file:
        output_path = output_file.name

    clean_chat_file(input_path, output_path)

    with open(output_path, "r") as f:
        result = sorted([line.strip() for line in f.readlines() if line.strip()])

    os.remove(input_path)
    os.remove(output_path)

    assert result == expected_lines