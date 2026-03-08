import { useState } from 'react';
import PromptInput from './components/PromptInput';
import LoadingScreen from './components/LoadingScreen';
import ResultsDisplay from './components/ResultsDisplay';

interface MarketingResponse {
  headline: string;
  body_copy: string;
  action_item: string;
}

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<MarketingResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async (prompt: string) => {
    setIsLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch('http://localhost:8000/generate-marketing-content', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt }),
      });

      if (!response.ok) {
        throw new Error('Failed to generate insights');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong');
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setResult(null);
    setError(null);
  };

  return (
    <main className="min-h-screen w-full flex flex-col items-center justify-center p-4">
      {isLoading && <LoadingScreen />}
      
      {!result && !isLoading && (
        <div className="text-center mb-12 animate-in fade-in zoom-in duration-1000">
          <h1 className="text-6xl font-black mb-4 tracking-tighter bg-gradient-to-r from-indigo-400 to-purple-400 bg-clip-text text-transparent">
            Tanulr/Aesop
          </h1>
          <p className="text-indigo-200/60 text-lg max-w-md mx-auto">
            Leverage AI to craft premium marketing strategies for your brand in seconds.
          </p>
        </div>
      )}

      {error && (
        <div className="mb-6 p-4 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm">
          {error}
        </div>
      )}

      {!result && !isLoading && (
        <PromptInput onSubmit={handleGenerate} isLoading={isLoading} />
      )}

      {result && !isLoading && (
        <ResultsDisplay data={result} onReset={handleReset} />
      )}
      
      <div className="fixed bottom-8 text-neutral-600 text-[10px] uppercase tracking-widest font-bold">
        Powered by React 19 + FastAPI
      </div>
    </main>
  );
}

export default App;
