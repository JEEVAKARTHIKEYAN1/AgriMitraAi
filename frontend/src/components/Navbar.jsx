import { Link, useLocation } from 'react-router-dom';
import { Leaf, Sun, Moon } from 'lucide-react';
import { motion } from 'framer-motion';
import { useTheme } from '../context/ThemeContext';

const Navbar = () => {
    const location = useLocation();

    const { theme, toggleTheme } = useTheme();
    const isActive = (path) => location.pathname === path;

    return (
        <nav className="fixed top-0 left-0 w-full z-50 bg-white/80 dark:bg-gray-900/80 backdrop-blur-md shadow-sm dark:shadow-none border-b border-white/0 dark:border-white/5 transition-all duration-300">
            <div className="container mx-auto px-6 h-20 flex items-center justify-between">
                <Link to="/" className="flex items-center gap-2 group">
                    <div className="bg-primary p-2 rounded-lg group-hover:bg-primary/90 transition-colors">
                        <Leaf className="text-white w-6 h-6" />
                    </div>
                    <span className="text-2xl font-bold text-gray-800 dark:text-white tracking-tight transition-colors">
                        Agri<span className="text-primary">Mitra</span>AI
                    </span>
                </Link>

                <div className="hidden md:flex items-center gap-8">
                    <NavLink to="/" active={isActive('/')}>Home</NavLink>
                    <NavLink to="/crop-recommendation" active={isActive('/crop-recommendation')}>Crop Recommend</NavLink>
                    <NavLink to="/plant-disease" active={isActive('/plant-disease')}>Plant Disease</NavLink>
                    <NavLink to="/soil-testing" active={isActive('/soil-testing')}>Soil Testing</NavLink>

                    <button
                        onClick={toggleTheme}
                        className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                        aria-label="Toggle Theme"
                    >
                        {theme === 'light' ? (
                            <Moon className="w-5 h-5 text-gray-600 dark:text-gray-300" />
                        ) : (
                            <Sun className="w-5 h-5 text-yellow-400" />
                        )}
                    </button>
                </div>

                <div className="md:hidden">
                    {/* Mobile menu button could go here */}
                </div>
            </div>
        </nav>
    );
};

const NavLink = ({ to, children, active }) => (
    <Link
        to={to}
        className={`relative font-medium transition-colors ${active ? 'text-primary' : 'text-gray-600 dark:text-gray-300 hover:text-primary dark:hover:text-primary'
            }`}
    >
        {children}
        {active && (
            <motion.div
                layoutId="underline"
                className="absolute -bottom-1 left-0 w-full h-0.5 bg-primary rounded-full"
            />
        )}
    </Link>
);

export default Navbar;
