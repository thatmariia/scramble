export const LEVELS: Record<number, string> = {
    1: 'beginner',
    2: 'improver',
    3: 'intermediate',
    4: 'advanced',
    5: 'expert',
};

export type Level = keyof typeof LEVELS; // "1" | "2" | ... (as strings)
export const LEVEL_VALUES = Object.keys(LEVELS).map(Number) as Level[];

export const LEVEL_COLORS: Record<Level, string> = {
    1: '#49D968', 
    2: '#5BB8FF', 
    3: '#FFCC02', 
    4: '#FE8AC4', 
    5: '#A492F5', 
};