import json
import os
from google import genai
from google.genai import types
import re

from scraper import scrape_multiple_websites
from schemas import BrandProfile, PersonaICP, StoryBrandStrategy
from typing import List

# Ensure you have your GOOGLE_API_KEY set in your environment
# os.environ['GOOGLE_API_KEY'] = 'YOUR_KEY_HERE'

def read_skills(filepath: str) -> str:
    """Helper function to read the markdown skills file for the agent."""
    if not os.path.exists(filepath):
        print(f"Warning: {filepath} not found. Falling back to default system instructions.")
        return ""
    with open(filepath, "r", encoding="utf-8") as f:
        return f.read()

def extract_urls(text: str) -> List[str]:
    """Finds all HTTP/HTTPS URLs within a block of text."""
    url_pattern = re.compile(r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+')
    return url_pattern.findall(text)

def run_agents(inputs: List[str]) -> List[StoryBrandStrategy]:
    print(f"Starting analysis with {len(inputs)} input(s)...")
    
    # 1. Gather all raw text and extract URLs
    raw_text = ""
    urls_to_scrape = []
    
    for item in inputs:
        if os.path.isfile(item):
            print(f"Reading file: {item}")
            try:
                with open(item, "r", encoding="utf-8") as f:
                    file_content = f.read()
                    raw_text += f"\n\n--- Client Text File ({item}) ---\n{file_content}"
                    urls_to_scrape.extend(extract_urls(file_content))
            except Exception as e:
                print(f"Error reading file {item}: {e}")
        elif item.startswith("http"):
            urls_to_scrape.append(item)
        else:
            raw_text += f"\n\n--- Raw Input ---\n{item}"
            
    # Deduplicate URLs
    urls_to_scrape = list(set(urls_to_scrape))
    
    # 2. Scrape the websites
    scraped_text = ""
    if urls_to_scrape:
        print(f"Found {len(urls_to_scrape)} URL(s) to scrape...")
        scraped_text = scrape_multiple_websites(urls_to_scrape)
        
    combined_context = raw_text + "\n" + scraped_text
    
    if not combined_context.strip():
        print("Error: Could not extract any text or URLs from the inputs.")
        return []

    # Initialize the Gemini Client
    try:
        client = genai.Client()
    except Exception as e:
        print(f"Error initializing client. Please ensure GOOGLE_API_KEY is set. Error: {e}")
        return []

    model_id = 'gemini-2.5-flash'
    
    print("\n--- Running Agent 1: Brand Analyst ---")
    
    # Read the Agent's persona and instructions from its dedicated MD file
    agent1_system_instruction = read_skills("agent1_skills.md")
    
    agent1_prompt = f"""
    Analyze the following client context. It may include raw text dumps and scraped website data.
    
    Context:
    {combined_context}
    """
    
    try:
        agent1_config = types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=BrandProfile,
            temperature=0.2
        )
        
        # Inject the skills document if it was read successfully
        if agent1_system_instruction:
             agent1_config.system_instruction = agent1_system_instruction

        agent1_response = client.models.generate_content(
            model=model_id,
            contents=agent1_prompt,
            config=agent1_config,
        )
        brand_profile_json = agent1_response.text
        
        # Save Agent 1 output
        with open("agent1_brand_profile.json", "w", encoding="utf-8") as f:
            # Format JSON nicely
            parsed_json = json.loads(brand_profile_json)
            json.dump(parsed_json, f, indent=4)
            
        print("Agent 1 Output (Brand Profile):")
        print(json.dumps(parsed_json, indent=2))
        
    except Exception as e:
        print(f"Error running Agent 1: {e}")
        return []

    print("\n--- Running Agent 2: Audience Profiler ---")
    
    agent2_system_instruction = read_skills("agent2_skills.md")
    
    agent2_prompt = f"""
    Generate exactly 3 extremely detailed, high-probability Ideal Customer Profiles (ICPs) 
    that this brand should target based on the provided Brand Profile. 
    
    Brand Profile:
    {brand_profile_json}
    """
    
    try:
        agent2_config = types.GenerateContentConfig(
            response_mime_type="application/json",
            # Wrap the PersonaICP in a list since we want exactly 3
            response_schema=list[PersonaICP],
            temperature=0.7 # Higher temp for brainstorming differing personas
        )
        
        if agent2_system_instruction:
            agent2_config.system_instruction = agent2_system_instruction

        agent2_response = client.models.generate_content(
            model=model_id,
            contents=agent2_prompt,
            config=agent2_config,
        )
        icp_json = agent2_response.text
        
        # Save Agent 2 output
        with open("agent2_icps.json", "w", encoding="utf-8") as f:
            parsed_icps = json.loads(icp_json)
            json.dump(parsed_icps, f, indent=4)
            
        print(f"\nAgent 2 Output ({len(parsed_icps)} Persona ICPs):")
        print(json.dumps(parsed_icps, indent=2))
        
    except Exception as e:
        print(f"Error running Agent 2: {e}")
        return []

    print("\n--- Running Agent 3: StoryBrand Strategist ---")
    
    agent3_system_instruction = read_skills("agent3_skills.md")
    all_storybrand_strategies = []
    
    # Iterate through each ICP generated by Agent 2
    for i, icp in enumerate(parsed_icps):
        print(f"Processing Strategy for Persona {i+1}...")
        
        agent3_prompt = f"""
        Using the overall Brand Profile, generate the 7-Part StoryBrand Framework 
        specifically for this single Persona ICP.
        
        Brand Profile:
        {brand_profile_json}
        
        Single Persona ICP:
        {json.dumps(icp, indent=2)}
        """
        
        try:
            agent3_config = types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=StoryBrandStrategy,
                temperature=0.4 # Lower temp for consistent framework mapping
            )
            
            if agent3_system_instruction:
                agent3_config.system_instruction = agent3_system_instruction

            agent3_response = client.models.generate_content(
                model=model_id,
                contents=agent3_prompt,
                config=agent3_config,
            )
            
            strategy_json = agent3_response.text
            
            # Convert JSON back into the actual Pydantic Object
            strategy_obj = StoryBrandStrategy.model_validate_json(strategy_json)
            all_storybrand_strategies.append(strategy_obj)
            
        except Exception as e:
            print(f"Error running Agent 3 for Persona {i+1}: {e}")
            continue

    # Save Agent 3 cumulative output
    if all_storybrand_strategies:
        with open("agent3_storybrand.json", "w", encoding="utf-8") as f:
            # We must convert the objects to dicts for JSON serialization
            json.dump([obj.model_dump() for obj in all_storybrand_strategies], f, indent=4)
            
        print(f"\nAgent 3 Output ({len(all_storybrand_strategies)} Strategies):")
        # Print the dictionaries nicely
        print(json.dumps([obj.model_dump() for obj in all_storybrand_strategies], indent=2))
        
    print("\nSUCCESS: Finished all 3 Agents. Check the .json files in this directory.")
    
    # Return the List of Pydantic Class Objects for downstream use
    return all_storybrand_strategies

if __name__ == "__main__":
    import sys
    
    # Simple CLI handling
    if len(sys.argv) > 1:
        target_inputs = sys.argv[1:]
    else:
        # Default test if no args provided
        print("No inputs provided. Pass a text file or URL.")
        target_inputs = ["https://trip.com"]
        
    final_strategies = run_agents(target_inputs)
    
    # Test that it returned the actual objects
    if final_strategies:
        print(f"\n[Validation] Returned {len(final_strategies)} Pydantic Objects.")
        if len(final_strategies) > 0:
            print(f"Example accessing an object attribute: {final_strategies[0].persona_name}")
