# ✨ Welcome to CosmoTalker v1.9 - Your Gateway to the Cosmos!

🚀 **CosmoTalker v1.8.7** is here! Explore space and science effortlessly with this offline Python library, now with a **beta image preview tool**, **enhanced data library**, **improved deep search algorithm**, **better response accuracy**, and **new cosmic event tracking**!

## 🌠 About CosmoTalker

Developed by **Bhuvanesh M**, CosmoTalker is a Python library that brings knowledge of celestial bodies, scientific phenomena, and space-related information directly to your system—no internet required for core data! However, enhanced search, real-time space updates, and news require an internet connection.

## ✨ Features:

✅ Chat with the **Cosmic Bot** using `cosmotalker.chat()` 🤖🌌
✅ Get detailed information about celestial bodies within the **Solar System** 🌍☀️ &#x20;
✅ Learn about various scientific phenomena 🔬 &#x20;
✅ Ask space and science-related questions for insightful responses 🧩 &#x20;
✅ Works **offline** with an optimized Python module 🖥️🚀 &#x20;
✅ Optional **online** features for enhanced exploration 🌌

📍 **Note:** CosmoTalker v1.0 focused on the **Solar System**. Future updates will expand its capabilities to explore galaxies and beyond! ✨

## 🌍 Contribute to a Greener Planet!

The `cosmotalker.search(str)` function in the Python library (since v1.1.1), supports a greener Earth by using the Ecosia search engine 🌱💚. Every search helps plant trees and contribute to reforestation 🌳. This function requires a string input and performs an online search.

## 🛠 Installation & Usage

### Installation:

```sh
pip install cosmotalker
```

### Basic Usage:

```python
import cosmotalker

# 💬 Chatbot
print(cosmotalker.chat())

# Retrieve information about a celestial body
earth_info = cosmotalker.get("earth")
print(earth_info)  # Offline function

# Provide feedback to improve CosmoTalker
print(cosmotalker.feedback())

# Online Features
print(cosmotalker.apod())          # Fetch Astronomy Picture of the Day
print(cosmotalker.celestrak())     # Get satellite tracking data
print(cosmotalker.search("yt"))    # Opens YouTube
print(cosmotalker.search("words")) # Eco-friendly web search
print(cosmotalker.get("yuri"))     # Deep search about Yuri
print(cosmotalker.spacex())        # SpaceX upcoming launches
print(cosmotalker.wiki("black hole"))  # New wiki summary (v1.6)

# 📸 New in v1.8.7: Image Function (Beta)
print(cosmotalker.img())           # Preview and download cosmic images (Beta)
```

📌 **Note:** In `cosmotalker.search()`, you can use shortcuts like `wa` for WhatsApp, `fb` for Facebook, `insta` for Instagram, `gpt` for ChatGPT, etc., or provide a query to perform an online search.

💇 **For Online Features:**
Future updates about **SpaceX** will be available through `cosmotalker.spacex()` 🚀.

### 🔍 New in v1.6: `cosmotalker.wiki()`

Now includes Wikipedia integration! Fetch high-quality summaries from Wikipedia and measure how fast it was retrieved:

```python
print(cosmotalker.wiki("black hole"))
```

**Output Sample:**

```
Summary fetched in 0.4843580722808838 seconds

Summary:
A black hole is a massive, compact astronomical object so dense that its gravity prevents anything from escaping, even light...
```

## 🌜 Benchmark Performance

CosmoTalker's core data is stored offline, ensuring **lightning-fast retrieval speeds** without network latency. Here are some benchmark results (measured in seconds):

```
0.000721485
0.000783112
0.017891257
0.000742356
0.000935621
0.000829374
0.000758492
0.000731948
0.000759844
```

## 🌌 Explore More

Visit **[bhuvaneshm.in/cosmotalker](https://bhuvaneshm.in/cosmotalker)** to discover more about the universe!

⭐ Star the Project
If you enjoy using CosmoTalker, consider giving it a ⭐ on GitHub:
👉 **[github.com/bhuvanesh-m-dev/cosmotalker](https://github.com/bhuvanesh-m-dev/cosmotalker)**

---

👨‍💻 **Developed by** [Bhuvanesh M](https://github.com/bhuvanesh-m-dev)

### 🌐 Connect with Me:

* **Portfolio**: [bhuvaneshm.in](https://bhuvaneshm.in/)
* **LinkedIn**: [linkedin.com/in/bhuvaneshm-developer](https://www.linkedin.com/in/bhuvaneshm-developer)
* **GitHub**: [github.com/bhuvanesh-m-dev](https://github.com/bhuvanesh-m-dev)
* **HackerRank**: [hackerrank.com/profile/bhuvaneshm\_dev](https://www.hackerrank.com/profile/bhuvaneshm_dev)
* **YouTube**: [youtube.com/@bhuvaneshm\_dev](https://www.youtube.com/@bhuvaneshm_dev)
* **LeetCode**: [leetcode.com/u/bhuvaneshm\_dev](https://leetcode.com/u/bhuvaneshm_dev/)
* **Dev**: [dev.to/bhuvaneshm\_dev](https://dev.to/bhuvaneshm_dev)
* **X (Twitter)**: [x.com/bhuvaneshm06](https://x.com/bhuvaneshm06)
* **Instagram**: [instagram.com/bhuvaneshm.developer](https://www.instagram.com/bhuvaneshm.developer)

