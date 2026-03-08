import React from 'react';

interface LinkResultProps {
  url: string;
  onReset: () => void;
}

const LinkResult: React.FC<LinkResultProps> = ({ url, onReset }) => {
  return (
    <div className="flex flex-col items-center gap-8 text-center px-4 animate-in fade-in slide-in-from-bottom-4 duration-700">

      {/* Success badge */}
      <div className="flex items-center gap-2 rounded-full bg-green-500/10 border border-green-500/20 px-4 py-2 text-green-400 text-sm font-medium">
        <span className="inline-block h-2 w-2 rounded-full bg-green-400 animate-pulse" />
        Your campaign is ready
      </div>

      {/* The link card */}
      <div className="glass glow w-full max-w-xl p-8 space-y-4">
        <p className="text-xs font-bold uppercase tracking-[0.2em] text-blue-400">
          Campaign URL
        </p>
        <a
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          className="block text-xl font-semibold text-white break-all hover:text-blue-300 transition-colors"
        >
          {url}
        </a>
        <a
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-block mt-2 rounded-full bg-blue-600 px-8 py-3 font-semibold text-white shadow-lg transition-all hover:bg-blue-500 hover:shadow-blue-500/40"
        >
          Open Campaign →
        </a>
      </div>

      {/* Reset */}
      <button
        onClick={onReset}
        className="text-sm font-medium text-neutral-400 hover:text-white transition-colors"
      >
        ← Start a new campaign
      </button>
    </div>
  );
};

export default LinkResult;
