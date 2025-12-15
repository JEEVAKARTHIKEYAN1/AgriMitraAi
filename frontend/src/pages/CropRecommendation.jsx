import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sprout, Thermometer, Droplets, Wind, Activity, Loader2, AlertCircle } from 'lucide-react';
import axios from 'axios';
import ChatInterface from '../components/ChatInterface';

const InputField = ({ label, name, value, onChange, icon: Icon, min = 0, max, step = 0.1 }) => (
    <div className="space-y-2">
        <label className="text-sm font-medium text-gray-700 dark:text-gray-300 flex items-center gap-2">
            <Icon className="w-4 h-4 text-primary" />
            {label}
        </label>
        <div className="relative">
            <input
                type="number"
                name={name}
                value={value}
                onChange={onChange}
                min={min}
                max={max}
                step={step}
                className="w-full px-4 py-3 bg-white dark:bg-gray-700/50 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-primary/20 focus:border-primary dark:focus:border-primary outline-none transition-all text-gray-900 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500"
                placeholder="0.0"
                required
            />
        </div>
    </div>
);

const CropRecommendation = () => {
    const [formData, setFormData] = useState({
        N: '', P: '', K: '',
        temperature: '', humidity: '', ph: '', rainfall: ''
    });
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setResult(null);

        // Convert values to float
        const payload = {};
        for (const key in formData) {
            payload[key] = parseFloat(formData[key]);
        }

        try {
            const response = await axios.post(import.meta.env.VITE_CROP_API_URL || 'http://localhost:5000/predict', payload);
            setResult(response.data);
        } catch (err) {
            setError('Failed to get recommendation. Ensure the backend is running on port 5000.');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen pt-24 pb-12 px-4 bg-[#F0F7F4] dark:bg-gray-900 transition-colors duration-300">
            <div className="container mx-auto max-w-4xl">
                <div className="text-center mb-12">
                    <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">Crop Recommendation</h1>
                    <p className="text-gray-600 dark:text-gray-400">Enter the soil and weather conditions to get an AI-powered crop suggestion.</p>
                </div>

                <div className="grid lg:grid-cols-3 gap-8">
                    {/* Form Section */}
                    <div className="lg:col-span-2">
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="bg-white dark:bg-gray-800 rounded-3xl p-8 shadow-xl shadow-gray-100/50 dark:shadow-none border border-white/50 dark:border-gray-700 transition-all"
                        >
                            <form onSubmit={handleSubmit} className="space-y-6">
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    <div className="col-span-full pb-2 border-b border-gray-100 text-gray-500 font-medium text-sm uppercase tracking-wider">
                                        Soil Nutrients
                                    </div>
                                    <InputField label="Nitrogen (N)" name="N" value={formData.N} onChange={handleChange} icon={Sprout} />
                                    <InputField label="Phosphorus (P)" name="P" value={formData.P} onChange={handleChange} icon={Sprout} />
                                    <InputField label="Potassium (K)" name="K" value={formData.K} onChange={handleChange} icon={Sprout} />

                                    <div className="col-span-full pb-2 border-b border-gray-100 text-gray-500 font-medium text-sm uppercase tracking-wider mt-4">
                                        Environmental Factors
                                    </div>
                                    <InputField label="Temperature (°C)" name="temperature" value={formData.temperature} onChange={handleChange} icon={Thermometer} />
                                    <InputField label="Humidity (%)" name="humidity" value={formData.humidity} onChange={handleChange} icon={Droplets} />
                                    <InputField label="pH Level" name="ph" value={formData.ph} onChange={handleChange} icon={Activity} min={0} max={14} />
                                    <InputField label="Rainfall (mm)" name="rainfall" value={formData.rainfall} onChange={handleChange} icon={Wind} />
                                </div>

                                <button
                                    type="submit"
                                    disabled={loading}
                                    className="w-full py-4 bg-primary text-white rounded-xl font-semibold shadow-lg shadow-primary/30 hover:shadow-xl hover:-translate-y-0.5 transition-all disabled:opacity-70 disabled:cursor-not-allowed flex items-center justify-center gap-2 mt-8"
                                >
                                    {loading ? <Loader2 className="animate-spin" /> : 'Analyze & Recommend'}
                                </button>
                            </form>
                        </motion.div>

                        {/* Chat Interface - Only show when we have a result */}
                        {result && !loading && (
                            <ChatInterface context={{ ...result, ...formData }} />
                        )}
                    </div>

                    {/* Result Section */}
                    <div className="lg:col-span-1">
                        <AnimatePresence mode="wait">
                            {result && !loading && (
                                <motion.div
                                    key="result"
                                    initial={{ opacity: 0, scale: 0.9 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    exit={{ opacity: 0, scale: 0.9 }}
                                    className="bg-white dark:bg-gray-800 rounded-3xl p-8 shadow-xl border-t-8 border-primary sticky top-24 transition-colors"
                                >
                                    <div className="flex flex-col items-center text-center space-y-4">
                                        <div className="w-20 h-20 bg-green-100 dark:bg-primary/20 rounded-full flex items-center justify-center text-primary mb-2">
                                            <Sprout className="w-10 h-10" />
                                        </div>
                                        <div>
                                            <h3 className="text-gray-500 dark:text-gray-400 font-medium mb-1">Recommended Crop</h3>
                                            <h2 className="text-3xl font-bold text-gray-800 dark:text-white capitalize">{result.recommended_crop}</h2>
                                        </div>

                                        <div className="w-full pt-6 border-t border-gray-100 dark:border-gray-700">
                                            <div className="flex justify-between items-center text-sm">
                                                <span className="text-gray-500 dark:text-gray-400">Confidence</span>
                                                <span className="font-bold text-primary">{result.confidence}</span>
                                            </div>
                                            <div className="w-full bg-gray-100 dark:bg-gray-700 rounded-full h-2 mt-2">
                                                <div
                                                    className="bg-primary h-2 rounded-full"
                                                    style={{ width: result.confidence }}
                                                />
                                            </div>
                                        </div>
                                    </div>
                                </motion.div>
                            )}

                            {error && (
                                <motion.div
                                    key="error"
                                    initial={{ opacity: 0 }}
                                    animate={{ opacity: 1 }}
                                    className="bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 p-6 rounded-2xl border border-red-100 dark:border-red-800 flex items-start gap-3"
                                >
                                    <AlertCircle className="w-5 h-5 shrink-0 mt-0.5" />
                                    <p className="text-sm">{error}</p>
                                </motion.div>
                            )}

                            {!result && !error && !loading && (
                                <div key="placeholder" className="bg-white/50 dark:bg-gray-800/50 border border-dashed border-gray-300 dark:border-gray-600 rounded-3xl p-8 text-center text-gray-400 dark:text-gray-500 h-full flex flex-col items-center justify-center transition-colors">
                                    <Sprout className="w-12 h-12 mb-4 opacity-50" />
                                    <p>Results will appear here</p>
                                </div>
                            )}
                        </AnimatePresence>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default CropRecommendation;
