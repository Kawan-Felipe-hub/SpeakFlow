import { Star, Quote } from 'lucide-react';

export default function Testimonials() {
  const testimonials = [
    {
      id: 1,
      name: "Ana Silva",
      role: "Gerente de Marketing",
      location: "São Paulo, SP",
      avatar: "AS",
      rating: 5,
      content: "O SpeakFlow transformou meu inglês! Em apenas 2 meses, consegui fazer apresentações em inglês para clientes internacionais. A correção de pronúncia em tempo real é incrível.",
      result: "Nível: Intermediário → Avançado",
      achievement: "🎯 Promoção conquistada"
    },
    {
      id: 2,
      name: "Carlos Mendes",
      role: "Desenvolvedor de Software",
      location: "Rio de Janeiro, RJ",
      avatar: "CM",
      rating: 5,
      content: "Como desenvolvedor, preciso comunicar com equipes globais. O SpeakFlow me deu confiança para participar de reuniões em inglês sem medo. Os flashcards automáticos são geniais!",
      result: "Nível: Básico → Intermediário",
      achievement: "🚀 Projeto internacional liderado"
    },
    {
      id: 3,
      name: "Mariana Costa",
      role: "Estudante de Medicina",
      location: "Belo Horizonte, MG",
      avatar: "MC",
      rating: 5,
      content: "Estudo entre as aulas e o SpeakFlow se encaixa perfeitamente na minha rotina. A gamificação me mantém motivada e já consigo ler artigos médicos em inglês.",
      result: "Nível: Iniciante → Intermediário",
      achievement: "📚 Artigo publicado internacionalmente"
    }
  ];

  const renderStars = (rating: number) => {
    return Array.from({ length: 5 }, (_, i) => (
      <Star
        key={i}
        className={`w-5 h-5 ${
          i < rating ? 'text-yellow-400 fill-current' : 'text-gray-300'
        }`}
      />
    ));
  };

  return (
    <section className="py-20 bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section header */}
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            Histórias de sucesso
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto leading-relaxed">
            Veja como o SpeakFlow está transformando a vida de milhares de estudantes
          </p>
        </div>

        {/* Testimonials grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-16">
          {testimonials.map((testimonial) => (
            <div
              key={testimonial.id}
              className="bg-white rounded-2xl p-8 shadow-lg hover:shadow-xl transition-all duration-300 relative"
            >
              {/* Quote icon */}
              <div className="absolute -top-4 -right-4 w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                <Quote className="w-4 h-4 text-blue-600" />
              </div>

              {/* Avatar and basic info */}
              <div className="flex items-center mb-6">
                <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-green-500 rounded-full flex items-center justify-center text-white font-bold mr-4">
                  {testimonial.avatar}
                </div>
                <div>
                  <h3 className="font-bold text-gray-900">{testimonial.name}</h3>
                  <p className="text-sm text-gray-600">{testimonial.role}</p>
                  <p className="text-xs text-gray-500">{testimonial.location}</p>
                </div>
              </div>

              {/* Rating */}
              <div className="flex mb-4">
                {renderStars(testimonial.rating)}
              </div>

              {/* Content */}
              <blockquote className="text-gray-700 leading-relaxed mb-6 italic">
                "{testimonial.content}"
              </blockquote>

              {/* Results */}
              <div className="border-t pt-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-600">Resultado:</span>
                  <span className="text-sm font-bold text-blue-600">
                    {testimonial.result}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-600">Conquista:</span>
                  <span className="text-sm font-bold text-green-600">
                    {testimonial.achievement}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Social proof stats */}
        <div className="bg-gradient-to-r from-blue-600 to-green-600 rounded-3xl p-12 text-center text-white">
          <div className="max-w-4xl mx-auto">
            <h3 className="text-3xl font-bold mb-8">
              Junte-se a milhares de estudantes satisfeitos
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
              <div>
                <div className="text-4xl font-bold mb-2">10K+</div>
                <div className="text-blue-100">Estudantes ativos</div>
              </div>
              <div>
                <div className="text-4xl font-bold mb-2">4.8★</div>
                <div className="text-blue-100">Avaliação média</div>
              </div>
              <div>
                <div className="text-4xl font-bold mb-2">95%</div>
                <div className="text-blue-100">Taxa de sucesso</div>
              </div>
              <div>
                <div className="text-4xl font-bold mb-2">50K+</div>
                <div className="text-blue-100">Sessões completadas</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
