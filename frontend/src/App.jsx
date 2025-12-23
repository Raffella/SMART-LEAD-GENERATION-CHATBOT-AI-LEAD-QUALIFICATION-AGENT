import ChatWidget from './components/ChatWidget'

function App() {
  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center">
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold text-gray-800">Everest View Property</h1>
        <p className="text-gray-600 max-w-md mx-auto">
          Welcome to our premium real estate platform. Browse the finest properties in Dubai.
        </p>
        <div className="p-8 bg-white rounded-xl shadow-sm border border-gray-200">
          <p className="text-sm text-gray-400">Content Placeholder</p>
        </div>
      </div>

      {/* Chat Widget integrated here */}
      <ChatWidget />
    </div>
  )
}

export default App
