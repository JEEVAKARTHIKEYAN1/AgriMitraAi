import { useNavigate, Link } from 'react-router-dom';
import { Sprout, Activity, ArrowRight, FlaskConical, CalendarDays } from 'lucide-react';
import { motion, useScroll, useTransform } from 'framer-motion';

const BackgroundEffects = () => (
    <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
        {/* Animated Gradient Blobs */}
        <motion.div
            animate={{
                scale: [1, 1.2, 1],
                x: [0, 100, 0],
                y: [0, 50, 0],
            }}
            transition={{
                duration: 20,
                repeat: Infinity,
                ease: "linear",
            }}
            className="absolute -top-[10%] -right-[10%] w-[500px] h-[500px] bg-primary/10 dark:bg-primary/5 rounded-full blur-[100px]"
        />
        <motion.div
            animate={{
                scale: [1, 1.3, 1],
                x: [0, -100, 0],
                y: [0, -50, 0],
            }}
            transition={{
                duration: 25,
                repeat: Infinity,
                ease: "linear",
            }}
            className="absolute -bottom-[10%] -left-[10%] w-[600px] h-[600px] bg-secondary/10 dark:bg-secondary/5 rounded-full blur-[120px]"
        />
        <motion.div
            animate={{
                scale: [1, 1.5, 1],
                opacity: [0.3, 0.5, 0.3],
            }}
            transition={{
                duration: 15,
                repeat: Infinity,
                ease: "easeInOut",
            }}
            className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-accent/5 dark:bg-accent/2 rounded-full blur-[150px]"
        />

        {/* Mesh Grid Pattern */}
        <div
            className="absolute inset-0 opacity-[0.03] dark:opacity-[0.05]"
            style={{
                backgroundImage: `radial-gradient(circle at 2px 2px, currentColor 1px, transparent 0)`,
                backgroundSize: '32px 32px'
            }}
        />
    </div>
);

const Home = () => {
    const navigate = useNavigate();
    const { scrollYProgress } = useScroll();
    const yHero = useTransform(scrollYProgress, [0, 1], [0, -200]);

    return (
        <div className="relative min-h-screen pt-16 pb-8 px-4 transition-colors duration-300">
            <BackgroundEffects />

            <header className="container mx-auto max-w-6xl text-center pt-12 pb-2 relative z-10">
                <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.5 }}
                    className="inline-block px-4 py-1.5 mb-6 border border-primary/20 rounded-full bg-primary/5 text-primary text-sm font-medium backdrop-blur-sm"
                >
                    🌱 Revolutionizing Agriculture with AI
                </motion.div>

                <motion.h1
                    style={{ y: yHero }}
                    initial={{ opacity: 0, y: 30 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.8, ease: "easeOut" }}
                    className="text-5xl md:text-7xl font-bold mb-6 text-gray-900 dark:text-white tracking-tight"
                >
                    Grow <span className="text-primary italic">Smarter</span> <br />
                    with <span className="bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">AgriMitra AI</span>
                </motion.h1>

                <motion.p
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2, duration: 0.8 }}
                    className="text-lg text-gray-600 dark:text-gray-300 mb-8 max-w-2xl mx-auto leading-relaxed"
                >
                    Empowering farmers with state-of-the-art machine learning to maximize yield,
                    detect diseases early, and build a sustainable future.
                </motion.p>

                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.4, duration: 0.8 }}
                    className="flex flex-col sm:flex-row justify-center gap-6 mb-8"
                >
                    <button
                        onClick={() => navigate('/crop-recommendation')}
                        className="group flex items-center justify-center gap-2 px-8 py-4 bg-primary text-white rounded-2xl font-bold text-lg shadow-xl shadow-primary/25 hover:bg-primary/90 hover:scale-[1.02] active:scale-95 transition-all relative overflow-hidden"
                    >
                        <span className="relative z-10">Get Started Now</span>
                        <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform relative z-10" />
                        <div className="absolute inset-0 bg-gradient-to-r from-white/0 via-white/20 to-white/0 -translate-x-full group-hover:translate-x-full transition-transform duration-1000" />
                    </button>

                    <button
                        onClick={() => document.getElementById('solutions')?.scrollIntoView({ behavior: 'smooth' })}
                        className="px-8 py-4 bg-white dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-200 dark:border-gray-700 rounded-2xl font-bold text-lg shadow-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-all backdrop-blur-sm"
                    >
                        Explore Solutions
                    </button>
                </motion.div>
            </header>

            {/* Features Section */}
            <section id="solutions" className="container mx-auto max-w-7xl pt-16 pb-20 relative z-10">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    className="text-center mb-12"
                >
                    <h2 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-3 tracking-tight">
                        Precision Tools for Modern Farming
                    </h2>
                    <p className="text-gray-600 dark:text-gray-400 max-w-2xl mx-auto text-base leading-relaxed">
                        Our integrated AI ecosystem provides comprehensive support for every stage of your agricultural journey.
                    </p>
                </motion.div>

                <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
                    <FeatureCard
                        icon={Sprout}
                        title="Crop Advisor"
                        description="Intelligent crop matching based on multi-factor environmental analysis."
                        link="/crop-recommendation"
                        delay={0.1}
                        color="text-green-600 dark:text-green-400"
                        bgColor="bg-green-500"
                    />
                    <FeatureCard
                        icon={Activity}
                        title="Leaf Guardian"
                        description="Professional-grade disease detection using high-precision computer vision."
                        link="/plant-disease"
                        delay={0.2}
                        color="text-emerald-600 dark:text-emerald-400"
                        bgColor="bg-emerald-500"
                    />
                    <FeatureCard
                        icon={FlaskConical}
                        title="Soil Analytics"
                        description="Deep chemical analysis and fertility mapping for data-driven nourishment."
                        link="/soil-testing"
                        delay={0.3}
                        color="text-amber-600 dark:text-amber-400"
                        bgColor="bg-amber-500"
                    />
                    <FeatureCard
                        icon={CalendarDays}
                        title="Smart Scheduler"
                        description="Personalized 365-day farming calendar with real-time task optimization."
                        link="/smart-calendar"
                        delay={0.4}
                        color="text-blue-600 dark:text-blue-400"
                        bgColor="bg-blue-500"
                    />
                </div>
            </section>

            {/* How It Works Section */}
            <section className="py-20 relative z-10 overflow-hidden">
                <div className="container mx-auto max-w-6xl px-4">
                    <motion.div
                        initial={{ opacity: 0 }}
                        whileInView={{ opacity: 1 }}
                        viewport={{ once: true }}
                        className="text-center mb-12"
                    >
                        <h2 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-6">How It Works</h2>
                        <div className="w-24 h-1.5 bg-primary mx-auto rounded-full" />
                    </motion.div>

                    <div className="grid md:grid-cols-3 gap-12 relative">
                        {/* Connecting Line (Desktop) */}
                        <div className="hidden md:block absolute top-1/2 left-0 w-full h-0.5 bg-gray-200 dark:bg-gray-800 -z-10 -translate-y-12" />

                        <StepCard
                            number="01"
                            title="Data Input"
                            description="Upload leaf photos or input soil parameters into our secure AI interface."
                            delay={0.1}
                        />
                        <StepCard
                            number="02"
                            title="AI Analysis"
                            description="Our neural networks process your data against millions of agricultural data points."
                            delay={0.3}
                        />
                        <StepCard
                            number="03"
                            title="Smart Results"
                            description="Receive actionable insights, treatment plans, and optimized crop suggestions."
                            delay={0.5}
                        />
                    </div>
                </div>
            </section>

        </div>
    );
};

const StepCard = ({ number, title, description, delay }) => (
    <motion.div
        initial={{ opacity: 0, y: 20 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ delay, duration: 0.6 }}
        className="relative bg-white dark:bg-gray-900/50 p-10 rounded-3xl border border-gray-100 dark:border-gray-800 shadow-xl"
    >
        <div className="text-5xl font-black text-primary/10 absolute top-4 right-8 select-none">
            {number}
        </div>
        <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">{title}</h3>
        <p className="text-gray-600 dark:text-gray-400 leading-relaxed">{description}</p>
    </motion.div>
);

const FeatureCard = ({ icon: Icon, title, description, link, delay, color, bgColor }) => (
    <motion.div
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ delay, duration: 0.5 }}
        whileHover={{ y: -10 }}
        className="group relative bg-white/70 dark:bg-gray-800/70 backdrop-blur-xl p-8 rounded-[2rem] shadow-2xl shadow-gray-200/50 dark:shadow-none border border-white dark:border-gray-700 transition-all duration-300"
    >
        <div className={`w-16 h-16 ${bgColor}/10 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-500 relative`}>
            <Icon className={`w-8 h-8 ${color}`} />
            <div className={`absolute inset-0 ${bgColor} opacity-0 group-hover:opacity-10 rounded-2xl blur-xl transition-opacity animate-pulse`} />
        </div>

        <h3 className="text-2xl font-bold text-gray-800 dark:text-white mb-4 group-hover:text-primary transition-colors">
            {title}
        </h3>

        <p className="text-gray-600 dark:text-gray-400 mb-6 leading-relaxed">
            {description}
        </p>

        <Link
            to={link}
            className="flex items-center gap-2 text-primary font-bold group-hover:gap-3 transition-all"
        >
            Try Tool <ArrowRight className="w-5 h-5" />
        </Link>

        {/* Decorative dots */}
        <div className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity">
            <div className={`w-2 h-2 rounded-full ${bgColor}`} />
        </div>
    </motion.div>
);

export default Home;

