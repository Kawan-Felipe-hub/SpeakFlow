import { Mic, MessageCircle, BookOpen, ArrowRight } from 'lucide-react';

export default function HowItWorks() {
  const steps = [
    {
      id: 1,
      icon: Mic,
      title: "Fale",
      description: "Grave sua voz conversando com nosso tutor de IA sobre qualquer tema",
      color: "from-blue-500 to-blue-600"
    },
    {
      id: 2,
      icon: MessageCircle,
      title: "Receba correção",
      description: "Obtenha feedback instantâneo sobre pronúncia, gramática e fluidez",
      color: "from-green-500 to-green-600"
    },
    {
      id: 3,
      icon: BookOpen,
      title: "Revise com flashcards",
      description: "Flashcards automáticos criados das suas conversas para revisão espaçada",
      color: "from-purple-500 to-purple-600"
    }
  ];

  return (
    <section className="py-20 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section header */}
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            Como funciona
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
            Aprendizado de inglês simplificado em 3 passos inteligentes
          </p>
        </div>

        {/* Steps */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
          {steps.map((step, index) => {
            const Icon = step.icon;
            return (
              <div key={step.id} className="relative">
                {/* Step number */}
                <div className="absolute -top-4 -left-4 w-8 h-8 bg-gray-900 text-white rounded-full flex items-center justify-center font-bold text-sm z-10">
                  {step.id}
                </div>

                {/* Step card */}
                <div className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-xl transition-shadow duration-300 h-full">
                  {/* Icon */}
                  <div className={`w-16 h-16 bg-gradient-to-br ${step.color} rounded-2xl flex items-center justify-center mb-6 shadow-lg`}>
                    <Icon className="w-8 h-8 text-white" />
                  </div>

                  {/* Content */}
                  <h3 className="text-2xl font-bold text-gray-900 mb-4">
                    {step.title}
                  </h3>
                  <p className="text-gray-600 leading-relaxed">
                    {step.description}
                  </p>
                </div>

                {/* Arrow connector (desktop only) */}
                {index < steps.length - 1 && (
                  <div className="hidden md:block absolute top-1/2 -right-4 transform -translate-y-1/2 z-20">
                    <div className="w-8 h-8 bg-gray-100 rounded-full flex items-center justify-center">
                      <ArrowRight className="w-4 h-4 text-gray-400" />
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Visual flow indicator (mobile) */}
        <div className="md:hidden flex items-center justify-center space-x-2">
          {steps.map((_, index) => (
            <div
              key={index}
              className={`h-2 rounded-full transition-all duration-300 ${
                index === 0 ? 'w-8 bg-blue-600' : 'w-2 bg-gray-300'
              }`}
            />
          ))}
        </div>

        {/* Additional info */}
        <div className="mt-16 bg-gradient-to-r from-blue-50 to-green-50 rounded-3xl p-8 text-center">
          <div className="max-w-3xl mx-auto">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">
              Aprendizado adaptativo e inteligente
            </h3>
            <p className="text-gray-600 leading-relaxed mb-6">
              Nosso sistema analisa seu progresso e adapta as conversas e flashcards 
              ao seu nível, garantindo aprendizado otimizado e contínuo.
            </p>
            <div className="flex flex-wrap justify-center gap-4">
              <div className="bg-white rounded-lg px-4 py-2 shadow-sm">
                <span className="text-sm font-medium text-gray-700">🎯 Nível personalizado</span>
              </div>
              <div className="bg-white rounded-lg px-4 py-2 shadow-sm">
                <span className="text-sm font-medium text-gray-700">📊 Progresso em tempo real</span>
              </div>
              <div className="bg-white rounded-lg px-4 py-2 shadow-sm">
                <span className="text-sm font-medium text-gray-700">🔄 Revisão espaçada</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
