/**
 * TypeScript Type Definitions
 *
 * These types match the backend Pydantic schemas and database models
 */

// Enums
export enum UserRole {
  MENTOR = 'mentor',
  SUPERVISOR = 'supervisor',
  ADMIN = 'admin',
}

export enum LogStatus {
  DRAFT = 'draft',
  SUBMITTED = 'submitted',
  APPROVED = 'approved',
  COMPLETED = 'completed',
}

export enum FollowUpStatus {
  PENDING = 'pending',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
}

// User Types
export interface User {
  id: string
  email: string
  name: string
  designation?: string
  region_state?: string
  role: UserRole
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

export interface UserCreate {
  email: string
  name: string
  designation?: string
  region_state?: string
  role: UserRole
  password: string
}

export interface UserUpdate {
  name?: string
  designation?: string
  region_state?: string
  role?: UserRole
  is_active?: boolean
}

// Facility Types
export interface Facility {
  id: string
  name: string
  code?: string
  location?: string
  state?: string
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
  facility_type?: string
  contact_person?: string
  contact_email?: string
  contact_phone?: string
}

// Visit Objective Types
export interface VisitObjective {
  id: string
  mentorship_log_id: string
  objective_text: string
  sequence?: number
  created_at: string
}

export interface VisitObjectiveCreate {
  objective_text: string
  sequence?: number
}

// Follow-Up Types
export interface FollowUp {
  id: string
  mentorship_log_id: string
  action_item: string
  status: FollowUpStatus
  assigned_to?: string
  due_date?: string
  notes?: string
  created_at: string
  updated_at: string
  completed_at?: string
}

export interface FollowUpCreate {
  action_item: string
  assigned_to?: string
  due_date?: string
  notes?: string
}

export interface FollowUpUpdate {
  action_item?: string
  status?: FollowUpStatus
  assigned_to?: string
  due_date?: string
  notes?: string
}

// Attachment Types
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

// Mentorship Log Types
export interface MentorshipLog {
  id: string
  facility_id: string
  mentor_id: string
  visit_date: string
  status: LogStatus

  // Planning section
  performance_summary?: string
  identified_gaps?: string
  trends_summary?: string
  previous_followup?: string
  persistent_challenges?: string
  progress_made?: string
  resources_needed?: string
  facility_requests?: string
  logistics_notes?: string

  // Reporting section
  visit_outcomes?: string
  lessons_learned?: string

  // Metadata
  created_at: string
  updated_at: string
  submitted_at?: string
  approved_at?: string
  approved_by?: string

  // Nested relationships
  objectives: VisitObjective[]
  follow_ups: FollowUp[]
  attachments: Attachment[]
}

export interface MentorshipLogCreate {
  facility_id: string
  visit_date: string
  performance_summary?: string
  identified_gaps?: string
  trends_summary?: string
  previous_followup?: string
  persistent_challenges?: string
  progress_made?: string
  resources_needed?: string
  facility_requests?: string
  logistics_notes?: string
  visit_outcomes?: string
  lessons_learned?: string
  objectives?: string[]
}

export interface MentorshipLogUpdate {
  facility_id?: string
  visit_date?: string
  performance_summary?: string
  identified_gaps?: string
  trends_summary?: string
  previous_followup?: string
  persistent_challenges?: string
  progress_made?: string
  resources_needed?: string
  facility_requests?: string
  logistics_notes?: string
  visit_outcomes?: string
  lessons_learned?: string
  objectives?: string[]
}

// User-Facility Assignment Types
export interface UserFacilityAssignment {
  id: string
  user_id: string
  facility_id: string
  assigned_at: string
}

// API Response Types
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}

export interface ApiError {
  detail: string
  status_code: number
}

// Dashboard Types
export interface DashboardMetrics {
  total_logs: number
  planned_visits: number
  completed_visits: number
  pending_approvals: number
  overdue_followups: number
}

export interface FacilityPerformance {
  facility_id: string
  facility_name: string
  visits_count: number
  completed_followups: number
  pending_followups: number
  last_visit_date?: string
}
