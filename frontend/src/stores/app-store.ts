import { create } from "zustand"
import type {
  User,
  Workspace,
  Post,
  Platform,
  PostStatus,
  GeneratedIdea,
  WritingTool,
  BrandVoiceConfig,
} from "@/types"

interface AppState {
  // Auth
  user: User | null
  setUser: (user: User | null) => void

  // Workspace
  currentWorkspace: Workspace | null
  workspaces: Workspace[]
  setCurrentWorkspace: (workspace: Workspace | null) => void
  setWorkspaces: (workspaces: Workspace[]) => void

  // Posts
  posts: Post[]
  setPosts: (posts: Post[]) => void
  addPost: (post: Post) => void
  updatePost: (id: string, updates: Partial<Post>) => void
  deletePost: (id: string) => void

  // Filters
  selectedPlatform: Platform | "all"
  selectedStatus: PostStatus | "all"
  setSelectedPlatform: (platform: Platform | "all") => void
  setSelectedStatus: (status: PostStatus | "all") => void

  // UI
  sidebarOpen: boolean
  toggleSidebar: () => void
  setSidebarOpen: (open: boolean) => void

  // Content Studio
  activeStudioTab: "ideas" | "generate" | "tools" | "brand-voice"
  setActiveStudioTab: (tab: "ideas" | "generate" | "tools" | "brand-voice") => void
  generatedIdeas: GeneratedIdea[]
  setGeneratedIdeas: (ideas: GeneratedIdea[]) => void
  selectedIdeaCategories: string[]
  setSelectedIdeaCategories: (cats: string[]) => void
  activeWritingTool: WritingTool
  setActiveWritingTool: (tool: WritingTool) => void
  brandVoice: BrandVoiceConfig | null
  setBrandVoice: (bv: BrandVoiceConfig | null) => void
  contentStudioLoading: boolean
  setContentStudioLoading: (loading: boolean) => void
}

export const useAppStore = create<AppState>((set) => ({
  // Auth
  user: null,
  setUser: (user) => set({ user }),

  // Workspace
  currentWorkspace: null,
  workspaces: [],
  setCurrentWorkspace: (workspace) => set({ currentWorkspace: workspace }),
  setWorkspaces: (workspaces) => set({ workspaces }),

  // Posts
  posts: [],
  setPosts: (posts) => set({ posts }),
  addPost: (post) => set((state) => ({ posts: [post, ...state.posts] })),
  updatePost: (id, updates) =>
    set((state) => ({
      posts: state.posts.map((p) => (p.id === id ? { ...p, ...updates } : p)),
    })),
  deletePost: (id) =>
    set((state) => ({
      posts: state.posts.filter((p) => p.id !== id),
    })),

  // Filters
  selectedPlatform: "all",
  selectedStatus: "all",
  setSelectedPlatform: (platform) => set({ selectedPlatform: platform }),
  setSelectedStatus: (status) => set({ selectedStatus: status }),

  // UI
  sidebarOpen: true,
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
  setSidebarOpen: (open) => set({ sidebarOpen: open }),

  // Content Studio
  activeStudioTab: "ideas",
  setActiveStudioTab: (tab) => set({ activeStudioTab: tab }),
  generatedIdeas: [],
  setGeneratedIdeas: (ideas) => set({ generatedIdeas: ideas }),
  selectedIdeaCategories: [],
  setSelectedIdeaCategories: (cats) => set({ selectedIdeaCategories: cats }),
  activeWritingTool: "rewrite",
  setActiveWritingTool: (tool) => set({ activeWritingTool: tool }),
  brandVoice: null,
  setBrandVoice: (bv) => set({ brandVoice: bv }),
  contentStudioLoading: false,
  setContentStudioLoading: (loading) => set({ contentStudioLoading: loading }),
}))
