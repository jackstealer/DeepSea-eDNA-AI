# 🧬 DeepSea eDNA AI

<div align="center">

![DeepSea eDNA AI](https://img.shields.io/badge/Version-2.1.0-yellow?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.9+-green?style=for-the-badge&logo=python)
![React](https://img.shields.io/badge/React-18.3-blue?style=for-the-badge&logo=react)
![PyTorch](https://img.shields.io/badge/PyTorch-2.5-red?style=for-the-badge&logo=pytorch)

**Advanced AI-Driven eDNA Analysis Platform for Marine Biodiversity Assessment**

[Live Demo](https://deepsea-edna-ai.com) · [Documentation](#documentation) · [Report Bug](https://github.com/jackstealer/issues) · [Request Feature](https://github.com/jackstealer/issues)

</div>

---

## 🌊 Overview

DeepSea eDNA AI is a cutting-edge platform that leverages deep learning and bioinformatics to analyze environmental DNA (eDNA) from marine ecosystems. Our platform achieves **99.9% accuracy** in taxonomic classification and discovers novel taxa through unsupervised learning.

### ✨ Key Features

- 🧠 **Deep Learning Classification** - CNN + Attention architecture with 1.28M parameters
- 🔬 **Novel Taxa Discovery** - Autoencoder-based anomaly detection for new species
- ⚡ **Real-time Processing** - GPU-accelerated analysis in 2-5 minutes per sample
- 🎯 **High Accuracy** - 99.9% classification rate on marine sequences
- 📊 **Comprehensive Analysis** - Diversity metrics, abundance data, and clustering
- 📁 **Multi-format Support** - FASTA, FASTQ, FA, FQ, FAS file formats
- 💾 **Flexible Export** - JSON, CSV, Excel formats with full metadata

---

## 🚀 Quick Start

### Prerequisites

- **Python** 3.9 or higher
- **Node.js** 18 or higher
- **CUDA** (optional, for GPU acceleration)
- **Anaconda** or **pip** for Python package management

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/jackstealer/deepsea-edna-ai.git
   cd deepsea-edna-ai
   ```

2. **Install backend dependencies**

   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Install frontend dependencies**

   ```bash
   cd ..
   npm install
   ```

4. **Set up environment variables**

   ```bash
   # Backend
   cp backend/.env.example backend/.env

   # Frontend
   cp .env.example .env
   ```

5. **Start the application**

   ```bash
   # Terminal 1: Start backend
   cd backend
   python -m uvicorn app.main:app --host 0.0.0.0 --port 3000 --reload

   # Terminal 2: Start frontend
   npm run dev
   ```

6. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:3000
   - API Docs: http://localhost:3000/docs

---

## 📖 Documentation

### Architecture

```
DeepSea eDNA AI
├── Frontend (React + TypeScript + Vite)
│   ├── Sci-fi themed UI with glassmorphism
│   ├── Real-time analysis visualization
│   └── Interactive results dashboard
│
├── Backend (FastAPI + Python)
│   ├── RESTful API endpoints
│   ├── Async processing with job queue
│   └── GPU-accelerated inference
│
└── AI Models (PyTorch)
    ├── DeepTaxaClassifier (CNN + Attention)
    ├── NovelTaxaDetector (Autoencoder)
    └── Sequence Processor (Bioinformatics)
```

### Model Specifications

| Component         | Details                               |
| ----------------- | ------------------------------------- |
| **Architecture**  | CNN + Attention Mechanism             |
| **Parameters**    | 1.28 Million                          |
| **Framework**     | PyTorch 2.5.1                         |
| **Training Data** | 4,000 NCBI marine sequences           |
| **Classes**       | 8 taxonomic groups                    |
| **Accuracy**      | 99.875% (training), 99.9% (inference) |
| **F1 Score**      | 0.9987                                |

### API Endpoints

| Method | Endpoint           | Description           |
| ------ | ------------------ | --------------------- |
| GET    | `/health`          | Health check          |
| POST   | `/api/upload`      | Upload eDNA files     |
| POST   | `/api/analyze`     | Start analysis        |
| GET    | `/api/status/{id}` | Check analysis status |
| GET    | `/api/export/{id}` | Export results        |

---

## 🧪 Usage

### 1. Upload eDNA Files

Upload your eDNA sequence files in FASTA or FASTQ format. Multiple files can be uploaded simultaneously.

### 2. AI Processing

The platform processes your sequences through:

- Quality filtering
- K-mer feature extraction
- Deep learning classification
- UMAP dimensionality reduction
- DBSCAN clustering
- Novel taxa detection

### 3. View Results

Explore comprehensive results including:

- Taxonomic classifications
- Abundance data
- Diversity metrics (Shannon, Simpson)
- Novel taxa discoveries
- Depth distribution analysis

### 4. Export Data

Export results in JSON, CSV, or Excel format with full metadata.

---

## 🎨 Technology Stack

### Frontend

- **React** 18.3.1 - UI framework
- **TypeScript** 5.5.3 - Type safety
- **Vite** 5.4.0 - Build tool
- **Tailwind CSS** 3.4.1 - Styling
- **Framer Motion** 10.18.0 - Animations
- **Lucide React** - Icons

### Backend

- **FastAPI** - Web framework
- **PyTorch** 2.5.1 - Deep learning
- **Biopython** - Bioinformatics
- **NumPy** & **Pandas** - Data processing
- **Uvicorn** - ASGI server

### AI/ML

- **PyTorch** - Neural networks
- **UMAP** - Dimensionality reduction
- **DBSCAN** - Clustering
- **Scikit-learn** - ML utilities

---

## 📊 Performance

- **Processing Speed**: 2-5 minutes per sample
- **Classification Accuracy**: 99.9%
- **GPU Acceleration**: NVIDIA CUDA support
- **Batch Processing**: Multiple files simultaneously
- **Real-time Updates**: WebSocket support

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Team

**Developer**: [jackstealer](https://github.com/jackstealer)

**Contact**: jackstealer690@gmail.com

---

## 🙏 Acknowledgments

- NCBI for marine sequence data
- PyTorch team for the deep learning framework
- FastAPI team for the excellent web framework
- Marine biology research community

---

## 📈 Roadmap

- [ ] Multi-language support
- [ ] Mobile application
- [ ] Real-time collaboration features
- [ ] Advanced visualization tools
- [ ] Integration with public databases
- [ ] Automated report generation
- [ ] Cloud deployment options

---

<div align="center">

**Made with ❤️ for marine conservation**

[⬆ Back to Top](#-deepsea-edna-ai)

</div>
