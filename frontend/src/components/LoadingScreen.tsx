import React, { useState, useEffect } from 'react';

const MESSAGES = [
  "Analyzing Brand DNA...",
  "Checking Competitor Trends...",
  "Optimizing Marketing Hooks...",
  "Generating Creative Copy...",
  "Refining Your Message...",
  "Almost there...",
];

const LoadingScreen: React.FC = () => {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setIndex((prev) => (prev + 1) % MESSAGES.length);
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="fixed inset-0 z-50 flex flex-col items-center justify-center bg-[#030712] text-white">
      <div className="relative mb-8">
        <div className="h-16 w-16 animate-spin rounded-full border-4 border-indigo-500 border-t-transparent shadow-[0_0_15px_rgba(99,102,241,0.5)]"></div>
        <div className="absolute inset-0 flex items-center justify-center">
            <div className="h-8 w-8 rounded-full bg-indigo-500/20 blur-sm"></div>
        </div>
      </div>
      <div className="h-8 overflow-hidden">
        <p key={index} className="animate-flash text-xl font-medium tracking-wide text-indigo-300">
          {MESSAGES[index]}
        </p>
      </div>
    </div>
  );
};

export default LoadingScreen;
