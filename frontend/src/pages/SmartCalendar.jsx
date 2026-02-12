import { useState, useEffect } from 'react';
import { Calendar, Plus, Trash2, Check, X, MessageSquare, Sparkles, ChevronLeft, ChevronRight, AlertTriangle, Edit2, List } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const SmartCalendar = () => {
    const [currentDate, setCurrentDate] = useState(new Date());
    const [tasks, setTasks] = useState([]);
    const [showAddTask, setShowAddTask] = useState(false);
    const [showScheduleGen, setShowScheduleGen] = useState(false);
    const [showChat, setShowChat] = useState(false);
    const [selectedDate, setSelectedDate] = useState(null);
    const [showSidebar, setShowSidebar] = useState(true);
    const [editingTask, setEditingTask] = useState(null);
    const [loading, setLoading] = useState(false);
    const [aiStatus, setAiStatus] = useState(false);

    // Form states
    const [newTask, setNewTask] = useState({
        title: '',
        date: '',
        category: 'general',
        description: '',
        priority: 'medium'
    });

    const [scheduleForm, setScheduleForm] = useState({
        crop: '',
        location: '',
        planting_date: ''
    });

    const [chatMessages, setChatMessages] = useState([]);
    const [chatInput, setChatInput] = useState('');

    const categories = [
        { value: 'preparation', label: 'Land Preparation', color: 'bg-amber-500' },
        { value: 'planting', label: 'Planting', color: 'bg-green-500' },
        { value: 'irrigation', label: 'Irrigation', color: 'bg-blue-500' },
        { value: 'fertilization', label: 'Fertilization', color: 'bg-purple-500' },
        { value: 'pest_control', label: 'Pest Control', color: 'bg-red-500' },
        { value: 'weeding', label: 'Weeding', color: 'bg-yellow-500' },
        { value: 'harvesting', label: 'Harvesting', color: 'bg-orange-500' },
        { value: 'general', label: 'General', color: 'bg-gray-500' }
    ];

    useEffect(() => {
        fetchTasks();
        checkAiStatus();
    }, []);

    const fetchTasks = async () => {
        try {
            const response = await fetch('http://localhost:5004/tasks');
            const data = await response.json();
            setTasks(data.tasks || []);
        } catch (error) {
            console.error('Error fetching tasks:', error);
        }
    };

    const checkAiStatus = async () => {
        try {
            const response = await fetch('http://localhost:5004/ai_status');
            const data = await response.json();
            setAiStatus(data.status === 'active');
        } catch (error) {
            console.error('Error checking AI status:', error);
            setAiStatus(false);
        }
    };

    const generateSchedule = async () => {
        if (!scheduleForm.crop || !scheduleForm.location || !scheduleForm.planting_date) {
            alert('Please fill all fields');
            return;
        }

        setLoading(true);
        try {
            const response = await fetch('http://localhost:5004/generate_schedule', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(scheduleForm)
            });

            const data = await response.json();

            if (response.ok) {
                await fetchTasks();
                setShowScheduleGen(false);
                setScheduleForm({ crop: '', location: '', planting_date: '' });
                alert(`Successfully generated ${data.tasks.length} tasks for ${data.crop}!`);
            } else {
                alert(`Failed to generate schedule: ${data.detail || 'Unknown error'}`);
            }
        } catch (error) {
            console.error('Error generating schedule:', error);
            alert('Error generating schedule');
        } finally {
            setLoading(false);
        }
    };

    const addTask = async () => {
        if (!newTask.title || !newTask.date) {
            alert('Please fill title and date');
            return;
        }

        setLoading(true);
        try {
            const response = await fetch('http://localhost:5004/add_task', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(newTask)
            });

            if (response.ok) {
                await fetchTasks();
                setShowAddTask(false);
                setNewTask({ title: '', date: '', category: 'general', description: '', priority: 'medium' });
            } else {
                alert('Failed to add task');
            }
        } catch (error) {
            console.error('Error adding task:', error);
            alert('Error adding task');
        } finally {
            setLoading(false);
        }
    };

    const updateTask = async (taskId, updates) => {
        try {
            const response = await fetch(`http://localhost:5004/update_task/${taskId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(updates)
            });

            if (response.ok) {
                await fetchTasks();
                setEditingTask(null);
            }
        } catch (error) {
            console.error('Error updating task:', error);
        }
    };

    const deleteTask = async (taskId) => {
        if (!confirm('Are you sure you want to delete this task?')) return;

        try {
            const response = await fetch(`http://localhost:5004/delete_task/${taskId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                await fetchTasks();
            }
        } catch (error) {
            console.error('Error deleting task:', error);
        }
    };

    const toggleTaskComplete = async (task) => {
        await updateTask(task.id, { completed: !task.completed });
    };

    const sendChatMessage = async () => {
        if (!chatInput.trim()) return;

        const userMessage = { role: 'user', content: chatInput };
        setChatMessages(prev => [...prev, userMessage]);
        setChatInput('');
        setLoading(true);

        try {
            const response = await fetch('http://localhost:5004/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: chatInput,
                    context: { current_date: new Date().toISOString().split('T')[0] },
                    history: chatMessages
                })
            });

            const data = await response.json();
            setChatMessages(prev => [...prev, { role: 'assistant', content: data.reply }]);
        } catch (error) {
            console.error('Error sending message:', error);
            setChatMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, I encountered an error.' }]);
        } finally {
            setLoading(false);
        }
    };

    const getDaysInMonth = (date) => {
        const year = date.getFullYear();
        const month = date.getMonth();
        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);
        const daysInMonth = lastDay.getDate();
        const startingDayOfWeek = firstDay.getDay();

        return { daysInMonth, startingDayOfWeek };
    };

    const getTasksForDate = (date) => {
        const dateStr = date.toISOString().split('T')[0];
        return tasks.filter(task => task.date === dateStr);
    };

    const getSortedTasks = () => {
        return [...tasks].sort((a, b) => new Date(a.date) - new Date(b.date));
    };

    const renderCalendar = () => {
        const { daysInMonth, startingDayOfWeek } = getDaysInMonth(currentDate);
        const days = [];

        for (let i = 0; i < startingDayOfWeek; i++) {
            days.push(<div key={`empty-${i}`} className="h-24 bg-gray-50 dark:bg-gray-800/50" />);
        }

        for (let day = 1; day <= daysInMonth; day++) {
            const date = new Date(currentDate.getFullYear(), currentDate.getMonth(), day);
            const dayTasks = getTasksForDate(date);
            const isToday = new Date().toDateString() === date.toDateString();

            days.push(
                <motion.div
                    key={day}
                    whileHover={{ scale: 1.02 }}
                    className={`h-24 border border-gray-200 dark:border-gray-700 p-2 cursor-pointer transition-colors ${isToday ? 'bg-primary/10 border-primary' : 'bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700'
                        }`}
                    onClick={() => setSelectedDate(date)}
                >
                    <div className={`text-sm font-semibold mb-1 ${isToday ? 'text-primary' : 'text-gray-700 dark:text-gray-300'}`}>
                        {day}
                    </div>
                    <div className="space-y-1 overflow-hidden">
                        {dayTasks.slice(0, 2).map(task => {
                            const category = categories.find(c => c.value === task.category);
                            return (
                                <div
                                    key={task.id}
                                    className={`text-xs px-1 py-0.5 rounded ${category?.color || 'bg-gray-500'} text-white truncate`}
                                >
                                    {task.title}
                                </div>
                            );
                        })}
                        {dayTasks.length > 2 && (
                            <div className="text-xs text-gray-500 dark:text-gray-400">+{dayTasks.length - 2} more</div>
                        )}
                    </div>
                </motion.div>
            );
        }

        return days;
    };

    const monthNames = ["January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"];

    return (
        <div className="pt-24 pb-12 px-4 min-h-screen flex gap-4">
            {/* Main Content */}
            <div className={`flex-1 transition-all duration-300 ${showSidebar ? 'mr-0' : 'mr-0'}`}>
                <div className="container mx-auto max-w-6xl mb-8">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="text-center mb-8"
                    >
                        <h1 className="text-5xl font-bold mb-4 text-gray-900 dark:text-white">
                            Smart Farming <span className="text-primary">Calendar</span>
                        </h1>
                        <p className="text-xl text-gray-600 dark:text-gray-300">
                            AI-powered farming schedules and task management
                        </p>
                    </motion.div>

                    {!aiStatus && (
                        <div className="max-w-xl mx-auto mb-8 bg-yellow-100 dark:bg-yellow-900/30 border border-yellow-200 dark:border-yellow-700 p-4 rounded-xl flex items-center gap-3">
                            <AlertTriangle className="w-6 h-6 text-yellow-600 dark:text-yellow-400" />
                            <div>
                                <h3 className="font-semibold text-yellow-800 dark:text-yellow-200">AI Features Unavailable</h3>
                                <p className="text-sm text-yellow-700 dark:text-yellow-300">
                                    AI schedule generation and chat are disabled. Please check backend API keys.
                                </p>
                            </div>
                        </div>
                    )}

                    <div className="flex flex-wrap justify-center gap-4 mb-8">
                        <button
                            onClick={() => setShowScheduleGen(true)}
                            disabled={!aiStatus}
                            className="px-6 py-3 bg-primary text-white rounded-xl font-semibold shadow-lg hover:shadow-xl hover:-translate-y-1 transition-all flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            <Sparkles className="w-5 h-5" />
                            Generate AI Schedule
                        </button>
                        <button
                            onClick={() => setShowAddTask(true)}
                            className="px-6 py-3 bg-green-600 text-white rounded-xl font-semibold shadow-lg hover:shadow-xl hover:-translate-y-1 transition-all flex items-center gap-2"
                        >
                            <Plus className="w-5 h-5" />
                            Add Task
                        </button>
                        <button
                            onClick={() => setShowChat(!showChat)}
                            disabled={!aiStatus}
                            className="px-6 py-3 bg-purple-600 text-white rounded-xl font-semibold shadow-lg hover:shadow-xl hover:-translate-y-1 transition-all flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            <MessageSquare className="w-5 h-5" />
                            AI Assistant
                        </button>
                        <button
                            onClick={() => setShowSidebar(!showSidebar)}
                            className="px-6 py-3 bg-gray-600 text-white rounded-xl font-semibold shadow-lg hover:shadow-xl hover:-translate-y-1 transition-all flex items-center gap-2"
                        >
                            <List className="w-5 h-5" />
                            {showSidebar ? 'Hide' : 'Show'} Task Queue
                        </button>
                    </div>

                    <div className="flex items-center justify-between mb-6 bg-white dark:bg-gray-800 p-4 rounded-xl shadow-lg">
                        <button
                            onClick={() => setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1))}
                            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                        >
                            <ChevronLeft className="w-6 h-6" />
                        </button>
                        <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                            {monthNames[currentDate.getMonth()]} {currentDate.getFullYear()}
                        </h2>
                        <button
                            onClick={() => setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1))}
                            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                        >
                            <ChevronRight className="w-6 h-6" />
                        </button>
                    </div>

                    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-xl overflow-hidden">
                        <div className="grid grid-cols-7 bg-gray-100 dark:bg-gray-700">
                            {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
                                <div key={day} className="p-3 text-center font-semibold text-gray-700 dark:text-gray-300">
                                    {day}
                                </div>
                            ))}
                        </div>
                        <div className="grid grid-cols-7">
                            {renderCalendar()}
                        </div>
                    </div>
                </div>
            </div>

            {/* Task Queue Sidebar */}
            <AnimatePresence>
                {showSidebar && (
                    <motion.div
                        initial={{ x: 400, opacity: 0 }}
                        animate={{ x: 0, opacity: 1 }}
                        exit={{ x: 400, opacity: 0 }}
                        className="w-96 bg-white dark:bg-gray-800 rounded-xl shadow-2xl p-6 overflow-y-auto max-h-[calc(100vh-120px)] sticky top-24"
                    >
                        <div className="flex items-center justify-between mb-6">
                            <h3 className="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
                                <List className="w-6 h-6" />
                                Task Queue
                            </h3>
                            <span className="text-sm bg-primary text-white px-3 py-1 rounded-full">
                                {tasks.length} tasks
                            </span>
                        </div>

                        <div className="space-y-3">
                            {getSortedTasks().length === 0 ? (
                                <p className="text-center text-gray-500 dark:text-gray-400 py-8">
                                    No tasks yet. Add some tasks to get started!
                                </p>
                            ) : (
                                getSortedTasks().map(task => (
                                    <TaskQueueItem
                                        key={task.id}
                                        task={task}
                                        categories={categories}
                                        onEdit={setEditingTask}
                                        onDelete={deleteTask}
                                        onToggle={toggleTaskComplete}
                                        isEditing={editingTask?.id === task.id}
                                        onUpdate={updateTask}
                                        onCancelEdit={() => setEditingTask(null)}
                                    />
                                ))
                            )}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>

            {/* Modals */}
            <AnimatePresence>
                {showScheduleGen && (
                    <Modal onClose={() => setShowScheduleGen(false)} title="Generate AI Farming Schedule">
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-semibold mb-2">Crop Type</label>
                                <input
                                    type="text"
                                    value={scheduleForm.crop}
                                    onChange={(e) => setScheduleForm({ ...scheduleForm, crop: e.target.value })}
                                    placeholder="e.g., Rice, Wheat, Cotton"
                                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-semibold mb-2">Location</label>
                                <input
                                    type="text"
                                    value={scheduleForm.location}
                                    onChange={(e) => setScheduleForm({ ...scheduleForm, location: e.target.value })}
                                    placeholder="e.g., Tamil Nadu, Punjab"
                                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-semibold mb-2">Planting Date</label>
                                <input
                                    type="date"
                                    value={scheduleForm.planting_date}
                                    min={new Date().toISOString().split('T')[0]}
                                    onChange={(e) => setScheduleForm({ ...scheduleForm, planting_date: e.target.value })}
                                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                                />
                            </div>
                            <button
                                onClick={generateSchedule}
                                disabled={loading}
                                className="w-full px-6 py-3 bg-primary text-white rounded-lg font-semibold hover:bg-primary/90 transition-colors disabled:opacity-50"
                            >
                                {loading ? 'Generating...' : 'Generate Schedule'}
                            </button>
                        </div>
                    </Modal>
                )}

                {showAddTask && (
                    <Modal onClose={() => setShowAddTask(false)} title="Add New Task">
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-semibold mb-2">Task Title</label>
                                <input
                                    type="text"
                                    value={newTask.title}
                                    onChange={(e) => setNewTask({ ...newTask, title: e.target.value })}
                                    placeholder="e.g., Apply fertilizer"
                                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-semibold mb-2">Date</label>
                                <input
                                    type="date"
                                    value={newTask.date}
                                    min={new Date().toISOString().split('T')[0]}
                                    onChange={(e) => setNewTask({ ...newTask, date: e.target.value })}
                                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-semibold mb-2">Category</label>
                                <select
                                    value={newTask.category}
                                    onChange={(e) => setNewTask({ ...newTask, category: e.target.value })}
                                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                                >
                                    {categories.map(cat => (
                                        <option key={cat.value} value={cat.value}>{cat.label}</option>
                                    ))}
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-semibold mb-2">Priority</label>
                                <select
                                    value={newTask.priority}
                                    onChange={(e) => setNewTask({ ...newTask, priority: e.target.value })}
                                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                                >
                                    <option value="low">Low</option>
                                    <option value="medium">Medium</option>
                                    <option value="high">High</option>
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-semibold mb-2">Description (Optional)</label>
                                <textarea
                                    value={newTask.description}
                                    onChange={(e) => setNewTask({ ...newTask, description: e.target.value })}
                                    placeholder="Additional details..."
                                    rows="3"
                                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                                />
                            </div>
                            <button
                                onClick={addTask}
                                disabled={loading}
                                className="w-full px-6 py-3 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 transition-colors disabled:opacity-50"
                            >
                                {loading ? 'Adding...' : 'Add Task'}
                            </button>
                        </div>
                    </Modal>
                )}

                {selectedDate && (
                    <Modal onClose={() => setSelectedDate(null)} title={`Tasks for ${selectedDate.toDateString()}`}>
                        <div className="space-y-3">
                            {getTasksForDate(selectedDate).length === 0 ? (
                                <p className="text-gray-500 dark:text-gray-400 text-center py-8">No tasks for this date</p>
                            ) : (
                                getTasksForDate(selectedDate).map(task => (
                                    <TaskCard key={task.id} task={task} onDelete={deleteTask} onToggle={toggleTaskComplete} categories={categories} />
                                ))
                            )}
                        </div>
                    </Modal>
                )}

                {showChat && (
                    <Modal onClose={() => setShowChat(false)} title="AI Farming Assistant">
                        <div className="flex flex-col h-96">
                            <div className="flex-1 overflow-y-auto mb-4 space-y-3">
                                {chatMessages.length === 0 && (
                                    <p className="text-gray-500 dark:text-gray-400 text-center py-8">
                                        Ask me about farming schedules, planting times, or crop management!
                                    </p>
                                )}
                                {chatMessages.map((msg, idx) => (
                                    <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                                        <div className={`max-w-[80%] px-4 py-2 rounded-lg ${msg.role === 'user'
                                            ? 'bg-primary text-white'
                                            : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white'
                                            }`}>
                                            {msg.content}
                                        </div>
                                    </div>
                                ))}
                                {loading && (
                                    <div className="flex justify-start">
                                        <div className="bg-gray-100 dark:bg-gray-700 px-4 py-2 rounded-lg">
                                            <div className="flex gap-1">
                                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
                                                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
                                            </div>
                                        </div>
                                    </div>
                                )}
                            </div>
                            <div className="flex gap-2">
                                <input
                                    type="text"
                                    value={chatInput}
                                    onChange={(e) => setChatInput(e.target.value)}
                                    onKeyPress={(e) => e.key === 'Enter' && sendChatMessage()}
                                    placeholder="Ask about farming schedules..."
                                    className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                                />
                                <button
                                    onClick={sendChatMessage}
                                    disabled={loading || !chatInput.trim()}
                                    className="px-6 py-2 bg-primary text-white rounded-lg font-semibold hover:bg-primary/90 transition-colors disabled:opacity-50"
                                >
                                    Send
                                </button>
                            </div>
                        </div>
                    </Modal>
                )}
            </AnimatePresence>
        </div>
    );
};

// Task Queue Item Component with Condensed/Expanded States
const TaskQueueItem = ({ task, categories, onEdit, onDelete, onToggle, isEditing, onUpdate, onCancelEdit }) => {
    const [isExpanded, setIsExpanded] = useState(false);
    const [editForm, setEditForm] = useState(task);
    const category = categories.find(c => c.value === task.category);
    const taskDate = new Date(task.date);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    const isOverdue = taskDate < today && !task.completed;

    if (isEditing) {
        return (
            <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg border-2 border-primary shadow-md">
                <div className="space-y-3">
                    <input
                        type="text"
                        value={editForm.title}
                        onChange={(e) => setEditForm({ ...editForm, title: e.target.value })}
                        className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:ring-2 focus:ring-primary/50"
                        placeholder="Task title"
                    />
                    <input
                        type="date"
                        value={editForm.date}
                        min={new Date().toISOString().split('T')[0]}
                        onChange={(e) => setEditForm({ ...editForm, date: e.target.value })}
                        className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                    />
                    <div className="grid grid-cols-2 gap-2">
                        <select
                            value={editForm.category}
                            onChange={(e) => setEditForm({ ...editForm, category: e.target.value })}
                            className="px-3 py-2 text-xs border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                        >
                            {categories.map(cat => (
                                <option key={cat.value} value={cat.value}>{cat.label}</option>
                            ))}
                        </select>
                        <select
                            value={editForm.priority}
                            onChange={(e) => setEditForm({ ...editForm, priority: e.target.value })}
                            className="px-3 py-2 text-xs border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                        >
                            <option value="low">Low Priority</option>
                            <option value="medium">Medium Priority</option>
                            <option value="high">High Priority</option>
                        </select>
                    </div>
                    <textarea
                        value={editForm.description || ''}
                        onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
                        className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                        placeholder="Detailed work description..."
                        rows="2"
                    />
                    <div className="flex gap-2">
                        <button
                            onClick={() => onUpdate(task.id, editForm)}
                            className="flex-1 px-4 py-2 bg-green-600 text-white rounded text-sm font-semibold hover:bg-green-700 transition-colors"
                        >
                            Save
                        </button>
                        <button
                            onClick={onCancelEdit}
                            className="flex-1 px-4 py-2 bg-gray-600 text-white rounded text-sm font-semibold hover:bg-gray-700 transition-colors"
                        >
                            Cancel
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <motion.div
            layout
            className={`rounded-lg border-l-4 ${category?.color || 'border-gray-500'} bg-gray-50 dark:bg-gray-700 shadow-sm overflow-hidden transition-all ${isOverdue ? 'border-red-500 bg-red-50 dark:bg-red-900/20' : ''
                }`}
        >
            {/* Condensed View (Always visible) */}
            <div
                className="p-3 cursor-pointer flex items-center justify-between"
                onClick={() => setIsExpanded(!isExpanded)}
            >
                <div className="flex-1 min-w-0 pr-2">
                    <div className="flex items-center gap-2">
                        <h4 className={`font-bold text-sm truncate ${task.completed ? 'line-through text-gray-500' : 'text-gray-900 dark:text-white'}`}>
                            {task.title}
                        </h4>
                        {isOverdue && <span className="text-[10px] bg-red-500 text-white px-1.5 py-0.5 rounded animate-pulse">OVERDUE</span>}
                    </div>
                    <p className="text-[11px] text-gray-600 dark:text-gray-400 font-medium">
                        📅 {taskDate.toLocaleDateString()} • <span className="capitalize">{task.category}</span>
                    </p>
                </div>
                <div className="flex items-center gap-1 shrink-0">
                    <button
                        onClick={(e) => { e.stopPropagation(); onToggle(task); }}
                        className={`p-1.5 rounded-full transition-colors ${task.completed
                                ? 'bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300'
                                : 'bg-gray-100 dark:bg-gray-600 text-gray-700 dark:text-gray-300'
                            }`}
                        title={task.completed ? "Mark Incomplete" : "Mark Complete"}
                    >
                        <Check className="w-3.5 h-3.5" />
                    </button>
                    <div className={`transition-transform duration-200 ${isExpanded ? 'rotate-180' : ''}`}>
                        <ChevronRight className="w-4 h-4 text-gray-400" />
                    </div>
                </div>
            </div>

            {/* Expanded View (Details) */}
            <AnimatePresence>
                {isExpanded && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        className="px-3 pb-3 border-t border-gray-100 dark:border-gray-600 pt-3"
                    >
                        {task.description && (
                            <div className="mb-3">
                                <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Work Details</p>
                                <p className="text-sm text-gray-700 dark:text-gray-200">{task.description}</p>
                            </div>
                        )}

                        <div className="grid grid-cols-2 gap-4 mb-4">
                            <div>
                                <p className="text-[10px] font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Priority</p>
                                <p className={`text-xs font-bold uppercase ${task.priority === 'high' ? 'text-red-600' :
                                        task.priority === 'medium' ? 'text-amber-600' : 'text-green-600'
                                    }`}>
                                    {task.priority}
                                </p>
                            </div>
                            <div>
                                <p className="text-[10px] font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Status</p>
                                <p className={`text-xs font-bold ${task.completed ? 'text-green-600' : 'text-gray-500'}`}>
                                    {task.completed ? 'COMPLETED' : 'IN PROGRESS'}
                                </p>
                            </div>
                        </div>

                        <div className="flex gap-2">
                            <button
                                onClick={() => onEdit(task)}
                                className="flex-1 flex items-center justify-center gap-1.5 p-2 bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 rounded-lg text-xs font-bold hover:bg-blue-200 dark:hover:bg-blue-800 transition-colors"
                            >
                                <Edit2 className="w-3.5 h-3.5" />
                                Edit Task
                            </button>
                            <button
                                onClick={() => onDelete(task.id)}
                                className="flex-1 flex items-center justify-center gap-1.5 p-2 bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300 rounded-lg text-xs font-bold hover:bg-red-200 dark:hover:bg-red-800 transition-colors"
                            >
                                <Trash2 className="w-3.5 h-3.5" />
                                Delete
                            </button>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </motion.div>
    );
};

// Modal Component
const Modal = ({ children, onClose, title }) => (
    <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
        onClick={onClose}
    >
        <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-md w-full p-6"
            onClick={(e) => e.stopPropagation()}
        >
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-2xl font-bold text-gray-900 dark:text-white">{title}</h3>
                <button
                    onClick={onClose}
                    className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                >
                    <X className="w-5 h-5" />
                </button>
            </div>
            {children}
        </motion.div>
    </motion.div>
);

// Task Card Component
const TaskCard = ({ task, onDelete, onToggle, categories }) => {
    const category = categories.find(c => c.value === task.category);

    return (
        <div className={`p-4 rounded-lg border-l-4 ${category?.color || 'border-gray-500'} bg-gray-50 dark:bg-gray-700`}>
            <div className="flex items-start justify-between">
                <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                        <h4 className={`font-semibold ${task.completed ? 'line-through text-gray-500' : 'text-gray-900 dark:text-white'}`}>
                            {task.title}
                        </h4>
                        <span className={`text-xs px-2 py-0.5 rounded ${category?.color || 'bg-gray-500'} text-white`}>
                            {category?.label || 'General'}
                        </span>
                    </div>
                    {task.description && (
                        <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">{task.description}</p>
                    )}
                    <div className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
                        <span>Priority: {task.priority}</span>
                    </div>
                </div>
                <div className="flex gap-2">
                    <button
                        onClick={() => onToggle(task)}
                        className={`p-2 rounded-lg transition-colors ${task.completed
                            ? 'bg-green-100 dark:bg-green-900 text-green-600 dark:text-green-400'
                            : 'bg-gray-100 dark:bg-gray-600 text-gray-600 dark:text-gray-400'
                            }`}
                    >
                        <Check className="w-4 h-4" />
                    </button>
                    <button
                        onClick={() => onDelete(task.id)}
                        className="p-2 bg-red-100 dark:bg-red-900 text-red-600 dark:text-red-400 rounded-lg hover:bg-red-200 dark:hover:bg-red-800 transition-colors"
                    >
                        <Trash2 className="w-4 h-4" />
                    </button>
                </div>
            </div>
        </div>
    );
};

export default SmartCalendar;
