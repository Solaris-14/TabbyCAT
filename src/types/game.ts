export interface WikiArticle {
  title: string;
  displayTitle: string;
  description?: string;
  extract: string;
  thumbnail?: string;
  outgoingLinks: string[];
  html?: string; // Full actual Wikipedia article HTML content
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
  parHops: number;
  hint?: string;
}

export interface WikiGameStats {
  played: number;
  won: number;
  bestHops: number;
  currentStreak: number;
}
