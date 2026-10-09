import re

with open('frontend/src/App.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update imports
content = content.replace(
    "import { Home, Receipt, Search, X, ShoppingCart, Coffee, Car, CreditCard, Pizza, XCircle, TrendingDown, TrendingUp } from 'lucide-react'",
    "import { Home, Receipt, Search, X, ShoppingCart, Coffee, Car, CreditCard, Pizza, XCircle, TrendingDown, TrendingUp, Bot, Send } from 'lucide-react'"
)

# 2. Add ChatMessage interface
if 'interface ChatMessage' not in content:
    content = content.replace(
        "interface Transaction {",
        "interface ChatMessage {\n  role: 'user' | 'bot';\n  text: string;\n}\n\ninterface Transaction {"
    )

# 3. Update activeTab type and add states
content = content.replace(
    "const [activeTab, setActiveTab] = useState<'home' | 'operations'>('home');",
    "const [activeTab, setActiveTab] = useState<'home' | 'operations' | 'chat'>('home');\n  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);\n  const [chatInput, setChatInput] = useState('');\n  const [isTyping, setIsTyping] = useState(false);\n  const messagesEndRef = useRef<HTMLDivElement>(null);\n\n  const scrollToBottom = () => {\n    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });\n  };\n\n  useEffect(() => {\n    if (activeTab === 'chat') {\n      scrollToBottom();\n    }\n  }, [chatMessages, activeTab]);"
)
# Add React import if needed for useRef
if 'useRef' not in content:
    content = content.replace(
        "import { useEffect, useState, useMemo } from 'react'",
        "import { useEffect, useState, useMemo, useRef } from 'react'"
    )

# 4. Handle send message function
handle_send = """
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
"""
content = content.replace(
    "const haptic = () => {",
    handle_send + "\n  const haptic = () => {"
)

# 5. Fix PieChart outerRadius
content = content.replace("outerRadius={100}", "outerRadius={90}")

# 6. Add Chat Tab UI
chat_ui = """
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
"""

content = content.replace(
    "{/* BOTTOM NAVIGATION BAR */}",
    chat_ui + "\n      {/* BOTTOM NAVIGATION BAR */}"
)

# 7. Add 3rd tab in bottom navigation
# Currently: 2 buttons in bottom bar (Home, Operations)
old_bar = """<div className="fixed bottom-0 left-1/2 -translate-x-1/2 w-full max-w-md bg-tg-bg/80 backdrop-blur-2xl border-t border-gray-500/10 px-6 py-2 flex justify-around items-center z-40 pb-safe">
        <button 
          onClick={() => {
            haptic();
            setActiveTab('home');
          }}
          className={`flex flex-col items-center gap-1 p-2 w-20 rounded-2xl transition-all duration-300 ${activeTab === 'home' ? 'text-blue-500 scale-110' : 'text-tg-hint hover:text-tg-text'}`}
        >
          <Home className="w-6 h-6" />
          <span className="text-[10px] font-bold">Главная</span>
        </button>
        <button 
          onClick={() => {
            haptic();
            setActiveTab('operations');
          }}
          className={`flex flex-col items-center gap-1 p-2 w-20 rounded-2xl transition-all duration-300 ${activeTab === 'operations' ? 'text-blue-500 scale-110' : 'text-tg-hint hover:text-tg-text'}`}
        >
          <Receipt className="w-6 h-6" />
          <span className="text-[10px] font-bold">Операции</span>
        </button>
      </div>"""

new_bar = """<div className="fixed bottom-0 left-1/2 -translate-x-1/2 w-full max-w-md bg-tg-bg/80 backdrop-blur-2xl border-t border-gray-500/10 px-6 py-2 flex justify-between items-center z-40 pb-safe">
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
      </div>"""

content = content.replace(old_bar, new_bar)

with open('frontend/src/App.tsx', 'w', encoding='utf-8') as f:
    f.write(content)

print("Modification complete.")
