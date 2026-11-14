import { HISTORICAL_EVENTS } from '../data/events';
import type { GameChallenge, HistoricalEvent } from '../types/game';

// Sort events chronologically
const SORTED_EVENTS = [...HISTORICAL_EVENTS].sort((a, b) => a.year - b.year);

// Generate a curated daily challenge based on a seed or date
export function getDailyChallenge(dayOffset = 0): GameChallenge {
  const today = new Date();
  today.setDate(today.getDate() + dayOffset);
  const dateKey = `${today.getFullYear()}-${today.getMonth() + 1}-${today.getDate()}`;

  // Deterministic seed based on date
  let seed = 0;
  for (let i = 0; i < dateKey.length; i++) {
    seed = (seed * 31 + dateKey.charCodeAt(i)) % 100000;
  }

  return generateChallengeFromSeed(seed, dateKey);
}

// Generate a random challenge for Quick Play / Endless mode
export function getRandomChallenge(): GameChallenge {
  const randomSeed = Math.floor(Math.random() * 100000);
  return generateChallengeFromSeed(randomSeed);
}

function generateChallengeFromSeed(seed: number, dateKey?: string): GameChallenge {
  const chainLength = 3; // 3 intermediate slots: Start -> [1] -> [2] -> [3] -> Target (Total 5 dominoes)
  
  // Pick an interval in SORTED_EVENTS that has at least 5-8 events between start and target
  const maxStartIndex = SORTED_EVENTS.length - (chainLength + 8);
  const startIndex = seed % Math.max(1, maxStartIndex);
  const startEvent = SORTED_EVENTS[startIndex];

  // Pick target event at a healthy distance
  const targetIndex = Math.min(SORTED_EVENTS.length - 1, startIndex + chainLength + 4 + (seed % 4));
  const targetEvent = SORTED_EVENTS[targetIndex];

  // Pick intermediate events that form a canonical ideal solution
  const intermediatePool = SORTED_EVENTS.slice(startIndex + 1, targetIndex);
  const step = Math.floor(intermediatePool.length / chainLength);
  const chain: HistoricalEvent[] = [];
  
  for (let i = 0; i < chainLength; i++) {
    const pickedIndex = Math.min(intermediatePool.length - 1, i * step + ((seed + i) % Math.max(1, step)));
    chain.push(intermediatePool[pickedIndex]);
  }

  return {
    id: `challenge-${seed}`,
    dateKey,
    startEvent,
    targetEvent,
    chain,
  };
}

// Evaluate if a player's placed chain is valid chronologically
export function validateChain(
  startEvent: HistoricalEvent,
  slots: (HistoricalEvent | undefined)[],
  targetEvent: HistoricalEvent
): {
  isFull: boolean;
  isValid: boolean;
  brokenAt?: number; // index of first broken link
} {
  const isFull = slots.every((s) => s !== undefined);
  if (!isFull) {
    return { isFull: false, isValid: false };
  }

  let prevYear = startEvent.year;
  for (let i = 0; i < slots.length; i++) {
    const current = slots[i]!;
    if (current.year <= prevYear) {
      return { isFull: true, isValid: false, brokenAt: i };
    }
    prevYear = current.year;
  }

  if (targetEvent.year <= prevYear) {
    return { isFull: true, isValid: false, brokenAt: slots.length };
  }

  return { isFull: true, isValid: true };
}

// Year closeness indicator (Hot / Warm / Cold)
export function getCloseness(deltaYears: number): {
  label: string;
  color: string;
  badgeBg: string;
} {
  const abs = Math.abs(deltaYears);
  if (abs === 0) {
    return { label: 'Exact Hit!', color: 'text-emerald-400', badgeBg: 'bg-emerald-500/20 border-emerald-500' };
  }
  if (abs <= 5) {
    return { label: `Blazing Hot (±${abs}y)`, color: 'text-rose-400', badgeBg: 'bg-rose-500/20 border-rose-500' };
  }
  if (abs <= 15) {
    return { label: `Warm (±${abs}y)`, color: 'text-amber-400', badgeBg: 'bg-amber-500/20 border-amber-500' };
  }
  if (abs <= 30) {
    return { label: `Cool (±${abs}y)`, color: 'text-sky-400', badgeBg: 'bg-sky-500/20 border-sky-500' };
  }
  return { label: `Freezing (±${abs}y)`, color: 'text-slate-400', badgeBg: 'bg-slate-700/30 border-slate-600' };
}
