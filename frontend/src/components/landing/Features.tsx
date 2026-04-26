import { Bot, Volume2, BrainCircuit, Trophy, Clock, Zap } from 'lucide-react';

export default function Features() {
  const features = [
    {
      icon: Bot,
      title: "Tutor IA 24/7",
      description: "Pratique quando quiser com nosso tutor inteligente disponível 24 horas por dia, 7 dias por semana.",
      color: "from-blue-500 to-blue-600",
      bgColor: "bg-blue-50"
    },
    {
      icon: Volume2,
      title: "Correção de pronúncia em tempo real",
      description: "Receba feedback instantâneo sobre sua pronúncia com análise detalhada de fonemas e entonação.",
      color: "from-green-500 to-green-600",
      bgColor: "bg-green-50"
    },
    {
      icon: BrainCircuit,
      title: "Flashcards automáticos",
      description: "Geração inteligente de flashcards baseada nas suas conversas para revisão otimizada.",
      color: "from-purple-500 to-purple-600",
      bgColor: "bg-purple-50"
    },
    {
      icon: Trophy,
      title: "Progresso gamificado",
      description: "Conquistas, streaks e recompensas para manter sua motivação e acompanhar sua evolução.",
      color: "from-yellow-500 to-yellow-600",
      bgColor: "bg-yellow-50"
    },
    {
      icon: Clock,
      title: "Aprendizado flexível",
      description: "Estude no seu próprio ritmo com sessões curtas ou longas adaptadas à sua rotina.",
      color: "from-red-500 to-red-600",
      bgColor: "bg-red-50"
    },
    {
      icon: Zap,
      title: "Resultados rápidos",
      description: "Veja sua fluência melhorar em semanas com nosso método comprovado de imersão conversacional.",
      color: "from-indigo-500 to-indigo-600",
      bgColor: "bg-indigo-50"
    }
  ];

  return (
    <section className="py-20 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section header */}
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            Recursos poderosos para seu aprendizado
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
            Tecnologia de ponta combinada com metodologia comprovada para resultados excepcionais
          </p>
        </div>

        {/* Features grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <div
                key={index}
                className="group relative bg-white border border-gray-200 rounded-2xl p-8 hover:shadow-xl transition-all duration-300 hover:border-gray-300"
              >
                {/* Background gradient on hover */}
                <div className={`absolute inset-0 ${feature.bgColor} opacity-0 group-hover:opacity-100 rounded-2xl transition-opacity duration-300`}></div>
                
                {/* Content */}
                <div className="relative z-10">
                  {/* Icon */}
                  <div className={`w-16 h-16 bg-gradient-to-br ${feature.color} rounded-2xl flex items-center justify-center mb-6 shadow-lg group-hover:scale-110 transition-transform duration-300`}>
                    <Icon className="w-8 h-8 text-white" />
                  </div>

                  {/* Text content */}
                  <h3 className="text-xl font-bold text-gray-900 mb-4 group-hover:text-gray-800">
                    {feature.title}
                  </h3>
                  <p className="text-gray-600 leading-relaxed group-hover:text-gray-700">
                    {feature.description}
                  </p>
                </div>
              </div>
            );
          })}
        </div>

        {/* Feature highlight */}
        <div className="bg-gradient-to-r from-blue-600 to-green-600 rounded-3xl p-12 text-center text-white">
          <div className="max-w-4xl mx-auto">
            <h3 className="text-3xl md:text-4xl font-bold mb-6">
              Comece a transformar seu inglês hoje
            </h3>
            <p className="text-xl mb-8 text-blue-100">
              Junte-se a milhares de estudantes que já estão alcançando fluência com o SpeakFlow
            </p>
            <div className="flex flex-wrap justify-center gap-6">
              <div className="bg-white/20 backdrop-blur-sm rounded-xl px-6 py-3">
                <div className="text-2xl font-bold">10K+</div>
                <div className="text-blue-100">Estudantes ativos</div>
              </div>
              <div className="bg-white/20 backdrop-blur-sm rounded-xl px-6 py-3">
                <div className="text-2xl font-bold">4.8★</div>
                <div className="text-blue-100">Avaliação média</div>
              </div>
              <div className="bg-white/20 backdrop-blur-sm rounded-xl px-6 py-3">
                <div className="text-2xl font-bold">95%</div>
                <div className="text-blue-100">Taxa de sucesso</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
