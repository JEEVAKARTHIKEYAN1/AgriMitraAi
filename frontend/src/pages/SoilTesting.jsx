import React, { useState } from 'react';
import { motion } from 'framer-motion';

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
        <div className="min-h-screen pt-20 pb-10 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
            >
                <div className="text-center mb-10">
                    <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-emerald-500 to-teal-700 mb-4">
                        Soil Testing & Analysis
                    </h1>
                    <p className="text-xl text-gray-600 dark:text-gray-300">
                        Advanced AI-driven soil health assessment for optimal crop yield.
                    </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    {/* Form Section */}
                    <div className="md:col-span-2 bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6 sm:p-8">
                        <h2 className="text-2xl font-semibold mb-6 flex items-center gap-2 text-gray-800 dark:text-white">
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
                                            className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 dark:bg-gray-700 focus:ring-2 focus:ring-emerald-500 focus:outline-none transition-all"
                                            placeholder="0.0"
                                        />
                                    </div>
                                ))}
                            </div>

                            {/* Environmental Grid */}
                            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 border-t pt-4 dark:border-gray-700">
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
                                            className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 dark:bg-gray-700 focus:ring-2 focus:ring-emerald-500 focus:outline-none transition-all"
                                        />
                                    </div>
                                ))}
                            </div>

                            <motion.button
                                whileHover={{ scale: 1.02 }}
                                whileTap={{ scale: 0.98 }}
                                type="submit"
                                disabled={loading}
                                className={`w-full py-4 text-lg font-bold text-white rounded-xl shadow-lg transition-all ${loading ? 'bg-gray-400 cursor-not-allowed' : 'bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700'
                                    }`}
                            >
                                {loading ? 'Analyzing Soil...' : 'Analyze Soil Health'}
                            </motion.button>
                        </form>
                    </div>

                    {/* Result Section */}
                    <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6 sm:p-8 flex flex-col items-center justify-center text-center">
                        {result ? (
                            <motion.div
                                initial={{ scale: 0.8, opacity: 0 }}
                                animate={{ scale: 1, opacity: 1 }}
                                className="space-y-6 w-full"
                            >
                                <div className="w-20 h-20 bg-emerald-100 rounded-full flex items-center justify-center mx-auto">
                                    <span className="text-4xl">🌱</span>
                                </div>

                                <h3 className="text-xl font-bold text-gray-800 dark:text-white border-b pb-2">Analysis Report</h3>

                                {/* Primary Prediction */}
                                <div className="p-3 bg-emerald-50 dark:bg-emerald-900/30 rounded-xl border border-emerald-200 dark:border-emerald-700">
                                    <span className="text-gray-500 dark:text-gray-400 text-xs uppercase tracking-wide">Soil Status</span>
                                    <div className="text-2xl font-extrabold text-emerald-600 dark:text-emerald-400 mt-1">
                                        {getStatusText(result.prediction)}
                                    </div>
                                </div>

                                {/* Secondary AI Insights */}
                                <div className="grid grid-cols-2 gap-3 text-left">
                                    <div className="p-3 bg-blue-50 dark:bg-blue-900/30 rounded-lg border border-blue-100 dark:border-blue-800">
                                        <span className="text-xs text-blue-600 dark:text-blue-300 block mb-1">Soil Type</span>
                                        <span className="font-bold text-gray-800 dark:text-white">{result.soil_type}</span>
                                    </div>
                                    <div className="p-3 bg-amber-50 dark:bg-amber-900/30 rounded-lg border border-amber-100 dark:border-amber-800">
                                        <span className="text-xs text-amber-600 dark:text-amber-300 block mb-1">Fertility Level</span>
                                        <span className="font-bold text-gray-800 dark:text-white">{result.fertility}</span>
                                    </div>
                                </div>

                            </motion.div>
                        ) : (
                            <div className="text-gray-400">
                                <div className="w-20 h-20 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-4">
                                    <span className="text-3xl">🔍</span>
                                </div>
                                <p>Fill out the form to let our AI analyze soil composition.</p>
                            </div>
                        )}

                        {error && (
                            <div className="mt-4 p-3 bg-red-100 text-red-700 rounded-lg w-full text-sm">
                                ❌ {error}
                            </div>
                        )}
                    </div>
                </div>
            </motion.div>
        </div>
    );
};

export default SoilTesting;
