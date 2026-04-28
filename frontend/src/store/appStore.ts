import { create } from 'zustand'

import type { IRReport } from '../types/reports'

interface AppState {
  selectedAlertIds: Set<string>
  activeReport: IRReport | null
  streamingText: string
  isStreaming: boolean
  drawerOpen: boolean
  pendingQueueCount: number

  toggleAlertSelection: (id: string) => void
  clearSelection: () => void
  setActiveReport: (report: IRReport | null) => void
  appendStreamToken: (token: string) => void
  resetStream: () => void
  setStreaming: (value: boolean) => void
  setDrawerOpen: (value: boolean) => void
  setPendingQueueCount: (count: number) => void
}

export const useAppStore = create<AppState>((set) => ({
  selectedAlertIds: new Set(),
  activeReport: null,
  streamingText: '',
  isStreaming: false,
  drawerOpen: false,
  pendingQueueCount: 0,

  toggleAlertSelection: (id) =>
    set((state) => {
      const next = new Set(state.selectedAlertIds)
      if (next.has(id)) {
        next.delete(id)
      } else {
        next.add(id)
      }
      return { selectedAlertIds: next }
    }),

  clearSelection: () => set({ selectedAlertIds: new Set() }),

  setActiveReport: (report) => set({ activeReport: report }),

  appendStreamToken: (token) =>
    set((state) => ({ streamingText: state.streamingText + token })),

  resetStream: () => set({ streamingText: '', isStreaming: false }),

  setStreaming: (value) => set({ isStreaming: value }),

  setDrawerOpen: (value) => set({ drawerOpen: value }),

  setPendingQueueCount: (count) => set({ pendingQueueCount: count }),
}))
