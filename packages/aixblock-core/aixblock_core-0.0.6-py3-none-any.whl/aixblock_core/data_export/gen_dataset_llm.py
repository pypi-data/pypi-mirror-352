import os 
import json
from sklearn.model_selection import train_test_split


def gen_dataset_llm(data, tmp_dir):
    dataset = []
    for item in data:
        annotations = item.get("annotations", [])
        input_text = ""
        output_text = ""

        for annotation in annotations:
            result = annotation.get("result", [])
            for res in result:
                from_name = res.get("from_name", "")
                if from_name == "question":
                    input_text = res.get("value", {}).get("text", "")
                    if isinstance(input_text, list):
                        input_text = input_text[0]
                elif from_name == "answer":
                    output_text = res.get("value", {}).get("text", "")
                    if isinstance(output_text, list):
                        output_text = output_text[0]

        instruction_text = item.get("data", {}).get("text", "")

        dataset.append({
            "instruction": instruction_text,
            "input": input_text,
            "output": output_text
        })
    
    train_data, test_data = train_test_split(dataset, test_size=0.2, random_state=42)

    # Tạo thư mục tạm thời nếu nó chưa tồn tại
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)

    # Ghi tập train và tập test vào file JSON
    with open(os.path.join(tmp_dir, 'train_data.json'), 'w') as train_file:
        json.dump(train_data, train_file, ensure_ascii=False, indent=4)

    with open(os.path.join(tmp_dir, 'test_data.json'), 'w') as test_file:
        json.dump(test_data, test_file, ensure_ascii=False, indent=4)