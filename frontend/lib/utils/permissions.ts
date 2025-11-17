import { User, UserRole } from '@/types'

/**
 * Utility functions for checking user permissions
 * These are pure functions that don't rely on React hooks
 * Use these in non-component contexts or when you have a user object directly
 */

/**
 * Check if user has any of the specified roles
 */
export const hasRole = (user: User | null, roles: UserRole | UserRole[]): boolean => {
  if (!user) return false
  const roleArray = Array.isArray(roles) ? roles : [roles]
  return roleArray.includes(user.role)
}

/**
 * Check if user is an admin
 */
export const isAdmin = (user: User | null): boolean => {
  return user?.role === UserRole.ADMIN
}

/**
 * Check if user is a supervisor
 */
export const isSupervisor = (user: User | null): boolean => {
  return user?.role === UserRole.SUPERVISOR
}

/**
 * Check if user is a mentor
 */
export const isMentor = (user: User | null): boolean => {
  return user?.role === UserRole.MENTOR
}

/**
 * Check if user is supervisor or admin
 */
export const isSupervisorOrAdmin = (user: User | null): boolean => {
  return hasRole(user, [UserRole.SUPERVISOR, UserRole.ADMIN])
}

/**
 * Check if user can manage other users (view, create, update)
 */
export const canManageUsers = (user: User | null): boolean => {
  return isSupervisorOrAdmin(user)
}

/**
 * Check if user can create new users
 */
export const canCreateUsers = (user: User | null): boolean => {
  return isAdmin(user)
}

/**
 * Check if user can approve mentorship logs
 */
export const canApproveLogs = (user: User | null): boolean => {
  return isSupervisorOrAdmin(user)
}

/**
 * Check if user can reject mentorship logs
 */
export const canRejectLogs = (user: User | null): boolean => {
  return isSupervisorOrAdmin(user)
}

/**
 * Check if user can manage facilities (create, update, delete)
 */
export const canManageFacilities = (user: User | null): boolean => {
  return isAdmin(user)
}

/**
 * Check if user can access reports
 */
export const canAccessReports = (user: User | null): boolean => {
  return isSupervisorOrAdmin(user)
}

/**
 * Check if user can edit content owned by another user
 */
export const canEditContent = (user: User | null, ownerId: string): boolean => {
  if (!user) return false
  // Admins and supervisors can edit any content
  if (isSupervisorOrAdmin(user)) return true
  // Users can edit their own content
  return user.id === ownerId
}

/**
 * Check if user can delete content owned by another user
 */
export const canDeleteContent = (user: User | null, ownerId: string): boolean => {
  if (!user) return false
  // Only admins can delete any content
  if (isAdmin(user)) return true
  // Users can delete their own content
  return user.id === ownerId
}

/**
 * Check if user can view all mentorship logs (or just their own)
 */
export const canViewAllLogs = (user: User | null): boolean => {
  return isSupervisorOrAdmin(user)
}

/**
 * Check if user can change user roles
 */
export const canChangeUserRoles = (user: User | null): boolean => {
  return isAdmin(user)
}

/**
 * Check if user can update another user's profile
 */
export const canUpdateUserProfile = (
  currentUser: User | null,
  targetUserId: string,
  targetUserRole: UserRole
): boolean => {
  if (!currentUser) return false

  // Admins can update anyone
  if (isAdmin(currentUser)) return true

  // Supervisors can update mentors only
  if (isSupervisor(currentUser) && targetUserRole === UserRole.MENTOR) {
    return true
  }

  // Users can update their own profile
  return currentUser.id === targetUserId
}
