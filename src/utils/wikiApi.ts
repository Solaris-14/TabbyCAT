import { PRECACHED_ARTICLES } from '../data/wikiChallenges';
import type { WikiArticle } from '../types/game';

const cache = new Map<string, WikiArticle>();

// Normalize article title
export function normalizeTitle(title: string): string {
  return title.replace(/_/g, ' ').trim();
}

/**
 * Fetch Wikipedia article summary, thumbnail, and outgoing main-namespace links
 */
export async function getWikiArticle(rawTitle: string): Promise<WikiArticle> {
  const title = normalizeTitle(rawTitle);

  // Check in-memory cache
  if (cache.has(title)) {
    return cache.get(title)!;
  }

  // Check precached starter bank
  if (PRECACHED_ARTICLES[title]) {
    cache.set(title, PRECACHED_ARTICLES[title]);
    return PRECACHED_ARTICLES[title];
  }

  try {
    // 1. Fetch page summary & thumbnail from Wikipedia REST API
    const summaryRes = await fetch(
      `https://en.wikipedia.org/api/rest_v1/page/summary/${encodeURIComponent(title)}`,
      { headers: { Accept: 'application/json' } }
    );

    if (!summaryRes.ok) {
      throw new Error(`Summary fetch failed: ${summaryRes.statusText}`);
    }

    const summaryData = await summaryRes.json();

    // 2. Fetch outgoing links (limit 500, namespace 0 for main encyclopedia articles)
    const linksRes = await fetch(
      `https://en.wikipedia.org/w/api.php?action=query&titles=${encodeURIComponent(
        title
      )}&prop=links&pllimit=500&plnamespace=0&format=json&origin=*`
    );

    let outgoingLinks: string[] = [];
    if (linksRes.ok) {
      const linksData = await linksRes.json();
      const pages = linksData?.query?.pages || {};
      const firstPage = Object.values(pages)[0] as { links?: { title: string }[] } | undefined;
      if (firstPage?.links) {
        outgoingLinks = firstPage.links
          .map((l) => l.title)
          .filter((t) => !t.includes(':') && !t.startsWith('List of ')); // Exclude namespaces & lists
      }
    }

    const article: WikiArticle = {
      title,
      displayTitle: summaryData.title || title,
      description: summaryData.description,
      extract: summaryData.extract || 'No article extract available.',
      thumbnail: summaryData.thumbnail?.source,
      outgoingLinks,
    };

    cache.set(title, article);
    return article;
  } catch (err) {
    console.warn(`[WikiApi] Network fetch failed for "${title}". Falling back to mock.`, err);

    // Fallback if network blocked or offline
    const fallbackArticle: WikiArticle = PRECACHED_ARTICLES[title] || {
      title,
      displayTitle: title,
      description: 'Wikipedia Article',
      extract: `This is the Wikipedia article for ${title}. (Offline preview mode)`,
      outgoingLinks: ['France', 'United States', 'United Kingdom', 'Rome', 'Napoleon', 'Julius Caesar'],
    };

    cache.set(title, fallbackArticle);
    return fallbackArticle;
  }
}
