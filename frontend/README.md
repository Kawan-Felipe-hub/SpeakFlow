# SpeakFlow Frontend

Frontend Next.js 14 do SpeakFlow - aplicativo de aprendizado de idiomas com tutor de voz por IA.

## 🚀 Tecnologias

- **Next.js 14** com App Router
- **TypeScript** para tipagem segura
- **TailwindCSS** para estilização
- **React Query (TanStack Query)** para gerenciamento de estado
- **Axios** para requisições HTTP
- **Lucide React** para ícones
- **React Hot Toast** para notificações

## 📁 Estrutura de Pastas

```
frontend/
├── src/
│   ├── app/                    # App Router pages
│   │   ├── dashboard/         # Dashboard page
│   │   ├── flashcards/        # Flashcards page
│   │   ├── login/            # Login page
│   │   ├── register/         # Register page
│   │   ├── session/[id]/     # Dynamic session page
│   │   ├── globals.css       # Global styles
│   │   └── layout.tsx        # Root layout
│   ├── components/            # Reusable components
│   │   ├── ui/               # Base UI components
│   │   │   ├── Button.tsx
│   │   │   └── Link.tsx
│   │   ├── ChatBubble.tsx    # Chat message component
│   │   ├── FlashCardReview.tsx # Flashcard review interface
│   │   ├── PronunciationBadge.tsx # Pronunciation score badge
│   │   └── VoiceButton.tsx   # Voice recording button
│   ├── hooks/                # Custom hooks
│   │   └── useVoiceRecorder.ts # MediaRecorder API hook
│   ├── lib/                  # Utilities
│   │   ├── api.ts           # API client with axios
│   │   └── utils.ts         # Helper functions
│   ├── store/               # Global state
│   │   └── queryClient.ts   # React Query configuration
│   └── types/               # TypeScript types
│       └── api.ts           # API response types
├── package.json
├── next.config.js
├── tailwind.config.ts
└── tsconfig.json
```

## 🛠️ Instalação

1. Instale as dependências:
```bash
npm install
```

2. Configure as variáveis de ambiente:
```bash
# .env.local
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000/api
```

3. Inicie o servidor de desenvolvimento:
```bash
npm run dev
```

Acesse `http://localhost:3000` no navegador.

## 🏗️ Funcionalidades Principais

### 🔐 Autenticação
- Login e registro com JWT
- Tokens armazenados em localStorage
- Refresh token automático
- Redirecionamento protegido

### 📊 Dashboard
- Estatísticas de aprendizado (streak, sessões, flashcards)
- Botão para criar nova sessão
- Histórico de sessões recentes
- Navegação para flashcards

### 🎙️ Sessão de Voz
- Gravação de áudio com MediaRecorder API
- Interface de chat em tempo real
- Badges de score de pronúncia
- Flashcards criados automaticamente
- Player de áudio para mensagens

### 📚 Flashcards
- Sistema de revisão spaced repetition (SM2)
- Interface de cartões viráveis
- Avaliação de qualidade (1-5)
- Lista de todos os flashcards
- Contador de cards para revisar

## 🎨 Componentes

### VoiceButton
- Botão circular para gravação
- Estados: ready, recording, paused
- Indicador visual de duração
- Controles de pause/resume
- Tratamento de erros

### ChatBubble
- Bolhas de chat para usuário/assistente
- Avatar diferenciado
- Player de áudio integrado
- Timestamp
- Badge de pronúncia para usuário

### PronunciationBadge
- Indicador visual de score (bom/regular/precisa melhorar)
- Ícones e cores correspondentes
- Detalhes expansivos (precisão, fluidez, completude)
- Lista de palavras problemáticas

### FlashCardReview
- Interface de cartão virável
- Sistema de avaliação SM2
- Feedback visual imediato
- Progresso da revisão

## 🔧 Hooks Customizados

### useVoiceRecorder
```typescript
const {
  isRecording,
  isPaused,
  duration,
  audioBlob,
  startRecording,
  stopRecording,
  pauseRecording,
  resumeRecording,
  clearRecording,
  error
} = useVoiceRecorder();
```

- Controle completo do MediaRecorder
- Timer automático
- Tratamento de permissões
- Cleanup automático
- Formato WebM/Opus

## 🌐 API Integration

### Cliente Axios
- Interceptadores para auth token
- Refresh token automático
- Tratamento de erros centralizado
- Tipagem completa

### React Query
- Cache automático de 5 minutos
- Refetch on window focus desativado
- Retry automático
- Invalidação otimizada

## 🎯 Fluxos de Usuário

### 1. Autenticação
1. Usuário acessa `/login` ou `/register`
2. Credenciais enviadas para API
3. Token JWT armazenado
4. Redirecionado para `/dashboard`

### 2. Dashboard
1. Carrega estatísticas do usuário
2. Exibe streak, sessões totais, flashcards pendentes
3. Opções: criar sessão ou revisar flashcards

### 3. Sessão de Voz
1. Usuário clica/segura VoiceButton
2. Grava áudio via MediaRecorder
3. Áudio enviado para `/api/sessions/{id}/message/`
4. Resposta processada (STT → LLM → TTS)
5. Mensagens exibidas em chat
6. Flashcards criados automaticamente

### 4. Flashcards
1. Lista de cards para revisar hoje
2. Interface de revisão um-a-um
3. Avaliação de qualidade (1-5)
4. Algoritmo SM2 calcula próximo intervalo
5. Progresso salvo automaticamente

## 🚀 Deploy

### Vercel (Recomendado)
```bash
npm run build
```

Configure as variáveis de ambiente no painel do Vercel:
- `NEXT_PUBLIC_API_URL`

### Outros provedores
O build está otimizado para plataformas serverless.

## 🔄 Desenvolvimento

### Comandos úteis
```bash
npm run dev          # Servidor de desenvolvimento
npm run build        # Build de produção
npm run start        # Servidor de produção
npm run lint         # Linting
```

### Adicionando novas páginas
1. Criar pasta em `src/app/`
2. Adicionar `page.tsx`
3. Exportar componente padrão
4. Atualizar navegação se necessário

### Novos componentes
1. Criar em `src/components/`
2. Usar TypeScript com props tipadas
3. Seguir padrão de nomenclatura
4. Adicionar stories se usar Storybook

## 🐛 Troubleshooting

### Erros comuns
- **Microfone não funciona**: Verifique permissões do navegador
- **CORS errors**: Configure `NEXT_PUBLIC_API_URL` corretamente
- **Token expirado**: Refresh token automático deve resolver
- **Build errors**: Verifique tipos TypeScript

### Debug
- Use React DevTools
- Console do navegador para erros de API
- Network tab para requisições HTTP
- Redux DevTools (se usado)

## 📝 Notas de Desenvolvimento

- O código usa TypeScript estrito
- Componentes são server-side quando possível
- Estado global gerenciado por React Query
- Estilos responsivos com Tailwind
- Acessibilidade considerada (ARIA labels)
- Performance otimizada (lazy loading, memoização)

## 🤝 Contribuição

1. Fork o projeto
2. Crie branch de feature
3. Faça commit das mudanças
4. Abra Pull Request

## 📄 Licença

MIT License - veja arquivo LICENSE para detalhes.
