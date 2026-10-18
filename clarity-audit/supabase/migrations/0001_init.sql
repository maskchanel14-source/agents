-- Clarity Audit — initial schema (Supabase/Postgres)
-- Apply: supabase db push, or paste into the Supabase SQL editor.
-- Security model: RLS ON everywhere. The public/anon role gets nothing by
-- default; the app server writes with the service-role key (which bypasses
-- RLS). Any future user-facing reads must add narrow policies deliberately.

create extension if not exists "pgcrypto";

-- Leads & consent ----------------------------------------------------------
create table if not exists leads (
  id uuid primary key default gen_random_uuid(),
  email text not null,
  source text not null default 'site',
  scan_id text,
  plan_interest text,
  created_at timestamptz not null default now()
);
create index if not exists leads_email_idx on leads (lower(email));

create table if not exists consent_events (
  id uuid primary key default gen_random_uuid(),
  email text not null,
  purpose text not null,
  granted boolean not null,
  ip_hash text,
  created_at timestamptz not null default now()
);

create table if not exists email_events (
  id uuid primary key default gen_random_uuid(),
  email text not null,
  event_type text not null, -- sent|opened|clicked|bounced|unsubscribed|complained
  campaign text,
  created_at timestamptz not null default now()
);

-- Scans & reports ----------------------------------------------------------
create table if not exists scans (
  id text primary key,
  url text not null,
  final_url text,
  score int,
  grade text,
  source_ref text, -- ?ref= attribution
  is_public boolean not null default true,
  created_at timestamptz not null default now()
);
create index if not exists scans_created_idx on scans (created_at desc);

create table if not exists scan_results (
  scan_id text primary key references scans(id) on delete cascade,
  report jsonb not null,
  created_at timestamptz not null default now()
);

create table if not exists reports (
  id uuid primary key default gen_random_uuid(),
  scan_id text references scans(id),
  tier text not null, -- quick|full|fixpack
  order_id uuid,
  document text, -- generated markdown
  delivered_at timestamptz,
  created_at timestamptz not null default now()
);

create table if not exists deliverables (
  id uuid primary key default gen_random_uuid(),
  report_id uuid references reports(id) on delete cascade,
  kind text not null, -- report_doc|template_kit|checklist
  storage_path text,
  created_at timestamptz not null default now()
);

-- Commerce (wired when the HUMAN connects a payment provider) --------------
create table if not exists orders (
  id uuid primary key default gen_random_uuid(),
  email text not null,
  plan text not null,
  amount_cents int not null,
  currency text not null default 'USD',
  status text not null default 'pending', -- pending|paid|refunded|chargeback|failed
  provider text, -- stripe|lemonsqueezy|gumroad|payhip
  provider_order_id text unique, -- idempotency anchor for webhooks
  ref_code text, -- affiliate attribution
  created_at timestamptz not null default now()
);

create table if not exists payments (
  id uuid primary key default gen_random_uuid(),
  order_id uuid references orders(id) on delete cascade,
  provider_event_id text unique, -- webhook idempotency
  event_type text not null,
  raw jsonb,
  created_at timestamptz not null default now()
);

-- Growth graph --------------------------------------------------------------
create table if not exists referrals (
  id uuid primary key default gen_random_uuid(),
  referrer_email text,
  ref_code text not null,
  scan_id text references scans(id),
  order_id uuid references orders(id),
  reward_status text not null default 'pending', -- pending|granted|void (fraud/self-ref)
  created_at timestamptz not null default now()
);

create table if not exists affiliates (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  email text not null unique,
  audience text,
  channel_url text,
  ref_code text unique,
  commission_bps int not null default 3000, -- 30%
  status text not null default 'applied', -- applied|approved|suspended
  created_at timestamptz not null default now()
);

create table if not exists widget_embeds (
  id uuid primary key default gen_random_uuid(),
  scan_id text,
  embed_domain text,
  views int not null default 0,
  clicks int not null default 0,
  created_at timestamptz not null default now()
);

create table if not exists traffic_sources (
  id uuid primary key default gen_random_uuid(),
  day date not null,
  source text not null,
  medium text,
  sessions int not null default 0,
  scans int not null default 0,
  orders int not null default 0
);

create table if not exists keywords (
  id uuid primary key default gen_random_uuid(),
  keyword text not null unique,
  intent text,
  volume_note text,
  target_url text,
  status text not null default 'idea' -- idea|draft|published|refresh
);

create table if not exists content_pages (
  id uuid primary key default gen_random_uuid(),
  slug text not null unique,
  title text,
  status text not null default 'published',
  published_at timestamptz,
  updated_at timestamptz not null default now()
);

create table if not exists experiments (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  hypothesis text,
  metric text,
  min_sample int,
  status text not null default 'planned', -- planned|running|won|lost|killed
  result_note text,
  created_at timestamptz not null default now()
);

-- Ops / risk ----------------------------------------------------------------
create table if not exists support_tickets (
  id uuid primary key default gen_random_uuid(),
  email text,
  subject text,
  body text,
  status text not null default 'open',
  created_at timestamptz not null default now()
);

create table if not exists risk_logs (
  id uuid primary key default gen_random_uuid(),
  area text not null, -- spam|privacy|platform|legal|security|brand|payments
  severity text not null default 'low', -- low|medium|high
  note text not null,
  mitigation text,
  created_at timestamptz not null default now()
);

create table if not exists audit_logs (
  id uuid primary key default gen_random_uuid(),
  actor text not null default 'system',
  action text not null,
  entity text,
  entity_id text,
  meta jsonb,
  created_at timestamptz not null default now()
);

-- Row Level Security: deny-by-default --------------------------------------
alter table leads enable row level security;
alter table consent_events enable row level security;
alter table email_events enable row level security;
alter table scans enable row level security;
alter table scan_results enable row level security;
alter table reports enable row level security;
alter table deliverables enable row level security;
alter table orders enable row level security;
alter table payments enable row level security;
alter table referrals enable row level security;
alter table affiliates enable row level security;
alter table widget_embeds enable row level security;
alter table traffic_sources enable row level security;
alter table keywords enable row level security;
alter table content_pages enable row level security;
alter table experiments enable row level security;
alter table support_tickets enable row level security;
alter table risk_logs enable row level security;
alter table audit_logs enable row level security;

-- No anon/authenticated policies: only the service role (server-side) touches
-- these tables.defense-in-depth against key leaks and direct PostgREST abuse.
-- Public scan retrieval goes through the app server, never direct table reads.

comment on table orders is 'provider_order_id UNIQUE = webhook idempotency. Human connects provider; final refund/chargeback decisions are human.';
comment on table payments is 'Store raw webhook payloads AFTER signature verification in the webhook handler.';
