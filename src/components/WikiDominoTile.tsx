import React from 'react';
import type { WikiArticle } from '../types/game';
import { Sparkles } from 'lucide-react';

interface WikiDominoTileProps {
  article: WikiArticle;
  stepNumber: number;
  isStart?: boolean;
  isTarget?: boolean;
  isToppled?: boolean;
  toppleDelay?: number;
  onClick?: () => void;
}

export const WikiDominoTile: React.FC<WikiDominoTileProps> = ({
  article,
  stepNumber,
  isStart,
  isTarget,
  isToppled,
  toppleDelay = 0,
  onClick,
}) => {
  return (
    <div
      onClick={onClick}
      style={{
        transitionDelay: isToppled ? `${toppleDelay}ms` : '0ms',
      }}
      className={`domino-tile flex-shrink-0 relative flex flex-col justify-between w-40 sm:w-48 h-60 sm:h-68 rounded-2xl overflow-hidden select-none border transition-all duration-300 ${
        isToppled ? 'domino-toppled' : ''
      } ${
        isStart
          ? 'bg-gradient-to-b from-blue-950/90 via-slate-900 to-slate-950 border-blue-500/50 shadow-lg shadow-blue-500/20'
          : isTarget
          ? 'bg-gradient-to-b from-emerald-950/90 via-slate-900 to-slate-950 border-emerald-500/50 shadow-lg shadow-emerald-500/20'
          : 'bg-gradient-to-b from-slate-800/90 via-slate-900 to-slate-950 border-slate-700/80 shadow-md'
      }`}
    >
      {/* Top Half: Article Thumbnail Image */}
      <div className="relative w-full h-28 sm:h-32 bg-slate-800/60 overflow-hidden flex items-center justify-center border-b border-slate-700/60">
        {article.thumbnail ? (
          <img
            src={article.thumbnail}
            alt={article.displayTitle}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
          />
        ) : (
          <div className="text-3xl opacity-40">📖</div>
        )}
        <div className="absolute inset-0 bg-gradient-to-t from-slate-950/90 via-slate-950/20 to-transparent" />

        {/* Step Badge */}
        <div className="absolute top-2.5 left-2.5">
          <span
            className={`px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider rounded-md border backdrop-blur-md ${
              isStart
                ? 'bg-blue-500/30 text-blue-300 border-blue-400/40'
                : isTarget
                ? 'bg-emerald-500/30 text-emerald-300 border-emerald-400/40'
                : 'bg-slate-900/70 text-slate-300 border-slate-700'
            }`}
          >
            {isStart ? 'Origin' : isTarget ? 'Goal' : `Hop ${stepNumber}`}
          </span>
        </div>
      </div>

      {/* Bottom Half: Title & Details */}
      <div className="p-3.5 flex flex-col justify-between flex-1">
        <div>
          <h3 className="font-extrabold text-xs sm:text-sm text-slate-100 line-clamp-2 leading-snug">
            {article.displayTitle}
          </h3>
          {article.description && (
            <p className="text-[10px] text-slate-400 line-clamp-2 mt-1">
              {article.description}
            </p>
          )}
        </div>

        <div className="pt-2 border-t border-slate-800 flex items-center justify-between text-[10px]">
          <span className="font-mono text-slate-500">
            {article.outgoingLinks?.length || 0} links
          </span>
          {isTarget && (
            <span className="text-emerald-400 font-bold flex items-center gap-1">
              <Sparkles className="w-3 h-3" /> Reached!
            </span>
          )}
        </div>
      </div>
    </div>
  );
};
