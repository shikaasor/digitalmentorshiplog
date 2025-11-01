# COMPREHENSIVE ROLE MANAGEMENT AND ACCESS CONTROL INVESTIGATION REPORT

**Date**: 2025-10-31
**Application**: Mentors Digital Log
**Security Assessment**: Backend Excellent, Frontend Critical Gaps

---

## Executive Summary

This mentorship logs application implements a **three-tier role-based access control (RBAC) system** with roles: **mentor**, **supervisor**, and **admin**. The system uses JWT-based authentication with role-based permissions enforced on both backend and frontend. While the implementation is solid in the backend, there are **gaps in frontend role enforcement** and some missing centralized utilities.

---

## 1. ROLE DEFINITIONS

### Backend Role Definition
**File**: `/backend/app/models.py` (Lines 12-15)

```python
class UserRole(str, enum.Enum):
    mentor = "mentor"
    supervisor = "supervisor"
    admin = "admin"
```

**File**: `/backend/app/schemas.py` (Lines 12-15)

```python
class UserRole(str, Enum):
    mentor = "mentor"
    supervisor = "supervisor"
    admin = "admin"
```

### Frontend Role Definition
**File**: `/frontend/types/index.ts` (Lines 11-15)

```typescript
export enum UserRole {
  MENTOR = 'mentor',
  SUPERVISOR = 'supervisor',
  ADMIN = 'admin',
}
```

**Note**: Frontend uses UPPERCASE enum keys while backend uses lowercase, but values are consistent.

---

## 2. AUTHENTICATION & ROLE ASSIGNMENT

### Login Flow
**File**: `/backend/app/routers/auth.py` (Lines 87-150)

1. User provides email/password (Lines 122-131)
2. Password is verified using bcrypt (Line 126)
3. User's `is_active` status is checked (Lines 133-138)
4. JWT token is created with user ID in "sub" claim (Lines 141-145)
5. **Role is NOT stored in JWT** - it's fetched from database on each request

### User Model
**File**: `/backend/app/models.py` (Lines 32-51)

```python
class User(Base):
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.mentor)  # Line 41
    is_active = Column(Boolean, default=True)
```

**Default Role**: `mentor` (Line 41)

### Frontend Authentication Store
**File**: `/frontend/lib/stores/auth.store.ts`

- JWT token stored in `localStorage` (Line 41)
- User object (including role) stored in `localStorage` (Line 47)
- User loaded from localStorage on app init (Lines 100-122)

---

## 3. BACKEND ACCESS CONTROL MECHANISMS

### A. Core Dependency Functions
**File**: `/backend/app/dependencies.py`

#### 3.1 `get_current_user` (Lines 23-85)
- Extracts JWT from Authorization header
- Verifies token validity
- Fetches user from database
- **Checks `is_active` status** (Lines 78-83)
- Returns authenticated User object

#### 3.2 `require_role(*allowed_roles)` (Lines 149-183)
**Role-based access control decorator factory**

```python
def require_role(*allowed_roles: UserRole):
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {[role.value for role in allowed_roles]}"
            )
        return current_user
    return role_checker
```

#### 3.3 Pre-configured Role Dependencies (Lines 187-189)
```python
require_admin = require_role(UserRole.admin)
require_supervisor_or_admin = require_role(UserRole.supervisor, UserRole.admin)
require_any_role = require_role(UserRole.mentor, UserRole.supervisor, UserRole.admin)
```

### B. Security Utilities
**File**: `/backend/app/utils/security.py`

- `hash_password()` - bcrypt hashing (Lines 15-46)
- `verify_password()` - bcrypt verification (Lines 49-76)
- `create_access_token()` - JWT creation (Lines 79-112)
- `verify_token()` - JWT validation (Lines 142-163)

---

## 4. ENDPOINT-LEVEL ROLE ENFORCEMENT

### A. Users Router
**File**: `/backend/app/routers/users.py`

| Endpoint | Method | Role Required | Line |
|----------|--------|---------------|------|
| List users | GET `/api/users` | supervisor OR admin | 74 |
| Get user | GET `/api/users/{id}` | authenticated (with ownership check) | 129 |
| Create user | POST `/api/users` | **admin only** | 160 |
| Update user | PUT `/api/users/{id}` | Complex permission logic | 195 |
| Deactivate user | PUT `/api/users/{id}/deactivate` | **admin only** | 231 |
| Activate user | PUT `/api/users/{id}/activate` | **admin only** | 258 |
| Delete user | DELETE `/api/users/{id}` | **admin only** | 285 |

**Complex Update Logic** (Lines 24-64):
```python
def check_user_update_permissions(current_user, target_user, update_data):
    # Admins: can update anyone and change roles
    if current_user.role == UserRole.admin:
        return

    # Supervisors: can update mentors but NOT change roles
    if current_user.role == UserRole.supervisor:
        if "role" in update_data:
            raise HTTPException(403, "Supervisors cannot change user roles")
        if target_user.role not in [UserRole.mentor]:
            raise HTTPException(403, "Supervisors can only update mentor profiles")
        return

    # Mentors: can only update themselves, cannot change roles
    if current_user.role == UserRole.mentor:
        if current_user.id != target_user.id:
            raise HTTPException(403, "Mentors can only update their own profile")
        if "role" in update_data:
            raise HTTPException(403, "You cannot change your own role")
```

### B. Mentorship Logs Router
**File**: `/backend/app/routers/mentorship_logs.py`

| Endpoint | Method | Role Logic | Lines |
|----------|--------|------------|-------|
| List logs | GET `/api/mentorship-logs` | Mentors see own logs; supervisors/admins see all | 56-60 |
| Get log | GET `/api/mentorship-logs/{id}` | Mentors see own logs; supervisors/admins see all | 114-118 |
| Create log | POST `/api/mentorship-logs` | All authenticated users | 127 |
| Update log | PUT `/api/mentorship-logs/{id}` | Own logs (draft only) for mentors | 203-207 |
| Submit log | POST `/api/mentorship-logs/{id}/submit` | Own logs for mentors | 282-286 |
| Approve log | POST `/api/mentorship-logs/{id}/approve` | **supervisor OR admin** | 309 |
| Return to draft | POST `/api/mentorship-logs/{id}/return-to-draft` | **supervisor OR admin** | 350 |
| Reject log | POST `/api/mentorship-logs/{id}/reject` | **supervisor OR admin** | 391 |
| Delete log | DELETE `/api/mentorship-logs/{id}` | Mentors (draft only), admins (any) | 458-468 |

### C. Facilities Router
**File**: `/backend/app/routers/facilities.py`

| Endpoint | Method | Role Required | Line |
|----------|--------|---------------|------|
| List facilities | GET `/api/facilities` | authenticated | 32 |
| Get facility | GET `/api/facilities/{id}` | authenticated | 89 |
| Create facility | POST `/api/facilities` | **admin only** | 111 |
| Update facility | PUT `/api/facilities/{id}` | **admin only** | 140 |
| Delete facility | DELETE `/api/facilities/{id}` | **admin only** | 179 |

### D. Follow-Ups Router
**File**: `/backend/app/routers/follow_ups.py`

**Custom Permission Functions** (Lines 23-76):
- `check_follow_up_permissions()` - Admins/supervisors OR mentor of parent log
- `check_follow_up_update_permissions()` - Above + assigned user can update

| Endpoint | Method | Permission Logic | Lines |
|----------|--------|------------------|-------|
| List follow-ups | GET `/api/follow-ups` | authenticated | 87 |
| Create follow-up | POST `/api/follow-ups` | Complex (own logs or admin/supervisor) | 174 |
| Update follow-up | PUT `/api/follow-ups/{id}` | Complex (own log, assigned user, or admin/supervisor) | 211 |
| Mark in progress | PUT `/api/follow-ups/{id}/in-progress` | Same as update | 247 |
| Mark complete | PUT `/api/follow-ups/{id}/complete` | Same as update | 281 |
| Delete follow-up | DELETE `/api/follow-ups/{id}` | Own log or admin/supervisor | 315 |

### E. Attachments Router
**File**: `/backend/app/routers/attachments.py`

**Permission Function** (Lines 41-63):
```python
def check_file_permissions(current_user, mentorship_log):
    # Admins/supervisors can manage all attachments
    if current_user.role in [UserRole.admin, UserRole.supervisor]:
        return
    # Mentors can only manage attachments for their own logs
    if current_user.role == UserRole.mentor:
        if mentorship_log.mentor_id != current_user.id:
            raise HTTPException(403, "You can only manage attachments for your own logs")
```

### F. Reports Router
**File**: `/backend/app/routers/reports.py`

| Endpoint | Method | Role Required | Line |
|----------|--------|---------------|------|
| Summary report | GET `/api/reports/summary` | **supervisor OR admin** | 26 |
| Logs report | GET `/api/reports/mentorship-logs` | **supervisor OR admin** | 86 |
| Follow-ups report | GET `/api/reports/follow-ups` | **supervisor OR admin** | 192 |
| Facility coverage | GET `/api/reports/facility-coverage` | **supervisor OR admin** | 259 |

---

## 5. FRONTEND ACCESS CONTROL

### A. ProtectedRoute Component
**File**: `/frontend/components/auth/ProtectedRoute.tsx`

**CRITICAL ISSUE**: The component accepts `allowedRoles` prop but **DOES NOT IMPLEMENT role checking**!

```typescript
interface ProtectedRouteProps {
  children: React.ReactNode
  // allowedRoles is used in code but NOT defined in interface!
}
```

**Current Implementation**:
- Only checks if user is authenticated (Lines 22-26)
- Redirects to `/auth/login` if no token
- **Does NOT validate roles**

**Usage Examples**:
- `/app/users/page.tsx` Line 103: `<ProtectedRoute allowedRoles={['admin', 'supervisor']}>`
- `/app/users/new/page.tsx` Line 42: `<ProtectedRoute allowedRoles={['admin']}>`

**SECURITY GAP**: These `allowedRoles` props have no effect!

### B. DashboardLayout Navigation
**File**: `/frontend/components/layouts/DashboardLayout.tsx`

**Properly Implements Role-Based Navigation** (Lines 25-82):

```typescript
const navigation: NavItem[] = [
  { name: 'Dashboard', href: '/dashboard' },  // All users
  { name: 'Mentorship Logs', href: '/mentorship-logs' },  // All users
  { name: 'Facilities', href: '/facilities' },  // All users
  { name: 'Follow-Ups', href: '/follow-ups' },  // All users
  {
    name: 'Reports',
    href: '/reports',
    roles: [UserRole.ADMIN, UserRole.SUPERVISOR]  // Restricted
  },
  {
    name: 'Users',
    href: '/users',
    roles: [UserRole.ADMIN, UserRole.SUPERVISOR]  // Restricted
  },
]

// Filter based on user role (Lines 85-87)
const filteredNavigation = navigation.filter(
  (item) => !item.roles || (user && item.roles.includes(user.role))
)
```

**This correctly hides nav items**, but does NOT prevent direct URL access!

### C. Inline Role Checks
**File**: `/frontend/app/mentorship-logs/[id]/page.tsx` (Lines 96-101)

```typescript
const canApprove =
  log &&
  log.status === 'submitted' &&
  user &&
  (user.role === 'admin' || user.role === 'supervisor')
```

**This is an example of ad-hoc role checking for UI rendering.**

---

## 6. ROLE HIERARCHY & PERMISSIONS MATRIX

### Role Hierarchy
```
Admin (highest privilege)
  └─ Can do everything supervisors can do
  └─ Can manage users (create, update roles, delete)
  └─ Can manage facilities (create, update, delete)

Supervisor
  └─ Can do everything mentors can do
  └─ Can view all logs and approve/reject them
  └─ Can view and update mentor profiles (but not change roles)
  └─ Can access reports

Mentor (base privilege)
  └─ Can create and manage own logs
  └─ Can view facilities
  └─ Can manage follow-ups for own logs
  └─ Can update own profile (but not role)
```

### Complete Permissions Matrix

| Feature | Mentor | Supervisor | Admin |
|---------|--------|------------|-------|
| **USERS** |
| View users list | ❌ | ✅ | ✅ |
| View own profile | ✅ | ✅ | ✅ |
| View other profiles | ❌ | ✅ (mentors only) | ✅ |
| Create users | ❌ | ❌ | ✅ |
| Update own profile | ✅ (not role) | ✅ (not role) | ✅ |
| Update mentor profiles | ❌ | ✅ (not role) | ✅ |
| Change user roles | ❌ | ❌ | ✅ |
| Activate/Deactivate users | ❌ | ❌ | ✅ |
| Delete users | ❌ | ❌ | ✅ |
| **MENTORSHIP LOGS** |
| View own logs | ✅ | ✅ | ✅ |
| View all logs | ❌ | ✅ | ✅ |
| Create logs | ✅ | ✅ | ✅ |
| Update own draft logs | ✅ | ✅ | ✅ |
| Update any draft logs | ❌ | ✅ | ✅ |
| Submit logs | ✅ (own) | ✅ (any) | ✅ (any) |
| Approve logs | ❌ | ✅ | ✅ |
| Reject logs | ❌ | ✅ | ✅ |
| Return to draft | ❌ | ✅ | ✅ |
| Delete own draft logs | ✅ | ✅ | ✅ |
| Delete any logs | ❌ | ❌ | ✅ |
| **FACILITIES** |
| View facilities | ✅ | ✅ | ✅ |
| Create facilities | ❌ | ❌ | ✅ |
| Update facilities | ❌ | ❌ | ✅ |
| Delete facilities | ❌ | ❌ | ✅ |
| **FOLLOW-UPS** |
| View follow-ups | ✅ | ✅ | ✅ |
| Create follow-ups | ✅ (own logs) | ✅ | ✅ |
| Update own log follow-ups | ✅ | ✅ | ✅ |
| Update assigned follow-ups | ✅ | ✅ | ✅ |
| Update any follow-ups | ❌ | ✅ | ✅ |
| Delete follow-ups | ✅ (own logs) | ✅ | ✅ |
| **ATTACHMENTS** |
| View attachments | ✅ | ✅ | ✅ |
| Upload to own logs | ✅ | ✅ | ✅ |
| Upload to any logs | ❌ | ✅ | ✅ |
| Delete from own logs | ✅ | ✅ | ✅ |
| Delete from any logs | ❌ | ✅ | ✅ |
| **REPORTS** |
| Access reports | ❌ | ✅ | ✅ |

---

## 7. SECURITY ANALYSIS

### ✅ Strengths

1. **Backend is Well-Protected**:
   - All sensitive endpoints use `require_role()` or custom permission functions
   - JWT-based authentication with bcrypt password hashing
   - Token verification on every request
   - Active user status checks

2. **Granular Permissions**:
   - Complex ownership-based checks (e.g., mentors can only edit own logs)
   - Status-based restrictions (e.g., only draft logs can be edited)
   - Assignment-based permissions (e.g., assigned users can update follow-ups)

3. **Separation of Concerns**:
   - Role definitions centralized in enums
   - Reusable dependency injection for role checks
   - Custom permission functions for complex logic

4. **Database-Backed Roles**:
   - Roles stored in database, not JWT
   - Prevents stale role information in tokens
   - Easier to revoke/change permissions

### ❌ Security Gaps & Risks

#### CRITICAL ISSUES

1. **Frontend Route Protection Not Implemented**
   - **File**: `ProtectedRoute.tsx`
   - **Issue**: `allowedRoles` prop is ignored
   - **Risk**: Users can access restricted pages by typing URL directly
   - **Example**: A mentor can access `/users` by direct navigation
   - **Mitigation**: Backend still blocks API calls, but UI shows sensitive structure

2. **No Centralized Frontend Permission Utilities**
   - **Issue**: Role checks are ad-hoc and scattered throughout components
   - **Example**: Hardcoded checks like `user.role === 'admin' || user.role === 'supervisor'`
   - **Risk**: Inconsistent permission logic, harder to maintain

3. **User Data in localStorage**
   - **File**: `auth.store.ts` Line 47
   - **Issue**: Entire user object (including role) stored in localStorage
   - **Risk**: Client-side role manipulation possible (though backend validates)
   - **Impact**: User could modify localStorage to show admin UI, but API calls would fail

#### MEDIUM ISSUES

4. **No Token Refresh Mechanism**
   - Tokens expire but no refresh token implementation
   - Users forcibly logged out after expiration

5. **No Token Blacklisting**
   - **File**: `auth.py` Lines 218-219
   - Logout is client-side only
   - Compromised tokens remain valid until expiration

6. **Missing CORS Configuration Check**
   - Not visible in provided files
   - Should verify CORS is properly configured in production

#### LOW ISSUES

7. **Inconsistent Enum Naming**
   - Frontend: `UserRole.ADMIN` (uppercase)
   - Backend: `UserRole.admin` (lowercase)
   - Works due to value matching, but potentially confusing

8. **No Rate Limiting Visible**
   - Login endpoint could be vulnerable to brute force
   - Should implement rate limiting on auth endpoints

---

## 8. RECOMMENDATIONS

### 🔴 CRITICAL - Immediate Action Required

#### 1. Implement Frontend Role Checking in ProtectedRoute

**File**: `/frontend/components/auth/ProtectedRoute.tsx`

```typescript
'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuthStore } from '@/lib/stores/auth.store'
import { UserRole } from '@/types'

interface ProtectedRouteProps {
  children: React.ReactNode
  allowedRoles?: UserRole[]  // Add this to interface!
}

export default function ProtectedRoute({ children, allowedRoles }: ProtectedRouteProps) {
  const router = useRouter()
  const { user, loadUser } = useAuthStore()
  const [isAuthorized, setIsAuthorized] = useState(false)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    loadUser()
  }, [loadUser])

  useEffect(() => {
    const token = localStorage.getItem('access_token')

    if (!token) {
      router.push('/auth/login')
      return
    }

    if (!user) {
      setIsLoading(true)
      return
    }

    // ADD THIS ROLE CHECK
    if (allowedRoles && !allowedRoles.includes(user.role)) {
      console.warn(`Unauthorized: User role ${user.role} not in allowed roles`)
      router.push('/dashboard')  // Redirect unauthorized users
      return
    }

    setIsAuthorized(true)
    setIsLoading(false)
  }, [user, router, allowedRoles])

  if (isLoading) {
    return <div>Loading...</div>  // Show loading while checking
  }

  if (!isAuthorized) {
    return null
  }

  return <>{children}</>
}
```

#### 2. Create Centralized Permission Utilities

**New File**: `/frontend/lib/hooks/usePermissions.ts`

```typescript
import { useAuthStore } from '@/lib/stores/auth.store'
import { UserRole } from '@/types'

export const usePermissions = () => {
  const { user } = useAuthStore()

  return {
    user,
    isAdmin: user?.role === UserRole.ADMIN,
    isSupervisor: user?.role === UserRole.SUPERVISOR,
    isMentor: user?.role === UserRole.MENTOR,
    isSupervisorOrAdmin: user && [UserRole.SUPERVISOR, UserRole.ADMIN].includes(user.role),
    hasRole: (roles: UserRole[]) => user && roles.includes(user.role),
    canManageUsers: user && [UserRole.SUPERVISOR, UserRole.ADMIN].includes(user.role),
    canApproveLogs: user && [UserRole.SUPERVISOR, UserRole.ADMIN].includes(user.role),
    canManageFacilities: user?.role === UserRole.ADMIN,
    canAccessReports: user && [UserRole.SUPERVISOR, UserRole.ADMIN].includes(user.role),
  }
}
```

**Usage Example**:
```typescript
const { canApproveLogs, canManageUsers } = usePermissions()

{canApproveLogs && (
  <button onClick={handleApprove}>Approve</button>
)}
```

**New File**: `/frontend/lib/utils/permissions.ts`

```typescript
import { User, UserRole } from '@/types'

export const hasRole = (user: User | null, roles: UserRole[]): boolean => {
  return user !== null && roles.includes(user.role)
}

export const isAdmin = (user: User | null): boolean => {
  return user?.role === UserRole.ADMIN
}

export const isSupervisorOrAdmin = (user: User | null): boolean => {
  return hasRole(user, [UserRole.SUPERVISOR, UserRole.ADMIN])
}

export const canManageUsers = (user: User | null): boolean => {
  return isSupervisorOrAdmin(user)
}

export const canApproveLogs = (user: User | null): boolean => {
  return isSupervisorOrAdmin(user)
}

export const canManageFacilities = (user: User | null): boolean => {
  return isAdmin(user)
}

export const canAccessReports = (user: User | null): boolean => {
  return isSupervisorOrAdmin(user)
}
```

### 🟡 HIGH PRIORITY

#### 3. Implement Token Refresh

**Backend**: Add refresh token endpoint
**Frontend**: Auto-refresh before expiration
**Benefit**: Better UX, no forced logouts

#### 4. Add Token Blacklist

**Implementation**:
- Use Redis for fast lookups
- Store revoked tokens on logout
- Check blacklist in `verify_token()`

**New File**: `/backend/app/utils/token_blacklist.py`

```python
from datetime import datetime, timedelta
from typing import Optional
import redis

# Initialize Redis connection
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def blacklist_token(token: str, expires_in: int = 3600):
    """Add token to blacklist"""
    redis_client.setex(f"blacklist:{token}", expires_in, "1")

def is_token_blacklisted(token: str) -> bool:
    """Check if token is blacklisted"""
    return redis_client.exists(f"blacklist:{token}") > 0
```

**Update**: `/backend/app/utils/security.py`

```python
from app.utils.token_blacklist import is_token_blacklisted

def verify_token(token: str) -> Optional[str]:
    # Check blacklist first
    if is_token_blacklisted(token):
        return None

    payload = decode_token(token)
    if payload is None:
        return None

    user_id: str = payload.get("sub")
    return user_id
```

#### 5. Add Rate Limiting

**Install**: `pip install slowapi`

**Update**: `/backend/app/main.py`

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
```

**Update**: `/backend/app/routers/auth.py`

```python
@router.post("/login")
@limiter.limit("5/minute")  # 5 attempts per minute
def login(request: Request, ...):
    ...
```

### 🟢 MEDIUM PRIORITY

#### 6. Add Permission Audit Logging

- Log permission denials
- Track who accesses what
- Use existing `AuditLog` model

#### 7. Standardize Enum Naming

- Choose one convention (recommend lowercase for values)
- Update frontend to match backend

#### 8. Add Role-Based Testing

- Test each endpoint with different roles
- Verify permission denials
- Test edge cases (inactive users, etc.)

### 🔵 LOW PRIORITY

#### 9. Add Permission Constants

- Create constants file for permission strings
- Avoid magic strings in code

#### 10. Document Permission Matrix

- Add to API documentation
- Include in developer onboarding

---

## 9. SUMMARY

### Current State
- **Backend**: ✅ Excellent role-based access control
- **Frontend**: ⚠️ Missing proper role enforcement on routes
- **Overall Security**: 🟡 Good but with critical gaps

### Risk Level
- **Backend API**: 🟢 LOW RISK (well protected)
- **Frontend UI**: 🔴 MEDIUM RISK (can access unauthorized pages)
- **Data Exposure**: 🟡 LOW-MEDIUM (backend prevents data access, but UI structure visible)

### Action Items Priority
1. 🔴 Fix ProtectedRoute role checking
2. 🔴 Create permission utilities
3. 🟡 Implement token refresh
4. 🟡 Add token blacklisting
5. 🟡 Add rate limiting
6. 🟢 Add audit logging
7. 🟢 Improve testing coverage

### Overall Assessment

**Rating**: 7/10

**Strengths**:
- Excellent backend security architecture
- Comprehensive role-based permissions
- Proper JWT authentication
- Complex permission logic well implemented

**Weaknesses**:
- Frontend route protection incomplete
- No token refresh mechanism
- No token blacklisting
- Scattered permission checks in frontend

**Conclusion**:
The system has a solid security foundation with excellent backend protection. The critical priority is implementing proper frontend route protection to prevent unauthorized UI access, even though the backend would still block API calls. Once the frontend security gaps are addressed, this will be a robust and secure RBAC implementation.

---

**Last Updated**: 2025-10-31
**Next Review**: After implementing critical fixes
