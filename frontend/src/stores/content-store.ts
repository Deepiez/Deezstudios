import { create } from "zustand";
import type { ContentItem, ContentVersion } from "@/types";

interface ContentStore {
  // Current content being viewed/edited
  currentContent: ContentItem | null;
  currentVersions: ContentVersion[];
  selectedVersion: number;

  // Actions
  setCurrentContent: (content: ContentItem | null) => void;
  setCurrentVersions: (versions: ContentVersion[]) => void;
  setSelectedVersion: (version: number) => void;
  reset: () => void;
}

export const useContentStore = create<ContentStore>((set) => ({
  currentContent: null,
  currentVersions: [],
  selectedVersion: 0,

  setCurrentContent: (content) =>
    set({ currentContent: content, selectedVersion: content?.current_version || 0 }),
  setCurrentVersions: (versions) => set({ currentVersions: versions }),
  setSelectedVersion: (version) => set({ selectedVersion: version }),
  reset: () =>
    set({ currentContent: null, currentVersions: [], selectedVersion: 0 }),
}));
