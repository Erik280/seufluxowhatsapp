-- ============================================================
-- SEED DATA - SISTEMA ATENDIMENTO WHATSAPP
-- Dados iniciais para desenvolvimento e testes
-- ============================================================

-- Empresa demo
INSERT INTO public.companies (id, name, cnpj, evolution_instance, evolution_apikey, is_active, plan_status)
VALUES (
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    'Transforma Futuro Demo',
    '00.000.000/0001-00',
    'tf-demo-instance',
    'your_evolution_api_key_here',
    true,
    'active'
) ON CONFLICT DO NOTHING;

-- SuperAdmin (ID especial definido no sistema)
INSERT INTO public.users (id, company_id, full_name, email, password_hash, role)
VALUES (
    'fd7e3273-4e7a-43df-80ed-1d00591cd656',
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    'Super Administrador',
    'superadmin@transformafuturo.com',
    -- senha: Admin@2024 (bcrypt hash)
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/Lew8sC5AOb3RHYIY2',
    'superadmin'
) ON CONFLICT (id) DO UPDATE SET role = 'superadmin';

-- Admin da empresa demo
INSERT INTO public.users (id, company_id, full_name, email, password_hash, role)
VALUES (
    uuid_generate_v4(),
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    'Admin Demo',
    'admin@demo.com',
    -- senha: Demo@2024
    '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi',
    'admin'
) ON CONFLICT DO NOTHING;

-- Agente de atendimento demo
INSERT INTO public.users (id, company_id, full_name, email, password_hash, role)
VALUES (
    uuid_generate_v4(),
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    'Agente Demo',
    'agente@demo.com',
    -- senha: Demo@2024
    '$2b$12$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi',
    'agent'
) ON CONFLICT DO NOTHING;

-- Tags padrão
INSERT INTO public.tags (company_id, name, color) VALUES
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'VIP', '#FFD700'),
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'Urgente', '#FF4444'),
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'Aguardando', '#FFA500'),
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'Resolvido', '#00CC66'),
('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'Novo Lead', '#00E5CC')
ON CONFLICT DO NOTHING;

-- Flow de bots padrão: Saudação
INSERT INTO public.chat_flows (id, company_id, name, trigger_keyword, match_type, is_active, priority)
VALUES (
    'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    'Saudação Inicial',
    'oi,olá,ola,hello,bom dia,boa tarde,boa noite,start',
    'contains',
    true,
    10
) ON CONFLICT DO NOTHING;

-- Steps do flow de saudação
INSERT INTO public.flow_steps (flow_id, message_type, content, delay_seconds, typing_indicator, position)
VALUES
(
    'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
    'text',
    '👋 Olá! Seja bem-vindo(a) à *Transforma Futuro*!\n\nSou seu assistente virtual. Como posso ajudar você hoje?',
    1,
    true,
    1
),
(
    'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
    'text',
    '📋 Escolha uma opção:\n\n1️⃣ Informações sobre nossos serviços\n2️⃣ Falar com um atendente\n3️⃣ Suporte técnico',
    2,
    true,
    2
);

-- Flow: BANCADA AUTOMATICA
INSERT INTO public.chat_flows (id, company_id, name, trigger_keyword, match_type, is_active, priority)
VALUES (
    'cccccccc-cccc-cccc-cccc-cccccccccccc',
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    'Bancada Automática',
    'BANCADA AUTOMATICA',
    'exact',
    true,
    100
) ON CONFLICT DO NOTHING;

INSERT INTO public.flow_steps (flow_id, message_type, content, delay_seconds, typing_indicator, position)
VALUES
(
    'cccccccc-cccc-cccc-cccc-cccccccccccc',
    'text',
    '🔧 Abrindo a *Bancada Automática*...\n\nAguarde um momento, estamos preparando seu atendimento especializado.',
    1,
    true,
    1
);

-- Contatos demo
INSERT INTO public.contacts (company_id, phone, full_name, email, chat_status, last_interaction)
VALUES
(
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    '5511999990001',
    'João Silva',
    'joao@example.com',
    'human',
    NOW() - INTERVAL '5 minutes'
),
(
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    '5511999990002',
    'Maria Santos',
    'maria@example.com',
    'bot',
    NOW() - INTERVAL '1 hour'
),
(
    'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
    '5511999990003',
    'Carlos Pereira',
    NULL,
    'bot',
    NOW() - INTERVAL '2 hours'
)
ON CONFLICT DO NOTHING;
