# Testing the Auto-Assignment Feature

## Quick Test Guide

### Setup Test Scenario

1. **Login to Admin Panel**
   ```
   http://localhost:8000/carwash-admin/
   ```

2. **Set All Washers Offline**
   - Go to "Manage Washers"
   - Toggle all washers to "unavailable" (offline)

3. **Create Test Orders as Client**
   - Logout from admin
   - Login as a client
   - Book 2-3 wash orders
   - These will be in "pending" status (no washers available)

### Test Auto-Assignment

#### Test 1: Toggle Washer Status
1. Login to admin panel
2. Go to "Manage Washers"
3. Toggle one washer to "available"
4. **Expected Result**: 
   - Success message: "Washer [Name] is now available"
   - Success message: "Automatically assigned X pending order(s) to available washers"
5. Check dashboard - pending orders should now be assigned

#### Test 2: Manual Auto-Assign Button
1. Make sure you have pending orders
2. Make sure you have available washers
3. Go to admin dashboard
4. Click "Auto-Assign Orders" button in pending orders section
5. **Expected Result**:
   - Success message: "Successfully assigned X pending order(s) to available washers"
   - Pending orders disappear from dashboard
   - Orders now show in "Manage Orders" with "assigned" status

#### Test 3: Cancel Order Triggers Assignment
1. Have at least 2 pending orders
2. Have 1 washer with an active order
3. Cancel the active order
4. **Expected Result**:
   - Order cancelled successfully
   - One pending order automatically assigned to the freed washer

### Verify Results

1. **Check Dashboard**
   - Pending orders count should decrease
   - Assigned orders should appear

2. **Check Manage Orders**
   - Orders should have status "assigned"
   - Orders should have washer assigned
   - `assigned_at` timestamp should be set

3. **Check Console Output**
   - Look for: "Auto-assigned order #X to [Washer Name]"

### Edge Cases to Test

1. **No Pending Orders**
   - Click "Auto-Assign Orders"
   - Should show: "No pending orders to assign or no available washers"

2. **No Available Washers**
   - Have pending orders
   - All washers offline or busy
   - Click "Auto-Assign Orders"
   - Should show: "No pending orders to assign or no available washers"

3. **More Orders Than Washers**
   - Create 5 pending orders
   - Have only 2 available washers
   - Click "Auto-Assign Orders"
   - Should assign 2 orders, leave 3 pending

4. **FIFO Order**
   - Create orders at different times
   - Auto-assign
   - Oldest orders should be assigned first

## Expected Behavior Summary

✅ **When washer becomes available** → Auto-assigns pending orders
✅ **When order is cancelled** → Frees washer and auto-assigns pending orders
✅ **Manual trigger button** → Assigns all possible pending orders
✅ **FIFO logic** → Oldest orders get priority
✅ **One order per washer** → Respects capacity limits
✅ **Clear feedback** → Success/info messages for all actions

## Troubleshooting

### Orders Not Auto-Assigning?

1. Check washer status:
   ```python
   # In Django shell
   from washers.models import Washer
   Washer.objects.filter(is_available=True, status='active')
   ```

2. Check pending orders:
   ```python
   from clients.models import WashOrder
   WashOrder.objects.filter(status='pending')
   ```

3. Check for active orders:
   ```python
   WashOrder.objects.filter(status__in=['assigned', 'in_progress'])
   ```

4. Check console for error messages

### Manual Test in Django Shell

```python
from clients.utils import auto_assign_pending_orders

# Run auto-assignment
count = auto_assign_pending_orders()
print(f"Assigned {count} orders")
```

## Success Criteria

- ✅ Pending orders automatically assigned when washers available
- ✅ Manual button works correctly
- ✅ Clear user feedback via messages
- ✅ No duplicate assignments
- ✅ FIFO order maintained
- ✅ System handles edge cases gracefully
