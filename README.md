# DOMINO 🀄 — The Timeline Chain Reaction Game

A daily history deduction game built for the **Entertainment Track** at **HackPrinceton Fall 2026**. Inspired by *Wordle*, *Globle*, and *Krillion*.

---

## 🎯 Gameplay & Concept
Connect two disparate historical moments across time by constructing a continuous chronological chain of dominoes.

1. **Origin & Target:** Every puzzle gives you a starting historical event and a target milestone (e.g. *1889: Eiffel Tower Opens* ➡️ *1969: Moon Landing*).
2. **Search & Slot:** Search and place 3 intermediate events into the domino slots.
3. **The Butterfly Effect:** Once filled, click **TOPPLE DOMINOES**. If your chain is strictly chronological, a domino cascade animation knocks down the tiles in sequence, triggering procedural sound effects and celebratory confetti!
4. **Game Modes:**
   - **Daily Domino:** A shared seed for everyone each calendar day.
   - **Quick Play (Unlimited):** Procedurally generated endless timeline challenges for fast hackathon judging demos.

---

## 🛠️ Tech Stack
- **Framework:** React 19 + Vite + TypeScript
- **Styling:** Tailwind CSS v4 + Lucide Icons
- **Audio:** Web Audio API (zero-latency synthetic sound engine for tile clicks, topples, and fanfares)
- **Effects:** Canvas Confetti + 3D CSS Perspectives

---

## 🚀 Running Locally

```bash
# Install dependencies
npm install

# Start Vite dev server
npm run dev

# Build for production
npm run build
```
