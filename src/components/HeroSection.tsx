import { Upload, Dna, Sparkles, ArrowRight } from 'lucide-react';
import { motion } from 'framer-motion';

export default function HeroSection({ onStartAnalysis }: { onStartAnalysis: () => void }) {

  return (
    <>
    <div className="relative min-h-screen flex items-center justify-center px-6 pt-24 sm:pt-32" style={{ zIndex: 100 }}>
      {/* Animated gradient orbs */}
      <div className="absolute top-20 right-20 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl animate-pulse pointer-events-none" style={{ zIndex: 1 }} />
      <div className="absolute bottom-20 left-20 w-96 h-96 bg-yellow-500/20 rounded-full blur-3xl animate-pulse delay-1000 pointer-events-none" style={{ zIndex: 1 }} />
      
      <div className="max-w-7xl mx-auto grid lg:grid-cols-2 gap-12 items-center relative" style={{ zIndex: 200 }}>
        {/* Left Content */}
        <motion.div
          initial={{ opacity: 0, x: -50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8 }}
          className="space-y-8"
        >
          {/* Badge */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="inline-flex items-center gap-2 px-4 py-2 bg-yellow-500/10 border border-yellow-500/30 rounded-full text-yellow-400 text-sm"
          >
            <Sparkles className="w-4 h-4" />
            <span>AI-Powered Deep Learning</span>
          </motion.div>

          {/* Main Heading */}
          <div className="space-y-4">
            <h1 className="text-6xl lg:text-7xl font-bold">
              <span className="text-white">Decode the</span>
              <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 to-orange-500">
                Ocean's DNA
              </span>
            </h1>
            <p className="text-xl text-gray-300 leading-relaxed">
              Advanced AI-driven eDNA analysis pipeline for marine biodiversity assessment.
              Identify taxonomic classifications with 99.9% accuracy using deep learning.
            </p>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-3 gap-6">
            <div className="space-y-1">
              <div className="text-3xl font-bold text-yellow-400">99.9%</div>
              <div className="text-sm text-gray-400">Accuracy</div>
            </div>
            <div className="space-y-1">
              <div className="text-3xl font-bold text-purple-400">4K+</div>
              <div className="text-sm text-gray-400">Sequences</div>
            </div>
            <div className="space-y-1">
              <div className="text-3xl font-bold text-blue-400">8</div>
              <div className="text-sm text-gray-400">Taxa Classes</div>
            </div>
          </div>

          {/* CTA Buttons */}
          <div className="flex flex-wrap gap-4 relative" style={{ zIndex: 300 }}>
            <button
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                console.log('Button clicked!');
                onStartAnalysis();
              }}
              type="button"
              className="group px-8 py-4 bg-gradient-to-r from-yellow-500 to-orange-500 text-gray-900 font-semibold rounded-xl hover:shadow-2xl hover:shadow-yellow-500/50 transition-all duration-300 flex items-center gap-2 cursor-pointer"
              style={{ position: 'relative', zIndex: 400 }}
            >
              <Upload className="w-5 h-5" />
              <span>Start Analysis</span>
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </button>
            
            <button 
              type="button"
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                const event = new CustomEvent('openDocumentation');
                window.dispatchEvent(event);
              }}
              className="px-8 py-4 bg-white/5 backdrop-blur-sm border border-white/10 text-white font-semibold rounded-xl hover:bg-white/10 transition-all duration-300 cursor-pointer"
              style={{ position: 'relative', zIndex: 400 }}
            >
              View Documentation
            </button>
          </div>

          {/* Features */}
          <div className="flex flex-wrap gap-6 pt-4">
            <div className="flex items-center gap-2 text-gray-300">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
              <span className="text-sm">Real-time Processing</span>
            </div>
            <div className="flex items-center gap-2 text-gray-300">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
              <span className="text-sm">GPU Accelerated</span>
            </div>
            <div className="flex items-center gap-2 text-gray-300">
              <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
              <span className="text-sm">Multi-format Export</span>
            </div>
          </div>
        </motion.div>

        {/* Right Visual */}
        <motion.div
          initial={{ opacity: 0, x: 50 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8, delay: 0.2 }}
          className="relative"
        >
          {/* DNA Helix Visualization */}
          <div className="relative w-full aspect-square">
            {/* Glowing orb */}
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-64 h-64 bg-gradient-to-br from-purple-500/30 to-blue-500/30 rounded-full blur-3xl animate-pulse" />
            </div>
            
            {/* DNA Icon */}
            <div className="absolute inset-0 flex items-center justify-center">
              <motion.div
                animate={{
                  rotate: 360,
                }}
                transition={{
                  duration: 20,
                  repeat: Infinity,
                  ease: "linear",
                }}
                className="relative"
              >
                <Dna className="w-48 h-48 text-yellow-400/80" strokeWidth={1} />
              </motion.div>
            </div>

            {/* Floating cards */}
            <motion.div
              animate={{ y: [0, -20, 0] }}
              transition={{ duration: 3, repeat: Infinity }}
              className="absolute top-10 right-10 p-4 bg-gray-900/80 backdrop-blur-sm border border-yellow-500/30 rounded-xl"
            >
              <div className="text-yellow-400 text-sm font-semibold">Perciformes</div>
              <div className="text-gray-400 text-xs">500 sequences</div>
            </motion.div>

            <motion.div
              animate={{ y: [0, 20, 0] }}
              transition={{ duration: 3, repeat: Infinity, delay: 0.5 }}
              className="absolute bottom-10 left-10 p-4 bg-gray-900/80 backdrop-blur-sm border border-purple-500/30 rounded-xl"
            >
              <div className="text-purple-400 text-sm font-semibold">Decapoda</div>
              <div className="text-gray-400 text-xs">500 sequences</div>
            </motion.div>

            <motion.div
              animate={{ y: [0, -15, 0] }}
              transition={{ duration: 3, repeat: Infinity, delay: 1 }}
              className="absolute top-1/2 left-0 p-4 bg-gray-900/80 backdrop-blur-sm border border-blue-500/30 rounded-xl"
            >
              <div className="text-blue-400 text-sm font-semibold">Bivalvia</div>
              <div className="text-gray-400 text-xs">500 sequences</div>
            </motion.div>
          </div>
        </motion.div>
      </div>
    </div>
    </>
  );
}
