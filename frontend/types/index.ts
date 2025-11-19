/**
 * TypeScript Type Definitions
 *
 * These types match the backend API Pydantic schemas
 */

// ============================================================================
// Enums
// ============================================================================

export enum UserRole {
  MENTOR = 'mentor',
  SUPERVISOR = 'supervisor',
  ADMIN = 'admin',
}

export enum LogStatus {
  DRAFT = 'draft',
  SUBMITTED = 'submitted',
  APPROVED = 'approved',
  COMPLETED = 'completed'
}

export enum FollowUpStatus {
  PENDING = 'pending',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
}

// ============================================================================
// Auth Types
// ============================================================================

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  password: string
  name: string
  designation?: string
  region_state?: string
  role: UserRole
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

// ============================================================================
// User Types
// ============================================================================

export interface UserSpecialization {
  id: string
  user_id: string
  thematic_area: string
  created_at: string
}

export interface User {
  id: string
  email: string
  name: string
  designation?: string
  region_state?: string
  role: UserRole
  supervisor_id?: string
  is_active: boolean
  created_at: string
  updated_at: string
  specializations: UserSpecialization[]
}

export interface UserCreate {
  email: string
  password: string
  name: string
  designation?: string
  region_state?: string
  role: UserRole
  supervisor_id?: string
  specializations?: string[]
}

export interface UserUpdate {
  name?: string
  designation?: string
  region_state?: string
  role?: UserRole
  is_active?: boolean
  supervisor_id?: string
  specializations?: string[]
}

// ============================================================================
// Facility Types
// ============================================================================

export interface Facility {
  id: string
  name: string
  code?: string
  location?: string
  state?: string
  lga?: string
  facility_type?: string
  contact_person?: string
  contact_email?: string
  contact_phone?: string
  created_at: string
  updated_at: string
}

export interface FacilityCreate {
  name: string
  code?: string
  location?: string
  state?: string
  lga?: string
  facility_type?: string
  contact_person?: string
  contact_email?: string
  contact_phone?: string
}

export interface FacilityUpdate {
  name?: string
  code?: string
  location?: string
  state?: string
  lga?: string
  facility_type?: string
  contact_person?: string
  contact_email?: string
  contact_phone?: string
}

// ============================================================================
// Mentorship Log Types
// ============================================================================

export interface MenteesPresent {
  name: string
  cadre?: string
}

export interface SkillsTransfer {
  skill_knowledge_transferred: string
  recipient_name: string
  recipient_cadre?: string
  method?: string
  competency_level?: string
  followup_needed?: boolean
}

export interface FollowUpNested {
  action_item: string
  responsible_person?: string
  assigned_to?: string
  target_date?: string
  resources_needed?: string
  priority?: string
  notes?: string
}

export interface LogComment {
  id: string
  mentorship_log_id: string
  user_id: string
  user_name: string
  user_role: UserRole
  comment_text: string
  is_specialist_comment: boolean
  created_at: string
  updated_at: string
}

export interface MentorshipLog {
  id: string
  facility_id: string
  mentor_id: string
  visit_date: string
  interaction_type?: string
  duration_hours?: number
  duration_minutes?: number
  status: LogStatus

  // Visit Details
  mentees_present?: MenteesPresent[]
  activities_conducted?: string[]
  activities_other_specify?: string
  thematic_areas?: string[]
  thematic_areas_other_specify?: string

  // Assessment
  strengths_observed?: string
  gaps_identified?: string
  root_causes?: string
  challenges_encountered?: string
  solutions_proposed?: string
  support_needed?: string
  success_stories?: string

  // Attachments
  attachment_types?: string[]

  // Nested data
  skills_transfers: SkillsTransfer[]
  follow_ups: FollowUpNested[]
  attachments: Attachment[]
  comments: LogComment[]

  // Relationships (loaded from backend)
  facility?: Facility
  mentor?: User
  approver?: User

  // Metadata
  created_at: string
  updated_at: string
  submitted_at?: string
  approved_at?: string
  approved_by?: string
  rejected_at?: string
  rejection_reason?: string
}

export interface MentorshipLogCreate {
  facility_id: string
  visit_date: string
  interaction_type?: string
  duration_hours?: number
  duration_minutes?: number

  mentees_present?: MenteesPresent[]
  activities_conducted?: string[]
  activities_other_specify?: string
  thematic_areas?: string[]
  thematic_areas_other_specify?: string

  strengths_observed?: string
  gaps_identified?: string
  root_causes?: string
  challenges_encountered?: string
  solutions_proposed?: string
  support_needed?: string
  success_stories?: string

  attachment_types?: string[]

  skills_transfers?: SkillsTransfer[]
  follow_ups?: FollowUpNested[]
}

export interface MentorshipLogUpdate extends MentorshipLogCreate {}

// ============================================================================
// Follow-Up Types (Standalone)
// ============================================================================

export interface FollowUp {
  id: string
  mentorship_log_id: string
  action_item: string
  responsible_person?: string
  assigned_to?: string
  target_date?: string
  resources_needed?: string
  priority?: string
  notes?: string
  status: FollowUpStatus
  completed_at?: string
  created_at: string
  updated_at: string
}

export interface FollowUpCreate {
  mentorship_log_id: string
  action_item: string
  responsible_person?: string
  assigned_to?: string
  target_date?: string
  resources_needed?: string
  priority?: string
  notes?: string
}

export interface FollowUpUpdate {
  action_item?: string
  status?: FollowUpStatus
  responsible_person?: string
  assigned_to?: string
  target_date?: string
  resources_needed?: string
  priority?: string
  notes?: string
}

// ============================================================================
// Attachment Types
// ============================================================================

export interface Attachment {
  id: string
  mentorship_log_id: string
  file_name: string
  file_path: string
  file_size?: number
  file_type?: string
  uploaded_by?: string
  created_at: string
}

// ============================================================================
// Report Types
// ============================================================================

export interface SummaryReport {
  total_logs: number
  logs_by_status: Record<string, number>
  total_facilities: number
  total_mentors: number
  total_follow_ups: number
  follow_ups_by_status: Record<string, number>
}

export interface MentorLogCount {
  mentor_id: string
  mentor_name: string
  count: number
}

export interface FacilityLogCount {
  facility_id: string
  facility_name: string
  count: number
}

export interface StateLogCount {
  state: string
  count: number
}

export interface MentorshipLogsReport {
  total_count: number
  logs_by_mentor: MentorLogCount[]
  logs_by_facility: FacilityLogCount[]
  logs_by_state: StateLogCount[]
}

export interface FollowUpsReport {
  total_count: number
  pending_count: number
  overdue_count: number
  by_status: Record<string, number>
}

export interface FacilityCoverageItem {
  facility_id: string
  facility_name: string
  facility_code?: string
  state?: string
  lga?: string
  visit_count: number
  last_visit_date?: string
}

export interface FacilityCoverageReport {
  total_facilities: number
  visited_facilities: number
  unvisited_facilities: number
  facilities: FacilityCoverageItem[]
}

// ============================================================================
// API Response Types
// ============================================================================

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  skip: number
  limit: number
}

export interface ApiError {
  detail: string
}

export interface ValidationError {
  loc: (string | number)[]
  msg: string
  type: string
}

export interface ApiValidationError {
  detail: ValidationError[]
}

// ============================================================================
// Notification Types
// ============================================================================

export enum NotificationType {
  COMMENT = 'comment',
  APPROVAL = 'approval',
  REJECTION = 'rejection',
  SPECIALIST_LOG = 'specialist_log',
}

// Unified notification interface (replaces SpecialistNotification)
export interface Notification {
  id: string
  user_id: string
  notification_type: NotificationType | string
  title: string
  message: string
  related_log_id?: string
  related_comment_id?: string
  extra_data?: {
    [key: string]: any
  }
  is_read: boolean
  created_at: string
  read_at?: string
}

// Legacy specialist notification (kept for backward compatibility)
export interface SpecialistNotification {
  id: string
  mentorship_log_id: string
  specialist_id: string
  thematic_area: string
  is_read: boolean
  notified_at: string
  read_at?: string
  log_facility_name?: string
  log_mentor_name?: string
  log_visit_date?: string
}

export interface MarkNotificationReadRequest {
  notification_ids: string[]
}

// ============================================================================
// Comment Types
// ============================================================================

export interface LogCommentCreate {
  comment_text: string
  is_specialist_comment?: boolean
}

export interface LogCommentUpdate {
  comment_text: string
}
