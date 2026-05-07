import React from 'react';
import { Waves, Dna, Sparkles, ArrowLeft } from 'lucide-react';

interface HeaderProps {
  showBackButton?: boolean;
  onBackClick?: () => void;
}

export const Header: React.FC<HeaderProps> = ({ showBackButton = false, onBackClick }) => {
  return (
    <header className="sticky top-0 z-[500] bg-slate-900/95 backdrop-blur-xl border-b border-yellow-500/20 shadow-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 sm:h-20">
          <div className="flex items-center space-x-3 sm:space-x-4">
            {showBackButton && (
              <button
                onClick={onBackClick}
                className="p-2 glass-card border border-yellow-500/30 rounded-lg hover:border-yellow-500/50 transition-all group"
                style={{ zIndex: 100 }}
                type="button"
              >
                <ArrowLeft className="h-5 w-5 text-yellow-400 group-hover:-translate-x-1 transition-transform" />
              </button>
            )}
            <div className="relative">
              <div className="relative flex items-center space-x-2 bg-gradient-to-r from-yellow-500/10 to-purple-500/10 p-2 rounded-xl border border-yellow-500/30">
                <Waves className="h-6 w-6 sm:h-8 sm:w-8 text-yellow-400" />
                <Dna className="h-6 w-6 sm:h-8 sm:w-8 text-purple-400" />
              </div>
            </div>
            <div>
              <h1 className="text-xl sm:text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 to-orange-500 glow-text">
                DeepSea eDNA AI
              </h1>
              <p className="text-gray-400 text-xs sm:text-sm hidden sm:block">
                Advanced Biodiversity Analysis Pipeline
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="hidden md:flex items-center space-x-2 px-4 py-2 glass-card">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
              <span className="text-sm text-gray-300">System Online</span>
            </div>
            
            <div className="text-right">
              <div className="flex items-center space-x-2 text-yellow-400">
                <Sparkles className="h-4 w-4" />
                <span className="text-sm font-semibold">v2.1.0</span>
              </div>
              <p className="text-xs text-gray-400 hidden sm:block">Neural Engine</p>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};
