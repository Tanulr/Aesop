import React from 'react';

interface MarketingResponse {
  headline: string;
  body_copy: string;
  action_item: string;
}

interface ResultsDisplayProps {
  data: MarketingResponse | null;
  onReset: () => void;
}

const ResultsDisplay: React.FC<ResultsDisplayProps> = ({ data, onReset }) => {
  if (!data) return null;

  return (
    <div className="w-full max-w-3xl px-4 py-12 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <div className="glass glow p-10 space-y-8">
        <div className="space-y-2">
          <span className="text-xs font-bold uppercase tracking-[0.2em] text-blue-400">Headline</span>
          <h2 className="text-4xl font-extrabold leading-tight text-white">{data.headline}</h2>
        </div>
        
        <div className="space-y-2 text-blue-100/80">
           <span className="text-xs font-bold uppercase tracking-[0.2em] text-blue-400">Body Copy</span>
           <p className="text-lg leading-relaxed">{data.body_copy}</p>
        </div>

        <div className="space-y-2">
           <span className="text-xs font-bold uppercase tracking-[0.2em] text-blue-400">Call to Action</span>
           <p className="text-xl font-semibold text-gray-300">{data.action_item}</p>
        </div>

        <div className="pt-6 border-t border-white/10 flex justify-center">
          <button
            onClick={onReset}
            className="text-sm font-medium text-neutral-400 hover:text-white transition-colors"
          >
            Create New Campaign
          </button>
        </div>
      </div>
    </div>
  );
};

export default ResultsDisplay;
