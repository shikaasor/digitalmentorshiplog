# Error Handling Guide

## Overview

This application implements a robust error handling system that prevents the app from crashing and provides clear feedback to users. The system handles errors gracefully without logging users out unnecessarily.

## Key Components

### 1. **Error Handler (`lib/errors/error-handler.ts`)**
Centralized error parsing and classification.

### 2. **Toast Notifications (`lib/stores/toast.store.ts`)**
User-friendly notification system for success/error messages.

### 3. **API Client (`lib/api/client.ts`)**
Axios interceptors with intelligent error handling.

### 4. **Error Boundary (`components/errors/ErrorBoundary.tsx`)**
Catches React rendering errors.

---

## How Errors Are Handled

### **Authentication Errors (401)**
- ✅ User is logged out
- ✅ Redirected to login page
- ✅ Toast notification shown
- ❌ Session preserved (intentionally cleared)

### **Authorization Errors (403)**
- ✅ User stays logged in
- ✅ Toast notification shown
- ✅ Can continue using other features
- ❌ No redirect

### **Validation Errors (422)**
- ✅ User stays logged in
- ✅ Detailed error messages shown
- ✅ Can retry the action
- ❌ No redirect

### **Server Errors (500, 502, 503)**
- ✅ User stays logged in
- ✅ User-friendly message shown
- ✅ Marked as retryable
- ❌ No redirect

### **Network Errors**
- ✅ User stays logged in
- ✅ Connection message shown
- ✅ Marked as retryable
- ❌ No redirect

---

## Using Toast Notifications

### **Import the toast utility**
```typescript
import { toast } from '@/lib/stores/toast.store'
```

### **Show Success Messages**
```typescript
// Simple success
toast.success('Operation Successful!')

// With details
toast.success('User Created', 'The user has been added to the system.')

// Custom duration (milliseconds)
toast.success('Saved!', 'Your changes have been saved.', 3000)
```

### **Show Error Messages**
```typescript
// Simple error
toast.error('Operation Failed')

// With details
toast.error('Failed to Save', 'Please check your input and try again.')

// Errors stay longer by default (7 seconds vs 5 seconds)
```

### **Show Warning Messages**
```typescript
toast.warning('Warning', 'This action cannot be undone.')
```

### **Show Info Messages**
```typescript
toast.info('Info', 'Your session will expire in 5 minutes.')
```

---

## Handling API Errors in Components

### **Method 1: Use `showErrorToast` helper**
```typescript
import { showErrorToast } from '@/lib/api/client'

const handleDelete = async (id: string) => {
  try {
    await facilitiesService.delete(id)
    toast.success('Deleted Successfully')
  } catch (error) {
    showErrorToast(error, 'Delete Failed')
  }
}
```

### **Method 2: Manual error handling**
```typescript
import { handleApiError } from '@/lib/api/client'
import { toast } from '@/lib/stores/toast.store'

const handleUpdate = async () => {
  try {
    await usersService.update(id, data)
    toast.success('Updated Successfully')
  } catch (error) {
    const message = handleApiError(error)
    toast.error('Update Failed', message)
  }
}
```

### **Method 3: Set error state (for displaying in UI)**
```typescript
const [error, setError] = useState<string | null>(null)

const loadData = async () => {
  try {
    setError(null)
    const data = await someService.getData()
    setData(data)
  } catch (err) {
    const message = handleApiError(err)
    setError(message)
    showErrorToast(err, 'Failed to Load Data')
  }
}

// In JSX:
{error && (
  <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
    {error}
  </div>
)}
```

---

## Using Error Boundaries

### **Wrap components that might crash**
```typescript
import ErrorBoundary from '@/components/errors/ErrorBoundary'

export default function SomePage() {
  return (
    <ErrorBoundary>
      <ComponentThatMightCrash />
    </ErrorBoundary>
  )
}
```

### **With custom fallback UI**
```typescript
<ErrorBoundary
  fallback={
    <div>
      <h2>Oops! Something went wrong in this section.</h2>
      <button onClick={() => window.location.reload()}>
        Reload Page
      </button>
    </div>
  }
>
  <ComponentThatMightCrash />
</ErrorBoundary>
```

---

## Best Practices

### **1. Always Catch Errors**
```typescript
// ✅ GOOD
const handleSubmit = async () => {
  try {
    await someAPI.call()
  } catch (error) {
    showErrorToast(error)
  }
}

// ❌ BAD - Uncaught errors will crash the app
const handleSubmit = async () => {
  await someAPI.call() // No error handling!
}
```

### **2. Provide Context in Error Messages**
```typescript
// ✅ GOOD - User knows what failed
showErrorToast(error, 'Failed to Create Facility')

// ❌ BAD - Generic message
showErrorToast(error)
```

### **3. Don't Log Out on Non-Auth Errors**
```typescript
// ✅ GOOD - Error is handled, user stays logged in
catch (error) {
  showErrorToast(error, 'Operation Failed')
}

// ❌ BAD - User is logged out for any error
catch (error) {
  logout()
}
```

### **4. Show Success Feedback**
```typescript
// ✅ GOOD - User gets confirmation
await facilitiesService.create(data)
toast.success('Facility Created', 'The facility has been added successfully.')
router.push('/facilities')

// ❌ BAD - Silent success, user unsure if it worked
await facilitiesService.create(data)
router.push('/facilities')
```

### **5. Allow Retries for Temporary Errors**
```typescript
const [retryCount, setRetryCount] = useState(0)

const loadData = async () => {
  try {
    const data = await someService.getData()
    setData(data)
  } catch (error) {
    const appError = parseError(error)

    if (isRetryable(appError) && retryCount < 3) {
      // Auto-retry for network errors
      setTimeout(() => {
        setRetryCount(retryCount + 1)
        loadData()
      }, 2000)
    } else {
      showErrorToast(error, 'Failed to Load Data')
    }
  }
}
```

---

## Error States in Components

### **Loading, Error, and Success States**
```typescript
export default function DataPage() {
  const [data, setData] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      setError(null)
      const result = await dataService.getAll()
      setData(result)
    } catch (err) {
      const message = handleApiError(err)
      setError(message)
      showErrorToast(err, 'Failed to Load Data')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <LoadingSpinner />
  }

  if (error) {
    return (
      <ErrorMessage
        message={error}
        onRetry={loadData}
      />
    )
  }

  return <DataTable data={data} />
}
```

---

## Testing Error Handling

### **Simulate 401 (Unauthorized)**
```typescript
// In API service, temporarily:
throw { response: { status: 401, data: { detail: 'Token expired' } } }
```

### **Simulate 403 (Forbidden)**
```typescript
throw { response: { status: 403, data: { detail: 'Access denied' } } }
```

### **Simulate Network Error**
```typescript
throw { message: 'Network Error' }
```

### **Simulate 500 (Server Error)**
```typescript
throw { response: { status: 500, data: { detail: 'Internal server error' } } }
```

---

## Common Scenarios

### **Scenario 1: User Tries to Access Admin Page**
**Error:** 403 Forbidden
**Behavior:**
- ✅ User stays logged in
- ✅ Toast: "Access Denied - You do not have permission to perform this action"
- ✅ User can navigate to other pages

### **Scenario 2: User's Token Expires**
**Error:** 401 Unauthorized
**Behavior:**
- ✅ User is logged out
- ✅ Toast: "Session Expired - Please log in again to continue"
- ✅ Redirected to login after 1 second

### **Scenario 3: Network Connection Lost**
**Error:** Network Error
**Behavior:**
- ✅ User stays logged in
- ✅ Toast: "Unable to connect to the server. Please check your internet connection."
- ✅ User can retry or navigate elsewhere

### **Scenario 4: Invalid Form Input**
**Error:** 422 Validation Error
**Behavior:**
- ✅ User stays logged in
- ✅ Toast: "Please check your input and try again" with field details
- ✅ User can correct and resubmit

---

## Migration Guide (For Existing Code)

### **Before (Old Pattern)**
```typescript
try {
  await api.call()
} catch (error: any) {
  setError(error.message)
  // User might get logged out unnecessarily
}
```

### **After (New Pattern)**
```typescript
try {
  await api.call()
  toast.success('Success!')
} catch (error) {
  showErrorToast(error, 'Operation Failed')
  // User stays logged in unless it's a 401 error
}
```

---

## Summary

✅ **Errors no longer crash the app**
✅ **Users are not logged out unnecessarily**
✅ **Clear, user-friendly error messages**
✅ **Toast notifications for all feedback**
✅ **Error boundaries catch rendering errors**
✅ **Centralized error handling logic**

The system is designed to maximize user experience by being forgiving and informative!
