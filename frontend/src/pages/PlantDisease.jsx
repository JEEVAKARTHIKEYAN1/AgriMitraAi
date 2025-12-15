import { useState, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, X, Check, Loader2, AlertCircle, Image as ImageIcon } from 'lucide-react';
import axios from 'axios';
import ChatInterface from '../components/ChatInterface';

const PlantDisease = () => {
    const [file, setFile] = useState(null);
    const [preview, setPreview] = useState(null);
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);
    const fileInputRef = useRef(null);

    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        if (selectedFile) {
            if (!selectedFile.type.startsWith('image/')) {
                setError('Please upload a valid image file');
                return;
            }
            setFile(selectedFile);
            setPreview(URL.createObjectURL(selectedFile));
            setResult(null);
            setError(null);
        }
    };

    const handleDragOver = (e) => {
        e.preventDefault();
    };

    const handleDrop = (e) => {
        e.preventDefault();
        const droppedFile = e.dataTransfer.files[0];
        if (droppedFile) {
            if (!droppedFile.type.startsWith('image/')) {
                setError('Please upload a valid image file');
                return;
            }
            setFile(droppedFile);
            setPreview(URL.createObjectURL(droppedFile));
            setResult(null);
            setError(null);
        }
    };

    const handleSubmit = async () => {
        if (!file) return;

        setLoading(true);
        setError(null);

        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await axios.post('http://localhost:5001/predict', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            setResult(response.data);
        } catch (err) {
            setError('Failed to analyze image. Ensure the plant disease backend is running on port 5001.');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen pt-24 pb-12 px-4 bg-[#F0F7F4] dark:bg-gray-900 transition-colors duration-300">
            <div className="container mx-auto max-w-3xl">
                <div className="text-center mb-12">
                    <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">Plant Disease Detection</h1>
                    <p className="text-gray-600 dark:text-gray-400">Upload a photo of your plant leaf to identify diseases instantly.</p>
                </div>

                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="bg-white dark:bg-gray-800 rounded-3xl p-8 shadow-xl shadow-gray-100/50 dark:shadow-none border border-white/50 dark:border-gray-700 transition-all"
                >
                    {/* Upload Area */}
                    <div
                        onDragOver={handleDragOver}
                        onDrop={handleDrop}
                        onClick={() => !file && fileInputRef.current?.click()}
                        className={`relative border-2 border-dashed rounded-2xl min-h-[300px] flex flex-col items-center justify-center transition-all cursor-pointer overflow-hidden ${file ? 'border-primary/50 bg-primary/5 dark:bg-primary/10' : 'border-gray-300 dark:border-gray-600 hover:border-primary dark:hover:border-primary hover:bg-gray-50 dark:hover:bg-gray-700/30'
                            }`}
                    >
                        <input
                            type="file"
                            ref={fileInputRef}
                            className="hidden"
                            accept="image/*"
                            onChange={handleFileChange}
                        />

                        {preview ? (
                            <div className="relative w-full h-full min-h-[300px] bg-black/5">
                                <img
                                    src={preview}
                                    alt="Preview"
                                    className="absolute inset-0 w-full h-full object-contain p-4"
                                />
                                <button
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        setFile(null);
                                        setPreview(null);
                                        setResult(null);
                                    }}
                                    className="absolute top-4 right-4 p-2 bg-white/90 rounded-full shadow-lg hover:bg-red-50 hover:text-red-500 transition-colors"
                                >
                                    <X className="w-5 h-5" />
                                </button>
                            </div>
                        ) : (
                            <div className="text-center p-8">
                                <div className="w-20 h-20 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4 text-primary">
                                    <Upload className="w-10 h-10" />
                                </div>
                                <h3 className="text-xl font-bold text-gray-800 dark:text-white mb-2">Click or Drag & Drop</h3>
                                <p className="text-gray-500 dark:text-gray-400 text-sm">Upload a clear image of the affected leaf</p>
                                <p className="text-xs text-gray-400 dark:text-gray-500 mt-2">JPG, PNG supported</p>
                            </div>
                        )}
                    </div>

                    <AnimatePresence>
                        {file && !result && (
                            <motion.div
                                initial={{ opacity: 0, height: 0 }}
                                animate={{ opacity: 1, height: 'auto' }}
                                exit={{ opacity: 0, height: 0 }}
                                className="mt-6 text-center"
                            >
                                <button
                                    onClick={handleSubmit}
                                    disabled={loading}
                                    className="px-8 py-3 bg-primary text-white rounded-xl font-semibold shadow-lg shadow-primary/30 hover:shadow-xl hover:-translate-y-0.5 transition-all disabled:opacity-70 disabled:cursor-not-allowed flex items-center gap-2 mx-auto"
                                >
                                    {loading ? (
                                        <>
                                            <Loader2 className="animate-spin w-5 h-5" /> Analyzing...
                                        </>
                                    ) : (
                                        <>
                                            <ImageIcon className="w-5 h-5" /> Identify Disease
                                        </>
                                    )}
                                </button>
                            </motion.div>
                        )}
                    </AnimatePresence>

                    {/* Results Area */}
                    <AnimatePresence mode="wait">
                        {result && (
                            <motion.div
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="mt-8 bg-green-50 dark:bg-green-900/20 rounded-2xl p-6 border border-green-100 dark:border-green-800 flex items-start gap-4"
                            >
                                <div className="bg-green-100 dark:bg-green-900/40 p-3 rounded-full shrink-0">
                                    <Check className="w-6 h-6 text-green-700 dark:text-green-400" />
                                </div>
                                <div>
                                    <h4 className="text-sm font-medium text-green-800 dark:text-green-300 uppercase tracking-wide mb-1">Analysis Result</h4>
                                    <h2 className="text-2xl font-bold text-gray-900 dark:text-white">{result.prediction}</h2>
                                    <p className="text-green-700/80 dark:text-green-400/80 text-sm mt-1">
                                        Our AI has identified this pattern with high confidence.
                                    </p>
                                </div>
                            </motion.div>
                        )}

                        {error && (
                            <motion.div
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="mt-8 bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 p-6 rounded-2xl border border-red-100 dark:border-red-800 flex items-center gap-3"
                            >
                                <AlertCircle className="w-6 h-6 shrink-0" />
                                <p>{error}</p>
                            </motion.div>
                        )}
                    </AnimatePresence>

                    {/* Chatbot Integration */}
                    {result && !loading && (
                        <ChatInterface
                            context={result}
                            apiEndpoint="http://localhost:5001/chat"
                        />
                    )}

                </motion.div>
            </div>
        </div>
    );
};

export default PlantDisease;
