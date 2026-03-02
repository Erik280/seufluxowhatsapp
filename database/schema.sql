-- ============================================================
-- SCHEMA COMPLETO - SISTEMA ATENDIMENTO WHATSAPP SAAS
-- Executar no Supabase SQL Editor
-- ============================================================

-- Extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ============================================================
-- TABELA: companies
-- ============================================================
CREATE TABLE IF NOT EXISTS public.companies (
    id uuid NOT NULL DEFAULT uuid_generate_v4(),
    name text NOT NULL,
    cnpj text UNIQUE,
    evolution_instance text,
    evolution_apikey text,
    is_active boolean DEFAULT true,
    plan_status text DEFAULT 'active' CHECK (plan_status IN ('active', 'suspended', 'trial')),
    created_at timestamp with time zone DEFAULT now(),
    CONSTRAINT companies_pkey PRIMARY KEY (id)
);

-- ============================================================
-- TABELA: users
-- ============================================================
CREATE TABLE IF NOT EXISTS public.users (
    id uuid NOT NULL DEFAULT uuid_generate_v4(),
    company_id uuid REFERENCES public.companies(id) ON DELETE CASCADE,
    full_name text NOT NULL,
    email text NOT NULL UNIQUE,
    password_hash text NOT NULL,
    role text DEFAULT 'agent' CHECK (role IN ('superadmin', 'admin', 'agent')),
    avatar_url text,
    is_online boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT now(),
    CONSTRAINT users_pkey PRIMARY KEY (id)
);

-- ============================================================
-- TABELA: tags
-- ============================================================
CREATE TABLE IF NOT EXISTS public.tags (
    id uuid NOT NULL DEFAULT uuid_generate_v4(),
    company_id uuid REFERENCES public.companies(id) ON DELETE CASCADE,
    name text NOT NULL,
    color text DEFAULT '#3498db',
    CONSTRAINT tags_pkey PRIMARY KEY (id),
    CONSTRAINT tags_company_name_unique UNIQUE (company_id, name)
);

-- ============================================================
-- TABELA: contacts
-- ============================================================
CREATE TABLE IF NOT EXISTS public.contacts (
    id uuid NOT NULL DEFAULT uuid_generate_v4(),
    company_id uuid REFERENCES public.companies(id) ON DELETE CASCADE,
    phone text NOT NULL,
    full_name text,
    email text,
    address jsonb DEFAULT '{}'::jsonb,
    notes text,
    chat_status text DEFAULT 'bot' CHECK (chat_status IN ('bot', 'human', 'paused')),
    assigned_agent_id uuid REFERENCES public.users(id) ON DELETE SET NULL,
    last_interaction timestamp with time zone DEFAULT now(),
    unread_count integer DEFAULT 0,
    created_at timestamp with time zone DEFAULT now(),
    CONSTRAINT contacts_pkey PRIMARY KEY (id),
    CONSTRAINT contacts_company_phone_unique UNIQUE (company_id, phone)
);

-- ============================================================
-- TABELA: contact_tags (relação N:N)
-- ============================================================
CREATE TABLE IF NOT EXISTS public.contact_tags (
    contact_id uuid NOT NULL REFERENCES public.contacts(id) ON DELETE CASCADE,
    tag_id uuid NOT NULL REFERENCES public.tags(id) ON DELETE CASCADE,
    CONSTRAINT contact_tags_pkey PRIMARY KEY (contact_id, tag_id)
);

-- ============================================================
-- TABELA: messages_history
-- ============================================================
CREATE TABLE IF NOT EXISTS public.messages_history (
    id uuid NOT NULL DEFAULT uuid_generate_v4(),
    company_id uuid REFERENCES public.companies(id) ON DELETE CASCADE,
    contact_id uuid REFERENCES public.contacts(id) ON DELETE CASCADE,
    direction text CHECK (direction IN ('in', 'out')),
    message_type text DEFAULT 'text' CHECK (message_type IN ('text', 'image', 'audio', 'video', 'document', 'sticker')),
    content text,
    media_url text,
    media_mime_type text,
    evolution_message_id text,
    status text DEFAULT 'received' CHECK (status IN ('received', 'sent', 'delivered', 'read', 'failed')),
    timestamp timestamp with time zone DEFAULT now(),
    CONSTRAINT messages_history_pkey PRIMARY KEY (id)
);

-- ============================================================
-- TABELA: chat_flows (gatilhos de bot)
-- ============================================================
CREATE TABLE IF NOT EXISTS public.chat_flows (
    id uuid NOT NULL DEFAULT uuid_generate_v4(),
    company_id uuid REFERENCES public.companies(id) ON DELETE CASCADE,
    name text NOT NULL,
    trigger_keyword text NOT NULL,
    match_type text DEFAULT 'contains' CHECK (match_type IN ('exact', 'contains', 'starts_with', 'regex')),
    is_active boolean DEFAULT true,
    priority integer DEFAULT 0,
    created_at timestamp with time zone DEFAULT now(),
    CONSTRAINT chat_flows_pkey PRIMARY KEY (id)
);

-- ============================================================
-- TABELA: flow_steps
-- ============================================================
CREATE TABLE IF NOT EXISTS public.flow_steps (
    id uuid NOT NULL DEFAULT uuid_generate_v4(),
    flow_id uuid REFERENCES public.chat_flows(id) ON DELETE CASCADE,
    message_type text CHECK (message_type IN ('text', 'image', 'audio', 'video')),
    content text,
    media_url text,
    delay_seconds integer DEFAULT 2,
    typing_indicator boolean DEFAULT true,
    position integer NOT NULL,
    CONSTRAINT flow_steps_pkey PRIMARY KEY (id)
);

-- ============================================================
-- TABELA: broadcasts
-- ============================================================
CREATE TABLE IF NOT EXISTS public.broadcasts (
    id uuid NOT NULL DEFAULT uuid_generate_v4(),
    company_id uuid REFERENCES public.companies(id) ON DELETE CASCADE,
    title text,
    content text NOT NULL,
    media_url text,
    media_type text,
    target_tags jsonb DEFAULT '[]'::jsonb,
    target_phone_list jsonb DEFAULT '[]'::jsonb,
    scheduled_at timestamp with time zone,
    sent_at timestamp with time zone,
    status text DEFAULT 'pending' CHECK (status IN ('pending', 'sending', 'completed', 'failed', 'cancelled')),
    sent_count integer DEFAULT 0,
    failed_count integer DEFAULT 0,
    created_by uuid REFERENCES public.users(id),
    created_at timestamp with time zone DEFAULT now(),
    CONSTRAINT broadcasts_pkey PRIMARY KEY (id)
);

-- ============================================================
-- TABELA: system_logs
-- ============================================================
CREATE TABLE IF NOT EXISTS public.system_logs (
    id uuid NOT NULL DEFAULT uuid_generate_v4(),
    company_id uuid REFERENCES public.companies(id) ON DELETE SET NULL,
    user_id uuid REFERENCES public.users(id) ON DELETE SET NULL,
    action text NOT NULL,
    details jsonb DEFAULT '{}'::jsonb,
    ip_address text,
    created_at timestamp with time zone DEFAULT now(),
    CONSTRAINT system_logs_pkey PRIMARY KEY (id)
);

-- ============================================================
-- ÍNDICES DE PERFORMANCE
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_contacts_company_id ON public.contacts(company_id);
CREATE INDEX IF NOT EXISTS idx_contacts_phone ON public.contacts(phone);
CREATE INDEX IF NOT EXISTS idx_contacts_last_interaction ON public.contacts(last_interaction DESC);
CREATE INDEX IF NOT EXISTS idx_contacts_chat_status ON public.contacts(chat_status);
CREATE INDEX IF NOT EXISTS idx_messages_contact_id ON public.messages_history(contact_id);
CREATE INDEX IF NOT EXISTS idx_messages_company_id ON public.messages_history(company_id);
CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON public.messages_history(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_broadcasts_company_id ON public.broadcasts(company_id);
CREATE INDEX IF NOT EXISTS idx_broadcasts_scheduled_at ON public.broadcasts(scheduled_at);
CREATE INDEX IF NOT EXISTS idx_broadcasts_status ON public.broadcasts(status);
CREATE INDEX IF NOT EXISTS idx_system_logs_company_id ON public.system_logs(company_id);
CREATE INDEX IF NOT EXISTS idx_system_logs_created_at ON public.system_logs(created_at DESC);

-- ============================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================
ALTER TABLE public.companies ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.contacts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.tags ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.messages_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_flows ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.flow_steps ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.broadcasts ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.system_logs ENABLE ROW LEVEL SECURITY;

-- Políticas permissivas para service role (backend usa service key)
CREATE POLICY "service_all" ON public.companies FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_all" ON public.users FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_all" ON public.contacts FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_all" ON public.tags FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_all" ON public.contact_tags FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_all" ON public.messages_history FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_all" ON public.chat_flows FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_all" ON public.flow_steps FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_all" ON public.broadcasts FOR ALL USING (true) WITH CHECK (true);
CREATE POLICY "service_all" ON public.system_logs FOR ALL USING (true) WITH CHECK (true);

-- ============================================================
-- REALTIME (habilitar para mensagens instantâneas)
-- ============================================================
ALTER PUBLICATION supabase_realtime ADD TABLE public.messages_history;
ALTER PUBLICATION supabase_realtime ADD TABLE public.contacts;
ALTER PUBLICATION supabase_realtime ADD TABLE public.broadcasts;
