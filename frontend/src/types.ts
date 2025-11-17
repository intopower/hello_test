export type TaskStatus =
  | 'pending'
  | 'analyzing'
  | 'scripting'
  | 'editing'
  | 'rendering'
  | 'completed'
  | 'failed'

export interface ScriptSegment {
  order: number
  text: string
  start: number
  end: number
  emotion?: string | null
  keywords: string[]
}

export interface VideoAsset {
  url: string
  duration?: number | null
  resolution?: string | null
}

export interface TimelineEvent {
  label: string
  start: number
  end: number
  category: string
}

export interface NarrationAsset {
  url: string
  locale: string
  voice_profile: string
  duration: number
}

export interface VideoTask {
  id: string
  status: TaskStatus
  created_at: string
  updated_at: string
  script: ScriptSegment[]
  source_asset?: VideoAsset | null
  output_asset?: VideoAsset | null
  progress: number
  failure_reason?: string | null
  options: CreateTaskMetadata
  timeline: TimelineEvent[]
  narration_assets: NarrationAsset[]
  bgm_theme?: string | null
}

export interface CreateTaskMetadata {
  title: string
  description: string
  language: string
  voice_profile: string
  target_duration: number
}
