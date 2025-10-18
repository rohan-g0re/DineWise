# DineWise MVP — Ultra‑Granular 15‑Minute Task Plan (React + FastAPI)

> Goal: Build a lean MVP that matches the feature list and your idea dump. No Redis, no over‑engineering. **Supabase Postgres (dev = prod) with Alembic migrations**. Firebase Auth on the web, FastAPI verifies tokens. Yelp Fusion for data; seed/cached records for boroughs to limit API calls.

---

## 0) Groundwork & Repo Scaffolding

* [x] **0.1 Create GitHub repo** `dinewise-mvp` with two folders: `/frontend`, `/backend`.
* [x] **0.2 Add root files**: `README.md`, `.gitignore` (Node+Python), `LICENSE` (MIT).
* [x] **0.3 Add a one‑page vision** in README (1 paragraph problem, 1 paragraph solution, 6 bullets of features).
* [x] **0.4 Add architecture sketch** (ASCII diagram in README for now: Browser → React → FastAPI → Supabase Postgres; Yelp Fusion).
* [x] **0.5 Create a task checklist** section in README; link to this doc for detailed tasks.
* [x] **0.6 Create `/docs/`** folder; add `data_model.md` (will fill later) and `api_contract.md` (will fill later).
* [x] **0.7 Make a `.env.template`** at repo root with placeholders: `YELP_API_KEY`, `FIREBASE_*`, `BACKEND_BASE_URL`, `FRONTEND_BASE_URL`, `JWT_AUDIENCE` (if needed), `GOOGLE_PROJECT_ID`.
* [x] **0.8 Decide seed locations**: `MAN`, `BK`, `QN`, `BX`, `SI` (Manhattan, Brooklyn, Queens, Bronx, Staten Island). Add to README.

---

## 0.9) Supabase Postgres Setup (dev=prod)

* [x] **0.9.1 Create Supabase project** (closest region).
* [x] **0.9.2 Copy pooled SQLAlchemy connection string** from Settings → Database.
* [x] **0.9.3 Ensure SSL**: verify `?sslmode=require` in the URL (append if missing).
* [x] **0.9.4 (Optional) Create restricted DB role** in SQL Editor:

```
CREATE ROLE app_user WITH LOGIN PASSWORD 'change_me_strong';
GRANT USAGE ON SCHEMA public TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_user;
```

* [x] **0.9.5 Build DATABASE_URL** using `app_user` (or the default user) with `sslmode=require`.
* [x] **0.9.6 Create `/backend/.env`** with `DATABASE_URL=...`, `YELP_API_KEY=...`, Firebase values.
* [x] **0.9.7 Duplicate to `/backend/.env.example`** with placeholders for teammates.
* [x] **0.9.8 Install DB deps**: `pip install sqlmodel sqlalchemy psycopg[binary] alembic`.
* [x] **0.9.9 Init Alembic Created**: `alembic init alembic`; set `sqlalchemy.url = %(DATABASE_URL)s` in `alembic.ini`.
* [x] **0.9.10 Add DB ping script** `/backend/scripts/db_ping.py` that opens a session and runs `SELECT 1`.

---

## 1) Backend: Project Skeleton (FastAPI)

* [x] **1.1 Create venv** in `/backend` (`python -m venv .venv`), activate, `pip install fastapi uvicorn[standard] python-dotenv pydantic-settings`.
* [x] **1.2 Create structure**:

```
/backend
  /app
    __init__.py
    main.py
    core/config.py
    core/deps.py
    routers/__init__.py
    routers/health.py
```

* [x] **1.3 Implement `core/config.py`**: load env via `pydantic-settings`; expose `settings` (origins, ports, Yelp key, Firebase project id, etc.).
* [x] **1.4 Implement `routers/health.py`**: `GET /health` → `{status:"ok"}`.
* [x] **1.5 Add CORS middleware** in `main.py`: allow `http://localhost:5173`.
* [x] **1.6 Run server**: `uvicorn app.main:app --reload`; hit `/health` in browser.
* [x] **1.7 Freeze deps**: create `requirements.txt` (use `pip freeze > requirements.txt`).

---

## 2) Backend: Database (Supabase Postgres) & Models (SQLModel + Alembic)

* [x] **2.1 Create `app/db.py`**

  * [x] 2.1.1 Read `DATABASE_URL` from env.
  * [x] 2.1.2 `engine = create_engine(DATABASE_URL, pool_pre_ping=True)`.
  * [x] 2.1.3 `SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)`.
  * [x] 2.1.4 `get_db()` dependency (yield session; close in `finally`).


* [x] **2.2 Create `app/models.py`** (with `SQLMODEL_METADATA = SQLModel.metadata`)

  * [x] 2.2.1 `User(id PK, email UNIQUE, full_name, firebase_uid, created_at TIMESTAMP DEFAULT now())`.
  * [x] 2.2.2 `RestaurantCache(id PK, yelp_id UNIQUE, name, location_code, lat, lng, price, rating, review_count, categories JSON, phone, address, provider, last_fetched_at TIMESTAMP)`.
  * [x] 2.2.3 `Wishlist(id PK, user_id FK→User.id, yelp_id, UNIQUE(user_id, yelp_id))`.
  * [x] 2.2.4 `Review(id PK, user_id FK, yelp_id, rating SMALLINT, text TEXT, created_at TIMESTAMP DEFAULT now())`.
  * [x] 2.2.5 `UserRestaurantFlags(id PK, user_id FK, yelp_id, visited BOOL DEFAULT FALSE, promo_opt_in BOOL DEFAULT FALSE, updated_at TIMESTAMP DEFAULT now())`.

* [x] **2.3 Create `app/schemas.py`**: request/response Pydantic models mirroring columns (no ORM leakage to FE).
* [x] **2.4 Wire Alembic**: in `alembic/env.py` set `target_metadata = SQLMODEL_METADATA`.
* [x] **2.5 First migration**: `alembic revision --autogenerate -m "init"` → review script → `alembic upgrade head`.
* [x] **2.6 Verify tables** in Supabase Table Editor; check PKs, UNIQUEs, and data types.
* [x] **2.7 Helpful indexes**: add on `RestaurantCache(location_code)`, `(rating)`, `(review_count)`.
* [x] **2.8 Update `/docs/data_model.md`** with final columns + constraints.

---

## 3) Backend: Firebase Auth Verification

* [x] **3.1 In Firebase console**: create project, enable **Email/Password** auth; create web app; copy web config.
* [x] **3.2 Save web config** to `/frontend/.env.local` placeholders (will fill later).
* [x] **3.3 Backend install**: `pip install google-auth google-auth-oauthlib google-auth-httplib2`.
* [x] **3.4 Create `app/auth/firebase.py`**: utility to verify Firebase ID token using Google certs (`google.oauth2.id_token.verify_firebase_token`).
* [x] **3.5 Create `app/auth/deps.py`**: FastAPI dependency `get_current_user()` → reads `Authorization: Bearer <id_token>`, verifies, upserts user by `email` if new.
* [x] **3.6 Add a protected test route** `GET /auth/me` returning `{email, full_name}` for a verified token.
* [x] **3.7 Document header usage** in `/docs/api_contract.md` (Authorization bearer).

---

## 4) Backend: Yelp Fusion Client

* [ ] **4.1 Install**: `pip install httpx`.
* [ ] **4.2 Create `app/clients/yelp.py`** with async httpx client, base headers (Authorization: `Bearer <YELP_API_KEY>` from settings).
* [ ] **4.3 Implement `search_businesses(term, location, price, rating, limit, offset)`**; map safe params only.
* [ ] **4.4 Implement `search_nearby(lat, lng, radius, categories, price, limit)`**.
* [ ] **4.5 Implement `get_business(id)`** and `get_reviews(id)` (up to the API’s limits).
* [ ] **4.6 Add thin DTO mappers** to `schemas.py`: `RestaurantSummary`, `RestaurantDetail`, `YelpReview`.
* [ ] **4.7 Handle 429/400**: raise typed exceptions with helpful messages.

---

## 5) Backend: Seed Jobs for Boroughs (limit API calls)

* [ ] **5.1 Create `app/seed/boroughs.py`**: hardcode 5 borough names → Yelp location string.
* [ ] **5.2 Implement `fetch_top_for_location(location_code, n=100)`** using `search_businesses()`; pick `term="restaurants"`.
* [ ] **5.3 Map fields into `RestaurantCache`** and upsert by `yelp_id`.
* [ ] **5.4 Add CLI script** `python -m app.seed.boroughs --limit 100` to seed all 5 boroughs.
* [ ] **5.5 Add `last_fetched_at` timestamp update on upsert.**
* [ ] **5.6 Create `/docs/seeding.md`**: steps to run seeding and what fields we store (minimal, link to Yelp page in UI).

---

## 6) Backend: Search & Details Routers (extra‑granular)

* [ ] **6.1 Create `app/routers/search.py`** and mount under `/api` in `main.py`.

* [ ] **6.2 Define query parser**: accept `q, location, cuisine, price (comma list), rating_min, limit, offset`.

* [ ] **6.3 Normalizers**: trim strings; clamp `limit` (e.g., 50 max); default `offset=0`.

* [ ] **6.4 DB path helper**: function `query_db_search(params)` that builds SQLModel query with filters.

* [ ] **6.5 Yelp path helper**: function `call_yelp_search(params)` that maps params → Yelp API and returns normalized items.

* [ ] **6.6 Location switch**: if `location in {MAN,BK,QN,BX,SI}` use DB path else Yelp path.

* [ ] **6.7 Response mapper**: convert both paths to a unified `RestaurantSummary` list.

* [ ] **6.8 Error handling**: catch Yelp 429/400 → return `detail, code` for FE banner.

* [ ] **6.9 Unit tests**: mock DB & mock Yelp; verify param parsing and mapping.

* [ ] **6.10 Create `app/routers/restaurants.py`** with `GET /restaurants/{yelp_id}`.

* [ ] **6.11 Cache check**: quick read from `RestaurantCache` by `yelp_id`.

* [ ] **6.12 Yelp enrich**: call `get_business(yelp_id)`; merge phone, hours, photos, url.

* [ ] **6.13 (Optional) Yelp reviews**: call and cap to 3.

* [ ] **6.14 Response mapper**: return `RestaurantDetail`.

* [ ] **6.15 Tests**: fixture for a cached business; fixture for Yelp detail; ensure merge works.

---

## 7) Backend: Wishlist & Reviews Routers (Auth‑gated)

* [ ] **7.1 Create `app/routers/wishlist.py`**: requires `get_current_user`.
* [ ] **7.2 `POST /wishlist`** body: `{yelp_id}` → upsert record for user; return status.
* [ ] **7.3 `GET /wishlist`** → list by user; join with `RestaurantCache` if present (else return minimal with `yelp_id`).
* [ ] **7.4 `DELETE /wishlist/{yelp_id}`** → delete if owned by user.
* [ ] **7.5 Create `app/routers/reviews.py`**: requires `get_current_user`.
* [ ] **7.6 `POST /reviews`** body: `{yelp_id, rating (1‑5), text (≤ 1,000 chars)}` → insert.
* [ ] **7.7 `GET /reviews?yelp_id=`** → list reviews (our DB) for a business.
* [ ] **7.8 `GET /users/me/reviews`** → list reviews authored by current user.
* [ ] **7.9 Add validation**: rating bounds, text length; normalize newline handling.

---

## 8) Backend: User Flags for Events/Visits (Future‑proof)

* [ ] **8.1 Create `app/routers/flags.py`** (auth‑gated).
* [ ] **8.2 `PUT /flags/{yelp_id}`** body: `{visited?: bool, promo_opt_in?: bool}` → upsert `UserRestaurantFlags` row.
* [ ] **8.3 `GET /flags`** → list all flags for the user.
* [ ] **8.4 Add indexes** on `(user_id, yelp_id)`.
* [ ] **8.5 Update `/docs/data_model.md`** with use cases (notifications later).

---

## 9) Frontend: Vite + TS + Tailwind + Router (extra‑granular)

* [x] **9.1 Scaffold app**: `npm create vite@latest frontend -- --template react-ts`.
* [x] **9.2 Install deps**: `cd frontend && npm i`.
* [x] **9.3 Run dev server**: `npm run dev` → open `http://localhost:5173`.
* [x] **9.4 Install Tailwind**: `npm i -D tailwindcss postcss autoprefixer`.
* [x] **9.5 Init Tailwind**: `npx tailwindcss init -p`.
* [x] **9.6 Configure content globs** in `tailwind.config.js`.
* [x] **9.7 Add base CSS** imports to `src/index.css`.
* [x] **9.8 Install Router**: `npm i react-router-dom`.
* [x] **9.9 Create routes**: `/login`, `/`, `/r/:id`, `/locator`, `/me` in `src/main.tsx`.
* [x] **9.10 Create `Layout`** component with `<Header>` + `<Outlet>`.
* [x] **9.11 Header nav**: links to Home, Locator, Me, Login.
* [x] **9.12 Basic container styles**: max‑width, padding, responsive grid utilities.

---

## 10) Frontend: Firebase Auth (Email/Password)

* [ ] **10.1 `npm i firebase`**; create `src/lib/firebase.ts` with config from Firebase console.
* [ ] **10.2 Implement `auth.ts` helpers**: `signUp(email, pwd, fullName)`, `signIn(email, pwd)`, `signOut()`, `getIdToken()`.
* [ ] **10.3 Create `AuthContext`** to hold current user and idToken (auto refresh on change).
* [ ] **10.4 Build `/login` page** with tabs: Login / Signup.
* [ ] **10.5 On success**: store idToken in memory; (optionally) cache in localStorage for reload.
* [ ] **10.6 Add `ProtectedRoute`** wrapper that checks user; redirect to `/login` if missing.
* [ ] **10.7 Add header buttons**: show “Login” if no user; show email + “Logout” if authed.

---

## 11) Frontend: API Client & Query Layer

* [ ] **11.1 `npm i @tanstack/react-query axios`**; create `src/lib/api.ts` axios with baseURL from `VITE_API_BASE_URL`.
* [ ] **11.2 Add axios interceptor** to inject `Authorization: Bearer <idToken>` when present.
* [ ] **11.3 Wrap app** in `<QueryClientProvider>`; add React Query Devtools in dev.
* [ ] **11.4 Create hooks**:

  * `useSearch(params)` → calls `/api/search`.
  * `useRestaurant(id)` → calls `/api/restaurants/:id`.
  * `useMyWishlist()` / `useAddToWishlist()` / `useRemoveFromWishlist()`.
  * `usePostReview()` / `useReviews(yelp_id)`.
  * `useFlags()` / `useUpsertFlag()`.

---

## 12) Frontend: Home (Search & Browse) — micro tasks

* [ ] **12.1 Add Location control (dropdown)**: MAN/BK/QN/BX/SI + `Custom…` option.
* [ ] **12.2 Add Custom Location input**: show text box only if `Custom…` picked.
* [ ] **12.3 Add Query (text input)** with placeholder "pizza, ramen...".
* [ ] **12.4 Add Cuisine (text input)** (optional).
* [ ] **12.5 Add Price (checkboxes)**: $, $$, $$$, $$$$.
* [ ] **12.6 Add Min Rating (range 1–5)** with numeric display.
* [ ] **12.7 Build `useSearchParams` hook** to sync form ↔ URL.
* [ ] **12.8 Wire `useSearch` query**: call `/api/search` with params from URL.
* [ ] **12.9 Show loading skeleton cards** (6 placeholders).
* [ ] **12.10 Show error banner** using standardized `detail`.
* [ ] **12.11 Render responsive card grid** (1–2 mobile, 3–5 desktop).
* [ ] **12.12 Card fields**: name, rating, price, categories snippet.
* [ ] **12.13 Card buttons**: “View” (link to `/r/:id`), “Wishlist”.
* [ ] **12.14 Guard Wishlist click**: if not authed, open login prompt.
* [ ] **12.15 Empty state**: “No results” with hint to adjust filters.

---

## 13) Frontend: Restaurant Details Page — micro tasks

* [ ] **13.1 Route setup**: read `yelp_id` from URL params.
* [ ] **13.2 Data fetch**: `useRestaurant(yelp_id)`; show skeleton while loading.
* [ ] **13.3 Header block**: name, rating, price, categories.
* [ ] **13.4 Contact block**: phone (click‑to‑copy), address (copy), hours (if present).
* [ ] **13.5 Photo strip**: small gallery from Yelp detail.
* [ ] **13.6 Yelp link button**: open new tab; aria‑label clearly states leaving site.
* [ ] **13.7 Wishlist button**: optimistic toggle; revert on error.
* [ ] **13.8 Reviews (Yelp)**: show up to 3 with “Powered by Yelp”.
* [ ] **13.9 Reviews (Community)**: list our DB reviews.
* [ ] **13.10 Review form** (authed): rating select + textarea + submit.
* [ ] **13.11 After submit**: optimistic append; clear form; toast success.
* [ ] **13.12 Empty states** for both review sections.

---

## 14) Frontend: Store Locator (Map + Browse Nearby) — micro tasks

* [ ] **14.1 Install map libs**: `npm i leaflet react-leaflet`; import Leaflet CSS.
* [ ] **14.2 Map container**: full‑width, fixed height (e.g., 60vh).
* [ ] **14.3 Geolocate user**: `navigator.geolocation.getCurrentPosition` with error fallback to NYC center.
* [ ] **14.4 Backend `/api/nearby` call** with lat/lng from geolocation.
* [ ] **14.5 NYC bbox branch**: DB nearest; else Yelp nearby.
* [ ] **14.6 Render markers**: business markers + “you are here” marker.
* [ ] **14.7 Marker popup**: name, rating, link to details, wishlist button.
* [ ] **14.8 “Browse Nearby” button**: navigate to `/` with lat/lng set as filters.
* [ ] **14.9 Loading + error UIs** on the map panel.

---

## 15) Frontend: Me (Wishlist & My Reviews) — micro tasks

* [ ] **15.1 Route guard**: redirect to `/login` if no user.
* [ ] **15.2 Load wishlist**: `useMyWishlist()`; show skeleton cards.
* [ ] **15.3 Wishlist UI**: list cards with remove button (optimistic remove).
* [ ] **15.4 Load my reviews**: `GET /users/me/reviews` via hook.
* [ ] **15.5 Reviews table**: columns: date, name (from cache if available), rating, excerpt.
* [ ] **15.6 Flags panel**: per wishlist item — checkboxes for `Visited` and `Promo updates`.
* [ ] **15.7 Save flags**: call `/flags` upsert; toast on success.
* [ ] **15.8 Empty states** for both lists.

---

## 16) Error Handling, States, and Guardrails

* [ ] **16.1 Standardize backend errors** to `{detail, code}`.
* [ ] **16.2 Frontend `extractApiError(e)`** util to read detail/code and show toasts.
* [ ] **16.3 Unauthed actions** show gentle prompt to login; preserve action intent if possible.
* [ ] **16.4 “Rate limit” UX**: if backend surfaces Yelp 429 → show banner suggesting narrower filters.
* [ ] **16.5 404 Page** with “Back to Home” button.
* [ ] **16.6 Global Error Boundary** to catch render errors.

---

## 17) Testing (Lean but Real)

* [ ] **17.1 Backend unit tests**: `pytest` for `/health`, `/auth/me` (mock token), wishlist CRUD, reviews.
* [ ] **17.2 Yelp client tests**: mock httpx to return fixtures; verify mapping and 429 handling.
* [ ] **17.3 Frontend component tests**: render Home, submit search, mock results, card renders.
* [ ] **17.4 Frontend auth test**: login form calls Firebase mock; header updates.
* [ ] **17.5 E2E Happy Path (manual script)**: login → search → details → wishlist add → `/me` check → post review.

---

## 18) Developer Experience

* [ ] **18.1 Scripts**: FE—`dev`, `build`, `test`; BE—`dev` (uvicorn), `test` (pytest), `seed` (boroughs), `fmt` (black/isort).
* [ ] **18.2 Prettier & ESLint** for FE; Black & isort for BE; add config files.
* [ ] **18.3 Concurrent dev**: run FE on 5173 and BE on 8000; document CORS origins.
* [ ] **18.4 Example `.env.local` files** for both apps; never commit real keys.

---

## 19) Demo Data & Screenshots

* [ ] **19.1 Run seeding** for 5 boroughs (100 each) so Home works without calling Yelp for NYC locations.
* [ ] **19.2 Create test user** and save creds in `/docs/demo.md`.
* [ ] **19.3 Take 3 screenshots**: Home (search results), Details (review form), Me (wishlist & flags).

---

## 20) Midterm Slides (Lean)

* [ ] **20.1 Slide 1**: Problem & audience.
* [ ] **20.2 Slide 2**: Architecture diagram (React, FastAPI, Supabase Postgres, Yelp, Firebase).
* [ ] **20.3 Slide 3**: Data model mini‑ERD (5 tables).
* [ ] **20.4 Slide 4**: API table (path, method, what it returns).
* [ ] **20.5 Slide 5**: Demo script steps (5 bullets).
* [ ] **20.6 Slide 6**: What’s next (UI polish, accessibility, pagination, performance).

---

## 21) Post‑Midterm Stretch (Optional)

* [ ] **21.1 Pagination** for search results (both DB and Yelp paths).
* [ ] **21.2 Accessibility**: keyboard navigation, focus rings, alt text.
* [ ] **21.3 UX polish**: nicer cards, skeletons, empty states, toasts.
* [ ] **21.4 Map clustering** for many points on locator.
* [ ] **21.5 Move DB to Postgres** (Neon) if needed; add migrations.

---

## Acceptance Criteria Summary (MVP)

* [ ] Can **sign up / log in** with Firebase (email/password) and call **/auth/me**.
* [ ] Can **search** with borough locations via DB and **other locations** via Yelp.
* [ ] Can open a **restaurant detail** page with Yelp link and show Yelp+community reviews.
* [ ] Can **add/remove wishlist** from cards, details, and locator popups.
* [ ] Can **post a review** (authed), and it appears immediately.
* [ ] Can use the **locator** to see nearby restaurants and click through to details.
* [ ] Can set **visited/promo** flags (DB only, for future notifications).
* [ ] Midterm **demo** runs locally with seeded NYC data and at least one happy path end‑to‑end.