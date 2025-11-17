# Frontend Implementation Roadmap
## Supervisor-Specialist System Integration

**Status:** Planning
**Backend Status:** ✅ Complete
**Frontend Status:** ❌ Not Started
**Target Completion:** TBD

---

## Overview

This roadmap outlines the frontend implementation needed to integrate the supervisor-mentor relationship and specialist system into the Digital Mentorship Log application.

## Implementation Phases

### **Phase 1: Foundation & User Management** (Highest Priority)
**Goal:** Enable admins to assign supervisors and specializations
**Estimated Effort:** 2-3 days
**Dependencies:** None

#### Tasks

1. **Update User Forms** ⭐ CRITICAL
   - [ ] **File:** `frontend/app/users/new/page.tsx`
   - [ ] Add supervisor selector dropdown
     - Fetch supervisors from `/api/users?role=supervisor`
     - Display as searchable dropdown
     - Only show for mentor role users
   - [ ] Add thematic area specializations multi-select
     - Use constants from backend (9 thematic areas)
     - Render as checkboxes or multi-select dropdown
     - Save as array in `specializations` field
   - [ ] Update form validation schema (Zod)
   - [ ] Test create user with supervisor and specializations

2. **Update User Edit Form**
   - [ ] **File:** `frontend/app/users/[id]/edit/page.tsx`
   - [ ] Add same fields as create form
   - [ ] Pre-populate existing supervisor and specializations
   - [ ] Test update user supervisor and specializations

3. **Update User Display/Profile**
   - [ ] **File:** `frontend/app/users/[id]/page.tsx`
   - [ ] Display assigned supervisor name (fetch and show)
   - [ ] Display specialization badges/tags
   - [ ] Show "My Mentees" section for supervisors
     - Fetch users where `supervisor_id == current_user.id`
     - Display as table/cards with links to profiles

4. **Update User List**
   - [ ] **File:** `frontend/app/users/page.tsx`
   - [ ] Add supervisor column (show supervisor name)
   - [ ] Add specializations column (show count or badges)
   - [ ] Add filter by supervisor
   - [ ] Add filter by specialization

**Deliverables:**
- Admins can assign supervisors to mentors
- Admins can assign specializations to users
- Users can view their supervisor and specializations
- Supervisors can see their mentees

**Testing:**
- Create mentor with supervisor assignment
- Create user with multiple specializations
- Update existing user's supervisor
- Verify display on profile page

---

### **Phase 2: Notifications System** (High Priority)
**Goal:** Enable specialists to receive and view notifications
**Estimated Effort:** 2-3 days
**Dependencies:** Phase 1 complete (users must have specializations)

#### Tasks

1. **Create Notification Service**
   - [ ] **File:** `frontend/lib/api/notifications.service.ts`
   - [ ] Implement API methods:
     ```typescript
     getNotifications(unreadOnly?: boolean)
     getUnreadCount()
     markAsRead(notificationIds: UUID[])
     markAllAsRead()
     deleteNotification(id: UUID)
     ```

2. **Create Notification Components**
   - [ ] **File:** `frontend/components/notifications/NotificationBell.tsx`
   - [ ] Bell icon component with unread badge
   - [ ] Dropdown panel on click
   - [ ] Show notifications list (last 10)
   - [ ] "Mark all as read" button
   - [ ] "View all" link to full page

3. **Create Notification Item Component**
   - [ ] **File:** `frontend/components/notifications/NotificationItem.tsx`
   - [ ] Display log details (facility, mentor, date, thematic area)
   - [ ] Click → navigate to log detail page
   - [ ] Mark as read on click
   - [ ] Delete button
   - [ ] Show timestamp (relative: "2 hours ago")

4. **Create Notifications Page**
   - [ ] **File:** `frontend/app/notifications/page.tsx`
   - [ ] Full list of notifications with pagination
   - [ ] Filter: All / Unread
   - [ ] Bulk actions (mark all as read, delete selected)
   - [ ] Empty state when no notifications

5. **Add to Navigation**
   - [ ] **File:** `frontend/components/layouts/DashboardLayout.tsx`
   - [ ] Add NotificationBell component to navbar
   - [ ] Position top-right, next to user menu
   - [ ] Poll for new notifications (every 30 seconds)

6. **Create Notification Store (Optional)**
   - [ ] **File:** `frontend/lib/stores/notification.store.ts`
   - [ ] Zustand store for notification state
   - [ ] Cache unread count
   - [ ] Update count when marked as read

**Deliverables:**
- Notification bell in navbar with unread count
- Dropdown showing recent notifications
- Full notifications page
- Click notification → go to log
- Mark as read functionality

**Testing:**
- Submit log with thematic areas
- Verify specialists receive notifications
- Click notification and navigate to log
- Mark notifications as read
- Delete notifications

---

### **Phase 3: Comments System** (Medium Priority)
**Goal:** Enable commenting on mentorship logs
**Estimated Effort:** 2-3 days
**Dependencies:** None

#### Tasks

1. **Create Comment Service**
   - [ ] **File:** `frontend/lib/api/comments.service.ts`
   - [ ] Implement API methods:
     ```typescript
     getComments(logId: UUID)
     createComment(logId: UUID, text: string)
     updateComment(commentId: UUID, text: string)
     deleteComment(commentId: UUID)
     ```

2. **Create Comment Components**
   - [ ] **File:** `frontend/components/logs/CommentList.tsx`
   - [ ] List all comments for a log
   - [ ] Show user name, role, timestamp
   - [ ] Highlight specialist comments (different background/badge)
   - [ ] Edit/delete buttons for own comments
   - [ ] Empty state when no comments

3. **Create Comment Form Component**
   - [ ] **File:** `frontend/components/logs/CommentForm.tsx`
   - [ ] Textarea for comment text
   - [ ] Submit button
   - [ ] Character count (optional)
   - [ ] Validation (min length)
   - [ ] Loading state during submission

4. **Create Comment Item Component**
   - [ ] **File:** `frontend/components/logs/CommentItem.tsx`
   - [ ] Display comment with user info
   - [ ] Show "Specialist Review" badge if `is_specialist_comment`
   - [ ] Edit mode (inline editing)
   - [ ] Delete confirmation dialog
   - [ ] Relative timestamp

5. **Integrate into Log Detail Page**
   - [ ] **File:** `frontend/app/mentorship-logs/[id]/page.tsx`
   - [ ] Add "Comments" section at bottom of log
   - [ ] Show CommentList component
   - [ ] Show CommentForm component (if user has access)
   - [ ] Auto-refresh comments after adding new one
   - [ ] Show comment count in section header

**Deliverables:**
- Comments section on log detail page
- Add, edit, delete comments
- Visual distinction for specialist comments
- Real-time updates after posting

**Testing:**
- Add comment as mentor (own log)
- Add comment as supervisor (mentee's log)
- Add comment as specialist (log in area)
- Verify specialist badge shows correctly
- Edit and delete own comments
- Verify non-owners cannot edit/delete

---

### **Phase 4: Enhanced Visibility & Filtering** (Medium Priority)
**Goal:** Update log listing to reflect new visibility rules
**Estimated Effort:** 1-2 days
**Dependencies:** Phase 1 complete

#### Tasks

1. **Update Mentorship Log List**
   - [ ] **File:** `frontend/app/mentorship-logs/page.tsx`
   - [ ] Remove client-side filtering (backend handles visibility)
   - [ ] API already returns correct logs based on role
   - [ ] Add "Specialist Access" badge on logs viewed as specialist
   - [ ] Add comment count badge (if comments > 0)

2. **Create Access Indicator Component**
   - [ ] **File:** `frontend/components/logs/AccessBadge.tsx`
   - [ ] Show why user has access:
     - "Your Log" (mentor)
     - "Mentee's Log" (supervisor)
     - "Specialist: [Thematic Area]" (specialist)
   - [ ] Different colors for each access type

3. **Update Log Detail Page**
   - [ ] **File:** `frontend/app/mentorship-logs/[id]/page.tsx`
   - [ ] Show AccessBadge component
   - [ ] Show which thematic areas match (for specialists)

**Deliverables:**
- Log list shows correct logs based on user role
- Visual indicators for access type
- Comment counts visible

**Testing:**
- Login as mentor → see only own logs
- Login as supervisor → see own + mentees' logs
- Login as specialist → see logs in their areas
- Verify badges show correctly

---

### **Phase 5: Approval Authorization** (High Priority)
**Goal:** Enforce supervisor-only approval
**Estimated Effort:** 1 day
**Dependencies:** Phase 1 complete

#### Tasks

1. **Update Approve Button Logic**
   - [ ] **File:** `frontend/app/mentorship-logs/[id]/page.tsx`
   - [ ] Check if current user can approve (client-side check)
   - [ ] Show approve button only if:
     - User is admin, OR
     - User is supervisor AND is assigned supervisor for this log
   - [ ] Add tooltip explaining why button is disabled (if not supervisor)

2. **Handle Approval Errors**
   - [ ] Catch 403 error from API
   - [ ] Show user-friendly error: "You can only approve logs from your assigned mentees"

3. **Update Log Status Badge**
   - [ ] Show approver name when approved
   - [ ] Link to approver profile (optional)

**Deliverables:**
- Only assigned supervisors see approve button
- Clear error messages for unauthorized approval attempts
- Display who approved the log

**Testing:**
- Supervisor tries to approve non-mentee's log → blocked
- Supervisor approves mentee's log → success
- Admin approves any log → success

---

### **Phase 6: Dashboard Enhancements** (Low Priority)
**Goal:** Add specialist and supervisor dashboard widgets
**Estimated Effort:** 2-3 days
**Dependencies:** Phases 1-4 complete

#### Tasks

1. **Create "Logs to Review" Widget (Specialists)**
   - [ ] **File:** `frontend/components/dashboard/LogsToReview.tsx`
   - [ ] Fetch logs in user's specialization areas
   - [ ] Filter to unread/uncommented logs
   - [ ] Show count and list (5 most recent)
   - [ ] Link to full list

2. **Create "My Mentees" Widget (Supervisors)**
   - [ ] **File:** `frontend/components/dashboard/MyMentees.tsx`
   - [ ] Fetch mentees (users where supervisor_id == current_user.id)
   - [ ] Show count and list
   - [ ] Show pending logs count for each mentee
   - [ ] Link to mentee profiles

3. **Create "Pending Approvals" Widget (Supervisors)**
   - [ ] **File:** `frontend/components/dashboard/PendingApprovals.tsx`
   - [ ] Fetch submitted logs from mentees
   - [ ] Show count and list
   - [ ] Quick approve action (optional)

4. **Update Dashboard Page**
   - [ ] **File:** `frontend/app/dashboard/page.tsx`
   - [ ] Add widgets based on user role:
     - Specialists: "Logs to Review", "Notifications"
     - Supervisors: "My Mentees", "Pending Approvals"
     - Mentors: Existing widgets

**Deliverables:**
- Role-specific dashboard widgets
- Quick access to relevant logs
- At-a-glance overview for specialists and supervisors

**Testing:**
- Login as specialist → see logs to review
- Login as supervisor → see mentees and pending approvals
- Verify counts are accurate

---

### **Phase 7: Polish & UX Improvements** (Low Priority)
**Goal:** Enhance user experience
**Estimated Effort:** 2-3 days
**Dependencies:** Phases 1-6 complete

#### Tasks

1. **Add Loading States**
   - [ ] Skeleton loaders for notifications
   - [ ] Loading spinners for comments
   - [ ] Optimistic updates (show comment immediately, sync later)

2. **Add Empty States**
   - [ ] No notifications illustration
   - [ ] No comments placeholder
   - [ ] No mentees for supervisor

3. **Add Tooltips & Help Text**
   - [ ] Explain what specializations are
   - [ ] Explain supervisor assignment
   - [ ] Guide for specialists on how to review logs

4. **Responsive Design**
   - [ ] Ensure notification dropdown works on mobile
   - [ ] Ensure comment section works on mobile
   - [ ] Test all new components on tablet/mobile

5. **Add Animations**
   - [ ] Notification bell animation on new notification
   - [ ] Smooth transitions for comment add/delete
   - [ ] Fade-in for newly loaded content

**Deliverables:**
- Polished, professional UI
- Responsive design
- Helpful guidance for users

**Testing:**
- Test on different screen sizes
- Verify animations are smooth
- Check accessibility (keyboard navigation, screen readers)

---

## TypeScript Types Needed

Create new type definitions:

**File:** `frontend/types/index.ts`

```typescript
// Add to existing types

export interface UserSpecialization {
  id: string;
  user_id: string;
  thematic_area: string;
  created_at: string;
}

export interface User {
  // Existing fields...
  supervisor_id?: string;
  specializations: UserSpecialization[];
}

export interface LogComment {
  id: string;
  mentorship_log_id: string;
  user_id: string;
  user_name: string;
  user_role: 'mentor' | 'supervisor' | 'admin';
  comment_text: string;
  is_specialist_comment: boolean;
  created_at: string;
  updated_at: string;
}

export interface SpecialistNotification {
  id: string;
  mentorship_log_id: string;
  specialist_id: string;
  thematic_area: string;
  is_read: boolean;
  notified_at: string;
  read_at?: string;
  log_facility_name?: string;
  log_mentor_name?: string;
  log_visit_date?: string;
}

export interface MentorshipLog {
  // Existing fields...
  comments: LogComment[];
}
```

---

## Constants to Add

**File:** `frontend/lib/constants/thematic-areas.ts` (New file)

```typescript
export const THEMATIC_AREAS = [
  'General HIV care and treatment',
  'Advanced HIV disease (AHD)',
  'Pediatric HIV management',
  'PMTCT',
  'TB/HIV',
  'Laboratory services',
  'Pharmacy/supply chain',
  'Data quality and use',
  'Quality improvement',
  'Other'
] as const;

export type ThematicArea = typeof THEMATIC_AREAS[number];
```

---

## Priority Matrix

| Phase | Priority | User Impact | Technical Complexity | Estimated Days |
|-------|----------|-------------|---------------------|----------------|
| Phase 1: User Management | **Critical** | High | Medium | 2-3 |
| Phase 5: Approval Auth | **Critical** | High | Low | 1 |
| Phase 2: Notifications | High | High | Medium | 2-3 |
| Phase 3: Comments | Medium | Medium | Medium | 2-3 |
| Phase 4: Visibility | Medium | Medium | Low | 1-2 |
| Phase 6: Dashboard | Low | Medium | Medium | 2-3 |
| Phase 7: Polish | Low | Low | Low | 2-3 |

**Total Estimated Time:** 13-20 days

---

## Recommended Implementation Order

### **Sprint 1: Critical Features (Week 1)**
1. Phase 1: User Management (Days 1-3)
2. Phase 5: Approval Authorization (Day 4)
3. Testing & Bug Fixes (Day 5)

**Outcome:** Admins can assign supervisors/specialists, approval works correctly

### **Sprint 2: Specialist Features (Week 2)**
1. Phase 2: Notifications System (Days 1-3)
2. Phase 3: Comments System (Days 4-5)

**Outcome:** Specialists can receive notifications and comment on logs

### **Sprint 3: Enhancements (Week 3)**
1. Phase 4: Visibility Enhancements (Days 1-2)
2. Phase 6: Dashboard Widgets (Days 3-5)

**Outcome:** Better UX, role-specific dashboards

### **Sprint 4: Polish (Week 4)**
1. Phase 7: UX Improvements (Days 1-3)
2. Final testing, bug fixes, documentation (Days 4-5)

**Outcome:** Production-ready system

---

## Testing Strategy

### **Unit Tests**
- [ ] Test user form validation (supervisor, specializations)
- [ ] Test comment form validation
- [ ] Test notification service methods
- [ ] Test access badge logic

### **Integration Tests**
- [ ] Test supervisor assignment workflow
- [ ] Test notification flow (submit log → notify specialists)
- [ ] Test comment workflow (add, edit, delete)
- [ ] Test approval authorization

### **E2E Tests**
- [ ] User journey: Admin creates specialist user
- [ ] User journey: Mentor submits log → specialist notified → specialist comments
- [ ] User journey: Supervisor approves mentee's log
- [ ] User journey: Specialist reviews logs in their area

### **Manual Testing Checklist**
- [ ] Test all user roles (mentor, supervisor with mentees, specialist, admin)
- [ ] Test edge cases (no supervisor, no specializations, no notifications)
- [ ] Test permissions (unauthorized actions blocked)
- [ ] Test responsive design (mobile, tablet, desktop)
- [ ] Test browser compatibility (Chrome, Firefox, Safari)

---

## Risks & Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Backend API changes | High | Low | Backend is stable; coordinate if changes needed |
| Type mismatches | Medium | Medium | Use TypeScript strict mode; validate responses |
| Performance issues (notifications polling) | Medium | Medium | Use efficient polling; consider WebSockets later |
| Complex permission logic | Medium | Low | Thoroughly test all role combinations |
| Mobile UX challenges | Low | Medium | Test early on mobile devices |

---

## Success Metrics

After implementation, measure:

1. **Adoption Rate**
   - % of mentors with assigned supervisors
   - % of users with specializations
   - Average time to assign supervisor to new mentor

2. **Engagement**
   - Average comments per log
   - % of specialists who comment on logs in their area
   - Average time from notification to specialist review

3. **Approval Workflow**
   - Average time from submission to approval
   - % of logs approved by assigned supervisor (vs admin)

4. **User Satisfaction**
   - Feedback from specialists on notification usefulness
   - Feedback from supervisors on mentee management

---

## Future Enhancements (Post-Launch)

1. **Email Notifications**
   - Send email when specialist is notified
   - Digest emails (daily summary)

2. **Advanced Filtering**
   - Filter notifications by thematic area
   - Filter logs by specialist access

3. **Notification Preferences**
   - Allow users to mute certain thematic areas
   - Configure notification frequency

4. **Specialist Review Workflow**
   - Optional specialist approval before supervisor approval
   - Specialist sign-off tracking

5. **Comment Features**
   - Reply to comments (threading)
   - @mentions in comments
   - Attach files to comments

6. **Analytics Dashboard**
   - Specialist engagement metrics
   - Supervisor approval metrics
   - Average review times

---

## Documentation Needs

After implementation:

1. **User Guides**
   - [ ] How to assign supervisors (for admins)
   - [ ] How to assign specializations (for admins)
   - [ ] How to use notifications (for specialists)
   - [ ] How to comment on logs
   - [ ] How to approve logs (for supervisors)

2. **Developer Docs**
   - [ ] Update API documentation
   - [ ] Document new components
   - [ ] Document new types/interfaces
   - [ ] Update architecture diagrams

3. **Training Materials**
   - [ ] Video walkthrough for administrators
   - [ ] FAQ for specialists
   - [ ] Troubleshooting guide

---

## Rollout Plan

### **Phase A: Internal Testing (Week 1)**
- Deploy to staging environment
- Test with development team
- Fix critical bugs

### **Phase B: Pilot with Admins (Week 2)**
- Enable for admins only
- Assign supervisors and specializations
- Gather feedback

### **Phase C: Pilot with Specialists (Week 3)**
- Enable notifications and comments
- Monitor engagement
- Gather feedback

### **Phase D: Full Rollout (Week 4)**
- Enable for all users
- Monitor system performance
- Provide user support

---

## Conclusion

This roadmap provides a structured approach to implementing the supervisor-specialist system in the frontend. By breaking down the work into phases and prioritizing critical features first, we can deliver value incrementally while minimizing risk.

**Next Steps:**
1. Review and approve this roadmap
2. Set up project tracking (Jira, Trello, GitHub Projects)
3. Assign developers to phases
4. Begin Phase 1 implementation

**Questions or Feedback:** [Add contact info or review process]
