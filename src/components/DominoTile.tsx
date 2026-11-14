import React from 'react';
import type { HistoricalEvent, SlotFeedback } from '../types/game';
import { Sparkles, AlertCircle } from 'lucide-react';

interface DominoTileProps {
  event?: HistoricalEvent;
  isStart?: boolean;
  isTarget?: boolean;
  slotIndex?: number;
  isSelected?: boolean;
  isToppled?: boolean;
  toppleDelay?: number;
  feedback?: SlotFeedback;
  yearDelta?: number;
  onClick?: () => void;
  onRemove?: () => void;
}

export const DominoTile: React.FC<DominoTileProps> = ({
  event,
  isStart,
  isTarget,
  slotIndex,
  isSelected,
  isToppled,
  toppleDelay = 0,
  feedback = 'empty',
  onClick,
  onRemove,
}) => {
  const isSlot = !isStart && !isTarget;

  // Render empty slot
  if (!event && isSlot) {
    return (
      <button
        onClick={onClick}
        type="button"
        className={`group relative flex flex-col items-center justify-center w-40 sm:w-48 h-64 sm:h-72 rounded-2xl border-2 border-dashed transition-all duration-300 ${
          isSelected
            ? 'border-amber-400 bg-amber-500/10 shadow-lg shadow-amber-500/20 scale-105'
            : 'border-slate-700 bg-slate-900/50 hover:border-slate-500 hover:bg-slate-800/40'
        }`}
      >
        <div className="w-10 h-10 rounded-full border border-slate-700 flex items-center justify-center text-slate-500 font-mono text-sm font-bold group-hover:scale-110 group-hover:border-amber-400 group-hover:text-amber-400 transition-all">
          {(slotIndex ?? 0) + 1}
        </div>
        <span className="mt-3 text-xs font-semibold uppercase tracking-wider text-slate-400 group-hover:text-slate-200">
          {isSelected ? 'Selecting Event...' : 'Slot Domino'}
        </span>
        <span className="text-[10px] text-slate-500 mt-1">Click to place guess</span>
      </button>
    );
  }

  // Active Domino Tile
  return (
    <div
      style={{
        transitionDelay: isToppled ? `${toppleDelay}ms` : '0ms',
      }}
      className={`domino-tile relative flex flex-col justify-between w-40 sm:w-48 h-64 sm:h-72 rounded-2xl p-4 select-none cursor-pointer border ${
        isToppled ? 'domino-toppled' : ''
      } ${
        isStart
          ? 'bg-gradient-to-b from-blue-950/90 via-slate-900 to-slate-950 border-blue-500/40 text-blue-100 shadow-blue-500/10'
          : isTarget
          ? 'bg-gradient-to-b from-emerald-950/90 via-slate-900 to-slate-950 border-emerald-500/40 text-emerald-100 shadow-emerald-500/10'
          : feedback === 'wrong-chronology'
          ? 'bg-gradient-to-b from-rose-950/90 via-slate-900 to-slate-950 border-rose-500/50 text-rose-100'
          : isSelected
          ? 'bg-gradient-to-b from-amber-950/90 via-slate-900 to-slate-950 border-amber-400 shadow-amber-500/20 scale-105'
          : 'bg-gradient-to-b from-slate-800 via-slate-900 to-slate-950 border-slate-700/80 hover:border-slate-500'
      }`}
      onClick={onClick}
    >
      {/* Top Banner & Pip Divider */}
      <div className="flex items-center justify-between">
        <span className="text-2xl filter drop-shadow">{event?.icon || '🀄'}</span>
        <span
          className={`px-2 py-0.5 text-[10px] uppercase font-bold tracking-wider rounded-full border ${
            isStart
              ? 'bg-blue-500/20 text-blue-400 border-blue-500/30'
              : isTarget
              ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30'
              : 'bg-slate-800 text-slate-300 border-slate-700'
          }`}
        >
          {isStart ? 'Origin' : isTarget ? 'Target' : `Step ${(slotIndex ?? 0) + 1}`}
        </span>
      </div>

      {/* Center Details */}
      <div className="my-auto py-2">
        <h3 className="font-bold text-sm sm:text-base leading-snug line-clamp-3 text-slate-100 group-hover:text-white">
          {event?.title}
        </h3>
        <p className="text-[11px] text-slate-400 line-clamp-2 mt-1">
          {event?.description}
        </p>
      </div>

      {/* Bottom Domino Half: Year & Feedback */}
      <div className="pt-2 border-t border-slate-700/60 flex items-center justify-between">
        <div className="font-mono text-lg sm:text-xl font-black tracking-tight text-amber-400">
          {event?.year}
        </div>
        
        {isSlot && onRemove && (
          <button
            type="button"
            onClick={(e) => {
              e.stopPropagation();
              onRemove();
            }}
            className="text-[11px] text-slate-500 hover:text-rose-400 hover:underline px-1 py-0.5"
          >
            Clear
          </button>
        )}

        {isStart && <span className="text-[10px] text-blue-400 font-semibold">Start</span>}
        {isTarget && (
          <span className="flex items-center gap-1 text-[10px] text-emerald-400 font-semibold">
            <Sparkles className="w-3 h-3" /> Finish
          </span>
        )}
        {feedback === 'wrong-chronology' && (
          <span className="flex items-center gap-1 text-[10px] text-rose-400 font-semibold">
            <AlertCircle className="w-3 h-3" /> Out of order
          </span>
        )}
      </div>
    </div>
  );
};
