# Car Wash Management System - Database Schema

## Overview
This document outlines the complete database schema for the Car Wash Management System built with Django.

---

## 1. CLIENTS APP TABLES

### 1.1 `clients` Table
**Purpose**: Stores customer information and authentication data

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `client_id` | AutoField | PRIMARY KEY | Unique client identifier |
| `email` | EmailField(255) | UNIQUE, NOT NULL | Client's email address (used for login) |
| `password_hash` | CharField(255) | NOT NULL | Hashed password for authentication |
| `first_name` | CharField(100) | NOT NULL | Client's first name |
| `last_name` | CharField(100) | NOT NULL | Client's last name |
| `phone` | CharField(20) | NULL, BLANK | Client's phone number |
| `date_created` | DateTimeField | AUTO_NOW_ADD | Account creation timestamp |

**Relationships**: 
- One-to-Many with `vehicles`
- One-to-Many with `wash_orders`
- One-to-Many with `appointments`
- One-to-Many with `password_reset_tokens`

---

### 1.2 `password_reset_tokens` Table
**Purpose**: Manages password reset functionality for clients

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | AutoField | PRIMARY KEY | Token record ID |
| `client_id` | ForeignKey | NOT NULL, CASCADE | Reference to client |
| `token` | UUIDField | UNIQUE | UUID token for password reset |
| `created_at` | DateTimeField | AUTO_NOW_ADD | Token creation time |
| `is_used` | BooleanField | DEFAULT FALSE | Whether token has been used |

**Relationships**:
- Many-to-One with `clients`

**Business Rules**:
- Tokens expire after 1 hour
- Tokens are single-use only

---

### 1.3 `vehicles` Table
**Purpose**: Stores client vehicle information

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `vehicle_id` | AutoField | PRIMARY KEY | Unique vehicle identifier |
| `client_id` | ForeignKey | NOT NULL, CASCADE | Vehicle owner |
| `make` | CharField(100) | NOT NULL | Vehicle manufacturer |
| `model` | CharField(100) | NOT NULL | Vehicle model |
| `year` | IntegerField | NULL, BLANK | Manufacturing year |
| `color` | CharField(50) | NULL, BLANK | Vehicle color |
| `license_plate` | CharField(20) | UNIQUE | License plate number |
| `vehicle_type` | CharField(20) | DEFAULT 'sedan' | Type of vehicle |
| `notes` | TextField | NULL, BLANK | Additional notes |
| `date_added` | DateTimeField | AUTO_NOW_ADD | Registration timestamp |

**Vehicle Type Choices**:
- `sedan` - Sedan
- `suv` - SUV
- `truck` - Truck
- `van` - Van
- `motorcycle` - Motorcycle
- `other` - Other

**Relationships**:
- Many-to-One with `clients`
- One-to-Many with `wash_orders`
- One-to-Many with `appointments`

---

### 1.4 `wash_orders` Table
**Purpose**: Manages car wash service orders

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `order_id` | AutoField | PRIMARY KEY | Unique order identifier |
| `client_id` | ForeignKey | NOT NULL, CASCADE | Order customer |
| `vehicle_id` | ForeignKey | NOT NULL, CASCADE | Vehicle to be washed |
| `washer_id` | ForeignKey | NULL, SET_NULL | Assigned washer |
| `wash_type` | CharField(20) | DEFAULT 'basic' | Type of wash service |
| `status` | CharField(20) | DEFAULT 'pending' | Current order status |
| `price` | DecimalField(10,2) | NOT NULL | Service price |
| `notes` | TextField | NULL, BLANK | Special instructions |
| `created_at` | DateTimeField | AUTO_NOW_ADD | Order creation time |
| `assigned_at` | DateTimeField | NULL, BLANK | Washer assignment time |
| `started_at` | DateTimeField | NULL, BLANK | Service start time |
| `completed_at` | DateTimeField | NULL, BLANK | Service completion time |
| `client_notified` | BooleanField | DEFAULT FALSE | Notification status |

**Status Choices**:
- `pending` - Pending Assignment
- `scheduled` - Scheduled for Future
- `assigned` - Assigned to Washer
- `in_progress` - Currently Being Washed
- `completed` - Service Completed
- `cancelled` - Order Cancelled

**Wash Type Choices**:
- `basic` - Basic Wash ($15.00)
- `premium` - Premium Wash ($25.00)
- `deluxe` - Deluxe Wash ($35.00)

**Relationships**:
- Many-to-One with `clients`
- Many-to-One with `vehicles`
- Many-to-One with `washers`
- One-to-One with `appointments` (optional)

**Business Rules**:
- A washer can only have one active order at a time
- Orders progress through status workflow
- Price is set based on wash type

---

### 1.5 `time_slots` Table
**Purpose**: Manages available appointment time slots

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | AutoField | PRIMARY KEY | Slot identifier |
| `date` | DateField | NOT NULL | Appointment date |
| `start_time` | TimeField | NOT NULL | Slot start time |
| `end_time` | TimeField | NOT NULL | Slot end time |
| `max_capacity` | PositiveIntegerField | DEFAULT 3 | Maximum appointments |
| `is_active` | BooleanField | DEFAULT TRUE | Slot availability |
| `created_at` | DateTimeField | AUTO_NOW_ADD | Creation timestamp |
| `updated_at` | DateTimeField | AUTO_NOW | Last update time |

**Constraints**:
- UNIQUE(`date`, `start_time`) - Prevents duplicate slots

**Relationships**:
- One-to-Many with `appointments`

**Business Rules**:
- Past time slots are automatically unavailable
- Capacity determines how many appointments can be booked
- Slots can be deactivated by admin

---

### 1.6 `appointments` Table
**Purpose**: Manages scheduled car wash appointments

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | AutoField | PRIMARY KEY | Appointment identifier |
| `client_id` | ForeignKey | NOT NULL, CASCADE | Appointment client |
| `vehicle_id` | ForeignKey | NOT NULL, CASCADE | Vehicle for service |
| `time_slot_id` | ForeignKey | NOT NULL, CASCADE | Scheduled time slot |
| `wash_order_id` | OneToOneField | NULL, CASCADE | Associated wash order |
| `wash_type` | CharField(20) | DEFAULT 'basic' | Type of wash service |
| `special_instructions` | TextField | BLANK | Client instructions |
| `is_confirmed` | BooleanField | DEFAULT TRUE | Confirmation status |
| `is_cancelled` | BooleanField | DEFAULT FALSE | Cancellation status |
| `cancelled_at` | DateTimeField | NULL, BLANK | Cancellation time |
| `cancellation_reason` | TextField | BLANK | Reason for cancellation |
| `created_at` | DateTimeField | AUTO_NOW_ADD | Booking timestamp |
| `updated_at` | DateTimeField | AUTO_NOW | Last update time |

**Relationships**:
- Many-to-One with `clients`
- Many-to-One with `vehicles`
- Many-to-One with `time_slots`
- One-to-One with `wash_orders`

**Business Rules**:
- Appointments automatically create wash orders
- Cancelled appointments free up time slot capacity
- Past appointments cannot be modified

---

## 2. WASHERS APP TABLES

### 2.1 `washers` Table
**Purpose**: Stores car wash staff/employee information

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `washer_id` | AutoField | PRIMARY KEY | Unique washer identifier |
| `email` | EmailField(255) | UNIQUE, NOT NULL | Washer's email (login) |
| `password_hash` | CharField(255) | NOT NULL | Hashed password |
| `first_name` | CharField(100) | NOT NULL | Washer's first name |
| `last_name` | CharField(100) | NOT NULL | Washer's last name |
| `phone` | CharField(20) | NOT NULL | Contact phone number |
| `is_available` | BooleanField | DEFAULT TRUE | Current availability |
| `hourly_rate` | DecimalField(10,2) | NULL, BLANK | Pay rate per hour |
| `date_hired` | DateTimeField | AUTO_NOW_ADD | Employment start date |
| `status` | CharField(20) | DEFAULT 'active' | Employment status |

**Status Choices**:
- `active` - Active Employee
- `inactive` - Inactive Employee
- `on_break` - Currently on Break

**Relationships**:
- One-to-Many with `wash_orders`

**Business Rules**:
- Washers can only work on one order at a time
- Availability affects order assignment
- Phone numbers must be unique

---

## 3. ADMIN APP

### 3.1 SystemStats (Helper Class)
**Purpose**: Provides dashboard statistics and analytics

**Note**: This is not a database table but a helper class that aggregates data from other tables for admin dashboard display.

**Calculated Metrics**:
- Total orders, clients, washers, vehicles
- Pending and in-progress orders
- Available washers (excluding those with active orders)
- Daily completion counts
- Total revenue from completed orders
- Scheduled appointments count

---

## 4. DATABASE RELATIONSHIPS DIAGRAM

```
clients (1) ──────── (*) vehicles
   │                      │
   │                      │
   │ (1)              (*) │
   │                      │
   └─── (*) wash_orders ──┘
           │
           │ (*) 
           │
           └─── (1) washers
           │
           │ (1:1)
           │
    appointments (*) ──── (1) time_slots
           │
           │ (*)
           │
           └─── (1) clients
           │
           │ (*)
           │
           └─── (1) vehicles

password_reset_tokens (*) ──── (1) clients
```

---

## 5. KEY BUSINESS RULES

### 5.1 Order Management
- Orders flow through status: pending → assigned → in_progress → completed
- Washers can only handle one active order at a time
- Orders can be cancelled at any stage before completion

### 5.2 Appointment System
- Appointments automatically create corresponding wash orders
- Time slots have capacity limits (default: 3 appointments)
- Past appointments and time slots are read-only
- Cancelling appointments frees up time slot capacity

### 5.3 User Management
- Clients and washers have separate authentication systems
- Email addresses must be unique within each user type
- Password reset tokens expire after 1 hour

### 5.4 Vehicle Management
- License plates must be unique across all vehicles
- Clients can own multiple vehicles
- Vehicle information is preserved even if orders are deleted

---

## 6. INDEXES AND PERFORMANCE

### 6.1 Recommended Indexes
- `clients.email` (unique index)
- `washers.email` (unique index)
- `vehicles.license_plate` (unique index)
- `wash_orders.status` (for filtering)
- `wash_orders.created_at` (for date-based queries)
- `time_slots.date, time_slots.start_time` (composite unique)
- `appointments.time_slot_id, appointments.is_cancelled` (composite)

### 6.2 Query Optimization
- Use select_related() for foreign key relationships
- Use prefetch_related() for reverse foreign key relationships
- Filter by status and date ranges for better performance
- Consider pagination for large result sets

---

## 7. DATA INTEGRITY CONSTRAINTS

### 7.1 Foreign Key Constraints
- `CASCADE`: Delete related records when parent is deleted
- `SET_NULL`: Set foreign key to NULL when referenced record is deleted
- Prevents orphaned records and maintains referential integrity

### 7.2 Unique Constraints
- Email addresses (clients and washers)
- License plates (vehicles)
- Time slots (date + start_time combination)
- Password reset tokens

### 7.3 Business Logic Constraints
- Washer availability validation
- Time slot capacity validation
- Order status workflow validation
- Appointment date validation (no past bookings)

---

This schema supports a complete car wash management system with client registration, vehicle management, appointment scheduling, order processing, and staff management capabilities.