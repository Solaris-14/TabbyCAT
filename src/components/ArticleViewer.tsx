import React, { useState, useRef, useEffect, useMemo } from 'react';
import type { WikiArticle } from '../types/game';
import { Search, Undo2, ExternalLink, Sparkles, BookOpen, ListFilter, X } from 'lucide-react';
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
  const [viewMode, setViewMode] = useState<'article' | 'links'>('article');
  const [filterQuery, setFilterQuery] = useState('');
  const contentRef = useRef<HTMLDivElement>(null);

  const links = currentArticle.outgoingLinks || [];

  // Filter links for the links tab
  const filteredLinks = useMemo(() => {
    const q = filterQuery.toLowerCase().trim();
    if (!q) return links;
    return links.filter((link) => link.toLowerCase().includes(q));
  }, [links, filterQuery]);

  // Is target in outgoing links?
  const hasTargetLink = links.some(
    (l) => l.toLowerCase() === targetTitle.toLowerCase()
  );

  // Intercept click on in-article <a> hyperlinks
  const handleArticleClick = (e: React.MouseEvent<HTMLDivElement>) => {
    const target = e.target as HTMLElement;
    const anchor = target.closest('a');
    if (!anchor) return;

    const href = anchor.getAttribute('href');
    if (!href) return;

    // Ignore in-page section hashes (#References)
    if (href.startsWith('#')) return;

    // Internal Wikipedia link patterns: /wiki/Title or ./Title or relative Title
    if (
      href.startsWith('/wiki/') ||
      href.startsWith('./') ||
      (!href.includes('://') && !href.startsWith('//'))
    ) {
      e.preventDefault();
      e.stopPropagation();

      let pageTitle = href.replace(/^\/wiki\//, '').replace(/^\.\//, '');
      // Strip section fragment
      pageTitle = pageTitle.split('#')[0];

      // Exclude special namespaces (File:, Help:, Talk:, etc.)
      if (pageTitle && !pageTitle.includes(':')) {
        const decoded = decodeURIComponent(pageTitle).replace(/_/g, ' ');
        sounds.playTileClick();
        onSelectLink(decoded);
      }
    }
  };

  // Enhance rendered HTML: tag the target link if present
  useEffect(() => {
    if (!contentRef.current) return;
    const container = contentRef.current;
    const anchors = container.querySelectorAll('a');

    anchors.forEach((a) => {
      const href = a.getAttribute('href') || '';
      const text = a.textContent?.trim().toLowerCase() || '';
      const title = a.getAttribute('title')?.toLowerCase() || '';
      const normalizedTarget = targetTitle.toLowerCase();

      if (
        text === normalizedTarget ||
        title === normalizedTarget ||
        href.toLowerCase().endsWith(encodeURIComponent(targetTitle.replace(/ /g, '_')).toLowerCase())
      ) {
        a.setAttribute('data-target-link', 'true');
        a.innerHTML = `🎯 <strong>${a.innerHTML}</strong>`;
      }
    });

    // Scroll to top of article on change
    container.scrollTop = 0;
  }, [currentArticle.title, targetTitle, viewMode]);

  return (
    <div className="w-full max-w-4xl mx-auto bg-slate-900/90 border border-slate-800 rounded-3xl p-5 sm:p-7 shadow-2xl backdrop-blur-md">
      {/* Article Header & Navigation */}
      <div className="flex flex-col sm:flex-row items-start justify-between gap-4 pb-5 border-b border-slate-800">
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
                Active Wikipedia Article
              </span>
              <a
                href={`https://en.wikipedia.org/wiki/${encodeURIComponent(currentArticle.title)}`}
                target="_blank"
                rel="noreferrer"
                className="text-xs text-slate-500 hover:text-slate-300 flex items-center gap-1"
                title="View original on Wikipedia"
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

        {/* View Mode Switch & Undo */}
        <div className="flex items-center gap-2 self-end sm:self-start">
          <div className="flex bg-slate-950 p-1 rounded-xl border border-slate-800">
            <button
              type="button"
              onClick={() => setViewMode('article')}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold flex items-center gap-1.5 transition-all ${
                viewMode === 'article'
                  ? 'bg-amber-500 text-slate-950 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <BookOpen className="w-3.5 h-3.5" /> Full Article
            </button>
            <button
              type="button"
              onClick={() => setViewMode('links')}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold flex items-center gap-1.5 transition-all ${
                viewMode === 'links'
                  ? 'bg-amber-500 text-slate-950 shadow-sm'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <ListFilter className="w-3.5 h-3.5" /> Link Index ({links.length})
            </button>
          </div>

          {canUndo && (
            <button
              type="button"
              onClick={onUndo}
              disabled={isLoading}
              className="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-bold flex items-center gap-1 transition-all border border-slate-700 active:scale-95"
              title="Undo previous hop"
            >
              <Undo2 className="w-3.5 h-3.5" /> Undo
            </button>
          )}
        </div>
      </div>

      {/* Target Sighted Alert Banner */}
      {hasTargetLink && (
        <div className="my-4 p-3 rounded-2xl bg-gradient-to-r from-emerald-950/80 to-amber-950/60 border-2 border-emerald-400 shadow-xl shadow-emerald-500/20 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <Sparkles className="w-5 h-5 text-amber-400 animate-spin" />
            <div>
              <div className="text-[10px] font-extrabold uppercase tracking-wider text-emerald-300">
                Direct Link Sighted in Article!
              </div>
              <div className="text-sm font-black text-white">
                "{targetTitle}" is hyperlinked on this page!
              </div>
            </div>
          </div>
          <button
            type="button"
            onClick={() => onSelectLink(targetTitle)}
            className="px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-black text-xs uppercase tracking-wider shadow-md hover:scale-105 active:scale-95 transition-all"
          >
            Hop to Target &rarr;
          </button>
        </div>
      )}

      {/* View 1: The Actual Wikipedia Article with In-Text Hyperlinks */}
      {viewMode === 'article' ? (
        <div className="relative mt-4">
          <div className="text-[11px] font-semibold text-slate-400 flex items-center justify-between mb-2 px-1">
            <span>Click any blue hyperlink in the article text to hop:</span>
            <span className="text-[10px] text-amber-400 font-mono">
              💡 Tip: Click in-text links to navigate
            </span>
          </div>

          {isLoading ? (
            <div className="w-full py-20 text-center text-xs text-slate-500 animate-pulse bg-slate-950/40 rounded-2xl border border-slate-800">
              Loading Wikipedia article content...
            </div>
          ) : currentArticle.html ? (
            <div
              ref={contentRef}
              onClick={handleArticleClick}
              dangerouslySetInnerHTML={{ __html: currentArticle.html }}
              className="wiki-content max-h-[500px] overflow-y-auto p-5 sm:p-7 bg-slate-950/60 border border-slate-800/80 rounded-2xl shadow-inner scrollbar-thin scrollbar-thumb-slate-800 scrollbar-track-transparent select-text"
            />
          ) : (
            <div
              ref={contentRef}
              onClick={handleArticleClick}
              className="wiki-content max-h-[500px] overflow-y-auto p-5 sm:p-7 bg-slate-950/60 border border-slate-800/80 rounded-2xl shadow-inner text-sm leading-relaxed"
            >
              <p>{currentArticle.extract}</p>
            </div>
          )}
        </div>
      ) : (
        /* View 2: Link Index Grid */
        <div className="mt-4">
          <div className="flex items-center justify-between gap-3 mb-4">
            <div className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Filtered Links ({filteredLinks.length} / {links.length})
            </div>
            <div className="relative w-full sm:w-64">
              <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
              <input
                type="text"
                value={filterQuery}
                onChange={(e) => setFilterQuery(e.target.value)}
                placeholder="Search links on page..."
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

          <div className="max-h-[460px] overflow-y-auto pr-1 flex flex-wrap gap-2 scrollbar-thin scrollbar-thumb-slate-800">
            {filteredLinks.map((link) => {
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
            })}
          </div>
        </div>
      )}
    </div>
  );
};
