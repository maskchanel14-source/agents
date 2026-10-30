-- ─────────────────────────────────────────────────────────────────────────────
-- AI Viral Clip Generator — production schema (Supabase / PostgreSQL 15+)
--
-- The API uses portable ASCII UUID strings as primary keys (String(36)), so the
-- same models run on SQLite for local dev and on Supabase Postgres in prod.
-- Row Level Security is enabled as defence-in-depth: the API connects with the
-- service role (RLS bypassed, authorisation enforced in application queries),
-- while any direct anon/authenticated client is restricted to its own rows.
-- ─────────────────────────────────────────────────────────────────────────────

create extension if not exists pgcrypto;

-- ── users ────────────────────────────────────────────────────────────────────
create table if not exists public.users (
    id                  text primary key default gen_random_uuid()::text,
    email               text not null unique,
    password_hash       text,                              -- null for Supabase-OAuth users
    display_name        text,
    plan                text not null default 'free'
                        check (plan in ('free', 'pro', 'business')),
    minutes_used        numeric(10, 3) not null default 0 check (minutes_used >= 0),
    clips_rendered      integer not null default 0 check (clips_rendered >= 0),
    supabase_sub        text unique,
    stripe_customer_id  text,
    is_admin            boolean not null default false,
    created_at          timestamptz not null default now()
);
create index if not exists ix_users_email on public.users (lower(email));

-- ── projects ─────────────────────────────────────────────────────────────────
create table if not exists public.projects (
    id                text primary key default gen_random_uuid()::text,
    user_id           text not null references public.users (id) on delete cascade,
    title             text not null,
    source_type       text not null default 'upload' check (source_type in ('upload', 'url')),
    source_url        text,
    source_key        text,
    poster_key        text,
    status            text not null default 'uploaded'
                      check (status in ('uploading','uploaded','queued','analyzing','analyzed',
                                        'rendering','ready','failed')),
    stage             text not null default 'uploaded',
    progress          integer not null default 0 check (progress between 0 and 100),
    duration_s        double precision,
    width             integer,
    height            integer,
    fps               double precision,
    language          text,
    error             text,
    analysis          jsonb,
    settings_snapshot jsonb,
    created_at        timestamptz not null default now(),
    updated_at        timestamptz not null default now()
);
create index if not exists ix_projects_user_created on public.projects (user_id, created_at desc);
create index if not exists ix_projects_status on public.projects (status);

-- ── transcripts ──────────────────────────────────────────────────────────────
create table if not exists public.transcripts (
    id         text primary key default gen_random_uuid()::text,
    project_id text not null unique references public.projects (id) on delete cascade,
    language   text,
    provider   text not null default 'none',
    model      text,
    full_text  text not null default '',
    segments   jsonb,
    words      jsonb,
    speakers   jsonb,
    created_at timestamptz not null default now()
);
create index if not exists ix_transcripts_project on public.transcripts (project_id);

-- ── clips ────────────────────────────────────────────────────────────────────
create table if not exists public.clips (
    id              text primary key default gen_random_uuid()::text,
    project_id      text not null references public.projects (id) on delete cascade,
    user_id         text not null references public.users (id) on delete cascade,
    start_s         double precision not null check (start_s >= 0),
    end_s           double precision not null check (end_s > start_s),
    duration_s      double precision not null,
    title           text not null,
    hook            text,
    text            text not null default '',
    score           double precision not null default 0 check (score between 0 and 100),
    score_breakdown jsonb,
    explanation     text,
    tags            jsonb,
    status          text not null default 'suggested'
                    check (status in ('suggested','rendering','ready','failed')),
    preset          text not null default 'bold_viral',
    crop_x          double precision check (crop_x between 0 and 1),
    fit_mode        text not null default 'crop' check (fit_mode in ('crop','blur')),
    subtitle_json   jsonb,
    render_key      text,
    thumb_key       text,
    render_error    text,
    created_at      timestamptz not null default now(),
    updated_at      timestamptz not null default now()
);
create index if not exists ix_clips_project_score on public.clips (project_id, score desc);
create index if not exists ix_clips_user on public.clips (user_id);

-- ── jobs ─────────────────────────────────────────────────────────────────────
create table if not exists public.jobs (
    id          text primary key default gen_random_uuid()::text,
    project_id  text references public.projects (id) on delete cascade,
    user_id     text not null references public.users (id) on delete cascade,
    type        text not null check (type in ('analyze','render','export')),
    status      text not null default 'queued'
                check (status in ('queued','running','done','failed')),
    stage       text not null default 'queued',
    progress    integer not null default 0 check (progress between 0 and 100),
    payload     jsonb,
    result      jsonb,
    error       text,
    created_at  timestamptz not null default now(),
    started_at  timestamptz,
    finished_at timestamptz
);
create index if not exists ix_jobs_user_created on public.jobs (user_id, created_at desc);
create index if not exists ix_jobs_project on public.jobs (project_id);
create index if not exists ix_jobs_status on public.jobs (status);

-- ── ai_usage (cost + token accounting) ───────────────────────────────────────
create table if not exists public.ai_usage (
    id                text primary key default gen_random_uuid()::text,
    user_id           text references public.users (id) on delete set null,
    project_id        text references public.projects (id) on delete set null,
    provider          text not null,
    model             text not null,
    task              text not null,
    prompt_tokens     integer not null default 0,
    completion_tokens integer not null default 0,
    audio_seconds     double precision not null default 0,
    cost_usd          numeric(12, 6) not null default 0,
    latency_ms        integer not null default 0,
    ok                boolean not null default true,
    error             text,
    created_at        timestamptz not null default now()
);
create index if not exists ix_ai_usage_user_created on public.ai_usage (user_id, created_at desc);

-- ── updated_at maintenance ───────────────────────────────────────────────────
create or replace function public.touch_updated_at() returns trigger as $$
begin
    new.updated_at = now();
    return new;
end;
$$ language plpgsql;

drop trigger if exists trg_projects_updated on public.projects;
create trigger trg_projects_updated before update on public.projects
    for each row execute function public.touch_updated_at();

drop trigger if exists trg_clips_updated on public.clips;
create trigger trg_clips_updated before update on public.clips
    for each row execute function public.touch_updated_at();

-- ── Row Level Security ───────────────────────────────────────────────────────
alter table public.users       enable row level security;
alter table public.projects    enable row level security;
alter table public.transcripts enable row level security;
alter table public.clips       enable row level security;
alter table public.jobs        enable row level security;
alter table public.ai_usage    enable row level security;

drop policy if exists users_self on public.users;
create policy users_self on public.users
    for select using (auth.uid()::text = id);

drop policy if exists projects_owner on public.projects;
create policy projects_owner on public.projects
    for all using (auth.uid()::text = user_id) with check (auth.uid()::text = user_id);

drop policy if exists transcripts_owner on public.transcripts;
create policy transcripts_owner on public.transcripts
    for all using (
        exists (select 1 from public.projects p
                where p.id = transcripts.project_id and p.user_id = auth.uid()::text)
    );

drop policy if exists clips_owner on public.clips;
create policy clips_owner on public.clips
    for all using (auth.uid()::text = user_id) with check (auth.uid()::text = user_id);

drop policy if exists jobs_owner on public.jobs;
create policy jobs_owner on public.jobs
    for all using (auth.uid()::text = user_id) with check (auth.uid()::text = user_id);

drop policy if exists ai_usage_owner on public.ai_usage;
create policy ai_usage_owner on public.ai_usage
    for select using (auth.uid()::text = user_id);

-- ── Storage (only if you keep media in Supabase instead of R2) ───────────────
-- insert into storage.buckets (id, name, public) values ('viral-clips', 'viral-clips', false)
--   on conflict (id) do nothing;
-- create policy "own media read" on storage.objects for select
--   using (bucket_id = 'viral-clips' and (storage.foldername(name))[1] = auth.uid()::text);
