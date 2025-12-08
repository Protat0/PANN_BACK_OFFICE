# Final Defense Study Notes (PANN POS)

_Last updated: 2025-12-07_

## Elevator Pitch (What & Why)
- Modern POS platform that couples a Vue 3 + Vite SPA with a Django REST + MongoDB backend to keep brick-and-mortar stores, online channels, and KPI dashboards in sync.
- Core differentiators: FIFO-aware inventory logic, proactive session management, automated online-order life cycle, and built-in CSV/Excel tooling for rapid data onboarding.
- Deployment story is straightforward (Netlify + Render) because everything is driven by environment variables and health endpoints that ops can probe before each demo.
- Defense angle: emphasize how a layered architecture lets the team reason about state changes (auth, inventory, orders, reports) without duplicating logic.

## System Architecture Snapshot
```
Vue 3 + Vite SPA (Pinia, Vue Router, composables)
        │
Axios client with JWT interceptors + toast-driven UX
        │
Django REST Framework API (auth, KPIs, POS modules)
        │
Service layer orchestrating MongoDB collections, notifications, schedulers
        │
MongoDB Atlas (primary document store for POS, KPIs, sessions)
```
Cross-cutting capabilities: notification service, token blacklist, FIFO batch math, online-order scheduler, CSV import/export pipelines, and `/api/v1/health` for runtime checks.

## Backend Concepts & Logic

### Configuration & Resilience
- A centralized `DatabaseManager` pulls the Atlas URI and database name from `.env`, opens the client once, pings the cluster to verify connectivity, and hands out collection handles to the rest of the app.
- Because services always request the database through that manager, reconnect logic, pooling, and error translation live in one place rather than being re-implemented per endpoint.
- Secrets and timeouts are environment-driven (JWT secrets, token expiry minutes/days, auto-cancel intervals), so behavior can be tuned per environment without code changes.

### Domain Services & Composition
- DRF views act as thin controllers; business rules live in `app/services`. Each service manages its own collection handles plus any collaborators (e.g., online transactions compose product, batch, notification, and session services).
- This separation lets multiple endpoints share the same invariants: stock deductions always go through the same FIFO helper, session state updates reuse the same audit trail, and KPI queries reuse aggregation logic rather than duplicating Mongo queries.
- Directory highlights to mention: `services/pos` for POS-specific pipelines, `services/session_services.py` for login/logout lifecycle management, and `notifications/` for reusable delivery channels.

### Authentication & Session Discipline
- JWT secrets resolve via a clear priority (explicit auth secret → Django `SECRET_KEY` → legacy fallback), which is easy to explain during defense when asked about key rotation.
- Token handling differentiates access vs. refresh lifespans; refresh tokens live longer and are exchanged server-side when Axios sees a `401`, while blacklisted tokens are stored in `token_blacklist` so logout is enforceable.
- Every successful login triggers a session log with a human-readable `SESS-#####` identifier, closes previous active sessions for that user, and emits notifications + shift summary emails. This demonstrates control over concurrent access and gives measurable KPIs (active sessions, session duration, etc.).

### Online Ordering Workflow & Automation
- Online order views are grouped by intent (create, status updates, payment confirmation, cancellations, analytics). Each view simply validates input and delegates to `OnlineTransactionService`.
- The service enforces a status state machine (`pending → confirmed → processing → ready → completed` with cancellation branches) and appends each transition to `status_history` for auditing.
- A background scheduler starts automatically when the service is instantiated. Every few minutes it scans for stale `pending` or `confirmed` orders, cancels the expired ones, restores inventory via FIFO batches, records who/what cancelled the order, and pushes staff notifications. Manual endpoints exist for ops teams to trigger checks or adjust intervals on the fly.
- KPI/reporting views reuse the same service methods to produce summaries (pending counts, at-risk orders, loyalty projections, fee calculations), so business logic stays centralized.

### Observability & Operational Controls
- Logging is loud by design (info/error with contextual details) so you can cite how issues are traced. Pair that with `/api/v1/health` and `/api/v1/docs` to show both machine and human-friendly diagnostics.
- Notifications cover login/logout, auto-cancel events, session cleanup, and shift summaries. This proves the system doesn’t just store data—it actively nudges operators.
- Long-running jobs (auto-cancel, session cleanup) expose management endpoints that let you start, stop, or reconfigure schedulers without redeploying—a strong talking point when asked about maintainability.

## Data Modeling & Relationships
- **Document references (normalized links):** Collections keep relationships lightweight by storing IDs instead of embedding entire documents. Examples include `online_transactions.customer_id → customers._id`, order items referencing `products._id`, and `session_logs.user_id → users._id`. This keeps frequently updated entities (customers, products) authoritative in one place while downstream collections simply point to them.
- **Embedded subdocuments (denormalized detail):** Where the history must travel with the parent entity, we embed arrays such as `status_history`, `payment_attempts`, `order_items`, notification metadata, and stock adjustments. This mix lets us answer “what happened to _this_ order?” without joining multiple collections.
- **One-to-many via categorization:** Products store `category_id`/`subcategory_name`, suppliers attach `branch_id`, and promotions list `product_ids`, giving us natural groupings for dashboard filters and aggregation pipelines (e.g., sales by category).
- **Temporal relationships:** Session logs, stock history, and loyalty point ledgers store timestamps plus references, enabling aggregation pipelines (`$group`, `$match`, `$sort`) that reconstruct user activity or inventory movement windows.
- **Identifier strategy:** Humans interact with prefixed sequential IDs (`SESS-00042`, `ORDER-2024-0001`) while Mongo maintains ObjectIds internally. This dual-ID approach satisfies both database efficiency and business readability during audits or customer support calls.

## Object-Oriented & Design Principles
- **Encapsulation:** Each service class (auth, products, batches, sessions, online transactions) hides raw Mongo queries behind intention-revealing methods (`create_online_order`, `log_login`, `validate_order_stock`). Views never touch collections directly, which makes it easier to swap implementation details without breaking controllers.
- **Composition over inheritance:** Services rarely subclass one another; instead they compose collaborators. `OnlineTransactionService` owns instances of `ProductService`, `BatchService`, and the notification client to orchestrate complex workflows. The same idea appears in session logging, which pulls in notification + email helpers instead of extending them.
- **Targeted inheritance where it helps:** On the backend, DRF view classes inherit from shared base classes such as `OnlineTransactionServiceView (APIView)` to preload dependencies and permission rules. On the frontend, layout components (e.g., `MainLayout`) wrap child routes to share navigation chrome—functionally similar to UI inheritance.
- **Abstraction layers:** Axios wrappers, composables, and serializers all act as mini-interfaces. They expose a constrained surface area (e.g., `apiProductsService.updateProduct`) and keep concrete HTTP or Mongo details hidden so the calling code focuses on intent.

## Frontend Concepts & Logic

### Application Shell & Routing
- `main.js` registers global UI assets (Bootstrap, VueDatePicker, Lucide icons), wires Pinia + router, and persists the theme at the `documentElement` level so every page honors the same dark/light setting.
- `router/index.js` builds a guarded route tree: `/login` and password flows stay public, while everything under `/` mounts `MainLayout` with a `beforeEnter` check that looks for `access_token` in `localStorage`. Meta fields control page titles and hide dev-only routes when building for production.
- Net effect: navigation state is predictable, unauthorized users get bounced back to `/login`, and the UI feels cohesive because layout + theme decisions live in one place.

### API Integration & Token Refresh Logic
- A single Axios instance handles base URLs, JSON headers, request timestamps (to avoid stale caching), and automatic Authorization headers pulled from `localStorage`.
- The response interceptor watches for `401` statuses. The first time one appears, it exchanges the stored refresh token for a new access token, retries the original call, and only redirects to `/login` if refresh fails. This keeps the UX smooth while still enforcing security.
- Logout clears both tokens regardless of API success, ensuring future requests don’t accidentally reuse invalid credentials.

### State Management, Composables & Validation
- Domain-specific composables (e.g., `useProducts`, `useCustomers`, `useSuppliers`) share reactive arrays, filters, loading flags, and reusable CRUD helpers. This pattern prevents duplicated fetch logic across pages and keeps computed data (filtered lists, stats, etc.) in one place.
- Validation flows typically run client-side checks (e.g., SKU uniqueness via `checkSkuExists`) before calling the API, then rely on backend responses to reconcile truth. Errors propagate through shared `error` refs and trigger toast messages so users see immediate feedback.
- Bulk operations (import/export, mass delete, category moves) follow a common pattern: set a dedicated loading flag, call the service, optimistically update local arrays, and emit toasts summarizing success/failure counts.

### UX & Feedback Patterns
- Toast notifications, skeleton loaders, and explicit `loading/deleteLoading/bulkDeleteLoading` flags keep users informed during long-running tasks such as CSV imports or batch restocks.
- Theme persistence and Bootstrap utility classes make the dashboard feel consistent; router meta titles ensure browser tabs read “Page - PANN POS,” which is useful for demos and user orientation.
- Form interactions often pair Vue’s reactivity (v-model) with computed hints (e.g., low-stock warnings), demonstrating that business rules are visible in the UI, not just the backend.

## Integration & Deployment Mindset
- Backend `.env`: `MONGODB_URI` (Atlas), `MONGODB_DATABASE`, JWT secrets, debug flag, and other timers. Frontend `.env`: `VITE_API_BASE_URL`. No secrets are hard-coded in the repo.
- Local loop: `python manage.py runserver` for API + schedulers, `npm run dev` for Vite server. Production: `npm run build` for Netlify, Render handles Django with Gunicorn/Uvicorn.
- Health checks: `/api/v1/health/` for automated probes, `/api/v1/docs/` for human verification of endpoints. README includes a Mongo connection snippet so teammates can validate credentials before the defense.
- Testing strategy: selective Django test modules (notifications, services) plus Vitest for Vue components; manual smoke testing (login, dashboards, online order creation, auto-cancel) remains essential before demo day.
- Backups (`backend/backups/`, `categories_backup_*.json`) provide sample data snapshots for quick reseeding if the Atlas dataset changes.

## Defense-Ready Talking Points & Likely Questions
1. **Connectivity resilience:** Describe how the `DatabaseManager` validates the Atlas connection, reuses a single client for all services, and centralizes retry/error messaging so controllers stay simple even if the database hiccups.
2. **Session integrity:** Outline how sequential session IDs, forced logout of overlapping sessions, and logout duration tracking keep KPIs honest and support audit trails.
3. **Order throughput:** Walk through the online-order state machine, the automated expiry checks, and how FIFO batch adjustments prevent ghost stock after cancellations.
4. **Token lifecycle:** Describe the client-side refresh interceptor plus server-side blacklist, showing that both UX and security are accounted for.
5. **Inventory accuracy:** Highlight SKU validation, stock history tracking, and batch-aware restocks/sales to show deterministic inventory math.
6. **Data portability/compliance:** Mention the CSV/Excel import-export endpoints and how the frontend turns responses into downloadable files for audits or mass updates.

## Final Week Checklist (Conceptual)
- ✅ Double-check `.env` secrets, Mongo URIs, and API base URLs on both tiers before every rehearsal.
- ✅ Spin up backend + frontend locally, then walk through the golden path: admin login, dashboard loading, product CRUD, online order creation, auto-cancel trigger, logout.
- ✅ Capture fresh screenshots or screen recordings of `/api/v1/health`, `/api/v1/docs`, and key dashboards for backup during the defense.
- ✅ Query the auto-cancellation status endpoint to confirm the scheduler is running and to gather real metrics to quote.
- ✅ Run at least one CSV export/import cycle (products or customers) so you can demonstrate data migration live or answer “what if we need to bulk update?” on the spot.
- ✅ Re-read the troubleshooting section (database auth issues, CORS, port conflicts) so you can respond confidently if judges probe failure scenarios.

_Tip: treat each section above as a flash card—state the concept, mention the logic that enforces it, and keep a mental pointer to the file or endpoint in case the panel asks for evidence._

