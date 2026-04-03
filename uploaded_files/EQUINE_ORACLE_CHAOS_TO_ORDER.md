# Equine Oracle — Chaos to Order
## Complete Asset Inventory & Consolidation Plan

**The Brutal Truth**: You have 5+ working sites, 16+ repositories, and enough documentation to fill a library—but no single source of truth. This doc fixes that.

---

## Working Sites Inventory (Verified Live)

| URL | Status | Purpose | Quality | Action |
|-----|--------|---------|---------|--------|
| `horseraceapp-8ezwxkzc.manus.space/live-races` | ✅ LIVE | Live races feed with predictions | Working UI, shows races | **PRIMARY DEMO** |
| `equinesum-4upakx6a.manus.space` | ✅ LIVE | Project summary/ecosystem overview | Marketing page, 85.8% accuracy claim | **MARKETING SITE** |
| `horserace-rasnmx5k.manus.space` | ✅ LIVE | Oracle Engine landing page | Basic landing, needs auth | **ARCHIVE OR REDIRECT** |
| `gkukhkxgn.manus.space` | ✅ LIVE | Admin dashboard + predictor | Full UI, logged in as John | **PRIMARY ADMIN** |
| `equineoro-q9pbwwx2d.manus.space` | ✅ LIVE | Feature overview + subscriptions | Good marketing page | **CONSOLIDATE INTO MAIN** |

**Decision**: Pick ONE site as your primary. I recommend `gkukhkxgn.manus.space` (admin dashboard) because it has:
- Full prediction interface
- Accuracy tracking (currently empty—needs data)
- CSV upload for batch predictions
- User logged in (low.k3yltd@gmail.com)

---

## Repository Chaos

### GitHub Repos (Active)

| Repo | Last Commit | Status | Contains |
|------|-------------|--------|----------|
| `equine_oracle_admin` | Jan 21, 2026 | ✅ ACTIVE | Admin panel, Python ML, God-Tier ensemble |
| `MVP.-1` | Jan 26, 2026 | ✅ ACTIVE | Full-stack, Stripe integration |

### The Problem
You're maintaining TWO separate codebases with overlapping functionality. This is killing your velocity.

### The Solution
**CONSOLIDATE INTO ONE REPO**

1. Keep `equine_oracle_admin` as primary (more recent ML work)
2. Copy Stripe/subscription code from `MVP.-1`
3. Archive `MVP.-1` with a redirect note

---

## What's Actually Working (vs. What's Broken)

### ✅ WORKING
- Live race feed (`horseraceapp-8ezwxkzc.manus.space/live-races`)
- Prediction UI with horse rankings
- Admin dashboard (`gkukhkxgn.manus.space`)
- CSV upload for batch predictions
- User authentication (logged in as John)
- Model retraining interface

### ❌ BROKEN / EMPTY
- Accuracy tracking shows 0% (no race outcomes recorded)
- Polling service is STOPPED (0 predictions, 0 success)
- No actual prediction data flowing through the system
- No payment/subscription flow connected

### 🔧 NEEDS IMMEDIATE FIX
1. **Start the polling service** — It's stopped, which means no live predictions
2. **Record race outcomes** — Accuracy tracking is empty because results aren't being saved
3. **Connect payments** — Stripe is configured but not integrated into the flow

---

## The Real Gap to Exit

You're at **~60% complete**, not 70-80%. Here's why:

| Component | Status | What's Missing |
|-----------|--------|----------------|
| ML Model | ✅ Done | 0.953 NDCG working |
| Prediction API | ✅ Done | Endpoint functional |
| Frontend UI | ✅ Done | Dashboard looks good |
| Live Race Feed | ✅ Done | Showing real races |
| **Accuracy Tracking** | ❌ Broken | No outcomes recorded = no proof |
| **Polling Service** | ❌ Stopped | Not generating predictions |
| **Payments** | ❌ Disconnected | Stripe not wired to UI |
| **Beta Users** | ❌ None | No one using it yet |

**The blocker**: You have a beautiful dashboard with no data. Buyers need to see:
- "We've made X predictions"
- "Our accuracy is Y%"
- "Z users are paying"

Currently: 0, 0%, 0 users.

---

## 7-Day Emergency Fix Plan

### Day 1: Start the Polling Service
1. Go to `gkukhkxgn.manus.space`
2. Navigate to Polling Service Manager
3. Click **Start Service**
4. Verify it's running (check Total Predictions > 0)

### Day 2: Record Race Outcomes
1. After races complete, manually enter results
2. Or better: automate result collection from Tab.co.nz
3. Watch accuracy metrics populate

### Day 3: Connect Stripe
1. Copy Stripe code from `MVP.-1` repo
2. Add subscription buttons to `gkukhkxgn` dashboard
3. Test payment flow

### Day 4: Get 5 Beta Users
1. Post in NZ racing forums
2. Offer free access in exchange for feedback
3. Track their usage in the dashboard

### Day 5: Generate Demo Data
1. Run predictions on last 50 NZ races
2. Record actual outcomes
3. Calculate accuracy metrics

### Day 6: Create Pitch Deck
1. Use accuracy data from Day 5
2. Screenshot the working dashboard
3. Write one-page overview

### Day 7: Start Outreach
1. Email TAB NZ
2. Email 5 Australian syndicates
3. Post on LinkedIn

---

## Site Consolidation Plan

### Primary Site: `gkukhkxgn.manus.space`
**What it has**:
- Full prediction interface
- Admin dashboard
- CSV upload
- User auth (John logged in)
- Polling service controls
- Accuracy tracking (needs data)

**What to add**:
- Marketing copy from `equinesum` and `equineoro`
- Stripe payment integration
- Public landing page

### Archive These
- `horserace-rasnmx5k.manus.space` — Basic landing, redirect to primary
- `equinesum-4upakx6a.manus.space` — Marketing page, merge content into primary
- `equineoro-q9pbwwx2d.manus.space` — Feature page, merge content into primary

### Keep as Separate
- `horseraceapp-8ezwxkzc.manus.space/live-races` — Live races feed (good demo URL)

---

## File Cleanup Strategy

### On Your Phone (The Chaos)
You mentioned "so many files and variants on my phone"—here's how to organize:

1. **Create folders**:
   - `Equine Oracle / 01-ACTIVE` — Current working files
   - `Equine Oracle / 02-ARCHIVE` — Old versions, backups
   - `Equine Oracle / 03-DOCUMENTATION` — Business plans, pitch decks
   - `Equine Oracle / 04-ASSETS` — Logos, screenshots, videos

2. **Delete duplicates**:
   - Keep only the latest version of each file
   - If unsure, move to ARCHIVE instead of deleting

3. **Cloud sync**:
   - Use Google Drive or Dropbox
   - Sync everything so you can access from laptop

---

## GitHub Cleanup

### Step 1: Pick One Repo
**Keep**: `equine_oracle_admin`
**Archive**: `MVP.-1` (add note redirecting to main repo)

### Step 2: Organize `equine_oracle_admin`
```
equine_oracle_admin/
├── README.md (one page, current status)
├── docs/
│   ├── BUSINESS_PLAN.md
│   ├── PITCH_DECK.pdf
│   └── API_REFERENCE.md
├── src/
│   ├── client/ (frontend)
│   ├── server/ (backend + ML)
│   └── shared/
├── models/ (trained ML models)
├── scripts/ (deployment, utilities)
└── tests/
```

### Step 3: Delete Old Branches
- Keep: `main`, `develop`
- Delete: All feature branches older than 30 days

---

## Documentation Consolidation

### Keep These (Current)
1. `README.md` — One page, what's working now
2. `API_REFERENCE.md` — For developers/buyers
3. `BUSINESS_PLAN.md` — For investors

### Archive These (Outdated)
- All versioned docs (v1, v2, etc.)
- Old implementation guides
- Duplicate strategy documents

### Create These (Missing)
1. `DEMO_SCRIPT.md` — How to demo the product
2. `BUYER_ONE_PAGER.pdf` — Single page for outreach
3. `TECHNICAL_OVERVIEW.md` — For due diligence

---

## The Single Source of Truth

### One Dashboard to Rule Them All
**URL**: `gkukhkxgn.manus.space`

**Sections**:
1. **Live Predictor** — Make predictions (✅ exists)
2. **Race Feed** — Live races (✅ exists)
3. **Accuracy Tracking** — Performance metrics (⚠️ empty)
4. **Admin Panel** — Polling service, retraining (✅ exists)
5. **Subscriptions** — Payments (❌ missing)
6. **Documentation** — Help, API docs (❌ missing)

### One Repo to Rule Them All
**Repo**: `github.com/low-k3YLTD/equine_oracle_admin`

**Branches**:
- `main` — Production
- `develop` — Working branch

**Everything else gets archived.**

---

## Immediate Action Items (Do Today)

### 1. Start the Polling Service
```
Go to: gkukhkxgn.manus.space
Click: Polling Service Manager
Click: Start Service
Verify: Total Predictions > 0
```

### 2. Test a Prediction
```
Go to: Live Predictor
Enter: Any horse name, track, distance
Click: Generate Prediction
Verify: You get a prediction result
```

### 3. Record a Race Outcome
```
Find: A race that already ran
Enter: Actual winner in accuracy tracking
Verify: Accuracy % updates
```

### 4. Clean Up Your Phone
```
Create: 4 folders (ACTIVE, ARCHIVE, DOCUMENTATION, ASSETS)
Move: All files into appropriate folders
Delete: Obvious duplicates
```

---

## The Exit Path (Revised)

### Original Timeline: 90 days
### Revised Timeline: 60 days (if you execute)

| Week | Focus | Deliverable |
|------|-------|-------------|
| 1 | Fix polling, record outcomes | Working system with data |
| 2 | Add payments, get 5 users | First revenue |
| 3 | Demo video, pitch deck | Investor-ready materials |
| 4 | Outreach to 20 buyers | 5 conversations |
| 5-6 | Negotiations | LOI |
| 7-8 | Due diligence | Close deal |

**Target Exit**: NZD 150,000-250,000 (lower than before because you need to prove traction faster)

---

## Bottom Line

You have the technology. You have the UI. What you DON'T have is:
1. Running predictions (polling service is stopped)
2. Recorded outcomes (accuracy tracking is empty)
3. Paying users (Stripe not connected)

**Fix these three things in the next 7 days, and you're back on track for exit.**

Don't build anything new. Don't write more docs. Just:
1. Start the service
2. Record outcomes
3. Get users

Then sell.

---

*Last Updated: January 2026*  
*Status: Execute immediately*
