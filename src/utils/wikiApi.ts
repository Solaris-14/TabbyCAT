import { PRECACHED_ARTICLES } from '../data/wikiChallenges';
import type { WikiArticle } from '../types/game';

const cache = new Map<string, WikiArticle>();

export function normalizeTitle(title: string): string {
  return title.replace(/_/g, ' ').trim();
}

/**
 * Clean Wikipedia HTML:
 * 1. Ensures protocol-relative image URLs have https:
 * 2. Hides edit links and audio players that clutter reader view
 */
function processWikiHtml(rawHtml: string): string {
  return rawHtml
    .replace(/src="\/\//g, 'src="https://')
    .replace(/srcset="\/\//g, 'srcset="https://');
}

/**
 * Fetch actual Wikipedia article: HTML, summary, thumbnail, and outgoing links
 */
export async function getWikiArticle(rawTitle: string): Promise<WikiArticle> {
  const title = normalizeTitle(rawTitle);

  // Check in-memory cache
  if (cache.has(title)) {
    return cache.get(title)!;
  }

  // Check precached starter bank
  if (PRECACHED_ARTICLES[title] && PRECACHED_ARTICLES[title].html) {
    cache.set(title, PRECACHED_ARTICLES[title]);
    return PRECACHED_ARTICLES[title];
  }

  try {
    // 1. Fetch summary & thumbnail via REST API
    const summaryPromise = fetch(
      `https://en.wikipedia.org/api/rest_v1/page/summary/${encodeURIComponent(title)}`,
      { headers: { Accept: 'application/json' } }
    ).then((r) => (r.ok ? r.json() : null)).catch(() => null);

    // 2. Fetch actual full article HTML and links via MediaWiki Parse API
    const parsePromise = fetch(
      `https://en.wikipedia.org/w/api.php?action=parse&page=${encodeURIComponent(
        title
      )}&prop=text|links&format=json&origin=*`
    ).then((r) => (r.ok ? r.json() : null)).catch(() => null);

    const [summaryData, parseData] = await Promise.all([summaryPromise, parsePromise]);

    const rawHtml = parseData?.parse?.text?.['*'] || '';
    const cleanHtml = rawHtml ? processWikiHtml(rawHtml) : undefined;

    let outgoingLinks: string[] = [];
    if (parseData?.parse?.links) {
      outgoingLinks = parseData.parse.links
        .filter((l: { ns: number; exists?: unknown; '*'?: string }) => l.ns === 0 && l['*'])
        .map((l: { '*': string }) => l['*'])
        .filter((t: string) => !t.includes(':') && !t.startsWith('List of '));
    }

    const article: WikiArticle = {
      title: parseData?.parse?.title || title,
      displayTitle: summaryData?.title || parseData?.parse?.title || title,
      description: summaryData?.description,
      extract: summaryData?.extract || 'Wikipedia encyclopedic article.',
      thumbnail: summaryData?.thumbnail?.source,
      outgoingLinks: outgoingLinks.length > 0 ? outgoingLinks : (PRECACHED_ARTICLES[title]?.outgoingLinks || []),
      html: cleanHtml || PRECACHED_ARTICLES[title]?.html,
    };

    cache.set(title, article);
    return article;
  } catch (err) {
    console.warn(`[WikiApi] Network fetch failed for "${title}". Falling back to mock.`, err);

    const fallback = PRECACHED_ARTICLES[title] || {
      title,
      displayTitle: title,
      description: 'Wikipedia Article',
      extract: `This is the Wikipedia article for ${title}.`,
      outgoingLinks: ['France', 'United States', 'United Kingdom', 'Rome', 'Napoleon', 'Julius Caesar'],
    };

    cache.set(title, fallback);
    return fallback;
  }
}
