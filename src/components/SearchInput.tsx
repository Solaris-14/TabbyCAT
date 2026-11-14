import React, { useState, useMemo, useRef, useEffect } from 'react';
import { HISTORICAL_EVENTS } from '../data/events';
import type { HistoricalEvent, Category } from '../types/game';
import { Search, X, Check } from 'lucide-react';
import { sounds } from '../utils/audio';

interface SearchInputProps {
  onSelectEvent: (event: HistoricalEvent) => void;
  placedEventIds: string[];
  activeSlotIndex: number;
}

const CATEGORIES: ('All' | Category)[] = [
  'All',
  'Science & Tech',
  'World History',
  'Arts & Culture',
  'Exploration',
  'Pop Culture',
];

export const SearchInput: React.FC<SearchInputProps> = ({
  onSelectEvent,
  placedEventIds,
  activeSlotIndex,
}) => {
  const [query, setQuery] = useState('');
  const [category, setCategory] = useState<'All' | Category>('All');
  const [isOpen, setIsOpen] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  // Auto focus input when mounted or active slot changes
  useEffect(() => {
    inputRef.current?.focus();
  }, [activeSlotIndex]);

  const filteredEvents = useMemo(() => {
    const q = query.toLowerCase().trim();
    return HISTORICAL_EVENTS.filter((e) => {
      // Category filter
      if (category !== 'All' && e.category !== category) return false;

      // Text query
      if (!q) return true;
      return (
        e.title.toLowerCase().includes(q) ||
        e.description.toLowerCase().includes(q) ||
        e.year.toString().includes(q) ||
        e.category.toLowerCase().includes(q)
      );
    });
  }, [query, category]);

  const handleSelect = (event: HistoricalEvent) => {
    sounds.playTileClick();
    onSelectEvent(event);
    setQuery('');
    setIsOpen(false);
  };

  return (
    <div className="w-full max-w-2xl mx-auto mt-6 relative">
      {/* Category Pills */}
      <div className="flex items-center gap-1.5 overflow-x-auto pb-2 mb-2 scrollbar-none text-xs">
        {CATEGORIES.map((cat) => (
          <button
            key={cat}
            type="button"
            onClick={() => setCategory(cat)}
            className={`px-3 py-1 rounded-full whitespace-nowrap font-medium transition-all ${
              category === cat
                ? 'bg-amber-500 text-slate-950 font-bold shadow-md shadow-amber-500/20'
                : 'bg-slate-800 text-slate-400 hover:bg-slate-700 hover:text-slate-200'
            }`}
          >
            {cat}
          </button>
        ))}
      </div>

      {/* Main Search Input */}
      <div className="relative flex items-center">
        <Search className="absolute left-4 w-5 h-5 text-slate-400 pointer-events-none" />
        <input
          ref={inputRef}
          type="text"
          value={query}
          onFocus={() => setIsOpen(true)}
          onChange={(e) => {
            setQuery(e.target.value);
            setIsOpen(true);
          }}
          placeholder={`Search historical event for Slot ${activeSlotIndex + 1} (e.g. Apollo 11, Titanic, Penicillin)...`}
          className="w-full pl-12 pr-10 py-3.5 bg-slate-900 border-2 border-slate-700 focus:border-amber-400 focus:outline-none rounded-xl text-slate-100 placeholder-slate-500 text-sm shadow-xl transition-all"
        />
        {query && (
          <button
            type="button"
            onClick={() => setQuery('')}
            className="absolute right-3.5 p-1 rounded-full hover:bg-slate-800 text-slate-400 hover:text-slate-200"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Autocomplete Dropdown */}
      {isOpen && (
        <div className="absolute z-50 left-0 right-0 mt-2 bg-slate-900/95 backdrop-blur-md border border-slate-700 rounded-xl max-h-80 overflow-y-auto shadow-2xl divide-y divide-slate-800">
          {filteredEvents.length === 0 ? (
            <div className="p-4 text-center text-sm text-slate-500">
              No historical events found matching "{query}".
            </div>
          ) : (
            filteredEvents.map((item) => {
              const isAlreadyPlaced = placedEventIds.includes(item.id);
              return (
                <button
                  key={item.id}
                  disabled={isAlreadyPlaced}
                  onClick={() => handleSelect(item)}
                  type="button"
                  className={`w-full px-4 py-3 text-left flex items-center justify-between group transition-colors ${
                    isAlreadyPlaced
                      ? 'opacity-40 cursor-not-allowed bg-slate-950/40'
                      : 'hover:bg-slate-800/80 cursor-pointer'
                  }`}
                >
                  <div className="flex items-start gap-3">
                    <span className="text-2xl mt-0.5">{item.icon}</span>
                    <div>
                      <div className="font-semibold text-sm text-slate-200 group-hover:text-amber-400 transition-colors">
                        {item.title}
                      </div>
                      <div className="text-xs text-slate-400 line-clamp-1 mt-0.5">
                        {item.description}
                      </div>
                      <div className="flex items-center gap-2 mt-1">
                        <span className="text-[10px] font-mono font-bold text-amber-400 bg-amber-400/10 px-1.5 py-0.5 rounded border border-amber-400/20">
                          {item.year}
                        </span>
                        <span className="text-[10px] text-slate-500">
                          {item.category}
                        </span>
                      </div>
                    </div>
                  </div>

                  {isAlreadyPlaced ? (
                    <span className="text-xs text-slate-500 flex items-center gap-1">
                      <Check className="w-3.5 h-3.5" /> Placed
                    </span>
                  ) : (
                    <span className="text-xs font-semibold text-amber-400 opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
                      Select Domino &rarr;
                    </span>
                  )}
                </button>
              );
            })
          )}
        </div>
      )}
    </div>
  );
};
