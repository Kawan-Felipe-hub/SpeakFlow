# PRD — SpeakFlow (Mini ecossistema educacional de inglês)

## 1) Visão e proposta de valor

### 1.1 Visão
Criar a forma mais simples e consistente de desenvolver **fluência conversacional** em inglês por meio de prática diária guiada por IA, com foco em **fala (speaking)**, **pronúncia** e **retenção de vocabulário**.

### 1.2 Problema
- A maioria dos estudantes até “entende” inglês, mas **não consegue falar** com naturalidade por falta de prática real.
- Prática com humanos é cara, limitada por agenda e pode gerar ansiedade.
- Sem um sistema de revisão, o aluno esquece vocabulário rapidamente e perde motivação.

### 1.3 Proposta de valor (SpeakFlow)
- **Tutor de voz conversacional com IA**: prática ilimitada, com contexto, correções e metas claras.
- **Feedback de pronúncia**: avaliação objetiva e acionável (Azure Speech Pronunciation Assessment).
- **Flashcards com repetição espaçada (SRS)**: retenção de vocabulário e frases extraídas das conversas.
- **Loop fechado**: conversa → detecta lacunas → gera cards → revisa → melhora a conversa.

### 1.4 Para quem é
Pessoas que querem **falar inglês** (trabalho, viagens, estudos) e precisam de um treino prático e contínuo, com baixo custo.

### 1.5 Diferenciais
- **Voice-first**: experiência centrada em voz (não só chat).
- **Pronúncia mensurável**: progresso baseado em métricas (ex.: fluência, precisão).
- **SRS integrado às conversas**: cards gerados do que o aluno realmente usa/erra.
- **Arquitetura simples e pragmática** para MVP com custo baixo (free tiers).

## 2) Personas (usuários-alvo)

### Persona A — “Júlia, a profissional em transição”
- **Idade**: 26–34
- **Contexto**: trabalha em tech/negócios; quer entrevistas e reuniões em inglês.
- **Objetivo**: falar com confiança em calls e entrevistas.
- **Dores**: medo de errar, pronúncia, travar no meio da frase; falta de consistência.
- **Critério de sucesso pessoal**: fazer uma reunião de 20 minutos em inglês sem travar.

### Persona B — “Carlos, o autodidata consistente”
- **Idade**: 18–28
- **Contexto**: aprende sozinho; gosta de apps e métricas; treina 10–20 min/dia.
- **Objetivo**: manter rotina e ver progresso mensurável.
- **Dores**: dispersão; conteúdo genérico; não sabe o que revisar.
- **Critério de sucesso pessoal**: streak de 30 dias + evolução em métricas de pronúncia.

### Persona C — “Marina, a viajante prática”
- **Idade**: 30–45
- **Contexto**: vai viajar e precisa do “inglês funcional” em situações reais.
- **Objetivo**: dominar frases e respostas rápidas (hotel, aeroporto, restaurante).
- **Dores**: tempo curto; quer simulações realistas e frases úteis.
- **Critério de sucesso pessoal**: conseguir se virar em 10 cenários com segurança.

## 3) Funcionalidades core (MVP) vs nice-to-have

### 3.1 MVP (obrigatório)

#### A) Tutor de voz conversacional (core)
- **Sessões de conversa por voz** com papéis/temas (ex.: entrevista, viagem, small talk).
- **STT** (fala → texto) e **TTS** (texto → fala) via Azure Speech.
- Estados de Feedback visual: Exibição de loaders específicos ('Ouvindo...', 'Transcrevendo...', 'Pensando...') para mitigar a percepção de latência.
- **Pronunciation Assessment** para cada turno falado do usuário:
  - precisão (accuracy), fluência (fluency), completude (completeness), prosódia (se disponível no tier), e/ou score geral.
- **Feedback pós-turno**:
  - correções sugeridas (frase natural), erros comuns, 1 dica objetiva.
  - 1–3 “melhorias” de pronúncia/vocabulário do turno.
- Controle de Feedback: O feedback detalhado de correções e dicas deve ser exibido de forma colapsada por padrão, permitindo que o usuário foque na fluência da conversa sem interrupções cognitivas.
- Funcionalidade de Replay: Botão para repetir o último áudio gerado pelo tutor.
- **Histórico de sessão** (texto + áudio opcional no MVP: armazenar apenas texto e métricas inicialmente).

#### B) Flashcards + SRS (SM-2)
- **Criação Assistida de cards**: O sistema deve sugerir termos ou frases baseadas nos erros/lacunas da conversa, mas a criação final depende da confirmação do usuário (botão 'Salvar').
  - vocabulário novo identificado na conversa,
  - frases corrigidas recomendadas pelo tutor.
- **Revisão diária** com algoritmo **SM-2** no backend.
- **Avaliação do recall** pelo usuário (ex.: 0–5) e recalculo do agendamento.

#### C) Conta e billing (mínimo viável)
- **Autenticação** (email + senha, ou magic link).
- **Plano gratuito** com limites (ex.: minutos/dia ou sessões/semana; tokens/turnos).
- **Pagamentos/assinatura** (pode ser simplificado no MVP: “waitlist + acesso” ou Stripe básico).

#### D) SaaS Web (Next.js) + Landing (Next.js)
- Landing com proposta de valor + CTA.
- App web com:
  - iniciar sessão de voz,
  - visualizar feedback,
  - revisar cards.

#### E) Backend (Django + Ninja + Postgres)
- APIs para:
  - usuários, sessões, turnos, métricas de pronúncia,
  - cards, decks, revisões (SM-2).

#### F) App Mobile (Flutter) — Companion App Offline-First
- Foco exclusivo em gerenciar as revisões de flashcards, complementando o SaaS sem duplicar funcionalidades.
- **Tela de login** (consumindo o mesmo auth do backend).
- **Lista de cards pendentes** (carregados do backend e persistidos em SQLite localmente).
- **Tela de revisão SRS** (frente/verso, botões 0–5, com cálculo do algoritmo SM-2 feito localmente).
- **Sincronização assíncrona**: Indicador de status (online/offline, cards pendentes) e sync automático das revisões com o backend assim que recuperar a conexão (offline-first genuíno). Resolução de Conflitos: Implementação de política 'Last Write Wins' baseada no timestamp da revisão local para garantir integridade dos dados entre mobile e backend.

### 3.2 Nice-to-have (pós-MVP)
- **App mobile Flutter com experiência voice-first completa** (no MVP, o app atua estritamente como um companion de revisão offline).
- **Coach de pronúncia dedicado** (modo “shadowing”, minimal pairs, drilling).
- **Detecção automática de nível (CEFR)** e trilhas (A1–C2).
- **Conteúdos estruturados** (lições, módulos) e “missões” diárias.
- **Análise de erros recorrentes** (gramática, pronúncia, vocabulário) com plano semanal.
- **Export/Import** de decks (Anki-like).
- **Comunidade / buddy system**.
- **Modo professor/turma** (B2B EdTech).
- **A/B testing** e personalização avançada do tutor (personalidade, velocidade, sotaque).
- **Armazenamento e replay de áudio** + highlights.
- **Suporte multilíngue** (UI e explicações na língua do usuário).

## 4) User stories — funcionalidade principal (Tutor de voz conversacional)

> **Funcionalidade principal**: “Falar com um tutor por voz, receber feedback útil e mensurável, e transformar o que aprendi em revisão (SRS).”

### US-01 — Iniciar uma sessão de conversa por tema
**Como** aluno, **quero** escolher um tema/objetivo de conversa, **para** praticar situações relevantes (ex.: entrevista, viagem, small talk).

### US-02 — Falar e ser transcrito com baixa fricção
**Como** aluno, **quero** falar pelo microfone e ver minha fala transcrita, **para** confirmar se o sistema entendeu corretamente.

### US-03 — Ouvir a resposta do tutor em voz natural
**Como** aluno, **quero** ouvir o tutor por TTS, **para** treinar compreensão e ritmo natural de conversa.

### US-04 — Receber feedback pós-turno (conteúdo + correções)
**Como** aluno, **quero** receber correções e uma versão mais natural do que eu disse, **para** melhorar gramática, vocabulário e naturalidade.

### US-05 — Receber avaliação de pronúncia objetiva
**Como** aluno, **quero** ver uma avaliação de pronúncia (scores) do que eu falei, **para** acompanhar evolução e focar em pontos fracos.

### US-06 — Salvar itens importantes como flashcards
**Como** aluno, **quero** transformar correções e vocabulário novo em flashcards com 1 clique, **para** revisar depois e não esquecer.

### US-07 — Retomar histórico de conversas
**Como** aluno, **quero** ver sessões anteriores e seus feedbacks, **para** revisar meu progresso e reaproveitar aprendizados.

## 5) Critérios de aceite (por user story)

### AC — US-01 Iniciar sessão por tema
- **Dado** que o usuário está autenticado, **quando** ele acessa “Nova sessão”, **então** ele consegue escolher:
  - um tema (lista inicial fixa no MVP: Entrevista de emprego, Reunião de Daily, Aeroporto, Restaurante e Small Talk) e
  - um nível aproximado (ex.: básico/intermediário/avançado).
- Ao confirmar, o sistema cria uma sessão persistida no backend com:
  - `session_id`, `user_id`, `topic`, `level`, `created_at`.
- A tela de conversa abre com estado “pronto para gravar”.

### AC — US-02 Falar e ser transcrito
- O app solicita permissão do microfone (web/mobile quando aplicável).
- O usuário consegue:
  - iniciar gravação,
  - finalizar gravação,
  - visualizar a transcrição do turno (STT).
- Se a transcrição falhar (timeout/erro), o usuário vê uma mensagem clara e pode tentar novamente.
- O turno é persistido com:
  - texto transcrito,
  - timestamps (início/fim),
  - status (`ok`/`failed`).

### AC — US-03 Ouvir resposta do tutor
- Após a transcrição do usuário, o tutor gera uma resposta textual (LLM).
- O sistema converte a resposta em áudio via TTS (Azure Speech).
- O usuário consegue:
  - ouvir a resposta,
  - pausar/retomar (no mínimo stop/play no MVP).
- Se TTS falhar, a resposta textual ainda é exibida e a UI indica indisponibilidade de áudio.

### AC — US-04 Feedback pós-turno (conteúdo + correções)
- Após cada turno do usuário, o sistema exibe um bloco de feedback contendo no mínimo:
  - “Sua frase (como você disse)” (transcrição),
  - “Forma mais natural” (rewrite),
  - 1 dica curta (<= 240 caracteres) com foco em 1 melhoria.
- O feedback deve estar em português (UI/explicação), enquanto exemplos/correções são em inglês.
- O feedback não deve interromper a conversa: o usuário pode seguir falando imediatamente.

### AC — US-05 Avaliação de pronúncia objetiva
- Para cada turno do usuário, o backend armazena métricas retornadas pelo Azure Pronunciation Assessment (quando disponível no tier/config):
  - score geral e/ou componentes (accuracy/fluency/completeness, etc.).
- A UI mostra ao menos:
  - um score de 0–100 (ou 0–1 convertido) e
  - um rótulo interpretável (“precisa melhorar”, “bom”, “ótimo”) baseado em faixas.
- Se o serviço estiver indisponível, o usuário vê “Pronúncia indisponível para este turno” e a conversa segue.

### AC — US-06 Salvar como flashcards
- A partir do feedback do turno, o usuário pode clicar em “Salvar como card” em:
  - uma correção (frase natural) e/ou
  - uma palavra/expressão destacada.
- Ao salvar:
  - o card é criado no backend,
  - um item de SRS é inicializado com parâmetros do SM-2 (ex.: `repetition=0`, `interval=1`, `ef=2.5`).
- O usuário recebe confirmação visual (ex.: “Salvo”) sem sair da conversa.

### AC — US-07 Histórico de conversas
- O usuário consegue ver uma lista de sessões com:
  - tema, data, duração (aprox), e um indicador de progresso (ex.: nº de turnos).
- Ao abrir uma sessão, ele vê:
  - timeline de turnos (usuário/tutor),
  - feedbacks e scores de pronúncia por turno.
- O histórico é paginado (ou lazy load) para não degradar performance.

## 6) Métricas de sucesso

### 6.1 Aquisição e ativação
- **Landing → signup conversion**: % visitantes que criam conta.
- **Time to First Conversation (TTFC)**: tempo mediano do signup até completar a 1ª sessão de voz.
- **Activation rate**: % usuários que completam ≥ 1 sessão + salvam ≥ 1 card em 24h.

### 6.2 Engajamento e retenção
- **DAU/WAU** e **WAU/MAU** (stickiness).
- **Retenção D1 / D7 / D30**.
- **Streak médio** (dias consecutivos de prática).
- **Minutos de fala por usuário/semana**.
- **Revisões por dia** e **taxa de conclusão da revisão diária**.

### 6.3 Aprendizado (outcomes)
- **Evolução de pronúncia**:
  - variação média do score por semana (por nível/tema).
- **WPM (Words Per Minute) médio por sessão**.
- **Duração média das respostas do usuário**.
- **Taxa de acerto no SRS**:
  - média do “quality score” (0–5) nas revisões.
- **Redução de erros recorrentes**:
  - frequência de padrões (ex.: “missing articles”, “verb tense”) ao longo do tempo (nice-to-have se exigir NLP extra).

### 6.4 Qualidade e confiabilidade
- **Latência ponta a ponta por turno** (P50/P95):
  - gravação finalizada → transcrição pronta,
  - transcrição → resposta do tutor,
  - resposta → áudio pronto.
- **Taxa de falhas** (STT/TTS/LLM) por 100 turnos.
- **Custo por usuário ativo** (especialmente STT/TTS).

### 6.5 Receita (se aplicável no MVP)
- **Conversion to paid** (free → pago).
- **Churn mensal**.
- **ARPA / MRR** (se assinatura).

## 7) Fora do escopo (MVP)

- **App mobile Flutter com todas as features do SaaS web** (conversas por voz e dashboards complexos ficam restritos à web neste momento, mantendo o mobile focado no fluxo offline).
- **Cursos completos/estruturados** com currículo longo (módulos/chapters).
- **Certificações, provas e simulados** (IELTS/TOEFL) com correção avançada.
- **Tutoria humana** / marketplace de professores.
- **Social/community** (amigos, grupos, ranking público).
- **Modo offline** e downloads de áudio.
- **Reconhecimento avançado de sotaque e coaching fonético profundo** (além do que o Azure entregar no free tier).
- **Personalização extrema do LLM** (fine-tuning, memória de longo prazo complexa).
- **Gamificação completa** (loja, badges complexos, quests em árvore).

## Apêndice A — Stack e componentes (referência)

### Frontend
- **Landing Page**: Next.js → Railway
- **SaaS Web**: Next.js → Railway

### Backend
- **API**: Django + Django Ninja
- **DB**: PostgreSQL
- **Deploy**: Railway

### IA e voz
- **STT/TTS + Pronunciation Assessment**: Azure Speech (free tier)
- **LLM**: Groq API com Llama 3.3 70B (free)

### SRS
- **Algoritmo**: SM-2 no backend (intervalos, EF, repetição, agendamento)

## Apêndice B — Suposições do MVP (para orientar decisões)
- O MVP prioriza **velocidade de entrega** e **redução de custo**, aceitando limites (free tiers).
- A experiência base deve funcionar bem no **web**; mobile entra como extensão.
- Armazenamento de áudio é opcional no MVP (começar com texto + métricas).

