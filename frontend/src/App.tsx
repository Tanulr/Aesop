import { useState } from 'react';
import PromptInput from './components/PromptInput';
import LoadingScreen from './components/LoadingScreen';
import LinkResult from './components/LinkResult';
import { generateCampaignLink } from './api/marketingApi';

function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [resultUrl, setResultUrl] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async (prompt: string) => {
    setIsLoading(true);
    setError(null);
    setResultUrl(null);

    try {
      const url = await generateCampaignLink(prompt);
      setResultUrl(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Something went wrong');
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setResultUrl(null);
    setError(null);
  };

  return (
    <main className="min-h-screen w-full flex flex-col items-center justify-center p-4">
      {isLoading && <LoadingScreen />}

      {!resultUrl && !isLoading && (
        <div className="text-center mb-12">
          <h1 className="text-6xl font-black mb-4 tracking-tighter bg-gradient-to-r from-gray-400 to-blue-500 bg-clip-text text-transparent">
            StoryMarketer
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

      {!resultUrl && !isLoading && (
        <PromptInput onSubmit={handleGenerate} isLoading={isLoading} />
      )}

      {resultUrl && !isLoading && (
        <LinkResult url={resultUrl} onReset={handleReset} />
      )}
    </main>
  );
}

export default App;
