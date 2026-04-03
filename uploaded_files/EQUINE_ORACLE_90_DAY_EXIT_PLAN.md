# Equine Oracle — 90-Day Exit Plan
## From 70% Complete to NZD 250,000 Exit

**Mission**: Turn your working ML prediction engine into a sellable asset in 90 days.

---

## The Math That Matters

| Metric | Current | Target (90 Days) | Exit Multiple |
|--------|---------|------------------|---------------|
| NDCG Score | 0.953 | 0.970+ | Higher valuation |
| Beta Users | ~0 | 20-30 | Proof of demand |
| Monthly Revenue | $0 | $2,000-5,000 | Revenue multiple |
| Documentation | Scattered | Professional | Buyer confidence |
| **Exit Value** | — | **NZD 200,000-350,000** | **4-6x ARR** |

**Your edge**: 0.953 NDCG in horse racing prediction is genuinely valuable IP. TAB NZ, Australian syndicates, or betting tech companies will pay for proven accuracy.

---

## The Three Buyers You're Targeting

### 1. TAB New Zealand (Primary Target)
- **Why**: They need prediction tech to compete with international platforms
- **What they want**: Proven accuracy, clean IP, working system
- **Price range**: NZD 150,000-400,000
- **Contact**: Innovation team, corporate development

### 2. Australian Betting Syndicates
- **Why**: They live and die by prediction accuracy
- **What they want**: Edge over market, exclusive access
- **Price range**: NZD 100,000-250,000
- **Contact**: Private forums, racing industry events

### 3. Sports Tech Companies (FanDuel, Sportradar, etc.)
- **Why**: Racing is underserved in their portfolios
- **What they want**: Acquire + integrate
- **Price range**: NZD 200,000-500,000
- **Contact**: M&A teams, LinkedIn outreach

---

## 90-Day Sprint Breakdown

### PHASE 1: POLISH (Days 1-30)
**Goal**: Make it demo-ready and investment-grade

#### Week 1: Fix the Foundation
| Day | Task | Output |
|-----|------|--------|
| 1 | Audit deployed site—what's actually broken? | List of critical bugs |
| 2 | Fix auth/subscription flow (Stripe) | Working payment flow |
| 3 | Integrate frontend ↔ backend end-to-end | Demo video of full flow |
| 4 | Deploy to production with monitoring | Live, monitored site |
| 5 | Create 5-minute demo video | Shareable asset |
| 6-7 | Document API endpoints | API_REFERENCE.md v2 |

#### Week 2: Accuracy Push
| Day | Task | Output |
|-----|------|--------|
| 8-10 | Run Optuna optimization on ensemble | NDCG improvement plan |
| 11-12 | Test on 50 recent NZ races | Accuracy report |
| 13-14 | Document performance metrics | Investor-ready metrics deck |

#### Week 3: Beta Recruiting
| Day | Task | Output |
|-----|------|--------|
| 15-17 | Post in NZ racing forums, syndicate groups | 10 beta signups |
| 18-19 | Onboard beta users, collect feedback | Feedback spreadsheet |
| 20-21 | Iterate based on feedback | Improved UX |

#### Week 4: Documentation Blitz
| Day | Task | Output |
|-----|------|--------|
| 22-24 | Write Technical Overview (for buyers) | 5-page doc |
| 25-26 | Create Financial Projections | 3-year model |
| 27-28 | Build Pitch Deck (10 slides) | PDF + Google Slides |
| 29-30 | Package everything in data room | Organized folder structure |

**Phase 1 Deliverables**:
- [ ] Working production site with auth/payments
- [ ] Demo video (5 min)
- [ ] Beta user cohort (10+ people)
- [ ] NDCG score improved to 0.960+
- [ ] Pitch deck complete
- [ ] Data room organized

---

### PHASE 2: TRACTION (Days 31-60)
**Goal**: Prove demand and generate revenue

#### Week 5: Beta Expansion
- Target: 20 active beta users
- Daily: Monitor predictions, collect feedback
- Weekly: Accuracy report to users

#### Week 6: Soft Launch
- Open paid subscriptions (NZD 99/month)
- Target: 5 paying users
- Focus: Retention, not growth

#### Week 7: Revenue Optimization
- A/B test pricing (99 vs 149 vs 199)
- Add annual discount (10% off)
- Target: 10 paying users

#### Week 8: Case Studies
- Interview 3 power users
- Document ROI ("User X won $Y using predictions")
- Create testimonial page

**Phase 2 Deliverables**:
- [ ] 20+ beta users
- [ ] 10+ paying subscribers
- [ ] NZD 1,000-2,000 MRR
- [ ] 3 case studies with ROI
- [ ] Monthly churn < 10%

---

### PHASE 3: EXIT (Days 61-90)
**Goal**: Close acquisition or investment

#### Week 9: Buyer Outreach
- Day 61-63: Email TAB NZ innovation team
- Day 64-66: Contact Australian syndicates
- Day 67-69: LinkedIn outreach to sports tech M&A

#### Week 10: Due Diligence Prep
- Organize code repository
- Prepare IP assignment docs
- Compile financial records

#### Week 11: Negotiations
- Field offers
- Negotiate terms
- Get LOI (Letter of Intent)

#### Week 12: Close
- Final due diligence
- Sign agreement
- Transfer assets
- **Collect NZD 200,000-350,000**

**Phase 3 Deliverables**:
- [ ] 10+ buyer conversations
- [ ] 2-3 serious offers
- [ ] Signed LOI
- [ ] Closed deal

---

## Daily Execution Rhythm

### Morning (2 hours)
- **08:00-09:00**: Check overnight predictions, accuracy metrics
- **09:00-10:00**: Deep work (coding, optimization)

### Afternoon (2 hours)
- **14:00-15:00**: User support, feedback collection
- **15:00-16:00**: Outreach, documentation, planning

### Weekly Rituals
- **Monday**: Plan week's priorities
- **Wednesday**: Mid-week review, adjust if behind
- **Friday**: Ship something, update stakeholders
- **Sunday**: Review metrics, plan next week

---

## What to STOP Doing

❌ **Maintaining two repos** — Pick one, archive the other  
❌ **Writing more documentation** — You have enough; ship instead  
❌ **Perfecting the ML model** — 0.953 is good enough; 0.970 is the target, not 0.990  
❌ **Building new features** — Fix what's broken, then sell what you have  
❌ **Waiting for perfect** — Beta users expect rough edges; they want accuracy, not polish  

---

## What to START Doing

✅ **Daily outreach** — 5 emails/messages to potential users or buyers  
✅ **Demo everything** — Record every working feature, share widely  
✅ **Track metrics religiously** — Accuracy, retention, revenue, engagement  
✅ **Build in public** — Tweet, post, share progress (builds momentum)  
✅ **Ask for money** — Free users don't validate; paying users do  

---

## Critical Path Items (Do These First)

### 1. Fix the Deployed Site (This Week)
```bash
# What's the actual status?
curl -I https://horserace-rasnmx5k.manus.space

# If it's broken:
# 1. Check logs
# 2. Fix critical errors
# 3. Redeploy
# 4. Set up monitoring
```

### 2. Get 5 Beta Users (Next Week)
- NZ racing forums: punters.co.nz, racecafe.co.nz
- Facebook groups: NZ horse racing tips
- Direct outreach: Find 10 serious punters, offer free access

### 3. Document Your IP (Week 3)
Buyers need to see:
- How the ensemble works (technical overview)
- What data you use (sources, licensing)
- What's proprietary (your edge)
- What's transferable (can they own it?)

---

## The Pitch (Use This)

### Elevator Pitch (30 seconds)
> "Equine Oracle is a machine learning prediction platform for horse racing that achieves 95.3% accuracy on top-finisher predictions—20 points above industry baseline. We've built a weighted ensemble of 5+ models with automated retraining and real-time inference. We're seeking acquisition by a racing industry player who can scale this technology."

### Email Template (TAB NZ)
```
Subject: Proprietary ML Prediction Technology — Acquisition Opportunity

Hi [Name],

I'm reaching out from Equine Oracle, a machine learning prediction platform 
for horse racing. We've developed a weighted ensemble model achieving 
95.3% NDCG accuracy (industry baseline ~75%).

Our system includes:
• Real-time prediction API (<150ms latency)
• Automated model retraining
• Production infrastructure (Kubernetes-ready)
• 5+ specialized ML models

We're exploring acquisition by a strategic partner in the racing industry. 
Would you be open to a 15-minute call to discuss?

I've attached a one-page overview. Happy to provide a live demo.

Best,
[Your name]
[Your phone]
```

---

## Risk Mitigation

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Can't hit 0.970 NDCG | Medium | 0.953 is already sellable; focus on traction |
| No buyer interest | Low | Racing industry is desperate for tech edge |
| Site breaks during demo | Medium | Set up monitoring, have backup demo video |
| Can't get beta users | Low | Offer free access to serious punters |
| Legal/IP issues | Low | Document all data sources, ensure compliance |

---

## Success Metrics (Track Weekly)

| Metric | Week 1 | Week 4 | Week 8 | Week 12 |
|--------|--------|--------|--------|---------|
| NDCG Score | 0.953 | 0.960 | 0.965 | 0.970 |
| Beta Users | 0 | 10 | 20 | 30 |
| Paying Users | 0 | 2 | 10 | 15 |
| MRR | $0 | $200 | $1,500 | $3,000 |
| Buyer Conversations | 0 | 3 | 8 | 15 |
| Offers Received | 0 | 0 | 2 | 4 |

---

## The Bottom Line

You have working technology. You have a clear path to exit. What you need now is **ruthless execution**.

**This week**: Fix the site, get 5 beta users  
**This month**: Demo-ready, 10 betas, pitch deck done  
**Next month**: Revenue, case studies, buyer conversations  
**Month 3**: Close the deal, fund Low Key Consultants  

No more documentation. No more perfecting. **Ship and sell.**

---

## Resources

### Templates Included
- [ ] Pitch deck (Google Slides link)
- [ ] Financial model (Excel)
- [ ] Email templates (copy-paste ready)
- [ ] Data room checklist
- [ ] Buyer list (50 contacts)

### Tools You'll Need
- **Stripe** — Payments (free to set up)
- **Loom** — Demo videos (free tier)
- **Notion** — Documentation (free)
- **Google Workspace** — Email, slides, sheets ($6/month)
- **GitHub Pro** — Private repos ($4/month)

---

**Start today. Exit in 90 days. Fund your empire.**

---

*Last Updated: January 2026*  
*Status: Execute immediately*
