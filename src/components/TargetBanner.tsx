import React from 'react';
import type { WikiArticle } from '../types/game';
import { Target, Flag, Sparkles } from 'lucide-react';

interface TargetBannerProps {
  targetTitle: string;
  targetArticle?: WikiArticle;
  parHops: number;
  currentHops: number;
  isTargetInSight: boolean;
}

export const TargetBanner: React.FC<TargetBannerProps> = ({
  targetTitle,
  targetArticle,
  parHops,
  currentHops,
  isTargetInSight,
}) => {
  return (
    <div
      className={`w-full max-w-4xl mx-auto mb-6 p-4 rounded-2xl border transition-all duration-300 flex flex-col sm:flex-row items-center justify-between gap-4 ${
        isTargetInSight
          ? 'bg-emerald-950/40 border-emerald-500 shadow-lg shadow-emerald-500/20 animate-pulse'
          : 'bg-slate-900/60 border-slate-800'
      }`}
    >
      {/* Left: Target info */}
      <div className="flex items-center gap-3.5 text-center sm:text-left">
        <div className="relative w-12 h-12 rounded-xl overflow-hidden bg-slate-800 border border-slate-700 flex-shrink-0 flex items-center justify-center">
          {targetArticle?.thumbnail ? (
            <img
              src={targetArticle.thumbnail}
              alt={targetTitle}
              className="w-full h-full object-cover"
            />
          ) : (
            <Target className="w-6 h-6 text-emerald-400" />
          )}
        </div>
        <div>
          <div className="flex items-center gap-2 justify-center sm:justify-start">
            <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/30 flex items-center gap-1">
              <Flag className="w-3 h-3" /> Target Destination
            </span>
            {isTargetInSight && (
              <span className="text-[10px] font-black uppercase tracking-wider text-amber-300 bg-amber-500/20 px-2 py-0.5 rounded border border-amber-400/40 flex items-center gap-1">
                <Sparkles className="w-3 h-3" /> Target in Sight!
              </span>
            )}
          </div>
          <h2 className="text-base sm:text-lg font-black text-white mt-0.5">
            {targetArticle?.displayTitle || targetTitle}
          </h2>
          {targetArticle?.description && (
            <p className="text-xs text-slate-400 line-clamp-1">
              {targetArticle.description}
            </p>
          )}
        </div>
      </div>

      {/* Right: Hops & Par counter */}
      <div className="flex items-center gap-4 bg-slate-950/60 px-4 py-2.5 rounded-xl border border-slate-800/80">
        <div className="text-center">
          <div className="text-lg font-mono font-black text-amber-400">
            {currentHops}
          </div>
          <div className="text-[10px] uppercase font-bold text-slate-400">
            Hops Taken
          </div>
        </div>
        <div className="h-6 w-px bg-slate-800" />
        <div className="text-center">
          <div className="text-lg font-mono font-black text-slate-300">
            {parHops}
          </div>
          <div className="text-[10px] uppercase font-bold text-slate-400">
            Par
          </div>
        </div>
      </div>
    </div>
  );
};
