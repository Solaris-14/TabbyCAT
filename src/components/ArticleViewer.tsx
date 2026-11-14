import React, { useRef, useEffect } from 'react';
import type { WikiArticle } from '../types/game';
import { Undo2, ExternalLink, Sparkles } from 'lucide-react';
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
  const contentRef = useRef<HTMLDivElement>(null);

  const links = currentArticle.outgoingLinks || [];
  const hasTargetLink = links.some(
    (l) => l.toLowerCase() === targetTitle.toLowerCase()
  );

  // Intercept clicks on in-article <a> links
  const handleArticleClick = (e: React.MouseEvent<HTMLDivElement>) => {
    const target = e.target as HTMLElement;
    const anchor = target.closest('a');
    if (!anchor) return;

    const href = anchor.getAttribute('href');
    if (!href) return;

    // In-page anchor hash (#Early_life)
    if (href.startsWith('#')) return;

    // Internal Wikipedia link (/wiki/Title or ./Title or relative Title)
    if (
      href.startsWith('/wiki/') ||
      href.startsWith('./') ||
      (!href.includes('://') && !href.startsWith('//'))
    ) {
      e.preventDefault();
      e.stopPropagation();

      let pageTitle = href.replace(/^\/wiki\//, '').replace(/^\.\//, '');
      pageTitle = pageTitle.split('#')[0];

      // Filter out non-article namespaces
      if (pageTitle && !pageTitle.includes(':')) {
        const decoded = decodeURIComponent(pageTitle).replace(/_/g, ' ');
        sounds.playTileClick();
        onSelectLink(decoded);
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
    }
  };

  // Highlight target link inside the live Wikipedia article if present
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
  }, [currentArticle.title, targetTitle]);

  return (
    <div className="w-full max-w-5xl mx-auto bg-slate-900/90 border border-slate-800 rounded-3xl p-6 sm:p-10 shadow-2xl backdrop-blur-md">
      {/* Sticky Quick-Bar on Mobile & Desktop */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 pb-6 mb-6 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-[10px] font-bold uppercase tracking-wider text-blue-400 bg-blue-500/10 px-2.5 py-0.5 rounded-full border border-blue-500/20">
              Wikipedia Article
            </span>
            <a
              href={`https://en.wikipedia.org/wiki/${encodeURIComponent(currentArticle.title)}`}
              target="_blank"
              rel="noreferrer"
              className="text-xs text-slate-500 hover:text-slate-300 flex items-center gap-1"
              title="Open on Wikipedia.org"
            >
              <span>View Source</span>
              <ExternalLink className="w-3 h-3" />
            </a>
          </div>
          <h1 className="text-2xl sm:text-4xl font-black text-white mt-1 tracking-tight">
            {currentArticle.displayTitle}
          </h1>
          {currentArticle.description && (
            <p className="text-xs sm:text-sm text-slate-400 mt-0.5 font-medium">
              {currentArticle.description}
            </p>
          )}
        </div>

        {/* Undo Hop Button */}
        {canUndo && (
          <button
            type="button"
            onClick={onUndo}
            disabled={isLoading}
            className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-bold flex items-center gap-1.5 transition-all border border-slate-700 active:scale-95 shadow-md flex-shrink-0"
          >
            <Undo2 className="w-4 h-4 text-amber-400" /> Undo Hop
          </button>
        )}
      </div>

      {/* Target Sighted Alert Banner */}
      {hasTargetLink && (
        <div className="mb-6 p-4 rounded-2xl bg-gradient-to-r from-emerald-950/90 via-slate-900 to-amber-950/80 border-2 border-emerald-400 shadow-xl shadow-emerald-500/20 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <Sparkles className="w-6 h-6 text-amber-400 animate-spin flex-shrink-0" />
            <div>
              <div className="text-[11px] font-black uppercase tracking-wider text-emerald-300">
                Target Link Found in this Article!
              </div>
              <div className="text-sm font-black text-white">
                "{targetTitle}" is hyperlinked in the text below!
              </div>
            </div>
          </div>
          <button
            type="button"
            onClick={() => onSelectLink(targetTitle)}
            className="px-4 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-black text-xs uppercase tracking-wider shadow-lg hover:scale-105 active:scale-95 transition-all flex items-center gap-1.5"
          >
            Hop Directly to Goal &rarr;
          </button>
        </div>
      )}

      {/* The Entire Authentic Wikipedia Article */}
      <div className="relative min-h-[400px]">
        {isLoading ? (
          <div className="w-full py-32 text-center text-sm text-slate-400 animate-pulse bg-slate-950/40 rounded-2xl border border-slate-800 flex flex-col items-center justify-center gap-2">
            <div className="w-8 h-8 rounded-full border-2 border-amber-400 border-t-transparent animate-spin mb-2" />
            <span>Loading full Wikipedia article for <strong>{currentArticle.displayTitle}</strong>...</span>
          </div>
        ) : currentArticle.html ? (
          <div
            ref={contentRef}
            onClick={handleArticleClick}
            dangerouslySetInnerHTML={{ __html: currentArticle.html }}
            className="wiki-article-container select-text"
          />
        ) : (
          <div
            ref={contentRef}
            onClick={handleArticleClick}
            className="wiki-article-container"
          >
            <p>{currentArticle.extract}</p>
          </div>
        )}
      </div>
    </div>
  );
};
