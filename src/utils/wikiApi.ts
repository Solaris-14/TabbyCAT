import { PRECACHED_ARTICLES } from '../data/wikiChallenges';
import type { WikiArticle } from '../types/game';

const cache = new Map<string, WikiArticle>();

export function normalizeTitle(title: string): string {
  return title.replace(/_/g, ' ').trim();
}

/**
 * Fix Wikipedia relative image and asset URLs so they render reliably
 */
function processWikiHtml(rawHtml: string): string {
  return rawHtml
    .replace(/src="\/\//g, 'src="https://')
    .replace(/srcset="\/\//g, 'srcset="https://')
    .replace(/href="\/\/upload/g, 'href="https://upload');
}

/**
 * Fetch the entire actual Wikipedia article directly from Wikipedia
 */
export async function getWikiArticle(rawTitle: string): Promise<WikiArticle> {
  const title = normalizeTitle(rawTitle);

  // Check in-memory cache
  if (cache.has(title)) {
    return cache.get(title)!;
  }

  // 1. Try fetching the LIVE complete Wikipedia article first
  try {
    const parseUrl = `https://en.wikipedia.org/w/api.php?action=parse&page=${encodeURIComponent(
      title
    )}&prop=text|links&format=json&origin=*`;

    const summaryUrl = `https://en.wikipedia.org/api/rest_v1/page/summary/${encodeURIComponent(
      title
    )}`;

    const [parseRes, summaryRes] = await Promise.all([
      fetch(parseUrl),
      fetch(summaryUrl, { headers: { Accept: 'application/json' } }).catch(() => null),
    ]);

    if (!parseRes.ok) {
      throw new Error(`Parse API error: ${parseRes.statusText}`);
    }

    const parseData = await parseRes.json();
    if (parseData.error) {
      throw new Error(parseData.error.info || 'Wikipedia API error');
    }

    const summaryData = summaryRes && summaryRes.ok ? await summaryRes.json() : null;
    const rawHtml = parseData?.parse?.text?.['*'];

    if (!rawHtml) {
      throw new Error('No article HTML returned from Wikipedia');
    }

    const cleanHtml = processWikiHtml(rawHtml);

    // Extract outgoing links
    const outgoingLinks: string[] = (parseData?.parse?.links || [])
      .filter((l: { ns: number; exists?: unknown; '*'?: string }) => l.ns === 0 && l['*'])
      .map((l: { '*': string }) => l['*'])
      .filter((t: string) => !t.includes(':') && !t.startsWith('List of '));

    const article: WikiArticle = {
      title: parseData?.parse?.title || title,
      displayTitle: summaryData?.title || parseData?.parse?.title || title,
      description: summaryData?.description,
      extract: summaryData?.extract || '',
      thumbnail: summaryData?.thumbnail?.source,
      outgoingLinks,
      html: cleanHtml,
    };

    cache.set(title, article);
    return article;
  } catch (err) {
    console.warn(`[WikiApi] Live fetch failed for "${title}". Falling back to cache/mock.`, err);

    // 2. Fallback to precached article if network is unavailable
    if (PRECACHED_ARTICLES[title]) {
      cache.set(title, PRECACHED_ARTICLES[title]);
      return PRECACHED_ARTICLES[title];
    }

    const fallback: WikiArticle = {
      title,
      displayTitle: title,
      description: 'Wikipedia Article',
      extract: `This is the Wikipedia article for ${title}.`,
      outgoingLinks: ['France', 'United States', 'Napoleon', 'Julius Caesar'],
    };
    cache.set(title, fallback);
    return fallback;
  }
}
