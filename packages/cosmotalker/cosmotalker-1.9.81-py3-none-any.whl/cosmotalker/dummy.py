import os
import pickle
import subprocess
import sys
import importlib.util

def is_installed(package_name):
    return importlib.util.find_spec(package_name) is not None

def install_package(package_name, import_name=None, extra_args=None):
    import_name = import_name or package_name
    if not is_installed(import_name):
        try:
            command = [sys.executable, "-m", "pip", "install", package_name]
            if extra_args:
                command += extra_args
            subprocess.check_call(command)

            if package_name == "numpy":
                print('''In just a few minutes, you’ll be exploring the cosmos like never before — all from the comfort of your terminal.\n\nBuckle up, the universe is calling — and CosmoTalker is your launchpad.\n\nCrafted by Bhuvanesh M, it delivers celestial insights, satellite tracking, daily space pics, and eco-friendly web searches.\n\nWith both online and offline support, every search helps grow real trees through Ecosia.\n\nReady to code with purpose? Dive in at bhuvaneshm.in | linkedin.com/in/bhuvaneshm-developer''')
                print("\n\nPls wait, Installing...")
                print("16.667% of the installation is completed.")
            elif package_name == "pandas":
                print("33.334% of the installation is completed.")
            elif package_name == "sentence-transformers":
                print("50% of the installation is completed.")
            elif package_name == "transformers":
                print("66.667% of the installation is completed.")
            elif package_name == "faiss-cpu":
                print("83.334% of the installation is completed.")
            elif "torch" in package_name:
                print("100% of the installation is completed.")
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package_name}")

def summarize_ss_txt():
    from transformers import pipeline

    summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

    with open("ss.txt", "r", encoding="utf-8") as file:
        long_text = file.read()

    chunks = [long_text[i:i+1024] for i in range(0, len(long_text), 1024)]

    summary = ""
    for chunk in chunks:
        result = summarizer(chunk, max_length=130, min_length=30, do_sample=False)
        summary += result[0]["summary_text"] + " "

    lines = summary.strip().split('. ')
    paras = [". ".join(lines[i:i+5]) + '.' for i in range(0, 15, 5)]

    print("\n📘 Summary of ss.txt:\n")
    print("\n\n".join(paras))
    print("\n" + "="*50 + "\n")

def autoin():
    import numpy as np
    from sentence_transformers import SentenceTransformer

    if not os.path.exists("ss.txt"):
        print("❗ 'ss.txt' file not found.")
        return

    summarize_ss_txt()

    with open("ss.txt", "r", encoding="utf-8") as file:
        paragraphs = [p.strip() for p in file.read().split("\n\n") if p.strip()]

    chunks = []
    current_chunk = ""

    for para in paragraphs:
        if len(current_chunk) + len(para) + 2 <= 2000:
            current_chunk += para + "\n\n"
        else:
            chunks.append(current_chunk.strip())
            current_chunk = para + "\n\n"

    if current_chunk:
        chunks.append(current_chunk.strip())

    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode(chunks, show_progress_bar=True)

    if not os.path.exists("embeddings"):
        os.makedirs("embeddings")

    with open("embeddings/chunks.pkl", "wb") as f:
        pickle.dump(chunks, f)
    np.save("embeddings/vector_store.npy", embeddings)

    print(f"✅ {len(chunks)} chunks saved to 'embeddings/' folder.")

def talk():
    import numpy as np
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    import pickle
    from transformers import pipeline, AutoModelForQuestionAnswering, AutoTokenizer

    with open("embeddings/chunks.pkl", "rb") as f:
        chunks = pickle.load(f)
    embeddings = np.load("embeddings/vector_store.npy")

    model = SentenceTransformer("all-MiniLM-L6-v2")

    model_name = "deepset/roberta-base-squad2"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    qa_model = AutoModelForQuestionAnswering.from_pretrained(model_name)
    qa_pipeline = pipeline("question-answering", model=qa_model, tokenizer=tokenizer)

    print("\n🪐 Ask anything about cosmos (type 'exit' to quit):")
    while True:
        query = input("You: ")
        if query.lower() in ["exit", "quit"]:
            print("🚀 CosmoTalker signing off. Keep stargazing!")
            break

        query_vec = model.encode([query])
        scores = cosine_similarity(query_vec, embeddings)[0]
        top_indices = scores.argsort()[-1:][::-1]

        top_chunk = chunks[top_indices[0]].strip()
        answer = qa_pipeline(question=query, context=top_chunk)

        print("\n🔭 CosmoTalker:\n")
        print(answer["answer"])
        print("\n" + "-"*40 + "\n")

def cosmotalker():
    install_package("numpy")
    install_package("pandas")
    install_package("sentence-transformers", import_name="sentence_transformers")
    install_package("transformers")
    install_package("faiss-cpu", import_name="faiss")
    install_package("torch==2.6.0+cpu", import_name="torch", extra_args=["-f", "https://download.pytorch.org/whl/cpu/torch_stable.html"])

    if not os.path.exists("embeddings/vector_store.npy") or not os.path.exists("embeddings/chunks.pkl"):
        autoin()

    talk()

# Run
if __name__ == "__main__":
    cosmotalker()
