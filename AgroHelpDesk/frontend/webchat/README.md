# 💬 AgroHelpDesk WebChat - React Frontend

Modern, responsive chat interface built with **React**, **TypeScript**, and **Tailwind CSS** for the AgroHelpDesk intelligent agricultural support system.

## 📋 Overview

The WebChat frontend provides a user-friendly interface for farmers, technicians, and agronomists to interact with the AI-powered multi-agent system. It features real-time chat, typing indicators, message history, and full transparency into agent decisions.

## ✨ Features

**Currently Implemented:**
- ✅ **Real-time Chat Interface** - Smooth, responsive chat experience
- ✅ **Multi-Agent Visibility** - See which agent is responding
- ✅ **Typing Indicators** - Visual feedback during processing
- ✅ **Message History** - Complete conversation tracking
- ✅ **Session Management** - Automatic session creation and closure
- ✅ **Error Handling** - Graceful error recovery with retry
- ✅ **Responsive Design** - Works on desktop, tablet, and mobile
- ✅ **Accessibility** - ARIA labels and keyboard navigation
- ✅ **Auto-scroll** - Automatic scroll to latest messages

**Future Enhancements:**
- 🔄 **WebSocket Support** - Real-time message streaming
- 🔄 **Voice Input** - Speech-to-text for farmers
- 🔄 **File Attachments** - Image upload for pest identification
- 🔄 **Offline Mode** - Service worker for offline access
- 🔄 **Push Notifications** - Browser notifications for responses

## 🏗️ Architecture

```
webchat/
├── public/
│   ├── index.html          # HTML template
│   └── manifest.json       # PWA manifest
├── src/
│   ├── App.tsx             # Main application component
│   ├── index.tsx           # Application entry point
│   ├── index.css           # Global styles
│   ├── components/
│   │   ├── chat/
│   │   │   ├── ChatInterface.tsx      # Main chat container
│   │   │   ├── ChatHeader.tsx         # Session status header
│   │   │   ├── ChatMessages.tsx       # Messages container
│   │   │   ├── ChatMessage.tsx        # Individual message
│   │   │   ├── ChatInput.tsx          # Message input field
│   │   │   ├── ChatClosedView.tsx     # Session closed view
│   │   │   └── TypingIndicator.tsx    # Typing animation
│   │   ├── common/
│   │   │   ├── ErrorBoundary.tsx      # Error boundary
│   │   │   ├── ErrorDisplay.tsx       # Error messages
│   │   │   └── LoadingState.tsx       # Loading spinner
│   │   └── layout/
│   │       ├── Header.tsx             # App header
│   │       └── Footer.tsx             # App footer
│   ├── hooks/
│   │   ├── useChat.ts                 # Chat state management
│   │   ├── useAutoScroll.ts           # Auto-scroll behavior
│   │   └── index.ts                   # Hooks exports
│   ├── services/
│   │   ├── chatService.ts             # API service
│   │   ├── api.ts                     # Axios configuration
│   │   └── index.ts                   # Service exports
│   ├── constants/
│   │   ├── config.ts                  # App configuration
│   │   ├── messages.ts                # UI messages
│   │   ├── api.ts                     # API endpoints
│   │   └── index.ts                   # Constants exports
│   └── types/
│       ├── chat.types.ts              # Chat types
│       ├── api.types.ts               # API types
│       └── index.ts                   # Type exports
├── package.json
├── tsconfig.json           # TypeScript configuration
├── tailwind.config.js      # Tailwind CSS configuration
└── postcss.config.js       # PostCSS configuration
```

## 🚀 Getting Started

### Prerequisites

**Required:**
- Node.js 18+ and npm
- Backend running on `http://localhost:8000`

**Optional (for future features):**
- Service Worker support (PWA)
- Media devices access (camera/microphone)

### Installation

```powershell
# Navigate to project
cd frontend/webchat

# Install dependencies
npm install
```

### Configuration

Create `.env` file:

```bash
# Backend API URL
REACT_APP_API_BASE_URL=http://localhost:8000

# Optional: Custom configuration
REACT_APP_ENABLE_LOGGING=true
```

### Running Development Server

```powershell
# Start development server
npm start
```

The app will open at: `http://localhost:3000`

### Building for Production

```powershell
# Create production build
npm run build

# The build folder will contain optimized files
```

### Running Tests

```powershell
# Run all tests
npm test

# Run tests with coverage
npm test -- --coverage

# Run tests in watch mode
npm test -- --watch
```

### Type Checking

```powershell
# Check TypeScript types without emitting files
npm run type-check
```

## 🎨 Styling

### Tailwind CSS

The project uses **Tailwind CSS** for styling with a custom agricultural theme:

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        green: {
          50: '#f0fdf4',
          100: '#dcfce7',
          // ... agricultural green palette
        }
      }
    }
  }
}
```

### Color Scheme

- **Primary**: Green shades (agricultural theme)
- **Accent**: Emerald and teal
- **User messages**: Green gradient
- **Bot messages**: White with green border
- **Error messages**: Red tones
- **Success**: Green tones

## 🔧 Key Components

### ChatInterface

Main chat container managing session and message flow:

```tsx
const ChatInterface: React.FC = () => {
  const { sessionId, messages, sendMessage } = useChat();
  
  return (
    <div>
      <ChatHeader sessionId={sessionId} />
      <ChatMessages messages={messages} />
      <ChatInput onSendMessage={sendMessage} />
    </div>
  );
};
```

### useChat Hook

Central hook for chat state management:

```typescript
const {
  sessionId,        // Current session ID
  messages,         // Message array
  chatStatus,       // 'active' | 'closed'
  isLoading,        // Session loading
  isSending,        // Message sending
  error,            // Error state
  startSession,     // Start new session
  sendMessage,      // Send message
  resetChat,        // Reset chat state
} = useChat();
```

### ChatMessage Component

Displays individual messages with agent badges:

```tsx
<ChatMessage
  message={{
    id: "msg-1",
    content: "How can I help you?",
    sender: "Technical assistance for Agriculture",
    timestamp: new Date(),
    isBot: true,
    agentType: "FieldSense"
  }}
/>
```

## 📡 API Integration

### Chat Service

```typescript
// Start session
const session = await chatService.startSession();

// Send message
const response = await chatService.sendMessage(
  sessionId,
  "My irrigation is failing",
  userId
);

// Get history
const history = await chatService.getHistory(sessionId);

// Close session
await chatService.closeSession(sessionId);
```

### API Endpoints Used

- `POST /api/chat/start-session` - Create new session
- `POST /api/chat/message` - Send message to agents
- `GET /api/chat/history/{session_id}` - Get conversation
- `POST /api/chat/close-session/{session_id}` - End session

## 🎯 Features in Detail

### Session Management

- Automatic session creation on mount
- Session ID tracking
- Session status display (Active/Closed)
- Graceful session closure with reset option

### Message Flow

1. User types message
2. Message validated and sent to backend
3. User message displayed immediately
4. Typing indicator shown during processing
5. Agent response received and displayed
6. Flow state checked for completion

### Error Handling

- Network errors with retry option
- Session creation failures
- Message send failures
- Validation errors
- Graceful degradation

### Accessibility

- ARIA labels on interactive elements
- Keyboard navigation support
- Screen reader friendly
- Focus management
- Semantic HTML

## 📱 Responsive Design

Breakpoints:
- **Mobile**: < 640px
- **Tablet**: 640px - 1024px
- **Desktop**: > 1024px

All components adapt to different screen sizes with Tailwind responsive classes.

## 🧪 Testing Strategy

### Unit Tests

```typescript
// Component tests
describe('ChatMessage', () => {
  it('renders user message correctly', () => {
    // Test implementation
  });
});

// Hook tests
describe('useChat', () => {
  it('starts session on mount', async () => {
    // Test implementation
  });
});
```

### Integration Tests

```typescript
describe('Chat Flow', () => {
  it('completes full conversation flow', async () => {
    // Test implementation
  });
});
```

## 🚢 Deployment

### Azure Static Web Apps

```powershell
# Build the app
npm run build

# Deploy to Azure Static Web Apps
az staticwebapp create \
  --name agrohelpdesk-webchat \
  --source ./build \
  --location "brazilsouth"
```

### Environment Variables in Production

Configure in Azure Portal:
- `REACT_APP_API_BASE_URL` - Backend URL (e.g., `https://api.agrohelpdesk.com`)

### Build Optimization

The production build includes:
- ✅ Code minification
- ✅ Tree shaking
- ✅ CSS purging
- ✅ Asset optimization
- ✅ Source maps (optional)

## 📊 Performance

### Optimization Techniques

- Lazy loading of ChatInterface
- React.memo for message components
- Debounced auto-scroll
- Efficient re-renders with proper dependencies
- Code splitting

### Bundle Size

- Main bundle: ~150KB (gzipped)
- Vendor bundle: ~180KB (gzipped)
- CSS: ~15KB (gzipped)

## 🔒 Security

### Best Practices

- Environment variables for sensitive data
- HTTPS in production
- CORS properly configured
- Input validation
- XSS protection via React
- No sensitive data in localStorage

## 🐛 Troubleshooting

### Common Issues

1. **Backend connection failed**
   - Check `REACT_APP_API_BASE_URL`
   - Verify backend is running
   - Check CORS configuration

2. **Build errors**
   - Clear node_modules: `rm -rf node_modules && npm install`
   - Clear cache: `npm cache clean --force`
   - Check Node version: `node --version`

3. **Type errors**
   - Run `npm run type-check`
   - Update TypeScript: `npm install typescript@latest`

## 📚 Technologies Used

- **React 18** - UI library
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first CSS
- **Axios** - HTTP client
- **Lucide React** - Icon library
- **React Scripts** - Build tooling

## 📖 Further Reading

- [React Documentation](https://react.dev)
- [TypeScript Documentation](https://www.typescriptlang.org)
- [Tailwind CSS Documentation](https://tailwindcss.com)
- [Axios Documentation](https://axios-http.com)

## 🔮 Future Enhancements

### Real-time Communication
- **WebSocket Integration**: Live message streaming without polling
- **Server-Sent Events**: Unidirectional updates from server
- **Optimistic Updates**: Instant UI feedback before server confirmation

### Media Support
- **Image Upload**: Attach photos for pest/disease identification
- **Voice Input**: Speech-to-text for hands-free operation
- **Voice Output**: Text-to-speech for accessibility
- **Video Support**: Video calls with specialists

### Progressive Web App
- **Service Worker**: Offline support and caching
- **Push Notifications**: Browser notifications for new messages
- **Install Prompt**: Add to home screen
- **Background Sync**: Queue messages when offline

### Enhanced UX
- **Message Reactions**: Like, helpful, not helpful
- **Message Search**: Find previous conversations
- **Chat Export**: Download conversation history
- **Dark Mode**: Theme toggle for better accessibility
- **Multi-language**: Language selector

### Advanced Features
- **Chat Templates**: Quick responses for common questions
- **Suggested Replies**: AI-powered reply suggestions
- **Rich Media**: Embed maps, charts, documents
- **Collaboration**: Share chat with team members

---

**Built with 💚 for Agriculture**
