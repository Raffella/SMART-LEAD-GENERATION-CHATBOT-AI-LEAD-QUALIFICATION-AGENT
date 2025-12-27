import React, { useState, useEffect, useRef } from 'react';
import { MessageCircle, X, Send, User, ChevronDown, Mic, Volume2 } from 'lucide-react';
import { v4 as uuidv4 } from 'uuid';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

export default function ChatWidget() {
    const [isOpen, setIsOpen] = useState(false);
    const [messages, setMessages] = useState([]);
    const [inputText, setInputText] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [sessionId, setSessionId] = useState('');
    const [userId, setUserId] = useState('');

    // Voice & Language State
    const [isListening, setIsListening] = useState(false);
    const [language, setLanguage] = useState('en');

    const messagesEndRef = useRef(null);
    const recognitionRef = useRef(null);

    useEffect(() => {
        // Initialize Session
        let storedSession = localStorage.getItem('ev_session_id');
        if (!storedSession) {
            storedSession = uuidv4();
            localStorage.setItem('ev_session_id', storedSession);
        }
        setSessionId(storedSession);

        let storedUser = localStorage.getItem('ev_user_id');
        if (!storedUser) {
            storedUser = uuidv4();
            localStorage.setItem('ev_user_id', storedUser);
        }
        setUserId(storedUser);

        // Initial greeting
        if (messages.length === 0) {
            setMessages([
                { role: 'assistant', content: 'Marhaba! I am your Everest View assistant. Are you looking to buy a property in Dubai today?' }
            ]);
        }

        // Initialize Speech Recognition
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognitionRef.current = new SpeechRecognition();
            recognitionRef.current.continuous = false;
            recognitionRef.current.interimResults = false;

            recognitionRef.current.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                setInputText(transcript);
                setIsListening(false);
                // Optional: Auto-send on voice end?
                // sendMessage(transcript); 
            };

            recognitionRef.current.onerror = (event) => {
                console.error('Speech recognition error', event.error);
                setIsListening(false);
            };

            recognitionRef.current.onend = () => {
                setIsListening(false);
            };
        }
    }, []);

    // Update language for recognition
    useEffect(() => {
        if (recognitionRef.current) {
            recognitionRef.current.lang = language === 'ar' ? 'ar-AE' :
                language === 'fr' ? 'fr-FR' :
                    language === 'es' ? 'es-ES' : 'en-US';
        }
    }, [language]);

    useEffect(() => {
        scrollToBottom();
    }, [messages, isOpen]);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    const toggleListening = () => {
        if (isListening) {
            recognitionRef.current?.stop();
        } else {
            setInputText('');
            recognitionRef.current?.start();
            setIsListening(true);
        }
    };

    const playAudio = (base64String) => {
        if (!base64String) return;
        try {
            const audio = new Audio(`data:audio/mp3;base64,${base64String}`);
            audio.play().catch(e => console.error("Audio play failed", e));
        } catch (e) {
            console.error("Audio init failed", e);
        }
    };

    const sendMessage = async (overrideText = null) => {
        const textToSend = overrideText || inputText;
        if (!textToSend.trim()) return;

        const userMsg = { role: 'user', content: textToSend };
        setMessages(prev => [...prev, userMsg]);
        setInputText('');
        setIsLoading(true);

        try {
            const response = await fetch(`${BACKEND_URL}/chat`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    userId: userId,
                    sessionId: sessionId,
                    userMessage: userMsg.content,
                    language: language
                })
            });

            if (!response.ok) throw new Error('Network response was not ok');

            const data = await response.json();
            const botMsg = {
                role: 'assistant',
                content: data.reply,
                audioBase64: data.audioBase64
            };
            setMessages(prev => [...prev, botMsg]);

            // Removed Auto-Play

        } catch (error) {
            console.error('Chat Error:', error);
            setMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, I am having trouble connecting. Please try again.' }]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter') sendMessage();
    };

    return (
        <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end">
            {/* Chat Window */}
            {isOpen && (
                <div className="mb-4 w-[350px] h-[550px] bg-[#001f3f] rounded-xl shadow-2xl flex flex-col overflow-hidden border border-[#003366] animate-in slide-in-from-bottom-5 duration-300 font-sans">

                    {/* Header */}
                    <div className="bg-[#0b1f3b] p-4 flex justify-between items-center text-white border-b border-[#003366]">
                        <div className="flex items-center gap-2">
                            <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center relative">
                                <User size={18} />
                                <div className="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 bg-green-400 rounded-full border border-[#0b1f3b]"></div>
                            </div>
                            <div>
                                <h3 className="font-semibold text-sm">Everest View AI</h3>
                                <div className="flex items-center gap-1">
                                    <span className="text-[10px] text-blue-300">Online</span>
                                </div>
                            </div>
                        </div>
                        <div className="flex items-center gap-2">
                            {/* Language Selector */}
                            <select
                                value={language}
                                onChange={(e) => setLanguage(e.target.value)}
                                className="bg-[#003366] text-white text-xs rounded px-2 py-1 border-none focus:ring-0 outline-none cursor-pointer"
                            >
                                <option value="en">🇺🇸 EN</option>
                                <option value="ar">🇦🇪 AR</option>
                                <option value="fr">🇫🇷 FR</option>
                                <option value="es">🇪🇸 ES</option>
                            </select>
                            <button onClick={() => setIsOpen(false)} className="text-gray-400 hover:text-white transition">
                                <X size={20} />
                            </button>
                        </div>
                    </div>

                    {/* Messages Area */}
                    <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-[#001f3f] scrollbar-thin scrollbar-thumb-[#003366]">
                        {messages.map((msg, idx) => (
                            <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                                <div
                                    dir={/[\u0600-\u06FF]/.test(msg.content) ? 'rtl' : 'ltr'}
                                    className={`max-w-[85%] p-3 rounded-2xl text-sm leading-relaxed shadow-sm flex items-start gap-2 ${msg.role === 'user'
                                        ? 'bg-blue-600 text-white rounded-tr-none'
                                        : 'bg-[#1e3a5f] text-gray-100 rounded-tl-none border border-blue-900/50'
                                        }`}
                                >
                                    <div className="flex-1">{msg.content}</div>
                                    {msg.role === 'assistant' && msg.audioBase64 && (
                                        <button
                                            onClick={() => playAudio(msg.audioBase64)}
                                            className="mt-0.5 p-1.5 rounded-full bg-blue-500/20 hover:bg-blue-500/40 text-blue-300 transition-colors flex-shrink-0"
                                            title="Play Audio"
                                        >
                                            <Volume2 size={14} />
                                        </button>
                                    )}
                                </div>
                            </div>
                        ))}
                        {isLoading && (
                            <div className="flex justify-start">
                                <div className="bg-[#1e3a5f] p-4 rounded-2xl rounded-tl-none border border-blue-900/50 flex gap-1.5 items-center h-10">
                                    <div className="w-2 h-2 bg-blue-400/80 rounded-full animate-bounce"></div>
                                    <div className="w-2 h-2 bg-blue-400/80 rounded-full animate-bounce delay-100"></div>
                                    <div className="w-2 h-2 bg-blue-400/80 rounded-full animate-bounce delay-200"></div>
                                </div>
                            </div>
                        )}
                        <div ref={messagesEndRef} />
                    </div>

                    {/* Input Area */}
                    <div className="p-3 bg-[#0b1f3b] border-t border-[#003366]">
                        {/* Status Bar */}
                        {isListening && (
                            <div className="text-center text-xs text-green-400 mb-2 animate-pulse flex justify-center items-center gap-1">
                                <Mic size={12} /> Listening...
                            </div>
                        )}

                        <div className="flex gap-2 items-end">
                            <div className="flex-1 relative">
                                <input
                                    type="text"
                                    value={inputText}
                                    onChange={(e) => setInputText(e.target.value)}
                                    onKeyPress={handleKeyPress}
                                    placeholder={language === 'ar' ? "أكتب رسالتك..." : "Type your message..."}
                                    dir={language === 'ar' ? 'rtl' : 'ltr'}
                                    className="w-full bg-[#001f3f] text-white text-sm rounded-xl px-4 py-3 pr-10 focus:outline-none focus:ring-2 focus:ring-blue-500/50 border border-[#003366] placeholder-gray-500 transition-all font-sans"
                                />
                                <button
                                    onClick={toggleListening}
                                    className={`absolute right-2 top-1/2 -translate-y-1/2 p-1.5 rounded-full transition-colors ${isListening ? 'text-red-500 hover:bg-red-500/10' : 'text-gray-400 hover:bg-gray-700/50 hover:text-white'}`}
                                >
                                    <Mic size={18} />
                                </button>
                            </div>

                            <button
                                onClick={() => sendMessage()}
                                disabled={isLoading || !inputText.trim()}
                                className="bg-blue-600 hover:bg-blue-500 text-white p-3 rounded-xl transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-blue-600/20 active:scale-95 flex-shrink-0"
                            >
                                <Send size={18} />
                            </button>
                        </div>
                        <div className="text-center mt-2 flex justify-center items-center gap-1 text-[10px] text-gray-500">
                            <Volume2 size={10} /> Voice Enabled
                        </div>
                    </div>
                </div>
            )}

            {/* Launcher Button */}
            <button
                onClick={() => setIsOpen(!isOpen)}
                className={`w-14 h-14 rounded-full shadow-2xl flex items-center justify-center transition-all hover:scale-105 active:scale-95 ${isOpen ? 'bg-red-500 rotate-90' : 'bg-blue-600 hover:bg-blue-500'}`}
            >
                {isOpen ? <X size={28} className="text-white" /> : <MessageCircle size={28} className="text-white" />}
            </button>
        </div>
    );
}
