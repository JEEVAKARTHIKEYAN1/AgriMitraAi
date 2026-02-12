import { useNavigate, Link } from 'react-router-dom';
import { Sprout, Activity, ArrowRight, Leaf, FlaskConical, CalendarDays } from 'lucide-react';
import { motion } from 'framer-motion';

const Home = () => {
    const navigate = useNavigate();

    return (
        <div className="pt-24 pb-12 px-4 transition-colors duration-300 overflow-hidden">
            {/* Hero Section */}
            <div className="absolute top-0 left-0 w-full h-[600px] bg-gradient-to-br from-green-50 via-white to-green-50 dark:from-gray-900 dark:via-gray-900 dark:to-green-900/10 -z-10 transition-colors duration-500" />

            {/* Ambient Background Blobs */}
            <div className="fixed top-0 right-0 w-[500px] h-[500px] bg-secondary/30 dark:bg-primary/10 rounded-full blur-[100px] -z-10 opacity-50 pointer-events-none" />
            <div className="fixed bottom-0 left-0 w-[500px] h-[500px] bg-accent/20 dark:bg-yellow-500/5 rounded-full blur-[100px] -z-10 opacity-30 pointer-events-none" />

            <header className="container mx-auto max-w-6xl text-center pt-20 pb-4 relative z-10">
                <motion.h1
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-5xl md:text-7xl font-bold mb-6 text-gray-900 dark:text-white"
                >
                    Smart Farming with <span className="text-primary">AI</span>
                </motion.h1>
                <motion.p
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    className="text-xl text-gray-600 dark:text-gray-300 mb-10 max-w-2xl mx-auto"
                >
                    Optimize your crop yield and detect plant diseases instantly using our advanced machine learning models.
                </motion.p>
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                    className="flex justify-center gap-4"
                >
                    <button
                        onClick={() => navigate('/crop-recommendation')}
                        className="px-8 py-4 bg-primary text-white rounded-xl font-semibold shadow-lg shadow-primary/30 hover:shadow-xl hover:-translate-y-1 transition-all flex items-center gap-2"
                    >
                        Get Started <ArrowRight className="w-5 h-5" />
                    </button>
                </motion.div>
            </header>

            {/* Features Section */}
            <section className="container mx-auto max-w-6xl pt-4 pb-16">
                <h2 className="text-4xl font-bold text-center mb-12 text-gray-900 dark:text-white">Our Solutions</h2>
                <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
                    <FeatureCard
                        icon={Sprout}
                        title="Crop Recommendation"
                        description="Data-driven suggestions for optimal crop selection based on soil & weather."
                        link="/crop-recommendation"
                        delay={0.3}
                    />
                    <FeatureCard
                        icon={Activity}
                        title="Disease Detection"
                        description="Instant identification of plant diseases from leaf images using Computer Vision."
                        link="/plant-disease"
                        delay={0.4}
                    />
                    <FeatureCard
                        icon={FlaskConical}
                        title="Soil Testing"
                        description="Analyze soil nutrients and get fertility insights with AI precision."
                        link="/soil-testing"
                        delay={0.5}
                    />
                    <FeatureCard
                        icon={CalendarDays}
                        title="Smart Calendar"
                        description="AI-powered farming schedules and task management for optimal crop planning."
                        link="/smart-calendar"
                        delay={0.6}
                    />
                </div>
            </section>
        </div>
    );
};

const FeatureCard = ({ icon: Icon, title, description, link, delay }) => (
    <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay }}
        whileHover={{ y: -5 }}
        className="bg-white dark:bg-gray-800 p-8 rounded-3xl shadow-xl shadow-gray-100/50 dark:shadow-none border border-white/50 dark:border-gray-700 transition-colors"
    >
        <div className="w-14 h-14 bg-primary/10 rounded-2xl flex items-center justify-center mb-6 text-primary">
            <Icon className="w-7 h-7" />
        </div>
        <h3 className="text-2xl font-bold text-gray-800 dark:text-white mb-3">{title}</h3>
        <p className="text-gray-600 dark:text-gray-400 mb-6 leading-relaxed">{description}</p>
        <Link
            to={link}
            className="inline-flex items-center text-primary font-semibold hover:gap-2 transition-all gap-1"
        >
            Try Now <ArrowRight className="w-4 h-4" />
        </Link>
    </motion.div>
);

export default Home;
