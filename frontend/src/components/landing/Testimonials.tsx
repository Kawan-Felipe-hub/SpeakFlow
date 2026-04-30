export default function Testimonials() {
  // TODO: Implement real testimonials system
  // This section should display actual user reviews from the database
  // For now, we'll show a simple call-to-action section instead


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

        {/* Call to action instead of fake testimonials */}
        <div className="text-center mb-16">
          <div className="bg-white rounded-2xl p-12 shadow-lg">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">
              Seja o primeiro a compartilhar sua experiência!
            </h3>
            <p className="text-gray-600 mb-8 max-w-2xl mx-auto">
              Estamos construindo a plataforma de aprendizado de inglês mais eficaz do Brasil. 
              Comece a usar o SpeakFlow e compartilhe seus resultados.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a 
                href="/register" 
                className="bg-blue-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
              >
                Começar agora
              </a>
              <a 
                href="/login" 
                className="border border-gray-300 text-gray-700 px-8 py-3 rounded-lg font-semibold hover:border-gray-400 transition-colors"
              >
                Fazer login
              </a>
            </div>
          </div>
        </div>

      </div>
    </section>
  );
}
