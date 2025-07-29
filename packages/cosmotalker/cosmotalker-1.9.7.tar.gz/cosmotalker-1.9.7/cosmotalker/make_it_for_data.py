import os

def make_it_for_data():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ss_path = os.path.join(base_dir, "ss.txt")
    knowledge_path = os.path.join(base_dir, "celestial_knowledge.txt")
    output_path = os.path.join(base_dir, "data.txt")

    # Step 1: Read and parse celestial_knowledge.txt
    with open(knowledge_path, 'r', encoding='utf-8') as f:
        knowledge_lines = f.readlines()

    knowledge_dict = {}
    current_topic = None
    buffer = []

    for line in knowledge_lines:
        if line.startswith("== Topic: ") and "==" in line:
            if current_topic and buffer:
                knowledge_dict[current_topic.strip(",")] = ''.join(buffer).strip()
            current_topic = line.replace("== Topic: ", "").replace("==", "").strip()
            buffer = []
        elif current_topic:
            buffer.append(line)

    if current_topic and buffer:
        knowledge_dict[current_topic.strip(",")] = ''.join(buffer).strip()

    # Step 2: Read ss.txt and extract first-word keywords
    with open(ss_path, 'r', encoding='utf-8') as f:
        ss_lines = f.readlines()

    used_keywords = set()
    output_lines = []

    for line in ss_lines:
        if line.strip() == '':
            continue
        keyword = line.split()[0].strip(",")
        if keyword not in used_keywords and keyword in knowledge_dict:
            output_lines.append(f"== {keyword} ==\n{knowledge_dict[keyword]}\n\n")
            used_keywords.add(keyword)

    # Step 3: Write to data.txt
    with open(output_path, "w", encoding="utf-8") as f:
        f.writelines(output_lines)

    print(f"✅ Data saved")

# Run the function
if __name__ == "__main__":
    make_it_for_data()
