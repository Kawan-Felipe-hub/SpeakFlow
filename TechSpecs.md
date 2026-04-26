# Tech Specs — SpeakFlow

## 0) Objetivo e escopo técnico

O SpeakFlow é um mini ecossistema educacional de inglês com:
- **Tutor de voz conversacional com IA (web)**: STT/TTS + avaliação de pronúncia + feedback.
- **Flashcards + SRS (web e mobile)**: criação assistida de cards e revisões com SM-2.
- **App mobile Flutter offline-first (companion)**: foco estrito em revisão SRS offline com sincronização (last write wins).

Este documento define decisões arquiteturais, modelo de dados e fluxos críticos, visando **MVP pragmático**, **baixo custo** (free tiers) e **evolução incremental**.

## 1) Decisões de arquitetura (com justificativas)

### 1.1 Separação por superfícies (Web vs Mobile)
- **Web (Next.js)** concentra o fluxo de conversa por voz (mais fácil de iterar UI/IA, menor fricção de distribuição).
- **Mobile (Flutter)** atua como **companion offline-first** para revisões SRS, atendendo o requisito do desafio técnico sem duplicar a complexidade do tutor de voz.

**Justificativa**: reduz escopo do mobile, garante entrega, e mantém o offline-first “real” em um domínio bem definido (SRS), com dados pequenos e sincronização robusta.

### 1.2 Backend monolítico modular (Django 5 + Ninja)
- Django serve como **núcleo de domínio** (usuário, sessões, cards, revisões, sync).
- Django Ninja oferece **APIs tipadas e rápidas** (OpenAPI), adequadas para web e mobile.

**Justificativa**: alta produtividade, ecossistema maduro, boa integração com Postgres, e simplicidade operacional no Railway.

### 1.3 Postgres como fonte de verdade + SQLite no mobile
- **Postgres 16** é o **source of truth**.
- **SQLite** no Flutter garante funcionamento offline e baixa latência nas revisões.

**Justificativa**: Postgres é robusto para SaaS; SQLite é padrão para offline-first.

### 1.4 Integrações externas (Azure Speech + Groq)
- **Azure Speech SDK** para STT/TTS e Pronunciation Assessment (limitado ao free tier).
- **Groq API (Llama 3.3 70B)** para geração de respostas do tutor e geração de feedback/itens sugeridos para cards.

**Justificativa**: melhor custo/benefício no MVP (free tiers), baixa latência (Groq) e serviços prontos (Azure).

### 1.5 Contratos estáveis e observabilidade mínima
- APIs versionadas (ex.: `/api/v1/...`) e payloads estáveis para permitir evolução independente.
- Logs estruturados e métricas básicas (latência, erros por serviço).

**Justificativa**: integrações STT/TTS/LLM são fontes comuns de instabilidade; instrumentação reduz tempo de debug.

### 1.6 SRS: SM-2 “puro” e determinístico
- Algoritmo SM-2 implementado em Python no backend para web.
- No mobile, o cálculo SM-2 é feito localmente (offline) e sincronizado como eventos de revisão.

**Justificativa**: algoritmo simples, determinístico e comprovado; facilita consistência entre plataformas.

## 2) Diagrama de componentes (Mermaid)

```mermaid
flowchart LR
  subgraph Web["Web SaaS (Next.js 14)"]
    W1["UI Conversa por voz"]
    W2["UI Flashcards / Revisão"]
  end

  subgraph Mobile["Mobile (Flutter 3.x) — Offline-first"]
    M1["UI Login"]
    M2["SQLite (cards, srs_state, review_events)"]
    M3["UI Revisão SRS (0–5)"]
    M4["Sync Worker (LWW)"]
  end

  subgraph Backend["Backend (Django 5 + Ninja)"]
    B1["API Gateway (Ninja)"]
    B2["Auth (JWT)"]
    B3["Conversas: Sessions/Turns"]
    B4["SRS Service (SM-2)"]
    B5["Sync API (pull/push)"]
    B6["PostgreSQL 16"]
  end

  subgraph External["Serviços externos"]
    A1["Azure Speech (STT/TTS/Pronunciation)"]
    G1["Groq LLM (Llama 3.3 70B)"]
  end

  W1 -->|audio/text| B1
  W2 --> B1
  M1 --> B1
  M4 -->|push/pull| B5

  B1 --> B2
  B1 --> B3
  B1 --> B4
  B5 --> B6
  B3 --> B6
  B4 --> B6

  B3 <-->|STT/TTS/score| A1
  B3 <-->|prompts/respostas| G1

  M3 <--> M2
  M4 <--> M2
```

## 3) Modelo de dados (tabelas principais)

> Tipos seguem convenções Postgres. Em Django: `UUIDField`, `TextField`, `JSONField`, `DateTimeField`, etc.

### 3.1 Autenticação e usuários

#### `users`
- `id` **uuid** (PK)
- `email` **varchar(254)** (unique, not null)
- `password_hash` **text** (se auth por senha; ou campos equivalentes do Django auth)
- `is_active` **boolean** (default true)
- `created_at` **timestamptz** (default now)
- `updated_at` **timestamptz**

#### `refresh_tokens` (opcional, se houver refresh token rotativo)
- `id` **uuid** (PK)
- `user_id` **uuid** (FK → users.id)
- `token_hash` **text**
- `expires_at` **timestamptz**
- `revoked_at` **timestamptz** (nullable)
- `created_at` **timestamptz**

### 3.2 Conversas (sessões e turnos)

#### `conversation_sessions`
- `id` **uuid** (PK)
- `user_id` **uuid** (FK)
- `topic` **varchar(64)** (ex.: `job_interview`, `daily_meeting`, `airport`, `restaurant`, `small_talk`)
- `level` **varchar(16)** (ex.: `basic|intermediate|advanced`)
- `started_at` **timestamptz**
- `ended_at` **timestamptz** (nullable)
- `metadata` **jsonb** (nullable; device, locale, etc.)

#### `conversation_turns`
- `id` **uuid** (PK)
- `session_id` **uuid** (FK → conversation_sessions.id)
- `role` **varchar(16)** (`user|tutor`)
- `stt_text` **text** (nullable; para turnos do usuário)
- `final_text` **text** (not null; texto exibido como “conteúdo final” do turno)
- `llm_model` **varchar(64)** (nullable; ex.: `llama-3.3-70b`)
- `created_at` **timestamptz**
- `latency_ms` **int** (nullable; latência end-to-end do turno)
- `status` **varchar(16)** (`ok|failed`)
- `error_code` **varchar(64)** (nullable)

#### `pronunciation_assessments`
- `id` **uuid** (PK)
- `turn_id` **uuid** (FK → conversation_turns.id, unique por turno do usuário)
- `provider` **varchar(32)** (default `azure`)
- `overall_score` **numeric(5,2)** (0–100)
- `accuracy_score` **numeric(5,2)** (nullable)
- `fluency_score` **numeric(5,2)** (nullable)
- `completeness_score` **numeric(5,2)** (nullable)
- `prosody_score` **numeric(5,2)** (nullable)
- `raw` **jsonb** (payload bruto para auditoria)
- `created_at` **timestamptz**

### 3.3 Flashcards e SRS

#### `decks`
- `id` **uuid** (PK)
- `user_id` **uuid** (FK)
- `name` **varchar(120)**
- `created_at` **timestamptz**

#### `cards`
- `id` **uuid** (PK)
- `user_id` **uuid** (FK)
- `deck_id` **uuid** (FK → decks.id, nullable no MVP)
- `front` **text** (prompt)
- `back` **text** (resposta)
- `source_type` **varchar(32)** (`conversation_suggestion|manual`)
- `source_ref` **uuid** (nullable; ex.: `turn_id`)
- `language` **varchar(16)** (default `en`)
- `created_at` **timestamptz**
- `updated_at` **timestamptz**

#### `srs_states` (estado SM-2 por card)
- `id` **uuid** (PK)
- `card_id` **uuid** (FK → cards.id, unique)
- `repetition` **int** (default 0)
- `interval_days` **int** (default 1)
- `ease_factor` **numeric(3,2)** (default 2.50)
- `due_at` **timestamptz**
- `last_reviewed_at` **timestamptz** (nullable)
- `updated_at` **timestamptz**

#### `srs_review_events` (event sourcing leve)
- `id` **uuid** (PK)
- `user_id` **uuid** (FK)
- `card_id` **uuid** (FK)
- `quality` **smallint** (0–5)
- `reviewed_at` **timestamptz** (momento da revisão no dispositivo/cliente)
- `client_id` **varchar(64)** (ex.: `web|mobile:<device_id>`)
- `client_event_id` **uuid** (idempotência; unique por client)
- `sync_status` **varchar(16)** (`pending|synced|conflict|rejected`)
- `created_at` **timestamptz**

### 3.4 Sync (mobile)

#### `client_devices` (opcional, recomendado)
- `id` **uuid** (PK)
- `user_id` **uuid** (FK)
- `device_id` **varchar(128)** (unique por usuário)
- `platform` **varchar(16)** (`android|ios`)
- `last_seen_at` **timestamptz**
- `created_at` **timestamptz**

#### Campos de suporte a sincronização (em tabelas existentes)
- `cards.updated_at` e `srs_states.updated_at` são essenciais para pull incremental.
- `srs_review_events.client_event_id` permite push idempotente.

## 4) Fluxo completo da sessão de voz (Web)

### 4.1 Objetivo do fluxo
Garantir uma experiência de conversa fluida, mitigando latência com estados visuais (“Ouvindo…”, “Transcrevendo…”, “Pensando…”), mantendo o feedback detalhado colapsado por padrão e permitindo replay do último áudio do tutor.

### 4.2 Sequência ponta a ponta (turno do usuário)
1. **UI (Web)** inicia gravação de áudio (WebAudio/MediaRecorder).
2. UI encerra gravação e envia áudio (ou referência) ao backend.
3. **Backend → Azure STT**:
   - transcreve áudio em texto.
   - retorna `stt_text`.
4. **Backend → Azure Pronunciation Assessment** (no mesmo áudio):
   - retorna scores e payload bruto.
   - persiste em `pronunciation_assessments`.
5. **Backend → Groq LLM**:
   - monta prompt com contexto (tema, nível, histórico curto da sessão).
   - gera:
     - resposta do tutor,
     - feedback resumido + correções,
     - sugestões de termos/frases para cards (criação assistida).
6. **Backend → Azure TTS**:
   - converte resposta do tutor em áudio.
7. **Backend** persiste:
   - `conversation_turns` (usuário e tutor),
   - latências e status.
8. **UI (Web)** renderiza:
   - transcrição do usuário,
   - resposta do tutor (texto) + áudio com botão **Replay**,
   - feedback (colapsado por padrão).

### 4.3 Considerações de performance
- **Batching**: sempre que possível, fazer STT + Pronunciation no mesmo request/config.
- **Timeouts**: limites agressivos e fallback para texto sem áudio.
- **Cache**: não recomendado para TTS por ser conteúdo dinâmico; apenas para vozes/configurações.

## 5) Estratégia de autenticação (JWT)

### 5.1 Fluxo
- **Login** (email/senha ou magic link no futuro) retorna:
  - `access_token` (JWT curto, ex.: 15 min)
  - `refresh_token` (opcional, ex.: 30 dias) com rotação e revogação
- Requests autenticados incluem `Authorization: Bearer <access_token>`.

### 5.2 Claims recomendadas
- `sub`: user id (uuid)
- `email`
- `iat`, `exp`
- `jti`: id do token (para revogação/rotação)

### 5.3 Armazenamento por cliente
- **Web**: preferir cookie `HttpOnly` para refresh e access via mecanismo seguro (ou access em memória).
- **Mobile**: armazenar tokens com `flutter_secure_storage`.

### 5.4 Endpoints (exemplo)
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh` (se aplicável)
- `POST /api/v1/auth/logout` (revoga refresh)

## 6) Estratégia de sync offline (Flutter → Django) — Last Write Wins

### 6.1 Premissas
- Mobile funciona 100% offline para:
  - listar cards pendentes (cache local),
  - revisar (SM-2 local),
  - registrar eventos de revisão localmente.
- Backend é fonte de verdade, mas **mobile pode produzir eventos offline**.

### 6.2 Dados locais (SQLite)
Tabelas locais sugeridas:
- `cards` (snapshot mínimo: `id`, `front`, `back`, `updated_at`)
- `srs_state` (estado SM-2 local por card)
- `review_events` (fila de eventos: `client_event_id`, `card_id`, `quality`, `reviewed_at`, `created_at`, `synced_at`, `sync_error`)
- `sync_cursor` (marca d’água: último `updated_at`/`server_sequence`)

### 6.3 Pull (server → mobile)
- Endpoint: `GET /api/v1/mobile/sync/pull?since=<cursor>`
  - retorna cards e `srs_states` atualizados desde `since`.
  - retorna novo `cursor`.

### 6.4 Push (mobile → server)
- Endpoint: `POST /api/v1/mobile/sync/push`
  - envia lote de `review_events` (cada um com `client_event_id` para idempotência).
  - backend aplica SM-2 no servidor (ou aplica o estado enviado com validação) e persiste `srs_review_events`.

### 6.5 Resolução de conflitos (LWW)
Política: **Last Write Wins com base no `reviewed_at` do evento local**.
- Para cada `card_id`, ao aplicar um evento:
  - se `reviewed_at` > `srs_states.last_reviewed_at` (ou null), aplica e atualiza estado.
  - se `reviewed_at` <= `last_reviewed_at`, marca evento como `conflict` ou `rejected` (mas mantém log).

**Observação**: LWW funciona bem porque revisões são eventos temporais; o objetivo é evitar regressão de estado por eventos atrasados.

### 6.6 Idempotência e robustez
- `client_event_id` unique no backend por `client_id` (ou global) evita duplicação.
- Push em lote deve ser **atômico por evento**: falha de um não impede aceitar os demais, retornando status por item.

## 7) Variáveis de ambiente necessárias

### 7.1 Backend (Django)
- **Core**
  - `DJANGO_SECRET_KEY`
  - `DJANGO_DEBUG` (`true|false`)
  - `DJANGO_ALLOWED_HOSTS` (csv)
  - `DATABASE_URL` (Railway/Local)
  - `CORS_ALLOWED_ORIGINS` (csv)
  - `CSRF_TRUSTED_ORIGINS` (csv)
- **JWT**
  - `JWT_SIGNING_KEY` (ou reutilizar secret key com rotação planejada)
  - `JWT_ACCESS_TTL_MINUTES` (ex.: 15)
  - `JWT_REFRESH_TTL_DAYS` (ex.: 30, se usar refresh)
- **Groq**
  - `GROQ_API_KEY`
  - `GROQ_MODEL` (ex.: `llama-3.3-70b-versatile` — ajustar ao nome real usado)
- **Azure Speech**
  - `AZURE_SPEECH_KEY`
  - `AZURE_SPEECH_REGION`
  - `AZURE_SPEECH_LANGUAGE` (ex.: `en-US`)
  - `AZURE_SPEECH_VOICE` (ex.: `en-US-JennyNeural`)
- **Observabilidade (mínimo)**
  - `LOG_LEVEL` (ex.: `INFO`)

### 7.2 Frontend Web (Next.js)
- `NEXT_PUBLIC_API_BASE_URL`
- `NEXT_PUBLIC_APP_ENV` (`local|staging|prod`)
- (se necessário) `NEXT_PUBLIC_AZURE_SPEECH_REGION` (preferir que STT/TTS seja via backend no MVP)

### 7.3 Mobile (Flutter)
- `API_BASE_URL` (via build config/flavors)
- `APP_ENV`

### 7.4 Docker Compose (local)
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
- `DATABASE_URL` apontando para o container

## 8) Riscos técnicos e mitigações

### 8.1 Limites do free tier (Azure Speech 5h/mês)
- **Risco**: consumo rápido por usuários ativos; falhas por quota.
- **Mitigação**:
  - limitar minutos/turnos por dia no plano free,
  - caching de configurações, timeouts agressivos,
  - fallback para modo texto (sem TTS) quando quota/erro.

### 8.2 Latência end-to-end (STT + LLM + TTS)
- **Risco**: conversa “parece lenta”, reduz retenção.
- **Mitigação**:
  - loaders explícitos (“Ouvindo…/Transcrevendo…/Pensando…”),
  - streaming onde possível (texto primeiro, áudio depois),
  - feedback detalhado colapsado por padrão,
  - medir P50/P95 e otimizar hotspots.

### 8.3 Qualidade variável de STT/pronúncia (ruído, sotaque, microfone)
- **Risco**: frustração e feedback incorreto.
- **Mitigação**:
  - instruções de microfone/ambiente,
  - permitir repetir turno,
  - apresentar score com faixas e disclaimers (“pode variar com ruído”).

### 8.4 Consistência do SM-2 entre mobile (local) e backend
- **Risco**: divergência de estado e agendamento.
- **Mitigação**:
  - tratar revisões como **eventos** (review_events) e recomputar estado no backend,
  - LWW baseado em `reviewed_at`,
  - testes de contrato (mesmos parâmetros/limites do SM-2).

### 8.5 Sync offline e duplicação de eventos
- **Risco**: eventos duplicados ou perdidos em reconexões instáveis.
- **Mitigação**:
  - idempotência com `client_event_id`,
  - retornos por item no push,
  - backoff exponencial no worker.

### 8.6 Custos e limites do Railway (free tier)
- **Risco**: sleeping/latência cold start, limites de conexão.
- **Mitigação**:
  - endpoints leves, conexões DB eficientes,
  - healthcheck e warmup simples,
  - separar landing e app apenas se necessário (ou monorepo com rotas).

### 8.7 Segurança (JWT, CORS, armazenamento de tokens)
- **Risco**: vazamento de token e acesso indevido.
- **Mitigação**:
  - TTL curto para access token,
  - refresh token rotativo + revogação,
  - armazenamento seguro no mobile,
  - CORS/CSRF configurados corretamente.

