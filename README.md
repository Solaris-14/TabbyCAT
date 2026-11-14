# WIKIDOMINO 🀄 — The Wikipedia Hyperlink Chain Reaction

A daily Wikiracing puzzle game built for the **Entertainment Track** at **HackPrinceton Fall 2026**. Inspired by *Wordle*, *Globle*, and *Wikiracing*.

---

## 🎯 Concept & Gameplay
Navigate across human knowledge by jumping through Wikipedia hyperlinks:
* **The Goal:** Connect an Origin article to a Target destination (e.g. **Taylor Swift** ➡️ **Napoleon**).
* **Every Click is a Domino:** Each hyperlink you click appends a new physical 3D Domino tile to your growing chain.
* **Radar & Link Filter:** Search and filter hundreds of article links instantaneously, or spot the target beacon when within 1 hop!
* **The Climax ("Topple the Chain"):** Once you reach your destination, hit **TOPPLE THE CHAIN** to watch your path knock down in sequence with tactile Web Audio sound effects, followed by a celebratory confetti shower and a Wordle-style share grid.

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
* **Styling:** Tailwind CSS v4 + Lucide Icons + 3D CSS Perspectives
* **Data Sources:** Live Wikipedia REST API + MediaWiki Action API with offline mock fallback
* **Audio:** Zero-dependency procedural Web Audio API sound synthesizer
* **Effects:** Canvas Confetti

---

## 💻 Running the Game

```powershell
# Start Vite development server
npm run dev

# Build for production
npm run build
```
