import React, { useState, useMemo } from 'react';
import type { WikiArticle } from '../types/game';
import { Search, Undo2, ExternalLink, Sparkles, X } from 'lucide-react';
import { sounds } from '../utils/audio';

interface ArticleViewerProps {
  currentArticle: WikiArticle;
  targetTitle: string;
  onSelectLink: (linkTitle: string) => void;
  onUndo: () => void;
  canUndo: boolean;
  isLoading: boolean;
}

export const ArticleViewer: React.FC<ArticleViewerProps> = ({
  currentArticle,
  targetTitle,
  onSelectLink,
  onUndo,
  canUndo,
  isLoading,
}) => {
  const [filterQuery, setFilterQuery] = useState('');

  const links = currentArticle.outgoingLinks || [];

  // Filter links
  const filteredLinks = useMemo(() => {
    const q = filterQuery.toLowerCase().trim();
    if (!q) return links;
    return links.filter((link) => link.toLowerCase().includes(q));
  }, [links, filterQuery]);

  // Is target in outgoing links?
  const hasTargetLink = links.some(
    (l) => l.toLowerCase() === targetTitle.toLowerCase()
  );

  return (
    <div className="w-full max-w-4xl mx-auto bg-slate-900/80 border border-slate-800 rounded-3xl p-5 sm:p-7 shadow-2xl backdrop-blur-md">
      {/* Current Article Header */}
      <div className="flex flex-col sm:flex-row items-start justify-between gap-5 pb-6 border-b border-slate-800">
        <div className="flex items-start gap-4 flex-1">
          {currentArticle.thumbnail && (
            <img
              src={currentArticle.thumbnail}
              alt={currentArticle.displayTitle}
              className="w-16 h-16 sm:w-20 sm:h-20 rounded-2xl object-cover border border-slate-700 shadow-md flex-shrink-0"
            />
          )}
          <div>
            <div className="flex items-center gap-2">
              <span className="text-[10px] font-bold uppercase tracking-wider text-blue-400 bg-blue-500/10 px-2.5 py-0.5 rounded-full border border-blue-500/20">
                Current Location
              </span>
              <a
                href={`https://en.wikipedia.org/wiki/${encodeURIComponent(currentArticle.title)}`}
                target="_blank"
                rel="noreferrer"
                className="text-xs text-slate-500 hover:text-slate-300 flex items-center gap-1"
                title="View on Wikipedia"
              >
                <ExternalLink className="w-3 h-3" />
              </a>
            </div>
            <h2 className="text-xl sm:text-2xl font-black text-white mt-1">
              {currentArticle.displayTitle}
            </h2>
            {currentArticle.description && (
              <p className="text-xs sm:text-sm text-slate-400 mt-0.5">
                {currentArticle.description}
              </p>
            )}
          </div>
        </div>

        {/* Undo button */}
        {canUndo && (
          <button
            type="button"
            onClick={onUndo}
            disabled={isLoading}
            className="px-3.5 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-bold flex items-center gap-1.5 transition-all border border-slate-700 active:scale-95 flex-shrink-0"
          >
            <Undo2 className="w-4 h-4" /> Undo Hop
          </button>
        )}
      </div>

      {/* Article Extract */}
      <div className="my-5 p-4 rounded-2xl bg-slate-950/50 border border-slate-800/80 text-xs sm:text-sm leading-relaxed text-slate-300 font-sans">
        {currentArticle.extract}
      </div>

      {/* Outgoing Links Section */}
      <div>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-4">
          <div className="flex items-center gap-2">
            <h3 className="text-xs sm:text-sm font-extrabold uppercase tracking-wider text-slate-200">
              Hyperlinks on this Page
            </h3>
            <span className="text-[11px] font-mono text-slate-500 px-2 py-0.5 rounded bg-slate-800">
              {filteredLinks.length} / {links.length}
            </span>
          </div>

          {/* Quick link filter */}
          <div className="relative w-full sm:w-64">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              value={filterQuery}
              onChange={(e) => setFilterQuery(e.target.value)}
              placeholder="Search links..."
              className="w-full pl-9 pr-8 py-1.5 bg-slate-950 border border-slate-700 focus:border-amber-400 focus:outline-none rounded-xl text-xs text-slate-100 placeholder-slate-500 transition-all"
            />
            {filterQuery && (
              <button
                type="button"
                onClick={() => setFilterQuery('')}
                className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}
          </div>
        </div>

        {/* Pinned Target Button if available */}
        {hasTargetLink && (
          <div className="mb-4 p-3 rounded-2xl bg-gradient-to-r from-emerald-950/80 to-amber-950/60 border-2 border-emerald-400 shadow-xl shadow-emerald-500/20 flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <Sparkles className="w-5 h-5 text-amber-400 animate-spin" />
              <div>
                <div className="text-[11px] font-extrabold uppercase tracking-wider text-emerald-300">
                  Direct Target Link Found!
                </div>
                <div className="text-sm font-black text-white">
                  {targetTitle}
                </div>
              </div>
            </div>
            <button
              type="button"
              onClick={() => onSelectLink(targetTitle)}
              className="px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-black text-xs uppercase tracking-wider shadow-md hover:scale-105 active:scale-95 transition-all flex items-center gap-1.5"
            >
              Finish Domino Chain &rarr;
            </button>
          </div>
        )}

        {/* Links Grid */}
        <div className="max-h-72 sm:max-h-80 overflow-y-auto pr-1 flex flex-wrap gap-2 scrollbar-thin scrollbar-thumb-slate-800">
          {isLoading ? (
            <div className="w-full py-10 text-center text-xs text-slate-500 animate-pulse">
              Loading Wikipedia article...
            </div>
          ) : filteredLinks.length === 0 ? (
            <div className="w-full py-8 text-center text-xs text-slate-500">
              No links matched "{filterQuery}".
            </div>
          ) : (
            filteredLinks.map((link) => {
              const isTarget = link.toLowerCase() === targetTitle.toLowerCase();
              return (
                <button
                  key={link}
                  type="button"
                  onClick={() => {
                    sounds.playTileClick();
                    onSelectLink(link);
                  }}
                  className={`px-3 py-1.5 rounded-xl text-xs font-semibold text-left transition-all duration-200 active:scale-95 border ${
                    isTarget
                      ? 'bg-emerald-500/30 text-emerald-200 border-emerald-400/80 shadow-md shadow-emerald-500/30 font-bold hover:bg-emerald-500 hover:text-slate-950'
                      : 'bg-slate-800/80 text-slate-300 border-slate-700/60 hover:bg-amber-500 hover:text-slate-950 hover:border-amber-400'
                  }`}
                >
                  {isTarget && '🎯 '}
                  {link}
                </button>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
};
