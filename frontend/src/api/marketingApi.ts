/**
 * marketingApi.ts
 *
 * All network logic lives here, isolated from the UI.
 * Swap the hardcoded return for a real fetch() call once the backend endpoint is ready.
 */

export async function generateCampaignLink(prompt: string): Promise<string> {
  console.log('Sending prompt to backend:', prompt);
  
  const response = await fetch('https://aesop-772493549962.us-central1.run.app/presentations/from-prompt', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ prompt }),
  });

  if (!response.ok) {
    throw new Error('Failed to generate campaign data from server.');
  }

  // Parses the response that the FastAPI server returns after its 3-6 second delay
  const data = await response.json();
  
  // Since the UI now displays a link instead of the raw data,
  // we'll return a dynamic mock URL based on the response.
  const campaignLink = data.link;
  return campaignLink;
}

