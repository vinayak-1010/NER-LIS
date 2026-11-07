import Link from 'next/link';

export default function HomePage() {
  return (
    <main className="min-h-screen bg-gray-900 text-white flex flex-col items-center justify-center px-6">
      <div className="text-center max-w-2xl">
        <div className="text-6xl mb-6">🗺️</div>
        <h1 className="text-4xl font-bold mb-2 tracking-tight">NER-LIS</h1>
        <p className="text-gray-400 text-lg mb-1">
          North Eastern Region — Logistics Intelligence System
        </p>
        <p className="text-gray-500 text-sm mb-10">
          AI-powered road disruption prediction, risk-aware routing, and essential
          shipment tracking across the North Eastern Region of India.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link
            href="/dashboard"
            className="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-8 py-3 rounded-xl transition-colors"
          >
            Open Dashboard →
          </Link>
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="bg-gray-700 hover:bg-gray-600 text-white font-semibold px-8 py-3 rounded-xl transition-colors"
          >
            API Docs ↗
          </a>
        </div>

        <div className="mt-14 grid grid-cols-2 sm:grid-cols-4 gap-4 text-center text-sm text-gray-400">
          {[
            { icon: '🛣️', label: 'Road Status Layers' },
            { icon: '🤖', label: 'AI Disruption Prediction' },
            { icon: '🔀', label: 'Risk-Aware Routing' },
            { icon: '📦', label: 'Shipment Priority' },
          ].map(({ icon, label }) => (
            <div key={label} className="bg-gray-800 rounded-xl py-4 px-2">
              <div className="text-2xl mb-1">{icon}</div>
              <div>{label}</div>
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}
