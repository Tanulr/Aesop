import React, { useState } from 'react';

interface PromptInputProps {
  onSubmit: (prompt: string) => void;
  isLoading: boolean;
}

const PromptInput: React.FC<PromptInputProps> = ({ onSubmit, isLoading }) => {
  const [prompt, setPrompt] = useState('');

  const handleSubmit = (e: React.SubmitEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (prompt.trim() && !isLoading) {
      onSubmit(prompt);
    }
  };

  return (
    <div className="w-full max-w-2xl px-4">
      <form onSubmit={handleSubmit} className="glass glow relative p-8">
        <label htmlFor="prompt" className="mb-4 block text-sm font-medium text-blue-300">
          Describe your brand, product, or service
        </label>
        <textarea
          id="prompt"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="e.g., A luxury sustainable skincare line for urban professionals..."
          className="w-full rounded-lg bg-white/5 p-4 text-white outline-none ring-1 ring-white/10 transition-all focus:ring-2 focus:ring-blue-500 min-h-[120px] resize-none"
          disabled={isLoading}
        />
        <div className="mt-6 flex justify-end">
          <button
            type="submit"
            disabled={isLoading || !prompt.trim()}
            className="rounded-full bg-gray-400 px-8 py-3 font-semibold text-white shadow-lg transition-all hover:bg-blue-500 hover:shadow-blue-500/40 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Generating...' : 'Generate Insights'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default PromptInput;
