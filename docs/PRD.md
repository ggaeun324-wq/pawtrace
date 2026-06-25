# PawTrace — Product Requirement & Architecture Document

> **Every Paw Has a Story. Every Story Deserves a Home.**
>
> PawTrace is a **Pet Life Transparency Platform** — not an adoption marketplace.
> It connects trustworthy information across a dog's life so people can make
> responsible adoption decisions, while helping every dog find a loving family.

## Guiding Philosophy
- Every dog deserves a family.
- More information creates better adoption decisions.
- **Transparency is more important than scoring.**
- Technology should support shelters, not replace them.
- **We never judge or rank a dog.** Transparency indicators describe *records*, not worth.

---

## CTO Notes — Key Decisions / Challenged Assumptions

1. **"Never rank dogs" vs. earlier "trust score".**
   Resolution: scoring targets **record transparency**, not the dog. Dogs have no score.
   Shelters show a descriptive `transparency_level` (unverified / basic / verified) and
   `record_completeness %` — framed as "information available", never "good/bad shelter".

2. **Scope vs. solo junior + 4-week MVP.**
   AI Adoption Assistant, Shelter Companion AI, and Happy Ending are **deferred to Phase 2**.
   MVP = Pet Passport + Shelter Map + Public-data seeding. AI is "nice to have", not the critical path.

3. **Data sourcing is existential.**
   Primary source = Korea APMS / public data portal stray-animal Open API.
   Starting from an empty DB = "a map with nothing to show". Public API sync sits near the MVP core.
   AI-estimated breed and any inferred fields are always labeled **"estimate / reference only"**.

---

## 1. Personas
| # | Persona | Goal | Pain |
|---|---|---|---|
| P1 | Adopter Jieun (28) | Find a fitting dog + trustworthy info | Cannot see origin/history |
| P2 | Shelter staff Yeongseok (45) | Present dogs well | No time/skill to write intros |
| P3 | Volunteer Haneul (22) | Help & promote shelters | Scattered activity/donation info |
| P4 | Admin (internal) | Data quality & verification | No report/verify workflow |
| P5 | Post-adoption guardian Minjae (33) | Share our dog's story | Nowhere to post follow-ups |

## 2. User Journeys
- **Adopter (P1):** Map -> nearby shelters -> shelter detail (transparency level, volunteer/donation) -> dog -> **Pet Passport timeline** -> (P2) AI assistant -> contact shelter.
- **Shelter (P2, Phase 2):** Login -> register dog -> upload photo -> Shelter Companion AI generates intro/personality/adoption card -> review & publish.
- **Post-adoption (P5, Phase 2):** Adopted dog -> add Happy Ending photos & story -> public -> inspires future adopters.

## 3. Information Architecture
```
Home / Map
  Shelter Detail
    Dogs -> Dog Detail -> Pet Passport (timeline)
    Volunteer info / Donation info
Happy Endings (feed)        [Phase 2]
AI Adoption Assistant       [Phase 2]
Report
Admin (shelters, dogs/passport, companion AI, reports, public sync)
```

## 4. Feature Priorities (MoSCoW)
- **Must (MVP):** map & shelter search, shelter detail, dog list/detail, **Pet Passport timeline**, public-data seeding, admin CRUD + auth, report submit/review, Docker/CI/CD/deploy.
- **Should (P2):** AI Adoption Assistant, Shelter Companion AI, Happy Ending, volunteer/donation info, user login, Redis caching.
- **Could (P3):** anomaly keyword detection, notifications, shelter self-portal, i18n, breed estimation AI.
- **Won't (now):** payments, adoption contracts, medical diagnosis, dog ranking.

## 5. MVP Scope (4 weeks, solo)
Anonymous users browse map -> shelter -> dog -> Pet Passport and submit reports.
Admin performs CRUD + verification. Public API seeds initial data.
Everything runs via Docker and deploys to AWS via CI/CD. No AI / Happy Ending / login.

## 6. Phase 2
AI Adoption Assistant (guidance only), Shelter Companion AI (intro/personality/adoption card; breed = estimate label),
Happy Ending feed + moderation, social login, volunteer/donation info, scheduled public-data sync, Redis caching.

## 7. Phase 3
Anomaly keyword detection, notifications, shelter self-registration portal + RBAC, EKS migration + autoscale,
observability (metrics/tracing/logs), IaC (Terraform), i18n.

## 8. Database Design (overview)
No dog score. Shelters carry descriptive `transparency_level`; lifetime tracked via `passport_events`.
```
shelters(id, name, description, address, location geography(Point,4326),
         is_gov_registered, gov_reg_no, source enum(public_api,manual), external_id,
         transparency_level enum(unverified,basic,verified), record_completeness numeric,
         phone, created_at, updated_at)
dogs(id, shelter_id FK, name, breed_label, birth_estimate, gender enum, is_neutered,
     adoption_status enum(protected,available,reserved,adopted), source enum, external_id,
     thumbnail_url, created_at, updated_at)
passport_events(id, dog_id FK, event_type enum(rescue,intake,medical,vaccination,neuter,
                available,adopted,post_adoption), event_date,
                location geography(Point,4326) null, memo, source enum, created_at)
happy_endings(id, dog_id FK, author_contact, story, is_approved, created_at)            [P2]
happy_ending_photos(id, happy_ending_id FK, image_url)                                  [P2]
reports(id, target_type enum(shelter,dog), target_id, reporter_contact null, description,
        image_url null, ai_category null, status enum(pending,reviewing,resolved,rejected),
        admin_memo null, created_at, reviewed_at)
verifications(id, shelter_id FK, old_level, new_level, reason, related_report_id null, created_at)
admins(id, email unique, password_hash, role enum(admin,superadmin), created_at)
volunteer_info / donation_info(id, shelter_id FK, ...)                                  [P2]
```
Design point: `source` / `external_id` separate public-data vs manual entries -> idempotent sync & provenance.

## 9. REST API (summary, /api/v1)
**Public:** `GET /shelters?lat,lng,radius,region`, `GET /shelters/{id}`, `GET /shelters/{id}/dogs`,
`GET /dogs/{id}`, `GET /dogs/{id}/passport`, `GET /happy-endings` (P2), `POST /reports`.
**Admin (JWT):** `POST /auth/login`, `POST/PUT/DELETE /admin/shelters`, `/admin/dogs`,
`POST/PUT /admin/dogs/{id}/passport`, `GET /admin/reports`, `PATCH /admin/reports/{id}`,
`POST /admin/sync/public`, `POST /admin/dogs/{id}/ai-card` (P2).
Standards: pagination `?page&size`, errors `{code,message}`, estimated/unverified fields carry meta.

## 10. Folder Structure
```
pawtrace/
  docker-compose.yml
  .github/workflows/{ci.yml,deploy.yml}
  backend/app/{core,domain,models,schemas,api/v1,services,repositories,integrations,db}
  frontend/src/{app,components,lib,styles}
  infra/   docs/{PRD.md,architecture.md,erd.png,api.md}
```

## 11. Backend Architecture
Clean Architecture: api -> services (use cases) -> repositories (DB abstraction) -> models.
Domain rules in `domain/`. External integrations (public API, Bedrock/OpenAI, S3) isolated in `integrations/`.
12-factor config via env. Report review -> verifications + transparency_level update is atomic.
Public sync is idempotent (`external_id` upsert).

## 12. Frontend Architecture
Next.js (App Router), rounded/pastel theme tokens. Components: Map, ShelterCard, PassportTimeline,
ReportForm, HappyEndingCard. `lib/` for api client + kakao map adapter. Estimated/unverified info
always shown with explicit badges (UX enforces ethics).

## 13. DevOps Architecture
```
PR -> ci.yml: lint + pytest + frontend build + GitGuardian (secret) + SonarQube (SAST/quality gate)
main -> deploy.yml: docker build -> Trivy image scan -> Amazon ECR -> ECS Fargate rolling update (+ alembic migrate task)
Secrets via GitHub Secrets / AWS Secrets Manager -> ECS task env. ElastiCache Redis. /health endpoint. CloudWatch + X-Ray (P3).
IaC-ready (infra/ Terraform in P3). Future ECS Fargate -> EKS reusing same image.
```

## 14. Development Roadmap (4-week MVP)
| Week | Focus | Epics |
|---|---|---|
| 1 | Setup + DB + public-data seeding + base read APIs | A, B |
| 2 | Map + shelter + Pet Passport | C, D |
| 3 | Reports + admin + verification loop | E, F |
| 4 | Docker/CI/CD/AWS deploy + docs | G |
Phase 2: AI + Happy Ending (H, I). Phase 3: scaling/observability (J).

## 15. README Structure
logo+tagline -> differentiation (list vs history/transparency) -> features -> screenshots/GIF ->
tech stack -> architecture diagram -> local run (docker-compose) -> env vars -> API docs link ->
data source/license -> roadmap -> ethics (no ranking; verify-before-publish) -> license.

## 16. Future Scaling Strategy
ECS Fargate (scale-to-zero via scheduled scaling) -> EKS with HPA reusing same image. ElastiCache Redis + RDS read replica.
GiST spatial index tuning, tile-based map clustering at scale. AI cost: cache results + async pre-generation.
Reliability: health/readiness, CloudWatch + X-Ray tracing, blue/green via ECS + CodeDeploy. IaC (Terraform) for reproducibility.
