'use client';

interface NavbarProps {
  alertCount: number;
}

export default function Navbar({ alertCount }: NavbarProps) {
  return (
    <header className="h-14 bg-gray-900 text-white flex items-center px-6 gap-4 shadow-lg shrink-0">
      {/* Logo / Title */}
      <div className="flex items-center gap-2">
        <span className="text-xl">🗺️</span>
        <span className="font-bold text-base tracking-tight">NER-LIS</span>
        <span className="text-gray-400 text-xs hidden sm:inline">
          North Eastern Region – Logistics Intelligence System
        </span>
      </div>

      <div className="flex-1" />

      {/* Alert indicator */}
      {alertCount > 0 && (
        <div className="flex items-center gap-1.5 bg-red-600 text-white text-xs font-bold px-3 py-1 rounded-full animate-pulse">
          🔔 {alertCount} Alert{alertCount > 1 ? 's' : ''}
        </div>
      )}

      {/* Pilot corridor badge */}
      <div className="hidden md:flex items-center gap-1.5 bg-gray-700 text-gray-300 text-xs px-3 py-1 rounded-full">
        <span className="w-1.5 h-1.5 rounded-full bg-green-400 inline-block" />
        Pilot: Guwahati → Shillong
      </div>
    </header>
  );
}
