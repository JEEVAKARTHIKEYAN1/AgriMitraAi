import { Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import CropRecommendation from './pages/CropRecommendation';
import PlantDisease from './pages/PlantDisease';
import SoilTesting from './pages/SoilTesting';
import { ThemeProvider } from './context/ThemeContext';

function App() {
  return (
    <ThemeProvider>
      <div className="bg-background min-h-screen font-sans text-gray-900 transition-colors duration-300 dark:bg-gray-900 dark:text-white">
        <Navbar />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/crop-recommendation" element={<CropRecommendation />} />
          <Route path="/plant-disease" element={<PlantDisease />} />
          <Route path="/soil-testing" element={<SoilTesting />} />
        </Routes>
      </div>
    </ThemeProvider>
  );
}

export default App;
