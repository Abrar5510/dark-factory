# Pocketful Stage 1 Implementation Plan

## Overview
Implementation of Pocketful payments and settlements service - Stage 1, providing:
- User authentication with email/password (signup/login)
- Wallet system with balance management
- Payments between users by handle
- Money requests (pending/paid/declined/cancelled)
- Bill splitting with equal share calculation
- Batch settlements for operators
- Activity feed with visibility rules
- Idempotent write operations
- Test endpoints for reset and state management

## Technology Stack
- **Runtime**: Node.js 20+ with TypeScript
- **Framework**: Express.js for HTTP server
- **Database**: SQLite with better-sqlite3 (in-memory/file-based)
- **Authentication**: Bearer tokens (JWT-like, without expiration)
- **Password Hashing**: bcrypt
- **Testing**: Built-in test endpoints for verification
- **Containerization**: Docker with multi-stage build

## Architecture Components

### 1. Data Models
- **Users**: id, email, password_hash, display_name, handle, balance, created_at
- **Payments**: id, from_user_id, to_user_id, amount, note, visibility, request_id, settlement_id, created_at
- **Requests**: id, requester_id, payer_id, amount, note, status, payment_id, created_at
- **Splits**: id, creator_id, amount, note, created_at
- **SplitParticipants**: split_id, user_id, amount
- **Settlements**: id, operator_id, committed_at
- **IdempotencyKeys**: user_id, key, method, path, request_hash, response_body, created_at
- **Sessions**: user_id, token, created_at

### 2. Key Constraints
- Wallet balances never negative (including transactionally)
- Total balance sum equals seeded amount after reset
- Atomic transfers (payments update both wallets in single transaction)
- Handle uniqueness and derivation from email
- Idempotency key scoped per user
- Visibility rules: public payments visible to all, private only to sender/receiver

### 3. Core Business Logic
- **Handle derivation**: local-part@domain → lowercase, replace non-[a-z0-9_] with _, truncate to 20
- **Equal split calculation**: Distribute remainder to first participants
- **Atomic settlements**: All transfers succeed or none
- **Feed visibility**: public OR caller is sender/receiver
- **Request state machine**: pending → paid/declined/cancelled

## API Endpoints

### Authentication
- `POST /auth/signup` - Create new account
- `POST /auth/login` - Get bearer token

### User
- `GET /me` - Get current user info

### Payments (Idempotent)
- `POST /payments` - Send money to handle

### Requests
- `POST /requests` - Create money request (Idempotent)
- `POST /requests/{id}/pay` - Pay a request (Idempotent)
- `POST /requests/{id}/decline` - Decline request
- `POST /requests/{id}/cancel` - Cancel request
- `GET /requests` - List requests (incoming/outgoing)

### Splits (Idempotent)
- `POST /splits` - Split bill and create requests

### Settlements (Idempotent)
- `POST /settlements` - Batch transfers (operators only)

### Activity
- `GET /activity` - Payment feed

### Test Endpoints
- `GET /health` - Service health check
- `POST /_test/reset` - Replace all state with fixture
- `GET /_test/export` - Export full state
- `POST /_test/import` - Import state from export

## Database Schema
SQLite with proper indices for:
- User lookups by email, handle
- Payment lookups by user_id, created_at
- Request lookups by payer_id, requester_id, status
- Idempotency key lookups by user_id + key

## Transaction Management
- All write operations wrapped in database transactions
- Balance updates use `UPDATE users SET balance = balance + ? WHERE id = ?`
- Concurrent requests handled with database-level locking
- Idempotency checks before transaction begins

## Error Handling
- Consistent error response format: `{ "error": { "code": "...", "message": "..." } }`
- Validation failures return 422 with specific codes
- Idempotency key reuse returns 409
- Insufficient funds returns 409

## Implementation Phases

### Phase 1: Foundation
- Database setup with schema
- User model and authentication
- Basic error handling middleware
- Health and test endpoints

### Phase 2: Core Features
- Payments system with atomic transfers
- Requests system with state management
- Activity feed with visibility rules

### Phase 3: Advanced Features
- Splits with equal share calculation
- Settlements for operators
- Idempotency support

### Phase 4: Polish & Testing
- Test endpoints (reset, export/import)
- Edge case handling
- Performance optimizations
- Docker configuration

## Resource Constraints
- 2 vCPU, 2 GiB RAM limit
- 60s startup time
- 5s per-request timeout (10s for /_test/reset)
- No outbound network at runtime
- All dependencies included in Docker image

## Success Criteria
- All endpoints implemented per specification
- Atomic balance updates with no negative balances
- Correct idempotency behavior
- Proper error codes and validation
- Passes isolated checks in test harness