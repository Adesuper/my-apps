const e=`-- =====================================================================
--  MATHS & CODE CLUB  ·  database setup
--  Run this whole file once in Supabase → SQL Editor → New query → Run.
--  It is safe to run again: nothing is duplicated or lost.
--  Then run CONTENT.sql (the weekly lessons and questions).
-- =====================================================================

create extension if not exists pgcrypto with schema extensions;

-- ---------------------------------------------------------------------
-- Helpers
-- ---------------------------------------------------------------------
-- "Today" for the club is Toronto time, so a week opens at midnight in Ontario.
create or replace function public.mc_today() returns date
language sql stable as $$ select (now() at time zone 'America/Toronto')::date $$;

-- ---------------------------------------------------------------------
-- Leaders (grown-ups who sign in with email and password)
-- ---------------------------------------------------------------------
create table if not exists public.mc_leaders (
  user_id      uuid primary key references auth.users(id) on delete cascade,
  display_name text not null default 'Leader',
  created_at   timestamptz not null default now()
);
alter table public.mc_leaders enable row level security;

create or replace function public.mc_is_leader() returns boolean
language sql stable security definer set search_path = public as $$
  select exists (select 1 from public.mc_leaders where user_id = auth.uid())
$$;

drop policy if exists "leaders see leaders" on public.mc_leaders;
create policy "leaders see leaders" on public.mc_leaders for select using (public.mc_is_leader());

-- The very first person to call this becomes a leader. After that, only a
-- leader can add another leader (mc_add_leader).
create or replace function public.mc_claim_first_leader(p_display_name text default 'Leader')
returns boolean language plpgsql security definer set search_path = public as $$
begin
  if auth.uid() is null then raise exception 'Sign in first.'; end if;
  if exists (select 1 from public.mc_leaders) then
    return exists (select 1 from public.mc_leaders where user_id = auth.uid());
  end if;
  insert into public.mc_leaders (user_id, display_name) values (auth.uid(), coalesce(nullif(trim(p_display_name), ''), 'Leader'));
  return true;
end $$;

create or replace function public.mc_add_leader(p_email text, p_display_name text default 'Leader')
returns boolean language plpgsql security definer set search_path = public as $$
declare v_id uuid;
begin
  if not public.mc_is_leader() then raise exception 'Leaders only.'; end if;
  select id into v_id from auth.users where lower(email) = lower(trim(p_email));
  if v_id is null then raise exception 'No account with that email yet. Ask them to create one first.'; end if;
  insert into public.mc_leaders (user_id, display_name) values (v_id, coalesce(nullif(trim(p_display_name), ''), 'Leader'))
  on conflict (user_id) do update set display_name = excluded.display_name;
  return true;
end $$;

-- ---------------------------------------------------------------------
-- Students (children sign in with their name and a 4-digit PIN)
--   band A = Sprouts (Grades 1-2), B = Explorers (3-4), C = Trailblazers (5-6)
-- ---------------------------------------------------------------------
create table if not exists public.mc_students (
  id         uuid primary key default gen_random_uuid(),
  name       text not null,
  band       text not null check (band in ('A','B','C')),
  grade      int  check (grade between 1 and 6),
  pin_hash   text not null,
  active     boolean not null default true,
  created_at timestamptz not null default now()
);
create unique index if not exists mc_students_name_active on public.mc_students (lower(name)) where active;
alter table public.mc_students enable row level security;
drop policy if exists "leaders read students" on public.mc_students;
create policy "leaders read students" on public.mc_students for select using (public.mc_is_leader());

-- Names only, for the "pick your name" list. Never the PIN.
create or replace view public.mc_roster_public with (security_invoker = false) as
  select name, band from public.mc_students where active order by lower(name);

-- Checks a name and PIN. Raises an error if they do not match.
create or replace function public.mc_student_check(p_name text, p_pin text)
returns public.mc_students language plpgsql stable security definer set search_path = public, extensions as $$
declare s public.mc_students;
begin
  select * into s from public.mc_students where active and lower(name) = lower(trim(p_name));
  if s.id is null or s.pin_hash <> crypt(coalesce(p_pin, ''), s.pin_hash) then
    raise exception 'That name and PIN do not match.';
  end if;
  return s;
end $$;

create or replace function public.mc_verify_student(p_name text, p_pin text)
returns jsonb language plpgsql stable security definer set search_path = public as $$
declare s public.mc_students;
begin
  s := public.mc_student_check(p_name, p_pin);
  return jsonb_build_object('name', s.name, 'band', s.band, 'grade', s.grade);
end $$;

-- Leader: add a child, or change their band, grade or PIN.
create or replace function public.mc_set_student(p_name text, p_band text, p_grade int, p_pin text default null)
returns jsonb language plpgsql security definer set search_path = public, extensions as $$
declare v_id uuid;
begin
  if not public.mc_is_leader() then raise exception 'Leaders only.'; end if;
  if coalesce(trim(p_name), '') = '' then raise exception 'A name is needed.'; end if;
  if p_band not in ('A','B','C') then raise exception 'Band must be A, B or C.'; end if;
  if p_pin is not null and p_pin !~ '^[0-9]{4}$' then raise exception 'The PIN must be 4 digits.'; end if;
  select id into v_id from public.mc_students where active and lower(name) = lower(trim(p_name));
  if v_id is null then
    if p_pin is null then raise exception 'A new child needs a PIN.'; end if;
    insert into public.mc_students (name, band, grade, pin_hash)
    values (trim(p_name), p_band, p_grade, crypt(p_pin, gen_salt('bf')));
  else
    update public.mc_students set band = p_band, grade = p_grade,
      pin_hash = case when p_pin is null then pin_hash else crypt(p_pin, gen_salt('bf')) end
    where id = v_id;
  end if;
  return jsonb_build_object('ok', true);
end $$;

create or replace function public.mc_remove_student(p_name text)
returns jsonb language plpgsql security definer set search_path = public as $$
begin
  if not public.mc_is_leader() then raise exception 'Leaders only.'; end if;
  update public.mc_students set active = false where active and lower(name) = lower(trim(p_name));
  return jsonb_build_object('ok', true);
end $$;

-- ---------------------------------------------------------------------
-- Weeks and questions
-- ---------------------------------------------------------------------
create table if not exists public.mc_weeks (
  week     int primary key,
  slug     text not null,
  title    text not null,
  strand   text not null,
  opens_on date,                       -- set by a leader; null = not scheduled yet
  lesson   jsonb not null default '{}' -- { "A": {...}, "B": {...}, "C": {...} }
);
alter table public.mc_weeks enable row level security;
drop policy if exists "open weeks are public" on public.mc_weeks;
create policy "open weeks are public" on public.mc_weeks for select
  using ((opens_on is not null and opens_on <= public.mc_today()) or public.mc_is_leader());

create table if not exists public.mc_questions (
  id      text primary key,
  week    int  not null references public.mc_weeks(week) on delete cascade,
  band    text not null check (band in ('A','B','C')),
  use     text not null check (use in ('daily','live','spare')),
  day     int  check (day between 1 and 4),
  kind    text not null check (kind in ('mc','num')),
  prompt  text not null,
  options jsonb,
  answer  numeric not null,   -- mc: index of the right option; num: the number
  explain text not null default ''
);
create index if not exists mc_questions_week_band on public.mc_questions (week, band, use, day);
alter table public.mc_questions enable row level security;   -- no policy: nobody reads the answer key directly
drop policy if exists "leaders read questions" on public.mc_questions;
create policy "leaders read questions" on public.mc_questions for select using (public.mc_is_leader());

-- What a child may see: daily questions from the day they unlock (Mon = day 1 … Thu = day 4)
-- and the spare "extra practice" questions of open weeks. No answers, no live questions.
create or replace view public.mc_questions_public with (security_invoker = false) as
  select q.id, q.week, q.band, q.use, q.day, q.kind, q.prompt, q.options
  from public.mc_questions q join public.mc_weeks w on w.week = q.week
  where w.opens_on is not null
    and ((q.use = 'daily' and w.opens_on + (q.day - 1) <= public.mc_today())
      or (q.use = 'spare' and w.opens_on <= public.mc_today()));

-- Leader: schedule a week (date = the Monday it opens).
create or replace function public.mc_set_week_open(p_week int, p_opens_on date)
returns jsonb language plpgsql security definer set search_path = public as $$
begin
  if not public.mc_is_leader() then raise exception 'Leaders only.'; end if;
  update public.mc_weeks set opens_on = p_opens_on where week = p_week;
  return jsonb_build_object('ok', found);
end $$;

-- Is this answer right? Numbers allow tiny rounding differences.
create or replace function public.mc_is_right(q public.mc_questions, v numeric)
returns boolean language sql immutable as $$
  select v is not null and (case when q.kind = 'mc' then v = q.answer else abs(v - q.answer) < 0.0001 end)
$$;

-- ---------------------------------------------------------------------
-- Daily practice: 5 questions a day, 3 tries, the first try counts
-- ---------------------------------------------------------------------
create table if not exists public.mc_attempts (
  id          bigserial primary key,
  student_id  uuid not null references public.mc_students(id) on delete cascade,
  week        int  not null,
  day         int  not null,
  attempt_no  int  not null,
  score       int  not null,
  total       int  not null,
  counted     boolean not null,
  details     jsonb not null default '[]',
  created_at  timestamptz not null default now(),
  unique (student_id, week, day, attempt_no)
);
alter table public.mc_attempts enable row level security;
drop policy if exists "leaders read attempts" on public.mc_attempts;
create policy "leaders read attempts" on public.mc_attempts for select using (public.mc_is_leader());

-- p_answers: { "question id": number }  (for multiple choice, the option index)
create or replace function public.mc_submit_daily(p_name text, p_pin text, p_week int, p_day int, p_answers jsonb)
returns jsonb language plpgsql security definer set search_path = public as $$
declare
  s public.mc_students; w public.mc_weeks; q public.mc_questions;
  v_no int; v_score int := 0; v_total int := 0; v_given numeric; v_ok boolean; v_results jsonb := '[]';
begin
  s := public.mc_student_check(p_name, p_pin);
  select * into w from public.mc_weeks where week = p_week;
  if w.opens_on is null or w.opens_on + (p_day - 1) > public.mc_today() then
    raise exception 'This day is not open yet.';
  end if;
  select coalesce(max(attempt_no), 0) + 1 into v_no from public.mc_attempts
    where student_id = s.id and week = p_week and day = p_day;
  if v_no > 3 then raise exception 'You have used your 3 tries for this day.'; end if;

  for q in select * from public.mc_questions
           where week = p_week and band = s.band and use = 'daily' and day = p_day order by id loop
    v_total := v_total + 1;
    begin v_given := (p_answers ->> q.id)::numeric; exception when others then v_given := null; end;
    v_ok := public.mc_is_right(q, v_given);
    if v_ok then v_score := v_score + 1; end if;
    v_results := v_results || jsonb_build_object('id', q.id, 'correct', v_ok, 'given', v_given,
      'answer', q.answer, 'explain', q.explain);
  end loop;
  if v_total = 0 then raise exception 'No questions found for this day.'; end if;

  insert into public.mc_attempts (student_id, week, day, attempt_no, score, total, counted, details)
  values (s.id, p_week, p_day, v_no, v_score, v_total, v_no = 1, v_results);
  return jsonb_build_object('score', v_score, 'total', v_total, 'attempt_no', v_no,
    'counted', v_no = 1, 'tries_left', 3 - v_no, 'results', v_results);
end $$;

-- Extra practice (spare questions of open weeks): graded, never recorded.
create or replace function public.mc_check_practice(p_answers jsonb)
returns jsonb language plpgsql stable security definer set search_path = public as $$
declare q public.mc_questions; v_given numeric; v_results jsonb := '[]';
begin
  for q in select qq.* from public.mc_questions qq join public.mc_weeks w on w.week = qq.week
           where qq.use = 'spare' and w.opens_on <= public.mc_today()
             and qq.id in (select jsonb_object_keys(p_answers)) loop
    begin v_given := (p_answers ->> q.id)::numeric; exception when others then v_given := null; end;
    v_results := v_results || jsonb_build_object('id', q.id, 'correct', public.mc_is_right(q, v_given),
      'answer', q.answer, 'explain', q.explain);
  end loop;
  return v_results;
end $$;

-- ---------------------------------------------------------------------
-- Coding lab progress (one row per finished challenge)
-- ---------------------------------------------------------------------
create table if not exists public.mc_code_done (
  student_id uuid not null references public.mc_students(id) on delete cascade,
  challenge  text not null,
  done_at    timestamptz not null default now(),
  primary key (student_id, challenge)
);
alter table public.mc_code_done enable row level security;
drop policy if exists "leaders read code" on public.mc_code_done;
create policy "leaders read code" on public.mc_code_done for select using (public.mc_is_leader());

create or replace function public.mc_mark_code_done(p_name text, p_pin text, p_challenge text)
returns jsonb language plpgsql security definer set search_path = public as $$
declare s public.mc_students;
begin
  s := public.mc_student_check(p_name, p_pin);
  if p_challenge !~ '^[a-z0-9-]{3,40}$' then raise exception 'Unknown challenge.'; end if;
  insert into public.mc_code_done (student_id, challenge) values (s.id, p_challenge) on conflict do nothing;
  return jsonb_build_object('ok', true);
end $$;

-- A child's own progress: daily results and finished coding challenges.
create or replace function public.mc_my_progress(p_name text, p_pin text)
returns jsonb language plpgsql stable security definer set search_path = public as $$
declare s public.mc_students;
begin
  s := public.mc_student_check(p_name, p_pin);
  return jsonb_build_object(
    'band', s.band,
    'days', coalesce((select jsonb_agg(jsonb_build_object('week', week, 'day', day, 'tries', n, 'first', first, 'best', best, 'total', total))
      from (select week, day, count(*) n, max(score) best, max(total) total,
                   max(case when counted then score end) first
            from public.mc_attempts where student_id = s.id group by week, day) t), '[]'),
    'code', coalesce((select jsonb_agg(challenge) from public.mc_code_done where student_id = s.id), '[]'));
end $$;

-- ---------------------------------------------------------------------
-- Live quiz (the weekly online session)
-- ---------------------------------------------------------------------
create table if not exists public.mc_live_sessions (
  id           uuid primary key default gen_random_uuid(),
  code         text not null,
  week         int  not null references public.mc_weeks(week),
  status       text not null default 'lobby' check (status in ('lobby','question','reveal','ended')),
  q_index      int  not null default -1,
  q_started_at timestamptz,
  q_seconds    int  not null default 30 check (q_seconds between 10 and 120),
  created_by   uuid,
  created_at   timestamptz not null default now()
);
create unique index if not exists mc_live_code_open on public.mc_live_sessions (code) where status <> 'ended';
alter table public.mc_live_sessions enable row level security;
-- The session row holds no answers, so everyone may read it (children's screens follow it live).
drop policy if exists "sessions are public" on public.mc_live_sessions;
create policy "sessions are public" on public.mc_live_sessions for select using (true);

create table if not exists public.mc_live_players (
  session_id uuid not null references public.mc_live_sessions(id) on delete cascade,
  student_id uuid not null references public.mc_students(id) on delete cascade,
  joined_at  timestamptz not null default now(),
  primary key (session_id, student_id)
);
create table if not exists public.mc_live_answers (
  session_id  uuid not null references public.mc_live_sessions(id) on delete cascade,
  student_id  uuid not null references public.mc_students(id) on delete cascade,
  q_index     int  not null,
  correct     boolean not null,
  points      int  not null,
  answered_at timestamptz not null default now(),
  primary key (session_id, student_id, q_index)
);
alter table public.mc_live_players enable row level security;
alter table public.mc_live_answers enable row level security;
drop policy if exists "leaders read players" on public.mc_live_players;
create policy "leaders read players" on public.mc_live_players for select using (public.mc_is_leader());
drop policy if exists "leaders read live answers" on public.mc_live_answers;
create policy "leaders read live answers" on public.mc_live_answers for select using (public.mc_is_leader());

-- How many live questions this session can play (the smallest band's count).
create or replace function public.mc_live_count(p_week int) returns int
language sql stable security definer set search_path = public as $$
  select coalesce(min(n), 0)::int from (
    select band, count(*) n from public.mc_questions where week = p_week and use = 'live' group by band) t
$$;

-- The question number i (0-based) of the live set, for one band.
create or replace function public.mc_live_question(p_week int, p_band text, p_index int)
returns public.mc_questions language sql stable security definer set search_path = public as $$
  select * from public.mc_questions where week = p_week and band = p_band and use = 'live'
  order by id offset greatest(p_index, 0) limit 1
$$;

create or replace function public.mc_live_create(p_week int, p_seconds int default 30)
returns public.mc_live_sessions language plpgsql security definer set search_path = public as $$
declare v_code text; r public.mc_live_sessions; v_try int := 0;
begin
  if not public.mc_is_leader() then raise exception 'Leaders only.'; end if;
  if public.mc_live_count(p_week) = 0 then raise exception 'Week % has no live questions.', p_week; end if;
  loop
    v_code := lpad((floor(random() * 10000))::int::text, 4, '0');
    exit when not exists (select 1 from public.mc_live_sessions where code = v_code and status <> 'ended');
    v_try := v_try + 1; if v_try > 50 then raise exception 'Could not make a code, try again.'; end if;
  end loop;
  insert into public.mc_live_sessions (code, week, q_seconds, created_by)
  values (v_code, p_week, p_seconds, auth.uid()) returning * into r;
  return r;
end $$;

-- Leader buttons: 'next' (show the next question), 'reveal' (show answers), 'end'.
create or replace function public.mc_live_control(p_session uuid, p_action text)
returns public.mc_live_sessions language plpgsql security definer set search_path = public as $$
declare r public.mc_live_sessions;
begin
  if not public.mc_is_leader() then raise exception 'Leaders only.'; end if;
  select * into r from public.mc_live_sessions where id = p_session for update;
  if r.id is null then raise exception 'No such session.'; end if;
  if p_action = 'next' then
    if r.q_index + 1 >= public.mc_live_count(r.week) then
      update public.mc_live_sessions set status = 'ended' where id = p_session returning * into r;
    else
      update public.mc_live_sessions set status = 'question', q_index = q_index + 1, q_started_at = now()
      where id = p_session returning * into r;
    end if;
  elsif p_action = 'reveal' then
    update public.mc_live_sessions set status = 'reveal' where id = p_session returning * into r;
  elsif p_action = 'end' then
    update public.mc_live_sessions set status = 'ended' where id = p_session returning * into r;
  else raise exception 'Unknown action.'; end if;
  return r;
end $$;

create or replace function public.mc_live_join(p_code text, p_name text, p_pin text)
returns jsonb language plpgsql security definer set search_path = public as $$
declare s public.mc_students; r public.mc_live_sessions;
begin
  s := public.mc_student_check(p_name, p_pin);
  select * into r from public.mc_live_sessions where code = trim(p_code) and status <> 'ended';
  if r.id is null then raise exception 'No live quiz with that code right now.'; end if;
  insert into public.mc_live_players (session_id, student_id) values (r.id, s.id) on conflict do nothing;
  return jsonb_build_object('session_id', r.id, 'week', r.week, 'band', s.band, 'total', public.mc_live_count(r.week));
end $$;

-- What a child's screen shows right now. Answers appear only after the leader reveals.
create or replace function public.mc_live_state(p_session uuid, p_name text, p_pin text)
returns jsonb language plpgsql stable security definer set search_path = public as $$
declare s public.mc_students; r public.mc_live_sessions; q public.mc_questions; a public.mc_live_answers; v_left int;
begin
  s := public.mc_student_check(p_name, p_pin);
  select * into r from public.mc_live_sessions where id = p_session;
  if r.id is null then raise exception 'No such session.'; end if;
  if r.status in ('question','reveal') then
    q := public.mc_live_question(r.week, s.band, r.q_index);
    select * into a from public.mc_live_answers where session_id = r.id and student_id = s.id and q_index = r.q_index;
  end if;
  v_left := greatest(0, r.q_seconds - floor(extract(epoch from (now() - coalesce(r.q_started_at, now()))))::int);
  return jsonb_build_object(
    'status', r.status, 'q_index', r.q_index, 'total', public.mc_live_count(r.week), 'seconds', r.q_seconds,
    'seconds_left', case when r.status = 'question' then v_left else 0 end,
    'question', case when q.id is null then null else jsonb_build_object('id', q.id, 'kind', q.kind, 'prompt', q.prompt, 'options', q.options) end,
    'answered', a.q_index is not null,
    'reveal', case when r.status = 'reveal' and q.id is not null then
      jsonb_build_object('answer', q.answer, 'explain', q.explain, 'correct', coalesce(a.correct, false), 'points', coalesce(a.points, 0)) end,
    'my_points', (select coalesce(sum(points), 0) from public.mc_live_answers where session_id = r.id and student_id = s.id));
end $$;

-- A child answers. 10 points for a right answer, plus up to 5 for speed.
create or replace function public.mc_live_answer(p_session uuid, p_name text, p_pin text, p_index int, p_value numeric)
returns jsonb language plpgsql security definer set search_path = public as $$
declare s public.mc_students; r public.mc_live_sessions; q public.mc_questions; v_left numeric; v_ok boolean; v_pts int;
begin
  s := public.mc_student_check(p_name, p_pin);
  select * into r from public.mc_live_sessions where id = p_session;
  if r.id is null or r.status <> 'question' or r.q_index <> p_index then
    raise exception 'This question is closed.';
  end if;
  v_left := r.q_seconds - extract(epoch from (now() - r.q_started_at));
  if v_left < -2 then raise exception 'Time is up for this question.'; end if;   -- 2 s grace for slow internet
  if not exists (select 1 from public.mc_live_players where session_id = r.id and student_id = s.id) then
    insert into public.mc_live_players (session_id, student_id) values (r.id, s.id);
  end if;
  q := public.mc_live_question(r.week, s.band, r.q_index);
  v_ok := public.mc_is_right(q, p_value);
  v_pts := case when v_ok then 10 + round(5 * greatest(v_left, 0) / r.q_seconds)::int else 0 end;
  insert into public.mc_live_answers (session_id, student_id, q_index, correct, points)
  values (r.id, s.id, r.q_index, v_ok, v_pts) on conflict do nothing;
  return jsonb_build_object('received', true);
end $$;

-- Scoreboard for one session (names and points only).
create or replace function public.mc_live_scores(p_session uuid)
returns table (name text, band text, points bigint, correct bigint)
language sql stable security definer set search_path = public as $$
  select st.name, st.band, coalesce(sum(a.points), 0) points, count(*) filter (where a.correct) correct
  from public.mc_live_players p join public.mc_students st on st.id = p.student_id
  left join public.mc_live_answers a on a.session_id = p.session_id and a.student_id = p.student_id
  where p.session_id = p_session
  group by st.name, st.band order by points desc, st.name
$$;

-- What the leader's screen shows: the current question for every band, with answers.
create or replace function public.mc_live_host(p_session uuid)
returns jsonb language plpgsql stable security definer set search_path = public as $$
declare r public.mc_live_sessions; v_q jsonb := '{}'; b text; q public.mc_questions;
begin
  if not public.mc_is_leader() then raise exception 'Leaders only.'; end if;
  select * into r from public.mc_live_sessions where id = p_session;
  if r.status in ('question','reveal') then
    foreach b in array array['A','B','C'] loop
      q := public.mc_live_question(r.week, b, r.q_index);
      if q.id is not null then
        v_q := v_q || jsonb_build_object(b, jsonb_build_object('prompt', q.prompt, 'kind', q.kind, 'options', q.options,
          'answer', q.answer, 'explain', q.explain,
          'answered', (select count(*) from public.mc_live_answers a join public.mc_students st on st.id = a.student_id
                       where a.session_id = r.id and a.q_index = r.q_index and st.band = b),
          'right', (select count(*) from public.mc_live_answers a join public.mc_students st on st.id = a.student_id
                    where a.session_id = r.id and a.q_index = r.q_index and st.band = b and a.correct)));
      end if;
    end loop;
  end if;
  return jsonb_build_object('session', to_jsonb(r), 'total', public.mc_live_count(r.week),
    'players', (select count(*) from public.mc_live_players where session_id = r.id), 'questions', v_q);
end $$;

-- ---------------------------------------------------------------------
-- Leaderboard: 10 points per right answer on a first daily try,
-- live quiz points, and 20 points per coding challenge.
-- ---------------------------------------------------------------------
create or replace function public.mc_leaderboard(p_week int default null)
returns table (name text, band text, daily_points bigint, live_points bigint, code_points bigint, total bigint)
language sql stable security definer set search_path = public as $$
  with d as (select student_id, sum(score) * 10 pts from public.mc_attempts
             where counted and (p_week is null or week = p_week) group by student_id),
       l as (select a.student_id, sum(a.points) pts from public.mc_live_answers a
             join public.mc_live_sessions s on s.id = a.session_id
             where p_week is null or s.week = p_week group by a.student_id),
       c as (select student_id, count(*) * 20 pts from public.mc_code_done
             where p_week is null or challenge like 'w' || lpad(p_week::text, 2, '0') || '-%' group by student_id)
  select st.name, st.band, coalesce(d.pts, 0), coalesce(l.pts, 0), coalesce(c.pts, 0),
         coalesce(d.pts, 0) + coalesce(l.pts, 0) + coalesce(c.pts, 0) total
  from public.mc_students st
  left join d on d.student_id = st.id left join l on l.student_id = st.id left join c on c.student_id = st.id
  where st.active order by total desc, st.name
$$;

-- Leader: one week's results for every child.
create or replace function public.mc_week_results(p_week int)
returns jsonb language plpgsql stable security definer set search_path = public as $$
begin
  if not public.mc_is_leader() then raise exception 'Leaders only.'; end if;
  return coalesce((select jsonb_agg(jsonb_build_object('name', st.name, 'band', st.band, 'grade', st.grade,
    'days', (select coalesce(jsonb_object_agg(day::text, jsonb_build_object('first', first, 'best', best, 'tries', n)), '{}')
             from (select day, max(case when counted then score end) first, max(score) best, count(*) n
                   from public.mc_attempts where student_id = st.id and week = p_week group by day) t),
    'code', (select count(*) from public.mc_code_done where student_id = st.id and challenge like 'w' || lpad(p_week::text, 2, '0') || '-%'))
    order by st.band, lower(st.name))
    from public.mc_students st where st.active), '[]');
end $$;

-- ---------------------------------------------------------------------
-- Permissions
-- ---------------------------------------------------------------------
revoke all on public.mc_students, public.mc_questions, public.mc_attempts, public.mc_code_done,
  public.mc_live_players, public.mc_live_answers, public.mc_leaders from anon;
grant select on public.mc_roster_public, public.mc_questions_public to anon, authenticated;
grant select on public.mc_weeks, public.mc_live_sessions to anon, authenticated;

revoke execute on function public.mc_student_check(text, text) from public, anon, authenticated;
revoke execute on function public.mc_live_question(int, text, int) from public, anon, authenticated;
revoke execute on function public.mc_is_right(public.mc_questions, numeric) from public, anon, authenticated;

-- Live updates: children's screens follow the session row.
do $$ begin
  if exists (select 1 from pg_publication where pubname = 'supabase_realtime')
     and not exists (select 1 from pg_publication_tables where pubname = 'supabase_realtime' and tablename = 'mc_live_sessions') then
    alter publication supabase_realtime add table public.mc_live_sessions;
  end if;
end $$;

notify pgrst, 'reload schema';

select 'Setup complete' as status,
  (select count(*) from public.mc_weeks) as weeks,
  (select count(*) from public.mc_questions) as questions;
`;export{e as default};
