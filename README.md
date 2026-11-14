# WIKIDOMINO 🀄 — The Wikipedia Hyperlink Chain Reaction

A daily Wikiracing puzzle game built for the **Entertainment Track** at **HackPrinceton Fall 2026**. Inspired by *Wordle*, *Globle*, and *Wikiracing*.

---

## 🎯 Concept & Gameplay
Navigate across human knowledge by reading actual Wikipedia articles and clicking real in-text hyperlinks:
* **The Goal:** Connect an Origin article to a Target destination (e.g. **Taylor Swift** ➡️ **Napoleon**).
* **Live In-Text Hyperlinks:** The actual Wikipedia article is rendered directly in the app. Click *any* blue hyperlink inside the prose or infobox to hop to that article.
* **Every Click is a Domino:** Each hop adds a physical 3D Domino tile with the article's photo and title to your horizontal domino chain.
* **Target Beacon & Radar:** If the target destination is hyperlinked on your current page, it lights up with a glowing emerald beacon so you never miss it!
* **The Climax ("Topple the Chain"):** When you land on the target article, click **TOPPLE THE CHAIN** to watch your dominoes knock down in a tactile sound-and-physics cascade, ending with confetti and a Wordle-style share grid.

---

## 🚀 Daily Challenges Included
1. **#1: Pop Royalty to Emperor of the French** (`Taylor Swift` ➡️ `Napoleon`, Par 3)
2. **#2: Blocky Worlds to Antiquity** (`Minecraft` ➡️ `Julius Caesar`, Par 3)
3. **#3: Pink Blockbuster to Nuclear Standoff** (`Barbie (film)` ➡️ `Cold War`, Par 2)
4. **#4: Crypto Frontier to Ancient Egypt** (`Bitcoin` ➡️ `Cleopatra`, Par 3)
5. **#5: 8-Bit Plumber to the Renaissance** (`Super Mario Bros.` ➡️ `Leonardo da Vinci`, Par 3)

---

## 🛠️ Tech Architecture
* **Frontend:** React 19 + Vite + TypeScript
* **Styling:** Tailwind CSS v4 + Custom Wikipedia Dark Reader Theme + 3D CSS Perspectives
* **Data Sources:** Live Wikipedia Parse & REST APIs with offline fallback caching
* **Audio:** Zero-latency Web Audio API sound synthesizer
* **Effects:** Canvas Confetti

---

## 💻 Running the Game

```powershell
# Start Vite development server
npm run dev

# Build for production
npm run build
```
