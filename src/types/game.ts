export type Category = 
  | 'Science & Tech'
  | 'Arts & Culture'
  | 'World History'
  | 'Exploration'
  | 'Pop Culture';

export interface HistoricalEvent {
  id: string;
  title: string;
  year: number;
  description: string;
  category: Category;
  icon: string; // emoji representation
}

export type SlotFeedback = 'empty' | 'correct' | 'wrong-chronology' | 'close';

export interface GameDominoSlot {
  index: number;
  expectedEvent: HistoricalEvent;
  placedEvent?: HistoricalEvent;
  feedback: SlotFeedback;
  yearDelta?: number;
}

export interface GameChallenge {
  id: string;
  dateKey?: string;
  startEvent: HistoricalEvent;
  targetEvent: HistoricalEvent;
  chain: HistoricalEvent[]; // Intermediate required events in chronological order
}

export interface GameStats {
  played: number;
  won: number;
  currentStreak: number;
  maxStreak: number;
  guessDistribution: Record<number, number>;
}
