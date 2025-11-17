import { useAuthStore } from '@/lib/stores/auth.store'
import { UserRole } from '@/types'

/**
 * Hook for checking user permissions and roles
 * Provides convenient helpers for role-based access control in components
 */
export const usePermissions = () => {
  const { user } = useAuthStore()

  return {
    // Current user
    user,

    // Role checks
    isAdmin: user?.role === UserRole.ADMIN,
    isSupervisor: user?.role === UserRole.SUPERVISOR,
    isMentor: user?.role === UserRole.MENTOR,
    isSupervisorOrAdmin: user ? [UserRole.SUPERVISOR, UserRole.ADMIN].includes(user.role) : false,

    // Generic role checker
    hasRole: (roles: UserRole | UserRole[]) => {
      if (!user) return false
      const roleArray = Array.isArray(roles) ? roles : [roles]
      return roleArray.includes(user.role)
    },

    // Feature-specific permissions
    canManageUsers: user ? [UserRole.SUPERVISOR, UserRole.ADMIN].includes(user.role) : false,
    canCreateUsers: user?.role === UserRole.ADMIN,
    canApproveLogs: user ? [UserRole.SUPERVISOR, UserRole.ADMIN].includes(user.role) : false,
    canRejectLogs: user ? [UserRole.SUPERVISOR, UserRole.ADMIN].includes(user.role) : false,
    canManageFacilities: user?.role === UserRole.ADMIN,
    canAccessReports: user ? [UserRole.SUPERVISOR, UserRole.ADMIN].includes(user.role) : false,

    // Ownership-based permission checker
    canEdit: (ownerId: string) => {
      if (!user) return false
      // Admins and supervisors can edit anything
      if ([UserRole.ADMIN, UserRole.SUPERVISOR].includes(user.role)) return true
      // Mentors can only edit their own content
      return user.id === ownerId
    },

    canDelete: (ownerId: string) => {
      if (!user) return false
      // Only admins can delete, or users can delete their own draft content
      if (user.role === UserRole.ADMIN) return true
      return user.id === ownerId
    },
  }
}
