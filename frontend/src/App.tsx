import { useEffect, useState, useMemo, useRef } from 'react'
import axios from 'axios'
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts'
import { Home, Receipt, Search, X, ShoppingCart, Coffee, Car, CreditCard, Pizza, XCircle, TrendingDown, TrendingUp, Bot, Send } from 'lucide-react'
import './App.css'

interface Stats {
  total_spent: number;
  categories: { name: string; value: number }[];
}

interface ChatMessage {
  role: 'user' | 'bot';
  text: string;
}

interface Transaction {
  id: number;
  amount: number;
  category: string;
  date: string;
  description?: string;
}

const COLORS = ['#D8B4E2', '#AEE5D8', '#FFD1BA', '#B5D8F7', '#F2C6C2', '#FDFD96'];

export default function App() {
  const [stats, setStats] = useState<Stats>({ total_spent: 0, categories: [] });
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'home' | 'operations' | 'chat'>('home');
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [chatInput, setChatInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (activeTab === 'chat') {
      scrollToBottom();
    }
  }, [chatMessages, activeTab]);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

  // Search & Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState<'all' | 'income' | 'expense'>('all');

  // @ts-ignore
  const twa = window.Telegram?.WebApp;
  const userId = twa?.initDataUnsafe?.user?.id || 1924457188;
  const userName = twa?.initDataUnsafe?.user?.first_name || 'Инвестор';

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const baseUrl = '/api';

        const [statsRes, txRes] = await Promise.all([
          axios.get(`${baseUrl}/stats`, { params: { user_id: userId } }).catch(() => ({ data: { total_spent: 0, categories: [] } })),
          axios.get(`${baseUrl}/transactions`, { params: { user_id: userId } }).catch(() => ({ data: [] }))
        ]);

        setStats(statsRes.data);
        setTransactions(txRes.data);
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [userId]);

  
  const handleSendMessage = async () => {
    if (!chatInput.trim() || isTyping) return;
    const text = chatInput.trim();
    setChatMessages(prev => [...prev, { role: 'user', text }]);
    setChatInput('');
    setIsTyping(true);
    haptic();
    
    try {
      const res = await axios.post('/api/chat', { user_id: userId, message: text });
      setChatMessages(prev => [...prev, { role: 'bot', text: res.data.answer || 'Ответ пуст' }]);
    } catch (error) {
      setChatMessages(prev => [...prev, { role: 'bot', text: 'Ошибка сети.' }]);
    } finally {
      setIsTyping(false);
    }
  };

  const haptic = () => {
    if (twa?.HapticFeedback) {
      twa.HapticFeedback.impactOccurred('light');
    }
  };

  const chartData = stats.categories.map(c => ({
    name: c.name,
    value: Math.abs(c.value)
  }));

  const categoryTransactions = transactions.filter(t => (t.category || '') === selectedCategory);

  const filteredOperations = useMemo(() => {
    return transactions.filter(t => {
      const cat = (t.category || '').toLowerCase();
      const desc = (t.description || '').toLowerCase();
      const search = searchQuery.toLowerCase();
      const matchSearch = cat.includes(search) || desc.includes(search);
      const type = t.amount < 0 ? 'expense' : 'income';
      const matchFilter = filterType === 'all' || filterType === type;
      return matchSearch && matchFilter;
    });
  }, [transactions, searchQuery, filterType]);

  const getCategoryIcon = (category: string | null | undefined) => {
    const cat = (category || '').toLowerCase();
    if (cat.includes('food') || cat.includes('restaurant') || cat.includes('еда') || cat.includes('мак') || cat.includes('додо') || cat.includes('пицца')) return <Pizza className="w-5 h-5 text-gray-700" />;
    if (cat.includes('coffee') || cat.includes('кофе')) return <Coffee className="w-5 h-5 text-gray-700" />;
    if (cat.includes('transport') || cat.includes('транспорт') || cat.includes('car') || cat.includes('такси') || cat.includes('авто')) return <Car className="w-5 h-5 text-gray-700" />;
    if (cat.includes('shop') || cat.includes('магазин') || cat.includes('supermarket') || cat.includes('маркет') || cat.includes('пятерочка') || cat.includes('магнит')) return <ShoppingCart className="w-5 h-5 text-gray-700" />;
    return <CreditCard className="w-5 h-5 text-gray-700" />;
  };

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-tg-bg text-tg-text">
        <div className="w-10 h-10 border-4 border-blue-400 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-tg-bg text-tg-text font-sans relative pb-24 overflow-x-hidden">
      
      {/* HOME TAB */}
      {activeTab === 'home' && (
        <div className="p-5 flex flex-col gap-6 max-w-md mx-auto animate-fade-in">
          <header className="flex justify-between items-center py-2">
            <h1 className="text-2xl font-bold tracking-tight">Привет, {userName} 👋</h1>
          </header>

          <section className="flex flex-col items-center justify-center p-8 bg-gradient-to-br from-indigo-500/10 to-purple-500/10 backdrop-blur-2xl rounded-[2rem] shadow-sm border border-white/20">
            <p className="text-sm text-tg-hint mb-2 font-medium uppercase tracking-wider">Всего потрачено</p>
            <h2 className="text-4xl sm:text-5xl font-extrabold tracking-tight">
              {Math.abs(stats.total_spent).toLocaleString('ru-RU')} ₽
            </h2>
          </section>

          {chartData.length > 0 && (
            <section className="h-80 bg-tg-secondaryBg/60 backdrop-blur-xl rounded-[2rem] shadow-sm border border-white/10 p-6 flex flex-col items-center justify-center">
              <h3 className="text-lg font-semibold w-full mb-4">Структура расходов</h3>
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={chartData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    innerRadius={70}
                    outerRadius={90}
                    paddingAngle={4}
                    stroke="none"
                    onClick={(data) => {
                      haptic();
                      // payload contains the actual data object
                      const name = data?.name || data?.payload?.name;
                      if (name) setSelectedCategory(name);
                    }}
                    className="cursor-pointer outline-none hover:opacity-80 transition-opacity duration-300"
                  >
                    {chartData.map((_, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip 
                    formatter={(value: any, name: any) => [`${Number(value).toLocaleString('ru-RU')} ₽`, name]}
                    contentStyle={{ backgroundColor: 'rgba(255, 255, 255, 0.95)', backdropFilter: 'blur(16px)', border: 'none', borderRadius: '16px', color: '#111', boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)' }}
                    itemStyle={{ color: '#111', fontWeight: '600' }}
                  />
                </PieChart>
              </ResponsiveContainer>
              <p className="text-xs text-tg-hint mt-4 text-center">Нажми на категорию для деталей</p>
            </section>
          )}
        </div>
      )}

      {/* OPERATIONS TAB */}
      {activeTab === 'operations' && (
        <div className="p-5 flex flex-col gap-6 max-w-md mx-auto h-full min-h-screen animate-fade-in">
          <header className="py-2">
            <h1 className="text-2xl font-bold tracking-tight">История операций</h1>
          </header>

          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
              <Search className="h-5 w-5 text-tg-hint" />
            </div>
            <input
              type="text"
              className="block w-full pl-12 pr-10 py-4 border-none rounded-[1.5rem] bg-tg-secondaryBg/80 backdrop-blur-md shadow-sm focus:ring-2 focus:ring-blue-400 focus:outline-none placeholder-tg-hint text-tg-text transition-all"
              placeholder="Поиск по истории..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            {searchQuery && (
              <button 
                className="absolute inset-y-0 right-0 pr-4 flex items-center"
                onClick={() => {
                  haptic();
                  setSearchQuery('');
                }}
              >
                <XCircle className="h-5 w-5 text-tg-hint hover:text-tg-text transition-colors" />
              </button>
            )}
          </div>

          <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide -mx-5 px-5">
            <button
              onClick={() => { haptic(); setFilterType('all'); }}
              className={`px-5 py-2.5 rounded-full whitespace-nowrap font-semibold transition-all duration-300 shadow-sm text-sm ${filterType === 'all' ? 'bg-blue-500 text-white scale-105' : 'bg-tg-secondaryBg/80 text-tg-text hover:bg-tg-secondaryBg'}`}
            >
              Все
            </button>
            <button
              onClick={() => { haptic(); setFilterType('expense'); }}
              className={`px-5 py-2.5 rounded-full whitespace-nowrap font-semibold transition-all duration-300 shadow-sm flex items-center gap-2 text-sm ${filterType === 'expense' ? 'bg-red-400 text-white scale-105' : 'bg-tg-secondaryBg/80 text-tg-text hover:bg-tg-secondaryBg'}`}
            >
              <TrendingDown className="w-4 h-4"/> Расходы
            </button>
            <button
              onClick={() => { haptic(); setFilterType('income'); }}
              className={`px-5 py-2.5 rounded-full whitespace-nowrap font-semibold transition-all duration-300 shadow-sm flex items-center gap-2 text-sm ${filterType === 'income' ? 'bg-green-500 text-white scale-105' : 'bg-tg-secondaryBg/80 text-tg-text hover:bg-tg-secondaryBg'}`}
            >
              <TrendingUp className="w-4 h-4"/> Доходы
            </button>
          </div>

          <div className="flex flex-col gap-3 pb-8">
            {filteredOperations.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-12 opacity-50">
                <Receipt className="w-12 h-12 mb-4" />
                <p className="text-center font-medium">Ничего не найдено</p>
              </div>
            ) : (
              filteredOperations.map((tx) => {
                const type = tx.amount < 0 ? 'expense' : 'income';
                return (
                  <div 
                    key={tx.id}
                    className="flex items-center gap-4 p-4 bg-tg-secondaryBg/60 backdrop-blur-md rounded-[1.5rem] shadow-sm border border-white/5 active:scale-[0.98] transition-transform"
                  >
                    <div className="w-12 h-12 min-w-[3rem] rounded-full bg-white/70 flex items-center justify-center shadow-sm">
                      {getCategoryIcon(tx.category)}
                    </div>
                    <div className="flex flex-col flex-1 overflow-hidden">
                      <span className="font-bold text-base truncate">{tx.category || 'Без категории'}</span>
                      <span className="text-sm text-tg-hint truncate">{tx.description || tx.date}</span>
                    </div>
                    <div className={`font-bold text-lg whitespace-nowrap ${type === 'income' ? 'text-green-500' : 'text-tg-text'}`}>
                      {type === 'income' ? '+' : '-'}{Math.abs(tx.amount).toLocaleString('ru-RU')} ₽
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </div>
      )}

      
      {/* CHAT TAB */}
      {activeTab === 'chat' && (
        <div className="flex flex-col h-[calc(100vh-80px)] animate-fade-in relative max-w-md mx-auto">
          <header className="py-4 px-5 bg-tg-bg/80 backdrop-blur-xl border-b border-white/5 sticky top-0 z-10 flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-blue-500/20 flex items-center justify-center text-blue-500">
              <Bot className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-lg font-bold">AI Ассистент</h1>
              <p className="text-xs text-tg-hint">Спроси меня о финансах</p>
            </div>
          </header>
          
          <div className="flex-1 overflow-y-auto p-5 space-y-4 pb-24">
            {chatMessages.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-tg-hint opacity-70">
                <Bot className="w-16 h-16 mb-4 opacity-50" />
                <p>Напишите сообщение, чтобы начать диалог.</p>
              </div>
            ) : (
              chatMessages.map((msg, idx) => (
                <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[80%] p-3 rounded-2xl ${
                    msg.role === 'user' 
                      ? 'bg-blue-500 text-white rounded-br-sm' 
                      : 'bg-tg-secondaryBg/80 backdrop-blur-md border border-white/5 text-tg-text rounded-bl-sm'
                  }`}>
                    <p className="whitespace-pre-wrap text-sm leading-relaxed">{msg.text}</p>
                  </div>
                </div>
              ))
            )}
            
            {isTyping && (
              <div className="flex justify-start animate-fade-in">
                <div className="bg-tg-secondaryBg/80 backdrop-blur-md border border-white/5 p-4 rounded-2xl rounded-bl-sm flex gap-1.5 items-center">
                  <div className="w-2 h-2 rounded-full bg-tg-hint animate-bounce" style={{ animationDelay: '0ms' }} />
                  <div className="w-2 h-2 rounded-full bg-tg-hint animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="w-2 h-2 rounded-full bg-tg-hint animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            )}
            <div ref={messagesEndRef} className="h-4" />
          </div>

          <div className="absolute bottom-0 left-0 w-full p-4 bg-tg-bg/90 backdrop-blur-2xl border-t border-white/5">
            <div className="relative flex items-center">
              <input
                type="text"
                value={chatInput}
                onChange={e => setChatInput(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleSendMessage()}
                placeholder="Спроси что-нибудь..."
                className="w-full bg-tg-secondaryBg/80 backdrop-blur-md border border-white/10 rounded-full py-3.5 pl-5 pr-14 focus:outline-none focus:ring-2 focus:ring-blue-500/50 text-sm text-tg-text"
              />
              <button
                onClick={handleSendMessage}
                disabled={!chatInput.trim() || isTyping}
                className="absolute right-1.5 p-2.5 bg-blue-500 text-white rounded-full disabled:opacity-50 disabled:scale-100 hover:scale-105 active:scale-95 transition-all"
              >
                <Send className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}

      {/* BOTTOM NAVIGATION BAR */}
      <div className="fixed bottom-0 left-1/2 -translate-x-1/2 w-full max-w-md bg-tg-bg/80 backdrop-blur-2xl border-t border-gray-500/10 px-6 py-2 flex justify-between items-center z-40 pb-safe">
        <button 
          onClick={() => {
            haptic();
            setActiveTab('home');
          }}
          className={`flex flex-col items-center gap-1 p-2 flex-1 rounded-2xl transition-all duration-300 ${activeTab === 'home' ? 'text-blue-500 scale-110' : 'text-tg-hint hover:text-tg-text'}`}
        >
          <Home className="w-6 h-6" />
          <span className="text-[10px] font-bold">Главная</span>
        </button>
        <button 
          onClick={() => {
            haptic();
            setActiveTab('chat');
          }}
          className={`flex flex-col items-center gap-1 p-2 flex-1 rounded-2xl transition-all duration-300 ${activeTab === 'chat' ? 'text-blue-500 scale-110' : 'text-tg-hint hover:text-tg-text'}`}
        >
          <Bot className="w-6 h-6" />
          <span className="text-[10px] font-bold">ИИ Чат</span>
        </button>
        <button 
          onClick={() => {
            haptic();
            setActiveTab('operations');
          }}
          className={`flex flex-col items-center gap-1 p-2 flex-1 rounded-2xl transition-all duration-300 ${activeTab === 'operations' ? 'text-blue-500 scale-110' : 'text-tg-hint hover:text-tg-text'}`}
        >
          <Receipt className="w-6 h-6" />
          <span className="text-[10px] font-bold">Операции</span>
        </button>
      </div>

      {/* CATEGORY MODAL (BOTTOM SHEET) */}
      {selectedCategory && (
        <div className="fixed inset-0 z-50 flex justify-center items-end pointer-events-none">
          <div 
            className="absolute inset-0 bg-black/50 backdrop-blur-sm transition-opacity animate-fade-in pointer-events-auto" 
            onClick={() => { haptic(); setSelectedCategory(null); }}
          />
          <div className="relative w-full max-w-md bg-tg-bg rounded-t-[2rem] p-6 flex flex-col gap-5 shadow-2xl max-h-[85vh] overflow-y-auto animate-slide-up border-t border-white/10 pointer-events-auto">
            <div className="w-12 h-1.5 bg-gray-400/50 rounded-full mx-auto opacity-80 shrink-0" />
            
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-white/70 flex items-center justify-center shadow-sm">
                  {getCategoryIcon(selectedCategory)}
                </div>
                <h3 className="text-2xl font-bold">{selectedCategory}</h3>
              </div>
              <button 
                onClick={() => { haptic(); setSelectedCategory(null); }}
                className="p-2 bg-tg-secondaryBg rounded-full active:scale-95 transition-transform"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <div className="flex flex-col gap-3 pb-8 mt-2">
              {categoryTransactions.length === 0 ? (
                <p className="text-tg-hint text-center py-4">Нет операций.</p>
              ) : (
                categoryTransactions.map((tx) => {
                  const type = tx.amount < 0 ? 'expense' : 'income';
                  return (
                    <div key={tx.id} className="flex justify-between items-center p-4 bg-tg-secondaryBg/70 backdrop-blur-md rounded-2xl shadow-sm border border-white/5">
                      <div className="flex flex-col overflow-hidden pr-4">
                        <span className="font-semibold text-base truncate">{tx.description || tx.category}</span>
                        <span className="text-sm text-tg-hint">{tx.date}</span>
                      </div>
                      <div className={`font-bold text-lg whitespace-nowrap ${type === 'income' ? 'text-green-500' : 'text-tg-text'}`}>
                        {type === 'income' ? '+' : '-'}{Math.abs(tx.amount).toLocaleString('ru-RU')} ₽
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>
        </div>
      )}

    </div>
  )
}
