# cosmotalker_chatbot.py

import re

# Simulate online features (mocked functions)
def apod():
    return "[📷 Astronomy Picture of the Day] - 'A stunning view of the Orion Nebula captured today by NASA.'"

def spacex():
    return "[🚀 SpaceX Update] - 'Falcon 9 set to launch Starlink satellites tomorrow at 14:30 UTC.'"

def wiki(query):
    return f"[🌐 Wikipedia Summary for '{query}']\nA {query} is a scientifically fascinating subject with much to explore."

def search(query):
    return f"[🌍 Ecosia Search] - Searching online for '{query}'..."

# Load offline data from file
with open("data.txt", "r", encoding="utf-8") as file:
    data = file.read()

# Extract headings and entries using regex
entries = re.findall(r"== (.*?) ==\n(.*?)(?=\n== |\Z)", data, re.DOTALL)
knowledge_base = {key.strip().lower(): value.strip() for key, value in entries}

# Main chat loop
print("✨ Welcome to CosmoTalker v1.8.3!")
print("Type 'exit' to quit. Ask me about planets, missions, SpaceX, APOD, or Wikipedia topics.")

while True:
    user_input = input("\nYou: ").lower()
    if user_input in ["exit", "quit"]:
        print("👋 Goodbye, explorer!")
        break

    # Extract keywords from user input
    words = re.findall(r"\b\w+\b", user_input)

    found = False
    responded = set()

    for word in words:
        word = word.strip().lower()

        if word in responded:
            continue

        if word in knowledge_base:
            print(f"\n[📘 {word.capitalize()}]\n{knowledge_base[word]}")
            found = True
            responded.add(word)

        elif word == "apod":
            print(f"\n{apod()}")
            found = True
            responded.add(word)

        elif word == "spacex":
            print(f"\n{spacex()}")
            found = True
            responded.add(word)

        elif word == "wiki":
            topic = input("🌐 What topic do you want from Wikipedia? ")
            print(f"\n{wiki(topic)}")
            found = True
            responded.add("wiki")

        elif word == "search":
            topic = input("🔎 What do you want to search? ")
            print(f"\n{search(topic)}")
            found = True
            responded.add("search")

    if not found:
        print("🤖 Sorry, I couldn't find information on that. Try asking about a planet, mission, or cosmic topic.")

