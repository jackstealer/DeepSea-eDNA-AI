import React from 'react';
import { Waves, Dna, Github, Mail, Heart, ExternalLink } from 'lucide-react';

export const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="glass-card border-t border-purple-500/30 mt-20 relative" style={{ zIndex: 200 }}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 relative" style={{ pointerEvents: 'auto' }}>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="col-span-1 md:col-span-2">
            <div className="flex items-center space-x-2 mb-4">
              <div className="flex items-center space-x-2 bg-gradient-to-r from-yellow-500/10 to-purple-500/10 p-2 rounded-xl border border-yellow-500/30">
                <Waves className="h-6 w-6 text-yellow-400" />
                <Dna className="h-6 w-6 text-purple-400" />
              </div>
              <div>
                <h3 className="text-xl font-bold text-gradient">DeepSea eDNA AI</h3>
                <p className="text-xs text-gray-400">Neural Engine v2.1.0</p>
              </div>
            </div>
            <p className="text-sm text-gray-400 leading-relaxed max-w-md">
              Advanced AI-driven eDNA analysis platform for marine biodiversity assessment. 
              Powered by deep learning and cutting-edge bioinformatics.
            </p>
            <div className="flex items-center gap-4 mt-4">
              <a
                href="https://github.com/jackstealer"
                target="_blank"
                rel="noopener noreferrer"
                className="p-2 glass-card border border-purple-500/30 rounded-lg hover:border-purple-500/50 transition-all group"
              >
                <Github className="h-5 w-5 text-purple-400 group-hover:text-purple-300" />
              </a>
              <a
                href="mailto:jackstealer690@gmail.com"
                className="p-2 glass-card border border-yellow-500/30 rounded-lg hover:border-yellow-500/50 transition-all group"
              >
                <Mail className="h-5 w-5 text-yellow-400 group-hover:text-yellow-300" />
              </a>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="text-sm font-semibold text-white mb-4">Platform</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <button 
                  onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
                  className="text-gray-400 hover:text-yellow-400 transition-colors"
                >
                  Features
                </button>
              </li>
              <li>
                <button 
                  onClick={() => {
                    // Trigger documentation modal
                    const event = new CustomEvent('openDocumentation');
                    window.dispatchEvent(event);
                  }}
                  className="text-gray-400 hover:text-yellow-400 transition-colors"
                >
                  Documentation
                </button>
              </li>
              <li>
                <a 
                  href="http://localhost:3000/docs" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-gray-400 hover:text-yellow-400 transition-colors"
                >
                  API Reference
                </a>
              </li>
              <li>
                <a 
                  href="mailto:jackstealer690@gmail.com?subject=Pricing Inquiry" 
                  className="text-gray-400 hover:text-yellow-400 transition-colors"
                >
                  Pricing
                </a>
              </li>
            </ul>
          </div>

          {/* Resources */}
          <div>
            <h4 className="text-sm font-semibold text-white mb-4">Resources</h4>
            <ul className="space-y-2 text-sm">
              <li>
                <a
                  href="https://github.com/jackstealer"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-gray-400 hover:text-yellow-400 transition-colors flex items-center gap-1"
                >
                  GitHub
                  <ExternalLink className="h-3 w-3" />
                </a>
              </li>
              <li>
                <a 
                  href="https://scholar.google.com/scholar?q=edna+marine+biodiversity+deep+learning" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-gray-400 hover:text-yellow-400 transition-colors"
                >
                  Research Papers
                </a>
              </li>
              <li>
                <a 
                  href="https://github.com/jackstealer#readme" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-gray-400 hover:text-yellow-400 transition-colors"
                >
                  Tutorials
                </a>
              </li>
              <li>
                <a 
                  href="mailto:jackstealer690@gmail.com?subject=Support Request" 
                  className="text-gray-400 hover:text-yellow-400 transition-colors"
                >
                  Support
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="border-t border-purple-500/20 mt-8 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
          <p className="text-sm text-gray-400">
            © {currentYear} DeepSea eDNA AI. All rights reserved.
          </p>
          <div className="flex items-center gap-1 text-sm text-gray-400">
            <span>Made with</span>
            <Heart className="h-4 w-4 text-red-400 fill-red-400" />
            <span>for marine conservation</span>
          </div>
          <div className="flex items-center gap-4 text-sm">
            <a href="#privacy" className="text-gray-400 hover:text-yellow-400 transition-colors">
              Privacy Policy
            </a>
            <a href="#terms" className="text-gray-400 hover:text-yellow-400 transition-colors">
              Terms of Service
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
};
