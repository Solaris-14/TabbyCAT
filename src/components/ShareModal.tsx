import React, { useState, useEffect } from 'react';
import confetti from 'canvas-confetti';
import type { GameChallenge, HistoricalEvent } from '../types/game';
import { Share2, Check, RefreshCw, Trophy, Sparkles } from 'lucide-react';

interface ShareModalProps {
  isOpen: boolean;
  onClose: () => void;
  challenge: GameChallenge;
  placedSlots: HistoricalEvent[];
  guessCount: number;
  timeElapsed: number; // in seconds
  onNextChallenge: () => void;
}

export const ShareModal: React.FC<ShareModalProps> = ({
  isOpen,
  challenge,
  placedSlots,
  guessCount,
  timeElapsed,
  onNextChallenge,
}) => {
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (isOpen) {
      // Fire celebratory confetti cascade
      confetti({
        particleCount: 100,
        spread: 70,
        origin: { y: 0.6 },
      });
      setTimeout(() => {
        confetti({
          particleCount: 50,
          angle: 60,
          spread: 55,
          origin: { x: 0 },
        });
        confetti({
          particleCount: 50,
          angle: 120,
          spread: 55,
          origin: { x: 1 },
        });
      }, 300);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const formatTime = (secs: number) => {
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return `${m}m ${s < 10 ? '0' : ''}${s}s`;
  };

  const generateShareText = () => {
    const fullChain = [challenge.startEvent, ...placedSlots, challenge.targetEvent];
    const emojiChain = fullChain.map(() => '🟩').join('');
    return `DOMINO 🀄
${challenge.startEvent.year} ➡️ ${challenge.targetEvent.year}
${emojiChain}
💥 Dominoes Toppled in ${guessCount} moves (${formatTime(timeElapsed)})
Play at: domino-hackprinceton.vercel.app`;
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(generateShareText());
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="relative w-full max-w-md bg-slate-900 border border-slate-700/80 rounded-2xl p-6 shadow-2xl text-center">
        {/* Trophy Header */}
        <div className="w-16 h-16 mx-auto rounded-2xl bg-gradient-to-tr from-amber-500 to-amber-300 flex items-center justify-center text-slate-950 shadow-lg shadow-amber-500/30">
          <Trophy className="w-8 h-8 stroke-[2.5]" />
        </div>

        <h2 className="text-2xl font-black mt-4 text-white flex items-center justify-center gap-2">
          Dominoes Toppled! <Sparkles className="w-5 h-5 text-amber-400" />
        </h2>
        <p className="text-xs text-slate-400 mt-1">
          You connected history with a seamless chronological chain!
        </p>

        {/* The Butterfly Effect Timeline */}
        <div className="my-5 p-3.5 bg-slate-950/60 rounded-xl border border-slate-800 text-left">
          <div className="text-[11px] font-bold uppercase tracking-wider text-amber-400 mb-2">
            The Timeline Chain Reaction:
          </div>
          <div className="space-y-1.5 text-xs text-slate-300">
            <div className="flex items-center gap-2">
              <span className="font-mono font-bold text-blue-400 w-12">{challenge.startEvent.year}</span>
              <span className="line-clamp-1">{challenge.startEvent.title}</span>
            </div>
            {placedSlots.map((ev) => (
              <div key={ev.id} className="flex items-center gap-2 pl-2 border-l border-amber-500/40">
                <span className="font-mono font-bold text-amber-400 w-12">↳ {ev.year}</span>
                <span className="line-clamp-1 text-slate-200">{ev.title}</span>
              </div>
            ))}
            <div className="flex items-center gap-2">
              <span className="font-mono font-bold text-emerald-400 w-12">{challenge.targetEvent.year}</span>
              <span className="line-clamp-1">{challenge.targetEvent.title}</span>
            </div>
          </div>
        </div>

        {/* Stats Row */}
        <div className="grid grid-cols-2 gap-3 mb-6">
          <div className="p-3 bg-slate-800/40 rounded-xl border border-slate-800">
            <div className="text-xl font-mono font-bold text-slate-100">{guessCount}</div>
            <div className="text-[10px] text-slate-400 uppercase font-semibold">Total Guesses</div>
          </div>
          <div className="p-3 bg-slate-800/40 rounded-xl border border-slate-800">
            <div className="text-xl font-mono font-bold text-slate-100">{formatTime(timeElapsed)}</div>
            <div className="text-[10px] text-slate-400 uppercase font-semibold">Time Elapsed</div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-3">
          <button
            type="button"
            onClick={handleCopy}
            className="flex-1 py-3 px-4 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold text-sm flex items-center justify-center gap-2 transition-all shadow-lg shadow-amber-500/20 active:scale-95"
          >
            {copied ? (
              <>
                <Check className="w-4 h-4" /> Copied Grid!
              </>
            ) : (
              <>
                <Share2 className="w-4 h-4" /> Share Result
              </>
            )}
          </button>
          
          <button
            type="button"
            onClick={onNextChallenge}
            className="py-3 px-4 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold text-sm flex items-center justify-center gap-2 transition-all border border-slate-700 active:scale-95"
          >
            <RefreshCw className="w-4 h-4" /> Next Round
          </button>
        </div>
      </div>
    </div>
  );
};
