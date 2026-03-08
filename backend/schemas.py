from pydantic import BaseModel, Field
from typing import List

class BrandProfile(BaseModel):
    brand_name: str = Field(description="The formal name of the brand or company.")
    core_value_proposition: str = Field(description="A concise statement defining the core benefit the brand provides.")
    products_and_services: List[str] = Field(description="A list of the main products or services offered.")
    tone_of_voice: str = Field(description="1-2 words describing the brand's tone of voice (e.g., 'playful and energetic', 'serious and authoritative').")

class PersonaICP(BaseModel):
    persona_name: str = Field(description="A catchy, summarizing name for the persona (e.g., 'Budget-Conscious Clara').")
    needs: str = Field(description="What conscious or unconscious rational goals does the customer have in relation to this product? What are the critical jobs to be done?")
    wants: str = Field(description="What are the emotional drivers of the customer's decision making? What aspirational thoughts do they have about improving their lives?")
    fears: str = Field(description="What are the possible negative consequences of buying the product or making a decision at all (fear of missing out, loss, mistake)?")
    influencers: str = Field(description="Who in the user's life has a stake in, or influences, their decision?")
    personal_characteristics: str = Field(description="What psychographic information is relevant? Describe their values, personality, attitudes, opinions, lifestyle.")
    observable_attributes: str = Field(description="What observable characteristics can we use to identify this target customer? Common behaviors?")
    journey: str = Field(description="How does the customer currently solve the problem at hand? What is their motivation to adopt a better solution?")
    observations_and_quotes: str = Field(description="What quotes or observations characterize them? E.g., 'I want to travel but hotel prices are insane.'")

class StoryBrandStrategy(BaseModel):
    persona_name: str = Field(description="The name of the persona this strategy applies to.")
    step_1_character: str = Field(description="Identify what the customer wants in 1-2 short sentences.")
    step_2_problem: str = Field(description="Define their external, internal, and philosophical frustrations.")
    step_3_guide: str = Field(description="Position the brand as the guide with Empathy and Authority.")
    step_4_plan: str = Field(description="Provide a clear 3-4 step process or agreement plan to reduce their fear of buying.")
    step_5_action: str = Field(description="Use clear Direct (Buy Now) and Transitional (Free Trial/Lead Magnet) Call To Actions (CTAs).")
    step_6_failure: str = Field(description="Explicitly state the negative consequences of inaction if they don't buy.")
    step_7_success: str = Field(description="Paint a picture of the customer’s life transformed after using the product.")
