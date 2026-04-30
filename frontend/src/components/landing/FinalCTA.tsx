'use client';

import { Link } from '@/components/ui/Link';
import { Button } from '@/components/ui/Button';
import { Rocket, CheckCircle, ArrowRight } from 'lucide-react';

export default function FinalCTA() {
  const benefits = [
    "Acesso gratuito ao tutor de IA",
    "Correção de pronúncia ilimitada", 
    "Flashcards automáticos inteligentes",
    "Progresso gamificado com conquistas",
    "Disponível 24/7 quando você precisar"
  ];

  return (
    <section className="py-20 bg-gradient-to-br from-blue-600 via-blue-700 to-green-600 relative overflow-hidden">
      {/* Background decorative elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute top-20 left-20 w-72 h-72 bg-white/10 rounded-full mix-blend-multiply filter blur-xl animate-pulse"></div>
        <div className="absolute bottom-20 right-20 w-72 h-72 bg-white/10 rounded-full mix-blend-multiply filter blur-xl animate-pulse animation-delay-2000"></div>
      </div>

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        {/* Main content */}
        <div className="max-w-4xl mx-auto">
          {/* Icon */}
          <div className="inline-flex items-center justify-center w-20 h-20 bg-white/20 backdrop-blur-sm rounded-full mb-8">
            <Rocket className="w-10 h-10 text-white" />
          </div>

          {/* Headline */}
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-6 leading-tight">
            Pronto para transformar seu inglês?
            <span className="block text-yellow-300">Comece hoje mesmo!</span>
          </h2>

          {/* Sub-headline */}
          <p className="text-xl md:text-2xl text-blue-100 mb-12 max-w-3xl mx-auto leading-relaxed">
            Junte-se a milhares de estudantes que estão alcançando fluência 
            com nossa tecnologia revolucionária de aprendizado
          </p>

          {/* CTA Button */}
          <div className="mb-16">
            <Link href="/register">
              <Button size="lg" className="bg-white text-blue-600 hover:bg-gray-100 font-bold py-6 px-12 rounded-2xl text-xl shadow-2xl transform hover:scale-105 transition-all duration-300 group">
                Começar agora - É grátis
                <ArrowRight className="w-6 h-6 ml-2 group-hover:translate-x-1 transition-transform duration-300" />
              </Button>
            </Link>
            <p className="text-blue-200 mt-4">
              Sem cartão de crédito • Cancelamento a qualquer momento
            </p>
          </div>

          {/* Benefits grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 max-w-5xl mx-auto">
            {benefits.map((benefit, index) => (
              <div
                key={index}
                className="bg-white/10 backdrop-blur-sm rounded-xl p-4 flex items-center space-x-3 hover:bg-white/20 transition-colors duration-300"
              >
                <CheckCircle className="w-5 h-5 text-yellow-300 flex-shrink-0" />
                <span className="text-white text-sm font-medium">{benefit}</span>
              </div>
            ))}
          </div>

        </div>
      </div>

    </section>
  );
}
