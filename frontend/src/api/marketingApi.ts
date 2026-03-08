/**
 * marketingApi.ts
 *
 * All network logic lives here, isolated from the UI.
 * Swap the hardcoded return for a real fetch() call once the backend endpoint is ready.
 */

export async function generateCampaignLink(prompt: string): Promise<string> {
  // --- HARDCODED STUB (replace with real fetch when backend is ready) ---
  console.log('Generating campaign for prompt:', prompt);
  await new Promise((resolve) => setTimeout(resolve, 5000)); // 5s fake latency
  return 'https://storymarketer.app/campaign/abc123';
  // --- END STUB ---

  // Real implementation will look like:
  // const response = await fetch('http://localhost:8000/generate-campaign', {
  //   method: 'POST',
  //   headers: { 'Content-Type': 'application/json' },
  //   body: JSON.stringify({ prompt }),
  // });
  // if (!response.ok) throw new Error('Failed to generate campaign link');
  // const data = await response.json();
  // return data.url;
}
