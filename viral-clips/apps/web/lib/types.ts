export type Plan = "free" | "pro" | "business";

export interface User {
  id: string;
  email: string;
  display_name: string | null;
  plan: Plan;
  is_admin?: boolean;
  created_at: string;
}

export interface Project {
  id: string;
  title: string;
  source_type: "upload" | "url";
  source_url: string | null;
  status: "uploading" | "uploaded" | "queued" | "analyzing" | "analyzed" | "rendering" | "ready" | "failed";
  stage: string;
  progress: number;
  duration_s: number | null;
  width: number | null;
  height: number | null;
  fps: number | null;
  language: string | null;
  error: string | null;
  poster_url: string | null;
  source_url_playable: string | null;
  clip_count: number;
  created_at: string;
  updated_at: string;
}

export interface ScoreBreakdown {
  hook_strength: number;
  curiosity: number;
  emotional_impact: number;
  story_completeness: number;
  shareability: number;
  engagement: number;
  information_value: number;
  context_independence: number;
  visual_engagement: number;
}

export interface SubtitleCue {
  start: number;
  end: number;
  text: string;
}

export interface SubtitleData {
  cues?: SubtitleCue[];
  words?: { w: string; s: number; e: number }[];
  keywords?: string[];
  edited?: boolean;
  strategy?: string;
  crop_confidence?: number;
}

export interface Clip {
  id: string;
  project_id: string;
  start_s: number;
  end_s: number;
  duration_s: number;
  title: string;
  hook: string | null;
  text: string;
  score: number;
  score_breakdown: ScoreBreakdown | null;
  explanation: string | null;
  tags: string[] | null;
  status: "suggested" | "rendering" | "ready" | "failed";
  preset: string;
  crop_x: number | null;
  fit_mode: "crop" | "blur";
  subtitle_json: SubtitleData | null;
  video_url: string | null;
  thumb_url: string | null;
  render_error: string | null;
  created_at: string;
}

export interface Job {
  id: string;
  project_id: string | null;
  type: "analyze" | "render" | "export";
  status: "queued" | "running" | "done" | "failed";
  stage: string;
  progress: number;
  error: string | null;
  result: { summary?: string } | null;
  created_at: string;
  started_at: string | null;
  finished_at: string | null;
}

export interface Usage {
  plan: {
    name: Plan;
    label: string;
    minutes_per_month: number;
    max_clips_per_video: number;
    max_projects: number;
    max_upload_mb: number;
    max_video_minutes: number;
    features: string[];
  };
  minutes_used: number;
  minutes_remaining: number;
  projects: number;
  clips: number;
  clips_rendered: number;
  ai_cost_usd: number;
  ai_calls: number;
}

export interface ProviderStatus {
  llm_provider: string;
  llm_configured: boolean;
  llm_model_fast: string;
  llm_model_deep: string;
  asr_provider: string;
  asr_configured: boolean;
  asr_model: string;
  storage_backend: string;
  queue_backend: string;
  vision_enabled: boolean;
  ffmpeg_version: string;
  ffmpeg_path: string;
  youtube_ingest: boolean;
  supabase_auth: boolean;
  warnings: string[];
}

export interface Preset {
  id: string;
  label: string;
  tier: Plan;
  font: string;
  size: number;
  primary: string;
  highlight: string;
  karaoke: boolean;
  max_words: number;
}

export interface Transcript {
  project_id: string;
  language: string | null;
  provider: string;
  model: string | null;
  full_text: string;
  segments: { start: number; end: number; text: string }[];
  words: { w: string; s: number; e: number }[];
}
