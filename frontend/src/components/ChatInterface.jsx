import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, Loader2, Sparkles } from 'lucide-react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';

const ChatInterface = ({ context, apiEndpoint = import.meta.env.VITE_CROP_CHAT_URL || 'http://localhost:5000/chat' }) => {
    const [messages, setMessages] = useState([
        {
            role: 'model',
            content: `Hello! I am your AI Consultant. Based on the analysis (${context.recommended_crop || context.prediction}), how can I help you?`
        }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSend = async (e) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userMsg = input.trim();
        setInput('');
        setMessages(prev => [...prev, { role: 'user', content: userMsg }]);
        setLoading(true);

        try {
            // Prepare history for backend
            const history = messages.slice(1).map(msg => ({
                role: msg.role,
                content: msg.content
            }));

            const response = await axios.post(apiEndpoint, {
                message: userMsg,
                context: context,
                history: history
            });

            const reply = response.data.reply;
            setMessages(prev => [...prev, { role: 'model', content: reply }]);
        } catch (error) {
            console.error("Chat error:", error);
            setMessages(prev => [...prev, { role: 'model', content: "Sorry, I am having trouble connecting to the server. Please check your connection." }]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white dark:bg-gray-800 rounded-3xl shadow-xl border border-gray-100 dark:border-gray-700 overflow-hidden mt-8 flex flex-col h-[500px]"
        >
            {/* Header */}
            <div className="p-4 bg-gradient-to-r from-primary to-green-600 text-white flex items-center gap-3">
                <div className="p-2 bg-white/20 rounded-full backdrop-blur-sm">
                    <Sparkles className="w-5 h-5" />
                </div>
                <div>
                    <h3 className="font-semibold text-lg">Agri-Expert AI</h3>
                    <p className="text-xs text-white/80">Ask about {context.recommended_crop}, fertilizers, or diseases</p>
                </div>
            </div>

            {/* Messages Area */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4 bg-gray-50 dark:bg-gray-900/50">
                {messages.map((msg, idx) => (
                    <motion.div
                        key={idx}
                        initial={{ opacity: 0, scale: 0.95 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className={`flex items-start gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}
                    >
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${msg.role === 'user' ? 'bg-blue-100 text-blue-600' : 'bg-green-100 text-green-600'
                            }`}>
                            {msg.role === 'user' ? <User className="w-5 h-5" /> : <Bot className="w-5 h-5" />}
                        </div>

                        <div className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed ${msg.role === 'user'
                            ? 'bg-blue-600 text-white rounded-tr-none'
                            : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-200 border border-gray-100 dark:border-gray-700 rounded-tl-none shadow-sm'
                            }`}>
                            {msg.role === 'model' ? (
                                <div className="whitespace-pre-wrap">{msg.content}</div>
                            ) : (
                                msg.content
                            )}
                        </div>
                    </motion.div>
                ))}

                {loading && (
                    <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-green-100 text-green-600 flex items-center justify-center">
                            <Bot className="w-5 h-5" />
                        </div>
                        <div className="bg-white dark:bg-gray-800 px-4 py-3 rounded-2xl rounded-tl-none border border-gray-100 dark:border-gray-700 shadow-sm flex items-center gap-2">
                            <Loader2 className="w-4 h-4 animate-spin text-primary" />
                            <span className="text-xs text-gray-500">Thinking...</span>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <form onSubmit={handleSend} className="p-4 bg-white dark:bg-gray-800 border-t border-gray-100 dark:border-gray-700">
                <div className="relative flex items-center">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Ask a follow-up question..."
                        className="w-full pl-5 pr-12 py-3 bg-gray-100 dark:bg-gray-900 rounded-xl focus:ring-2 focus:ring-primary/20 focus:outline-none text-gray-800 dark:text-gray-200"
                        disabled={loading}
                    />
                    <button
                        type="submit"
                        disabled={!input.trim() || loading}
                        className="absolute right-2 p-2 bg-primary text-white rounded-lg hover:bg-primary/90 disabled:opacity-50 disabled:hover:bg-primary transition-colors"
                    >
                        <Send className="w-4 h-4" />
                    </button>
                </div>
            </form>
        </motion.div>
    );
};

export default ChatInterface;
