import { useState, useEffect } from 'react';
import { getDailyChallenge, getRandomChallenge, validateChain } from './utils/gameLogic';
import type { GameChallenge, HistoricalEvent } from './types/game';
import { DominoTile } from './components/DominoTile';
import { SearchInput } from './components/SearchInput';
import { ShareModal } from './components/ShareModal';
import { sounds } from './utils/audio';
import { 
  Play, 
  Volume2, 
  VolumeX, 
  HelpCircle, 
  RotateCcw, 
  Zap,
  Calendar,
  Flame
} from 'lucide-react';

export function App() {
  // Game Mode: 'daily' or 'unlimited'
  const [mode, setMode] = useState<'daily' | 'unlimited'>('daily');
  const [challenge, setChallenge] = useState<GameChallenge>(() => getDailyChallenge());
  
  // Placed slots (array of 3 items, undefined if empty)
  const [slots, setSlots] = useState<(HistoricalEvent | undefined)[]>([undefined, undefined, undefined]);
  const [activeSlotIndex, setActiveSlotIndex] = useState<number>(0);
  
  // Game states
  const [guessCount, setGuessCount] = useState<number>(0);
  const [timeElapsed, setTimeElapsed] = useState<number>(0);
  const [isTimerRunning, setIsTimerRunning] = useState<boolean>(true);
  
  // Animation / Topple states
  const [isToppling, setIsToppling] = useState<boolean>(false);
  const [isToppled, setIsToppled] = useState<boolean>(false);
  const [showShareModal, setShowShareModal] = useState<boolean>(false);
  const [showHelpModal, setShowHelpModal] = useState<boolean>(false);
  const [soundEnabled, setSoundEnabled] = useState<boolean>(true);
  const [validationError, setValidationError] = useState<string | null>(null);

  // Timer tick
  useEffect(() => {
    let interval: ReturnType<typeof setInterval>;
    if (isTimerRunning && !isToppled) {
      interval = setInterval(() => {
        setTimeElapsed((prev) => prev + 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isTimerRunning, isToppled]);

  // Audio mute/unmute
  const toggleSound = () => {
    sounds.enabled = !soundEnabled;
    setSoundEnabled(!soundEnabled);
  };

  // Switch challenge mode
  const handleSwitchMode = (newMode: 'daily' | 'unlimited') => {
    sounds.playTileClick();
    setMode(newMode);
    resetGame(newMode === 'daily' ? getDailyChallenge() : getRandomChallenge());
  };

  // Reset current game
  const resetGame = (newChallenge = challenge) => {
    setChallenge(newChallenge);
    setSlots([undefined, undefined, undefined]);
    setActiveSlotIndex(0);
    setGuessCount(0);
    setTimeElapsed(0);
    setIsTimerRunning(true);
    setIsToppling(false);
    setIsToppled(false);
    setShowShareModal(false);
    setValidationError(null);
  };

  // Handle slot event selection
  const handleSelectEvent = (event: HistoricalEvent) => {
    const nextSlots = [...slots];
    nextSlots[activeSlotIndex] = event;
    setSlots(nextSlots);
    setGuessCount((prev) => prev + 1);
    setValidationError(null);

    // Auto advance to next empty slot if available
    const nextEmptyIndex = nextSlots.findIndex((s) => s === undefined);
    if (nextEmptyIndex !== -1) {
      setActiveSlotIndex(nextEmptyIndex);
    }
  };

  // Clear slot
  const handleRemoveSlot = (index: number) => {
    sounds.playTileClick();
    const nextSlots = [...slots];
    nextSlots[index] = undefined;
    setSlots(nextSlots);
    setActiveSlotIndex(index);
    setValidationError(null);
  };

  // Topple evaluation
  const handleTopple = () => {
    const result = validateChain(challenge.startEvent, slots, challenge.targetEvent);

    if (!result.isFull) {
      sounds.playError();
      setValidationError('Fill all domino slots before toppling!');
      return;
    }

    if (!result.isValid) {
      sounds.playError();
      setValidationError('Broken chain! The dominoes must be placed in strict chronological order.');
      return;
    }

    // Success! Start cascade topple
    setValidationError(null);
    setIsToppling(true);
    setIsTimerRunning(false);

    // Domino cascade sound & visual trigger
    sounds.playToppleCascade(5, () => {
      setIsToppled(true);
      setTimeout(() => {
        setShowShareModal(true);
      }, 500);
    });
  };

  // Check if chain is ready to topple
  const isChainFilled = slots.every((s) => s !== undefined);
  const placedEventIds = [
    challenge.startEvent.id,
    challenge.targetEvent.id,
    ...slots.filter((s): s is HistoricalEvent => !!s).map((s) => s.id),
  ];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col justify-between selection:bg-amber-500 selection:text-slate-950">
      {/* Top Navigation */}
      <header className="border-b border-slate-800/80 bg-slate-900/60 backdrop-blur-md sticky top-0 z-40 px-4 py-3">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-500 to-amber-300 flex items-center justify-center text-slate-950 font-black text-xl shadow-lg shadow-amber-500/20">
              🀄
            </div>
            <div>
              <h1 className="font-extrabold text-lg sm:text-xl tracking-tight text-white flex items-center gap-2">
                DOMINO
                <span className="text-[10px] uppercase font-bold tracking-widest px-2 py-0.5 rounded bg-amber-500/20 text-amber-400 border border-amber-500/30">
                  HackPrinceton
                </span>
              </h1>
              <p className="text-[11px] text-slate-400 hidden sm:block">The Timeline Chain Reaction Game</p>
            </div>
          </div>

          {/* Mode Switch & Controls */}
          <div className="flex items-center gap-2">
            <div className="flex bg-slate-800 p-1 rounded-xl border border-slate-700">
              <button
                type="button"
                onClick={() => handleSwitchMode('daily')}
                className={`px-3 py-1 rounded-lg text-xs font-bold flex items-center gap-1.5 transition-all ${
                  mode === 'daily'
                    ? 'bg-amber-500 text-slate-950 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <Calendar className="w-3.5 h-3.5" /> Daily
              </button>
              <button
                type="button"
                onClick={() => handleSwitchMode('unlimited')}
                className={`px-3 py-1 rounded-lg text-xs font-bold flex items-center gap-1.5 transition-all ${
                  mode === 'unlimited'
                    ? 'bg-amber-500 text-slate-950 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <Flame className="w-3.5 h-3.5" /> Quick Play
              </button>
            </div>

            <button
              type="button"
              onClick={toggleSound}
              className="p-2 rounded-xl bg-slate-800/80 border border-slate-700 hover:bg-slate-700 text-slate-300 transition-all"
              title={soundEnabled ? 'Mute Audio' : 'Unmute Audio'}
            >
              {soundEnabled ? <Volume2 className="w-4 h-4 text-amber-400" /> : <VolumeX className="w-4 h-4 text-slate-500" />}
            </button>

            <button
              type="button"
              onClick={() => setShowHelpModal(true)}
              className="p-2 rounded-xl bg-slate-800/80 border border-slate-700 hover:bg-slate-700 text-slate-300 transition-all"
              title="How to Play"
            >
              <HelpCircle className="w-4 h-4" />
            </button>
          </div>
        </div>
      </header>

      {/* Main Game Arena */}
      <main className="max-w-6xl mx-auto w-full px-4 py-6 flex-1 flex flex-col justify-center">
        {/* Challenge Goal Banner */}
        <div className="text-center mb-6">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-slate-800/80 border border-slate-700 text-xs text-slate-300 mb-2">
            <Zap className="w-3.5 h-3.5 text-amber-400" />
            <span>Connect <strong className="text-blue-400 font-mono">{challenge.startEvent.year}</strong> to <strong className="text-emerald-400 font-mono">{challenge.targetEvent.year}</strong></span>
          </div>
          <p className="text-xs text-slate-400 max-w-lg mx-auto">
            Place 3 intermediate historical events in chronological sequence, then hit <strong>TOPPLE</strong> to trigger the butterfly effect!
          </p>
        </div>

        {/* 3D Domino Track */}
        <div className="perspective-1000 py-6 overflow-x-auto scrollbar-none">
          <div className="flex items-center justify-center gap-3 sm:gap-6 min-w-max px-4">
            {/* Start Domino */}
            <DominoTile
              event={challenge.startEvent}
              isStart
              isToppled={isToppling || isToppled}
              toppleDelay={0}
            />

            {/* Intermediate Slots */}
            {slots.map((slotEvent, idx) => (
              <DominoTile
                key={idx}
                slotIndex={idx}
                event={slotEvent}
                isSelected={activeSlotIndex === idx}
                isToppled={isToppling || isToppled}
                toppleDelay={(idx + 1) * 160}
                onClick={() => {
                  sounds.playTileClick();
                  setActiveSlotIndex(idx);
                }}
                onRemove={() => handleRemoveSlot(idx)}
              />
            ))}

            {/* Target Domino */}
            <DominoTile
              event={challenge.targetEvent}
              isTarget
              isToppled={isToppling || isToppled}
              toppleDelay={4 * 160}
            />
          </div>
        </div>

        {/* Validation Error Banner */}
        {validationError && (
          <div className="max-w-md mx-auto my-3 p-3 rounded-xl bg-rose-500/20 border border-rose-500 text-rose-200 text-xs font-semibold text-center animate-bounce">
            {validationError}
          </div>
        )}

        {/* Topple Trigger Button */}
        <div className="flex items-center justify-center gap-3 my-4">
          <button
            type="button"
            disabled={isToppling || isToppled}
            onClick={handleTopple}
            className={`px-8 py-3.5 rounded-2xl font-black text-sm tracking-wider uppercase flex items-center gap-2 transition-all shadow-xl active:scale-95 ${
              isChainFilled
                ? 'bg-gradient-to-r from-amber-500 to-amber-400 text-slate-950 shadow-amber-500/30 hover:shadow-amber-500/50 hover:scale-105 animate-pulse'
                : 'bg-slate-800 text-slate-500 border border-slate-700 cursor-not-allowed'
            }`}
          >
            <Play className="w-4 h-4 fill-current" />
            {isToppling ? 'Toppling...' : 'Topple Dominoes'}
          </button>

          <button
            type="button"
            onClick={() => resetGame()}
            className="p-3 rounded-xl bg-slate-800 border border-slate-700 hover:bg-slate-700 text-slate-400 hover:text-white transition-all"
            title="Reset Board"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>

        {/* Search Input for the Active Slot */}
        {!isToppled && (
          <SearchInput
            activeSlotIndex={activeSlotIndex}
            placedEventIds={placedEventIds}
            onSelectEvent={handleSelectEvent}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 py-4 px-4 text-center text-xs text-slate-500">
        Built for HackPrinceton Fall 2026 • Entertainment Track • Inspired by Wordle, Globle & Krillion
      </footer>

      {/* Share / Victory Modal */}
      <ShareModal
        isOpen={showShareModal}
        onClose={() => setShowShareModal(false)}
        challenge={challenge}
        placedSlots={slots.filter((s): s is HistoricalEvent => !!s)}
        guessCount={guessCount}
        timeElapsed={timeElapsed}
        onNextChallenge={() => handleSwitchMode('unlimited')}
      />

      {/* How to Play Modal */}
      {showHelpModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="w-full max-w-md bg-slate-900 border border-slate-700 rounded-2xl p-6 shadow-2xl text-left">
            <h3 className="text-xl font-bold text-white flex items-center gap-2">
              How to Play DOMINO 🀄
            </h3>
            <div className="space-y-3 mt-4 text-xs text-slate-300">
              <p>
                <strong>1. Bridge the Timeline:</strong> You are given an <em>Origin Event</em> (e.g. 1889) and a <em>Target Event</em> (e.g. 1969).
              </p>
              <p>
                <strong>2. Pick Dominoes:</strong> Search and insert 3 historical events into the middle slots.
              </p>
              <p>
                <strong>3. Chronological Order:</strong> Each event MUST occur after the one before it and before the one after it!
              </p>
              <p>
                <strong>4. Topple the Chain:</strong> When you think your timeline is sound, click <strong>TOPPLE DOMINOES</strong>. If your chain is valid, the dominoes will knock down in sequence!
              </p>
            </div>
            <button
              type="button"
              onClick={() => setShowHelpModal(false)}
              className="mt-6 w-full py-2.5 rounded-xl bg-amber-500 text-slate-950 font-bold text-sm hover:bg-amber-400 transition-all"
            >
              Got it, let's play!
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
