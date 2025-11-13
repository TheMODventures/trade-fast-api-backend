import os
import json
import re
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from dotenv import load_dotenv
from app.utils.swift_codes import get_swift_system_prompt

load_dotenv()

class PromptAgent:
    def __init__(self):
        """Initialize the prompt-based agent with Gemini and SWIFT code understanding"""
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")

        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=api_key, # type: ignore
            temperature=0.3  # Lower temperature for more consistent LC form filling
        )

        # Get comprehensive SWIFT-aware system prompt
        system_prompt = get_swift_system_prompt()

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", "{input}")
        ])

    def _clean_json_response(self, text: str) -> dict:
        """Clean and parse JSON from model response"""
        try:
            # Remove markdown code blocks if present
            text = re.sub(r'```json\s*', '', text)
            text = re.sub(r'```\s*', '', text)
            text = text.strip()

            # Try to parse JSON
            return json.loads(text)
        except json.JSONDecodeError:
            # If direct parsing fails, try to extract JSON object
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except:
                    pass
            return {"raw_response": text, "parsed": False}

    async def run(self, input_text: str) -> dict:
        """
        Run the agent with the given prompt
        Handles both natural language and SWIFT code format
        """
        try:
            chain = self.prompt | self.llm
            response = await chain.ainvoke({"input": input_text})

            # Try to parse as JSON first
            parsed_response = self._clean_json_response(response.content) # pyright: ignore[reportArgumentType]

            # If successfully parsed JSON, return structured response
            if parsed_response.get("parsed") != False:
                return {
                    "success": True,
                    "response": parsed_response,
                    "raw_text": response.content
                }

            # Otherwise return as plain text
            return {
                "success": True,
                "response": response.content
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
