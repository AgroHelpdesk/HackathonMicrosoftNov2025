import { Leaf, Send } from 'lucide-react';
import React, { FormEvent, useState } from 'react';
import { PLACEHOLDER_MESSAGES } from '../../constants';

interface ChatInputProps {
    onSendMessage: (message: string) => void;
    disabled: boolean;
}

/**
 * Chat input component with send button
 */
export const ChatInput: React.FC<ChatInputProps> = ({ onSendMessage, disabled }) => {
    const [message, setMessage] = useState('');

    const handleSubmit = (e: FormEvent) => {
        e.preventDefault();
        if (message.trim() && !disabled) {
            onSendMessage(message.trim());
            setMessage('');
        }
    };

    return (
        <form onSubmit={handleSubmit} className="flex items-center space-x-3">
            <div className="flex-1 relative">
                <input
                    type="text"
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    placeholder={disabled ? PLACEHOLDER_MESSAGES.SENDING : PLACEHOLDER_MESSAGES.DEFAULT}
                    className="w-full px-4 py-3 pl-12 border-2 border-green-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-green-500 transition-all duration-200 bg-green-50/50"
                    disabled={disabled}
                    aria-label="Chat message"
                />
                <Leaf className="absolute left-4 top-3.5 w-5 h-5 text-green-400" />
            </div>
            <button
                type="submit"
                disabled={!message.trim() || disabled}
                className="px-6 py-3 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-xl hover:from-green-700 hover:to-emerald-700 disabled:from-gray-300 disabled:to-gray-400 disabled:cursor-not-allowed flex items-center space-x-2 transition-all duration-200 shadow-lg hover:shadow-xl"
                aria-label="Send message"
            >
                <Send className="w-5 h-5" />
                <span className="font-medium">Send</span>
            </button>
        </form>
    );
};
