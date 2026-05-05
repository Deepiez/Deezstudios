export default function Home() {
  return (
    <main className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          AI Content Studio
        </h1>
        <p className="text-lg text-gray-600 mb-8">
          Internal Content Automation Tool
        </p>
        <a
          href="/dashboard"
          className="inline-flex items-center px-6 py-3 bg-primary-600 text-white font-medium rounded-lg hover:bg-primary-700 transition-colors"
        >
          Go to Dashboard
        </a>
      </div>
    </main>
  );
}
