import { create } from "zustand";

interface GenerationPreferences {
  provider: string;
  model: string;
  temperature: number;
  maxTokens: number;
}

interface GenerationStore {
  // User preferences (persisted across sessions)
  preferences: GenerationPreferences;

  // Actions
  setPreferences: (prefs: Partial<GenerationPreferences>) => void;
  resetPreferences: () => void;
}

const DEFAULT_PREFERENCES: GenerationPreferences = {
  provider: "openai",
  model: "gpt-4o",
  temperature: 0.7,
  maxTokens: 4096,
};

export const useGenerationStore = create<GenerationStore>((set) => ({
  preferences: DEFAULT_PREFERENCES,

  setPreferences: (prefs) =>
    set((state) => ({
      preferences: { ...state.preferences, ...prefs },
    })),

  resetPreferences: () => set({ preferences: DEFAULT_PREFERENCES }),
}));
