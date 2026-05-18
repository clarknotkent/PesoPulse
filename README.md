<div align="center">

# PesoPulse

A small, private finance ledger for closed households — with ephemeral AI receipt scanning and Google-Sheets-style read-only sharing.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](#license)
[![Nuxt 3](https://img.shields.io/badge/Nuxt-3-00DC82?logo=nuxt.js&logoColor=white)](https://nuxt.com)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Firebase](https://img.shields.io/badge/Firebase-FFCA28?logo=firebase&logoColor=black)](https://firebase.google.com)
[![PWA](https://img.shields.io/badge/PWA-installable-5A0FC8?logo=pwa&logoColor=white)](https://web.dev/progressive-web-apps/)

</div>

---

PesoPulse is a Progressive Web App for tracking personal income and expenses across a closed group of up to 5 users.

- **Nuxt 3** PWA on the frontend
- **Python FastAPI** gateway on the backend
- **Cloud Firestore** as the system of record — never touched directly by the browser

It was originally built for a Filipino household (₱ is the default currency), but the codebase is generic enough to adapt to any single-currency context.

---

## Table of Contents

- [Why PesoPulse?](#why-pesopulse)
- [Features](#features)
- [Screenshots](#screenshots)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Quickstart](#quickstart)
- [Environment Variables](#environment-variables)
- [Project Structure](#project-structure)
- [API Reference](#api-reference)
- [Data Model](#data-model)
- [Security & Privacy](#security--privacy)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [Acknowledgments](#acknowledgments)
- [License](#license)

---

## Why PesoPulse?

Most personal-finance apps are either (a) cloud SaaS where your data leaves your control, or (b) heavyweight self-hosted suites built for double-entry accounting. PesoPulse sits between them:

- **Yours.** You bring your own Firebase project. There is no PesoPulse-the-service.
- **Tiny.** One repo, one `.env`, one `npm run dev`. The whole backend fits in ~10 files.
- **Honest.** Server stamps the timestamps. Clients cannot retro-date entries.
- **Shareable.** A spouse or accountant can view your ledger without the ability to edit it.

---

## Features

- **Authoritative timestamps.** Transaction `date` and `createdAt` are stamped by the server (Asia/Manila for the date string, UTC for `createdAt`). Pydantic schemas reject any attempt to send these from a client.
- **AI receipt scanning.** Upload a receipt photo and Gemini 2.0 Flash returns `{ merchant, total, date }`. The image bytes are processed in memory and discarded — there is no Firebase Storage bucket.
- **Hybrid categories.** Five hardcoded defaults (Food, Utilities, Transport, Allowance, Salary) merge with each user's custom Firestore-backed list at read time.
- **View-only sharing.** Grant any registered user read access to your ledger by email. Viewers see balances and transactions; any mutation returns `403`.
- **Hard user cap.** Configurable at 5 by default. Registration past the cap returns `403`.
- **Installable PWA.** Manifest, 192×192 / 512×512 icons, dark theme, mobile-first layout, offline-aware.
- **One currency, one symbol.** Every monetary value renders through `formatPHP()` — no bare numbers.

---

## Screenshots

> Add screenshots in `docs/screenshots/` and reference them here.

| Dashboard | Add Transaction | Settings |
|---|---|---|
| _(coming soon)_ | _(coming soon)_ | _(coming soon)_ |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Nuxt 3, Vue 3 Composition API (`<script setup>`), TailwindCSS |
| Backend | Python 3.11+, FastAPI, Pydantic v2 |
| Auth | Firebase Auth (client) + Firebase Admin SDK (server) |
| Database | Cloud Firestore (Native mode), accessed only via the Admin SDK |
| AI | Gemini 2.0 Flash via `google-genai` |
| PWA | `@vite-pwa/nuxt` |
| Orchestration | `concurrently`, Nuxt Nitro dev proxy |

---

## Architecture

PesoPulse uses a **single-root coupled architecture**: the repo root is the Nuxt 3 PWA, and the Python FastAPI service lives in a nested `api/` directory. One `.env`, one `npm run dev`, two processes.

```
┌─────────────────────────────────────────────────────────────┐
│  Browser (PWA)                                              │
│    ├─ Firebase Auth SDK ── sign in / sign up / ID token     │
│    └─ useApi() ─── $fetch('/api/...') with Bearer token     │
└──────────────────────────────┬──────────────────────────────┘
                               │ /api/*
                               ▼
┌─────────────────────────────────────────────────────────────┐
│  Nuxt 3 Dev Server (:3000)                                  │
│    └─ Nitro devProxy: /api/* → 127.0.0.1:8000/api/*         │
└──────────────────────────────┬──────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────┐
│  FastAPI (:8000)                                            │
│    ├─ get_current_user()        verify_id_token (Admin SDK) │
│    ├─ require_owner() / _or_viewer()                        │
│    └─ Firestore (Admin SDK) ─────────┐                      │
└──────────────────────────────────────┼──────────────────────┘
                                       ▼
                          ┌────────────────────────┐
                          │  Cloud Firestore       │
                          │  users / transactions  │
                          │  categories / sharing  │
                          └────────────────────────┘
```

**Hard constraints (enforced in review):**

- The frontend never imports Firestore. Firebase JS SDK is used only for Auth.
- Receipt images are ephemeral. No Storage bucket exists.
- All monetary UI values go through `formatPHP()`.
- Transaction `date` and `createdAt` are server-set. Clients cannot supply them.
- Firestore Security Rules deny all client access (`allow read, write: if false`). The Admin SDK bypasses rules.

---

## Quickstart

### Prerequisites

- **Node.js** 20 or newer
- **Python** 3.11 or newer (tested on 3.14)
- A **Firebase project** with Firestore (Native mode) and Email/Password Auth enabled

### 1. Install

```bash
git clone <your-fork-url> pesopulse
cd pesopulse
npm run install:all
```

`install:all` installs Node packages, runs `nuxt prepare`, creates a Python venv at `api/venv/`, and installs Python dependencies.

### 2. Add Firebase credentials

- Drop your service account key at `api/serviceAccountKey.json` (git-ignored).
- Copy `.env.example` to `.env` and fill in the values (see [Environment Variables](#environment-variables)).

### 3. Create Firestore composite indexes

The relevant queries fail with `FailedPrecondition` until each index is `Enabled`.

| Collection | Fields |
|---|---|
| `transactions` | `userId` Asc, `date` Desc |
| `sharing_permissions` | `ownerId` Asc, `viewerId` Asc |

If you skip this step, Firebase returns an error containing a direct create-link.

### 4. Publish Firestore Security Rules

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read, write: if false;
    }
  }
}
```

### 5. Run

```bash
npm run dev
```

- Nuxt: <http://localhost:3000>
- FastAPI: <http://127.0.0.1:8000> (OpenAPI docs at `/docs`)

Auto-reload is on for both.

---

## Environment Variables

A single `.env` at the project root is shared by both processes.

```env
# Frontend (Nuxt auto-maps NUXT_PUBLIC_* into runtimeConfig.public.*)
NUXT_PUBLIC_API_BASE_URL=/api
NUXT_PUBLIC_FIREBASE_API_KEY=...
NUXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
NUXT_PUBLIC_FIREBASE_PROJECT_ID=your-project-id
NUXT_PUBLIC_FIREBASE_APP_ID=1:...:web:...

# Backend
FIREBASE_SERVICE_ACCOUNT_PATH=./api/serviceAccountKey.json
GEMINI_API_KEY=...
```

The service account path is resolved relative to the project root, with a sensible fallback to `api/serviceAccountKey.json`.

---

## Project Structure

```
pesopulse/
├── api/                       Python FastAPI backend
│   ├── app/
│   │   ├── main.py            FastAPI entry, CORS, router registration
│   │   ├── config.py          Firebase Admin singleton, env loader
│   │   ├── middleware.py      Bearer token verification, owner/viewer guards
│   │   └── routes/
│   │       ├── auth.py
│   │       ├── transactions.py
│   │       ├── categories.py
│   │       ├── receipts.py    Gemini parsing — ephemeral, in-memory only
│   │       └── sharing.py
│   ├── requirements.txt
│   └── serviceAccountKey.json (git-ignored)
│
├── components/
│   └── ReceiptScanner.vue
├── composables/
│   ├── useAuth.ts             signIn / signUp / signOut / idToken
│   └── useApi.ts              get / post / put / del with Bearer header
├── middleware/
│   └── auth.ts                Route guard — redirects to /auth when signed out
├── pages/
│   ├── dashboard.vue          Balance, add / edit / delete tx, receipt scan
│   ├── auth.vue               Sign in / sign up
│   ├── settings.vue           Categories + Sharing tabs
│   └── shared/[ownerId].vue   Read-only ledger view for granted viewers
├── plugins/
│   └── firebase.client.ts     Initializes Firebase web SDK
├── utils/
│   └── currency.ts            formatPHP(amount) — ₱ formatted string
│
├── nuxt.config.ts             PWA manifest, Tailwind, /api dev proxy
├── package.json               Orchestration scripts
└── .env                       Shared frontend + backend config
```

---

## API Reference

All endpoints are prefixed with `/api` and require a Firebase ID token in the `Authorization: Bearer <token>` header.

### Auth

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET`  | `/auth/me`        | Any user | Current user profile |
| `POST` | `/auth/register`  | Any user | Create user doc; returns `403` past the user cap |

### Transactions

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET`    | `/transactions/{owner_id}`               | Owner or Viewer | List transactions, `date DESC` |
| `POST`   | `/transactions/{owner_id}`               | Owner only      | Create — server stamps `date` + `createdAt` |
| `PUT`    | `/transactions/{owner_id}/{tx_id}`       | Owner only      | Update `amount / type / category / notes` only |
| `DELETE` | `/transactions/{owner_id}/{tx_id}`       | Owner only      | Delete |

Bodies that include `date`, `createdAt`, `id`, or `userId` are rejected with `422 Unprocessable Entity` (Pydantic `extra="forbid"`).

### Categories

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET`    | `/categories/{owner_id}`             | Any user   | System defaults + custom |
| `POST`   | `/categories/{owner_id}`             | Owner only | Create custom category |
| `DELETE` | `/categories/{owner_id}/{cat_id}`    | Owner only | Delete custom category |

### Receipts

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/receipts/parse` | Any user | Multipart upload → Gemini returns `{ merchant, total, date }`. Image discarded after parse. |

### Sharing

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET`    | `/sharing/{owner_id}`              | Owner only | List viewer grants |
| `POST`   | `/sharing/{owner_id}`              | Owner only | Grant access by email |
| `DELETE` | `/sharing/{owner_id}/{perm_id}`    | Owner only | Revoke access |

### Health

| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | `{"status": "ok"}` |

Interactive docs: <http://127.0.0.1:8000/docs>.

---

## Data Model

```
users/                      doc id = Firebase Auth UID
  uid, email, name

transactions/               doc id = UUID
  id, userId, amount (float),
  type ('income' | 'expense'),
  date (YYYY-MM-DD, Asia/Manila, server-set),
  category, notes,
  createdAt (UTC ISO-8601, server-set)

categories/                 doc id = UUID
  id, userId, name, icon, type
  (system defaults live in routes/categories.py)

sharing_permissions/        doc id = UUID
  id, ownerId, viewerId, viewerEmail, grantedAt
```

---

## Security & Privacy

| Threat | Mitigation |
|---|---|
| Forged transaction `date` | Server-set; Pydantic `extra="forbid"` returns `422` |
| Forged `createdAt` | Same |
| Cross-tenant read or write | `require_owner()` / `require_owner_or_viewer()` checks the decoded token UID |
| Direct Firestore client access | Frontend never imports the Firestore SDK; rules deny all |
| Receipt image leakage | Bytes live only in request scope; no Storage bucket exists |
| User-cap bypass | `POST /auth/register` counts the `users` collection and returns `403` past the limit |
| Stale or replayed tokens | Firebase ID tokens expire (~1 h); `verify_id_token` validates signature and expiry |
| Stored secrets | `.env` and `serviceAccountKey.json` are git-ignored |

---

## Roadmap

- [ ] Transaction filter and search
- [ ] Pagination for long ledgers
- [ ] Offline PWA caching for last-known balances
- [ ] Production CORS allowlist driven by env (`CORS_ORIGINS`)
- [ ] Automated test suite (pytest + Vitest)
- [ ] CSV / JSON export
- [ ] Multi-currency support (currently single-currency by design)
- [ ] Configurable user cap

Open an issue if you want to discuss any of these — or propose your own.

---

## Contributing

Contributions are welcome and appreciated.

1. **Open an issue first** for non-trivial changes so we can align on scope.
2. **Fork** the repo and create a feature branch (`feat/your-thing`).
3. **Match the existing style.** Vue 3 `<script setup>`, TailwindCSS only, FastAPI `async def`, strict Pydantic types.
4. **Keep PRs small.** One concern per PR. Avoid unrelated refactors.
5. **Run the app** end-to-end before submitting (`npm run dev`).
6. **Open a PR** against `main` with a clear summary and screenshots for UI changes.

If you find a security issue, please **do not open a public issue**. Email the maintainer instead.

---

## Acknowledgments

- [Nuxt 3](https://nuxt.com) and the Vue ecosystem
- [FastAPI](https://fastapi.tiangolo.com) and Pydantic
- [Firebase](https://firebase.google.com) Auth and Firestore
- [Gemini API](https://ai.google.dev) for receipt parsing
- [TailwindCSS](https://tailwindcss.com)
- Everyone who tracks every centavo. You inspire this.

---

## License

Released under the [MIT License](LICENSE).

```
MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.
```
