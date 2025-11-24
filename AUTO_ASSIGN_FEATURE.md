# Auto-Assignment Feature for Pending Orders

## Problem
When a client places an order and all washers are offline, the order remains in "pending" status. Even when washers come back online, these pending orders are not automatically assigned.

## Solution
Implemented an automatic order assignment system that:
1. Assigns pending orders when washers become available
2. Assigns pending orders when active orders are cancelled
3. Provides a manual trigger button for admins

## Changes Made

### 1. New Utility Function (`clients/utils.py`)
- `auto_assign_pending_orders()`: Automatically assigns pending orders to available washers
- Uses FIFO (First In, First Out) logic
- Returns count of orders assigned
- Prevents double-assignment by checking active orders

### 2. Updated Admin Views (`admin/views.py`)
- **`toggle_washer_status_view`**: Triggers auto-assignment when washer becomes available
- **`cancel_order_view`**: Triggers auto-assignment when order is cancelled (frees up washer)
- **`auto_assign_orders_view`**: New view for manual trigger

### 3. Updated Admin URLs (`admin/urls.py`)
- Added route: `/orders/auto-assign/` for manual triggering

### 4. Updated Dashboard (`admin/templates/admin/dashboard.html`)
- Added "Auto-Assign Orders" button in pending orders section
- Button triggers manual assignment of all pending orders

## How It Works

### Automatic Triggers
1. **Washer Status Change**: When admin toggles washer to "available"
   - System checks for pending orders
   - Assigns them to newly available washer

2. **Order Cancellation**: When an active order is cancelled
   - Washer becomes available
   - System assigns pending orders to that washer

3. **Order Completion**: When washer completes an order
   - Washer becomes available for new orders
   - Next pending order can be assigned

### Manual Trigger
- Admin can click "Auto-Assign Orders" button
- Useful for:
  - Bulk assignment after system maintenance
  - Resolving stuck pending orders
  - Testing the assignment logic

## Assignment Logic

```python
1. Get all pending orders (ordered by creation time - FIFO)
2. Get all available washers (not busy with active orders)
3. For each pending order:
   - Find an available washer
   - Assign order to washer
   - Update order status to 'assigned'
   - Set assigned_at timestamp
4. Return count of orders assigned
```

## Benefits

1. **Better Customer Experience**: Orders get assigned as soon as washers are available
2. **Reduced Manual Work**: Admins don't need to manually assign each order
3. **Fair Distribution**: FIFO ensures orders are handled in order received
4. **Flexibility**: Manual trigger available for edge cases

## Future Enhancements

1. **Email Notifications**: Notify clients when their order is assigned
2. **SMS Notifications**: Send text alerts for order updates
3. **Scheduled Task**: Run auto-assignment periodically (e.g., every 5 minutes)
4. **Priority System**: VIP customers get priority assignment
5. **Load Balancing**: Distribute orders evenly among washers
6. **Washer Preferences**: Assign based on washer specialties or ratings

## Testing

To test the feature:

1. **Create pending orders**:
   - Set all washers to offline
   - Have clients book wash orders
   - Orders will be in "pending" status

2. **Test auto-assignment**:
   - Toggle a washer to "available"
   - Pending orders should auto-assign
   - Check success message

3. **Test manual trigger**:
   - Click "Auto-Assign Orders" button
   - Verify orders are assigned
   - Check notification messages

## Notes

- Auto-assignment respects washer capacity (one active order per washer)
- System prevents double-assignment
- Failed assignments are logged for debugging
- Assignment is atomic (all-or-nothing per order)
