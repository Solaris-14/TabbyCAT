import { useState, useEffect } from 'react';
import { DAILY_CHALLENGES } from './data/wikiChallenges';
import { getWikiArticle } from './utils/wikiApi';
import type { WikiChallenge, WikiArticle } from './types/game';
import { WikiDominoTile } from './components/WikiDominoTile';
import { TargetBanner } from './components/TargetBanner';
import { ArticleViewer } from './components/ArticleViewer';
import { ShareModal } from './components/ShareModal';
import { sounds } from './utils/audio';
import { 
  Play, 
  Volume2, 
  VolumeX, 
  HelpCircle, 
  RotateCcw, 
  Flame,
  ArrowRight,
} from 'lucide-react';

export function App() {
  const [currentChallengeIndex, setCurrentChallengeIndex] = useState(0);
  const challenge: WikiChallenge = DAILY_CHALLENGES[currentChallengeIndex];

  // Game state
  const [currentArticle, setCurrentArticle] = useState<WikiArticle | null>(null);
  const [targetArticle, setTargetArticle] = useState<WikiArticle | null>(null);
  const [path, setPath] = useState<WikiArticle[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Timer
  const [timeElapsed, setTimeElapsed] = useState<number>(0);
  const [isTimerRunning, setIsTimerRunning] = useState<boolean>(true);

  // Topple animation states
  const [isToppling, setIsToppling] = useState<boolean>(false);
  const [isToppled, setIsToppled] = useState<boolean>(false);
  const [showShareModal, setShowShareModal] = useState<boolean>(false);
  const [showHelpModal, setShowHelpModal] = useState<boolean>(false);
  const [soundEnabled, setSoundEnabled] = useState<boolean>(true);

  // Initialize or reset challenge
  useEffect(() => {
    let isCancelled = false;
    async function loadChallenge() {
      setIsLoading(true);
      setIsToppling(false);
      setIsToppled(false);
      setShowShareModal(false);
      setTimeElapsed(0);
      setIsTimerRunning(true);

      const [start, target] = await Promise.all([
        getWikiArticle(challenge.startTitle),
        getWikiArticle(challenge.targetTitle),
      ]);

      if (!isCancelled) {
        setCurrentArticle(start);
        setTargetArticle(target);
        setPath([start]);
        setIsLoading(false);
      }
    }

    loadChallenge();
    return () => {
      isCancelled = true;
    };
  }, [currentChallengeIndex, challenge.startTitle, challenge.targetTitle]);

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

  // Audio toggle
  const toggleSound = () => {
    sounds.enabled = !soundEnabled;
    setSoundEnabled(!soundEnabled);
  };

  // Switch challenge
  const handleSelectChallenge = (index: number) => {
    sounds.playTileClick();
    setCurrentChallengeIndex(index);
  };

  // Next random challenge
  const handleNextChallenge = () => {
    const nextIdx = (currentChallengeIndex + 1) % DAILY_CHALLENGES.length;
    handleSelectChallenge(nextIdx);
  };

  // Reset current run
  const handleResetRun = async () => {
    sounds.playTileClick();
    if (path.length > 0) {
      const start = path[0];
      setCurrentArticle(start);
      setPath([start]);
      setTimeElapsed(0);
      setIsTimerRunning(true);
      setIsToppling(false);
      setIsToppled(false);
      setShowShareModal(false);
    }
  };

  // Player clicks a hyperlink
  const handleSelectLink = async (linkTitle: string) => {
    setIsLoading(true);
    const nextArticle = await getWikiArticle(linkTitle);
    
    const newPath = [...path, nextArticle];
    setPath(newPath);
    setCurrentArticle(nextArticle);
    setIsLoading(false);

    // Check if target reached!
    if (nextArticle.title.toLowerCase() === challenge.targetTitle.toLowerCase()) {
      sounds.playSuccess();
      setIsTimerRunning(false);
    }
  };

  // Undo one hop
  const handleUndo = () => {
    if (path.length <= 1) return;
    sounds.playTileClick();
    const newPath = path.slice(0, -1);
    setPath(newPath);
    setCurrentArticle(newPath[newPath.length - 1]);
  };

  // Trigger Topple Sequence
  const handleTopple = () => {
    setIsToppling(true);
    sounds.playToppleCascade(path.length, () => {
      setIsToppled(true);
      setTimeout(() => {
        setShowShareModal(true);
      }, 600);
    });
  };

  const isTargetReached =
    currentArticle?.title.toLowerCase() === challenge.targetTitle.toLowerCase();

  const isTargetInSight =
    currentArticle?.outgoingLinks.some(
      (l) => l.toLowerCase() === challenge.targetTitle.toLowerCase()
    ) || false;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col justify-between selection:bg-amber-500 selection:text-slate-950 font-sans">
      {/* Header */}
      <header className="border-b border-slate-800/80 bg-slate-900/60 backdrop-blur-md sticky top-0 z-40 px-4 py-3">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-500 to-amber-300 flex items-center justify-center text-slate-950 font-black text-xl shadow-lg shadow-amber-500/20">
              🀄
            </div>
            <div>
              <h1 className="font-extrabold text-lg sm:text-xl tracking-tight text-white flex items-center gap-2">
                WIKIDOMINO
                <span className="text-[10px] uppercase font-bold tracking-widest px-2 py-0.5 rounded bg-amber-500/20 text-amber-400 border border-amber-500/30">
                  HackPrinceton
                </span>
              </h1>
              <p className="text-[11px] text-slate-400 hidden sm:block">
                The Wikipedia Hyperlink Chain Reaction Game
              </p>
            </div>
          </div>

          {/* Challenge Selector & Controls */}
          <div className="flex items-center gap-2">
            <div className="hidden sm:flex bg-slate-800 p-1 rounded-xl border border-slate-700">
              {DAILY_CHALLENGES.map((ch, idx) => (
                <button
                  key={ch.id}
                  type="button"
                  onClick={() => handleSelectChallenge(idx)}
                  className={`px-3 py-1 rounded-lg text-xs font-bold transition-all ${
                    currentChallengeIndex === idx
                      ? 'bg-amber-500 text-slate-950 shadow-sm'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  #{idx + 1}
                </button>
              ))}
            </div>

            <button
              type="button"
              onClick={handleNextChallenge}
              className="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-bold flex items-center gap-1.5 transition-all border border-slate-700"
              title="Next Challenge"
            >
              <Flame className="w-3.5 h-3.5 text-amber-400" />
              <span>Next</span>
            </button>

            <button
              type="button"
              onClick={toggleSound}
              className="p-2 rounded-xl bg-slate-800 border border-slate-700 hover:bg-slate-700 text-slate-300 transition-all"
              title={soundEnabled ? 'Mute Audio' : 'Unmute Audio'}
            >
              {soundEnabled ? (
                <Volume2 className="w-4 h-4 text-amber-400" />
              ) : (
                <VolumeX className="w-4 h-4 text-slate-500" />
              )}
            </button>

            <button
              type="button"
              onClick={() => setShowHelpModal(true)}
              className="p-2 rounded-xl bg-slate-800 border border-slate-700 hover:bg-slate-700 text-slate-300 transition-all"
              title="How to Play"
            >
              <HelpCircle className="w-4 h-4" />
            </button>
          </div>
        </div>
      </header>

      {/* Main Arena */}
      <main className="max-w-6xl mx-auto w-full px-4 py-6 flex-1 flex flex-col justify-start">
        {/* Target Banner */}
        <TargetBanner
          targetTitle={challenge.targetTitle}
          targetArticle={targetArticle || undefined}
          parHops={challenge.parHops}
          currentHops={Math.max(0, path.length - 1)}
          isTargetInSight={isTargetInSight}
        />

        {/* 3D Domino Track Section */}
        <div className="mb-6">
          <div className="flex items-center justify-between mb-2 px-1">
            <div className="text-xs font-bold uppercase tracking-wider text-slate-400 flex items-center gap-1.5">
              <span>Your Domino Chain</span>
              <span className="text-[10px] text-amber-400 font-mono">
                ({path.length} tiles)
              </span>
            </div>

            {path.length > 1 && (
              <button
                type="button"
                onClick={handleResetRun}
                className="text-xs text-slate-500 hover:text-rose-400 flex items-center gap-1 transition-colors"
              >
                <RotateCcw className="w-3 h-3" /> Reset Trail
              </button>
            )}
          </div>

          {/* Horizontal Domino Slider */}
          <div className="perspective-1000 py-3 overflow-x-auto scrollbar-thin scrollbar-thumb-slate-800">
            <div className="flex items-center gap-3 sm:gap-4 min-w-max px-2 py-4">
              {path.map((item, idx) => {
                const isStart = idx === 0;
                const isLast = idx === path.length - 1;
                const isGoal =
                  item.title.toLowerCase() === challenge.targetTitle.toLowerCase();
                return (
                  <div key={item.title + idx} className="flex items-center gap-2 sm:gap-3">
                    <WikiDominoTile
                      article={item}
                      stepNumber={idx}
                      isStart={isStart}
                      isTarget={isGoal}
                      isToppled={isToppling || isToppled}
                      toppleDelay={idx * 160}
                      onClick={() => {
                        sounds.playTileClick();
                        setCurrentArticle(item);
                      }}
                    />
                    {!isLast && (
                      <ArrowRight className="w-4 h-4 text-slate-600 flex-shrink-0" />
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Topple Trigger Button when Target Reached */}
        {isTargetReached && (
          <div className="flex flex-col items-center justify-center gap-2 my-4 animate-in fade-in zoom-in duration-300">
            <button
              type="button"
              disabled={isToppling || isToppled}
              onClick={handleTopple}
              className="px-8 py-4 rounded-2xl bg-gradient-to-r from-amber-500 via-emerald-400 to-amber-500 text-slate-950 font-black text-sm tracking-wider uppercase flex items-center gap-2 transition-all shadow-xl shadow-emerald-500/30 hover:scale-105 active:scale-95 animate-pulse"
            >
              <Play className="w-5 h-5 fill-current" />
              {isToppling ? 'Toppling Dominoes...' : 'TOPPLE THE CHAIN!'}
            </button>
            <span className="text-[11px] text-emerald-400 font-semibold">
              Target reached! Click to trigger the physical cascade!
            </span>
          </div>
        )}

        {/* Current Article Viewer Hub */}
        {currentArticle && (
          <ArticleViewer
            currentArticle={currentArticle}
            targetTitle={challenge.targetTitle}
            onSelectLink={handleSelectLink}
            onUndo={handleUndo}
            canUndo={path.length > 1}
            isLoading={isLoading}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-800/80 py-4 px-4 text-center text-xs text-slate-500">
        WIKIDOMINO • Built for HackPrinceton Fall 2026 • Powered by Wikipedia API & Web Audio
      </footer>

      {/* Share / Victory Modal */}
      <ShareModal
        isOpen={showShareModal}
        onClose={() => setShowShareModal(false)}
        challenge={challenge}
        path={path}
        timeElapsed={timeElapsed}
        onNextChallenge={handleNextChallenge}
      />

      {/* How to Play Modal */}
      {showHelpModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/85 backdrop-blur-md animate-in fade-in duration-200">
          <div className="w-full max-w-md bg-slate-900 border border-slate-700 rounded-3xl p-6 sm:p-8 shadow-2xl text-left">
            <h3 className="text-xl font-black text-white flex items-center gap-2">
              How to Play WIKIDOMINO 🀄
            </h3>
            <div className="space-y-3 mt-4 text-xs text-slate-300 leading-relaxed">
              <p>
                <strong>1. The Challenge:</strong> You are given an Origin article (e.g. <em>Taylor Swift</em>) and a Target destination (e.g. <em>Napoleon</em>).
              </p>
              <p>
                <strong>2. Traverse Hyperlinks:</strong> Browse the current article and click any outgoing Wikipedia hyperlink to hop to the next page.
              </p>
              <p>
                <strong>3. Build the Domino Chain:</strong> Every hop you make adds a new physical 3D domino to your chain on top!
              </p>
              <p>
                <strong>4. Topple the Dominoes:</strong> When you reach the target article, click <strong>TOPPLE THE CHAIN</strong> to knock down your path in a glorious sound-and-physics chain reaction!
              </p>
            </div>
            <button
              type="button"
              onClick={() => setShowHelpModal(false)}
              className="mt-6 w-full py-3 rounded-xl bg-amber-500 text-slate-950 font-black text-sm hover:bg-amber-400 transition-all"
            >
              Let's Race!
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
