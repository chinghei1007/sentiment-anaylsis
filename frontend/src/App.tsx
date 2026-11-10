import { Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import HomePage from './pages/HomePage'
import PredictPage from './pages/PredictPage'
import BatchPredictPage from './pages/BatchPredictPage'
import KeywordAnalysisPage from './pages/KeywordAnalysisPage'
import TrainingPage from './pages/TrainingPage'
import EvaluationPage from './pages/EvaluationPage'
import DatasetPage from './pages/DatasetPage'
import NotFoundPage from './pages/NotFoundPage'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/predict" element={<PredictPage />} />
        <Route path="/batch" element={<BatchPredictPage />} />
        <Route path="/keywords" element={<KeywordAnalysisPage />} />
        <Route path="/train" element={<TrainingPage />} />
        <Route path="/evaluate" element={<EvaluationPage />} />
        <Route path="/dataset" element={<DatasetPage />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </Layout>
  )
}

export default App
