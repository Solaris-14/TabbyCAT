import React, { useState, useEffect } from 'react';
import confetti from 'canvas-confetti';
import type { WikiArticle, WikiChallenge } from '../types/game';
import { Share2, Check, RefreshCw, Trophy, Sparkles, ExternalLink } from 'lucide-react';

interface ShareModalProps {
  isOpen: boolean;
  onClose: () => void;
  challenge: WikiChallenge;
  path: WikiArticle[];
  timeElapsed: number;
  onNextChallenge: () => void;
}

export const ShareModal: React.FC<ShareModalProps> = ({
  isOpen,
  challenge,
  path,
  timeElapsed,
  onNextChallenge,
}) => {
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (isOpen) {
      confetti({
        particleCount: 100,
        spread: 70,
        origin: { y: 0.6 },
      });
      setTimeout(() => {
        confetti({
          particleCount: 60,
          angle: 60,
          spread: 60,
          origin: { x: 0 },
        });
        confetti({
          particleCount: 60,
          angle: 120,
          spread: 60,
          origin: { x: 1 },
        });
      }, 300);
    }
  }, [isOpen]);

  if (!isOpen) return null;

  const hops = Math.max(0, path.length - 1);
  const diffFromPar = hops - challenge.parHops;

  const formatTime = (secs: number) => {
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return `${m}m ${s < 10 ? '0' : ''}${s}s`;
  };

  const getScoreRating = () => {
    if (diffFromPar < 0) return { title: 'Legendary Path (-' + Math.abs(diffFromPar) + ')', color: 'text-amber-400' };
    if (diffFromPar === 0) return { title: 'Exact Par! 🎯', color: 'text-emerald-400' };
    if (diffFromPar === 1) return { title: '+1 Hop (Great Run!)', color: 'text-blue-400' };
    return { title: `+${diffFromPar} Hops (Explorer!)`, color: 'text-purple-400' };
  };

  const rating = getScoreRating();

  const generateShareText = () => {
    const emojiBlocks = path.map(() => '🟩').join('');
    const pathTitles = path.map((p) => p.displayTitle).join(' ➡️ ');
    return `WIKIDOMINO 🀄
${challenge.startTitle} ➡️ ${challenge.targetTitle}
${emojiBlocks}
🎯 ${hops} Hops (Par ${challenge.parHops}) • ⏱️ ${formatTime(timeElapsed)}
Trail: ${pathTitles}
💥 Dominoes Toppled!
Play at: wikidomino.app`;
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(generateShareText());
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/85 backdrop-blur-md animate-in fade-in duration-200">
      <div className="relative w-full max-w-lg bg-slate-900 border border-slate-700 rounded-3xl p-6 sm:p-8 shadow-2xl text-center">
        {/* Trophy icon */}
        <div className="w-16 h-16 mx-auto rounded-2xl bg-gradient-to-tr from-amber-500 to-amber-300 flex items-center justify-center text-slate-950 shadow-xl shadow-amber-500/20">
          <Trophy className="w-8 h-8 stroke-[2.5]" />
        </div>

        <h2 className="text-2xl font-black mt-4 text-white flex items-center justify-center gap-2">
          Domino Chain Toppled! <Sparkles className="w-5 h-5 text-amber-400" />
        </h2>
        <p className={`text-xs font-bold uppercase tracking-wider mt-1 ${rating.color}`}>
          {rating.title}
        </p>

        {/* Path Trail Display */}
        <div className="my-5 p-4 bg-slate-950/70 rounded-2xl border border-slate-800 text-left">
          <div className="text-[11px] font-bold uppercase tracking-wider text-slate-400 mb-2.5">
            Your Wikipedia Hyperlink Path:
          </div>
          <div className="space-y-2">
            {path.map((item, idx) => {
              const isFirst = idx === 0;
              const isLast = idx === path.length - 1;
              return (
                <div key={item.title + idx} className="flex items-center justify-between gap-2 text-xs">
                  <div className="flex items-center gap-2.5">
                    <span
                      className={`font-mono text-[10px] font-bold px-1.5 py-0.5 rounded ${
                        isFirst
                          ? 'bg-blue-500/20 text-blue-400'
                          : isLast
                          ? 'bg-emerald-500/20 text-emerald-400'
                          : 'bg-slate-800 text-slate-400'
                      }`}
                    >
                      {isFirst ? 'START' : isLast ? 'GOAL' : `HOP ${idx}`}
                    </span>
                    <span className="font-semibold text-slate-200 line-clamp-1">
                      {item.displayTitle}
                    </span>
                  </div>
                  <a
                    href={`https://en.wikipedia.org/wiki/${encodeURIComponent(item.title)}`}
                    target="_blank"
                    rel="noreferrer"
                    className="text-slate-500 hover:text-slate-300 flex-shrink-0"
                  >
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              );
            })}
          </div>
        </div>

        {/* Stats Row */}
        <div className="grid grid-cols-3 gap-3 mb-6">
          <div className="p-3 bg-slate-800/40 rounded-xl border border-slate-800">
            <div className="text-xl font-mono font-bold text-slate-100">{hops}</div>
            <div className="text-[10px] text-slate-400 uppercase font-semibold">Total Hops</div>
          </div>
          <div className="p-3 bg-slate-800/40 rounded-xl border border-slate-800">
            <div className="text-xl font-mono font-bold text-slate-100">{challenge.parHops}</div>
            <div className="text-[10px] text-slate-400 uppercase font-semibold">Target Par</div>
          </div>
          <div className="p-3 bg-slate-800/40 rounded-xl border border-slate-800">
            <div className="text-xl font-mono font-bold text-slate-100">{formatTime(timeElapsed)}</div>
            <div className="text-[10px] text-slate-400 uppercase font-semibold">Time</div>
          </div>
        </div>

        {/* Buttons */}
        <div className="flex flex-col sm:flex-row gap-3">
          <button
            type="button"
            onClick={handleCopy}
            className="flex-1 py-3 px-4 rounded-xl bg-amber-500 hover:bg-amber-400 text-slate-950 font-black text-sm flex items-center justify-center gap-2 transition-all shadow-lg shadow-amber-500/20 active:scale-95"
          >
            {copied ? (
              <>
                <Check className="w-4 h-4" /> Copied Path Grid!
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
            <RefreshCw className="w-4 h-4" /> Next Challenge
          </button>
        </div>
      </div>
    </div>
  );
};
