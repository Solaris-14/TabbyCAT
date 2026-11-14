export interface WikiArticle {
  title: string;
  displayTitle: string;
  description?: string;
  extract: string;
  thumbnail?: string;
  outgoingLinks: string[];
}

export interface WikiHop {
  step: number;
  article: WikiArticle;
}

export interface WikiChallenge {
  id: string;
  dateKey?: string;
  title: string;
  startTitle: string;
  targetTitle: string;
  parHops: number; // optimal shortest path estimate
  hint?: string;
}

export interface WikiGameStats {
  played: number;
  won: number;
  bestHops: number;
  currentStreak: number;
}
