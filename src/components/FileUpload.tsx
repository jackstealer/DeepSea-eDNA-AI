import React, { useState, useRef } from 'react';
import { Upload, File, X, FileText, Zap } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface FileUploadProps {
  onFilesSelected: (files: File[]) => void;
  acceptedFormats: string[];
}

export const FileUpload: React.FC<FileUploadProps> = ({ onFilesSelected, acceptedFormats }) => {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    const files = Array.from(e.dataTransfer.files);
    handleFiles(files);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    e.preventDefault();
    if (e.target.files) {
      const files = Array.from(e.target.files);
      handleFiles(files);
    }
  };

  const handleFiles = (files: File[]) => {
    const validFiles = files.filter(file => 
      acceptedFormats.some(format => file.name.toLowerCase().endsWith(format))
    );
    setSelectedFiles(prev => [...prev, ...validFiles]);
    onFilesSelected(validFiles);
  };

  const removeFile = (index: number) => {
    const newFiles = selectedFiles.filter((_, i) => i !== index);
    setSelectedFiles(newFiles);
    onFilesSelected(newFiles);
  };

  const onButtonClick = () => {
    inputRef.current?.click();
  };

  return (
    <div className="w-full space-y-4">
      <motion.div
        whileHover={{ scale: 1.02 }}
        className={`relative glass-card border-2 border-dashed rounded-xl p-6 sm:p-8 text-center transition-all duration-300 ${
          dragActive 
            ? 'border-yellow-500 bg-yellow-500/10 glow-border' 
            : 'border-purple-500/30 hover:border-purple-500/50'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          ref={inputRef}
          type="file"
          multiple
          onChange={handleChange}
          accept={acceptedFormats.join(',')}
          className="hidden"
        />
        
        <motion.div
          animate={dragActive ? { scale: 1.1, rotate: 5 } : { scale: 1, rotate: 0 }}
          transition={{ duration: 0.3 }}
        >
          <div className="relative inline-block mb-4">
            <div className="absolute inset-0 bg-yellow-500/20 blur-2xl rounded-full" />
            <Upload className="relative mx-auto h-12 w-12 sm:h-16 sm:w-16 text-yellow-400" />
          </div>
        </motion.div>
        
        <p className="text-lg sm:text-xl font-semibold text-white mb-2">
          Upload eDNA Sequence Files
        </p>
        <p className="text-sm text-gray-400 mb-4">
          Drag and drop your files here, or click to browse
        </p>
        <div className="flex flex-wrap justify-center gap-2 mb-4">
          {acceptedFormats.map((format, i) => (
            <span key={i} className="px-2 py-1 text-xs bg-purple-500/20 text-purple-300 rounded border border-purple-500/30">
              {format}
            </span>
          ))}
        </div>
        
        <button
          onClick={onButtonClick}
          className="group px-6 py-3 bg-gradient-to-r from-yellow-500 to-orange-500 text-gray-900 font-semibold rounded-lg hover:shadow-2xl hover:shadow-yellow-500/50 transition-all duration-300 flex items-center gap-2 mx-auto"
        >
          <Zap className="h-5 w-5 group-hover:rotate-12 transition-transform" />
          <span>Select Files</span>
        </button>
      </motion.div>

      <AnimatePresence>
        {selectedFiles.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="glass-card p-4"
          >
            <h3 className="text-lg font-semibold text-white mb-3 flex items-center">
              <FileText className="h-5 w-5 mr-2 text-yellow-400" />
              Selected Files ({selectedFiles.length})
            </h3>
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {selectedFiles.map((file, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="flex items-center justify-between bg-white/5 p-3 rounded-lg border border-purple-500/20 hover:border-purple-500/40 transition-colors"
                >
                  <div className="flex items-center space-x-3 min-w-0 flex-1">
                    <File className="h-5 w-5 text-purple-400 flex-shrink-0" />
                    <div className="min-w-0">
                      <p className="font-medium text-white text-sm truncate">{file.name}</p>
                      <p className="text-xs text-gray-400">
                        {(file.size / (1024 * 1024)).toFixed(2)} MB
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => removeFile(index)}
                    className="p-1.5 text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded transition-colors flex-shrink-0"
                  >
                    <X className="h-4 w-4" />
                  </button>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};
