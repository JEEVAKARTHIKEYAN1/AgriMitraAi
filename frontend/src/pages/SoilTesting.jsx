import React, { useState } from 'react';
import { motion } from 'framer-motion';
import ChatInterface from '../components/ChatInterface';

const SoilTesting = () => {
    const [formData, setFormData] = useState({
        N: '', P: '', K: '', pH: '', EC: '', OC: '', S: '',
        Zn: '', Fe: '', Cu: '', Mn: '', B: '',
        Moisture: '', Annual_Rainfall: '', Temperature: ''
    });

    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setResult(null);

        try {
            // Helper to safely parse float
            const safeFloat = (val) => {
                const parsed = parseFloat(val);
                return isNaN(parsed) ? 0.0 : parsed;
            };

            // Convert numeric fields
            const payload = {
                N: safeFloat(formData.N),
                P: safeFloat(formData.P),
                K: safeFloat(formData.K),
                pH: safeFloat(formData.pH),
                EC: safeFloat(formData.EC),
                OC: safeFloat(formData.OC),
                S: safeFloat(formData.S),
                Zn: safeFloat(formData.Zn),
                Fe: safeFloat(formData.Fe),
                Cu: safeFloat(formData.Cu),
                Mn: safeFloat(formData.Mn),
                B: safeFloat(formData.B),
                Moisture: safeFloat(formData.Moisture),
                Annual_Rainfall: safeFloat(formData.Annual_Rainfall),
                Temperature: safeFloat(formData.Temperature),
            };

            const response = await fetch('http://localhost:5002/predict_soil', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(payload),
            });

            if (!response.ok) {
                // Try to parse error message from JSON response
                try {
                    const errorData = await response.json();
                    throw new Error(errorData.error || 'Server returned an error');
                } catch (jsonError) {
                    throw new Error(`Prediction failed with status: ${response.status}`);
                }
            }

            const data = await response.json();
            setResult(data);
        } catch (err) {
            console.error(err);
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    // Map numeric prediction to descriptive text
    const getStatusText = (pred) => {
        // Mapping based on dataset analysis: 0=Low, 1=Medium, 2=High
        const map = {
            0: "Needs Attention (Low)",
            1: "Balanced (Medium)",
            2: "High Yielding (High)"
        };
        return map[pred] || "Unknown";
    };

    return (
        <div className="min-h-screen pt-24 pb-12 px-4 bg-[#F0F7F4] dark:bg-gray-900 transition-colors duration-300">
            <div className="container mx-auto max-w-4xl">
                <div className="text-center mb-12">
                    <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">Soil Testing & Analysis</h1>
                    <p className="text-gray-600 dark:text-gray-400">Advanced AI-driven soil health assessment for optimal crop yield.</p>
                </div>

                <div className="grid lg:grid-cols-3 gap-8">
                    {/* Form Section */}
                    <div className="lg:col-span-2">
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            className="bg-white dark:bg-gray-800 rounded-3xl p-8 shadow-xl shadow-gray-100/50 dark:shadow-none border border-white/50 dark:border-gray-700 transition-all"
                        >
                            <h2 className="text-xl font-semibold mb-6 flex items-center gap-2 text-gray-800 dark:text-white pb-4 border-b border-gray-100 dark:border-gray-700">
                                📝 Enter Soil Matrix Data
                            </h2>

                            <form onSubmit={handleSubmit} className="space-y-6">
                                {/* Nutrient Grid */}
                                <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
                                    {['N', 'P', 'K', 'pH', 'EC', 'OC', 'S', 'Zn', 'Fe', 'Cu', 'Mn', 'B'].map((field) => (
                                        <div key={field}>
                                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{field}</label>
                                            <input
                                                type="number"
                                                step="any"
                                                name={field}
                                                value={formData[field]}
                                                onChange={handleChange}
                                                required
                                                className="w-full px-4 py-3 bg-white dark:bg-gray-700/50 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-primary/20 focus:border-primary dark:focus:border-primary outline-none transition-all text-gray-900 dark:text-gray-100 placeholder-gray-400"
                                                placeholder="0.0"
                                            />
                                        </div>
                                    ))}
                                </div>

                                {/* Environmental Grid */}
                                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 border-t border-gray-100 dark:border-gray-700 pt-6">
                                    {['Moisture', 'Annual_Rainfall', 'Temperature'].map((field) => (
                                        <div key={field}>
                                            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">{field.replace('_', ' ')}</label>
                                            <input
                                                type="number"
                                                step="any"
                                                name={field}
                                                value={formData[field]}
                                                onChange={handleChange}
                                                required
                                                className="w-full px-4 py-3 bg-white dark:bg-gray-700/50 border border-gray-200 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-primary/20 focus:border-primary dark:focus:border-primary outline-none transition-all text-gray-900 dark:text-gray-100 placeholder-gray-400"
                                            />
                                        </div>
                                    ))}
                                </div>

                                <motion.button
                                    whileHover={{ scale: 1.01 }}
                                    whileTap={{ scale: 0.99 }}
                                    type="submit"
                                    disabled={loading}
                                    className="w-full py-4 bg-primary text-white rounded-xl font-semibold shadow-lg shadow-primary/30 hover:shadow-xl hover:-translate-y-0.5 transition-all disabled:opacity-70 disabled:cursor-not-allowed flex items-center justify-center gap-2 mt-8"
                                >
                                    {loading ? 'Analyzing Soil...' : 'Analyze Soil Health'}
                                </motion.button>
                            </form>
                        </motion.div>

                        {/* Chatbot Integration - Only show when we have a result */}
                        {result && !loading && (
                            <ChatInterface
                                context={{ ...result, prediction: getStatusText(result.prediction), input_params: formData }}
                                apiEndpoint="http://localhost:5002/chat"
                            />
                        )}
                    </div>

                    {/* Result Section */}
                    <div className="lg:col-span-1">
                        {result ? (
                            <motion.div
                                initial={{ opacity: 0, scale: 0.9 }}
                                animate={{ opacity: 1, scale: 1 }}
                                className="bg-white dark:bg-gray-800 rounded-3xl p-8 shadow-xl border-t-8 border-primary sticky top-24 transition-colors"
                            >
                                <div className="flex flex-col items-center text-center space-y-6">
                                    <div className="w-20 h-20 bg-green-100 dark:bg-primary/20 rounded-full flex items-center justify-center text-primary">
                                        <span className="text-4xl">🌱</span>
                                    </div>

                                    <div>
                                        <h3 className="text-gray-500 dark:text-gray-400 font-medium mb-1 uppercase tracking-wider text-xs">Soil Status</h3>
                                        <h2 className="text-2xl font-bold text-gray-800 dark:text-white">{getStatusText(result.prediction)}</h2>
                                    </div>

                                    <div className="w-full pt-6 border-t border-gray-100 dark:border-gray-700 space-y-4">
                                        <div className="flex justify-between items-center p-3 bg-blue-50 dark:bg-blue-900/20 rounded-xl">
                                            <span className="text-sm text-gray-600 dark:text-gray-400">Soil Type</span>
                                            <span className="font-bold text-blue-700 dark:text-blue-400">{result.soil_type}</span>
                                        </div>
                                        <div className="flex justify-between items-center p-3 bg-amber-50 dark:bg-amber-900/20 rounded-xl">
                                            <span className="text-sm text-gray-600 dark:text-gray-400">Fertility</span>
                                            <span className="font-bold text-amber-700 dark:text-amber-400">{result.fertility}</span>
                                        </div>
                                    </div>
                                </div>
                            </motion.div>
                        ) : (
                            !error && !loading && (
                                <div className="bg-white/50 dark:bg-gray-800/50 border border-dashed border-gray-300 dark:border-gray-600 rounded-3xl p-8 text-center text-gray-400 dark:text-gray-500 h-64 flex flex-col items-center justify-center transition-colors">
                                    <span className="text-4xl mb-4 opacity-50">🔍</span>
                                    <p>Results will appear here</p>
                                </div>
                            )
                        )}

                        {error && (
                            <motion.div
                                initial={{ opacity: 0 }}
                                animate={{ opacity: 1 }}
                                className="bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 p-6 rounded-2xl border border-red-100 dark:border-red-800 flex items-start gap-3 mt-6"
                            >
                                <span className="text-xl">❌</span>
                                <p className="text-sm">{error}</p>
                            </motion.div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default SoilTesting;
