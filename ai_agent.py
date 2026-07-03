import json

from openai import AsyncOpenAI

from config.data import OPENAI_API_KEY
from database import Database


SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "You are an expert, friendly, and proactive AI Sales Assistant for a premium smartphone retail store. "
        "Your primary goal is to help customers find the perfect smartphone, provide detailed specifications, "
        "and confidently close sales.\n\n"
        
        "CRITICAL OPERATIONAL RULES:\n"
        "1. INFORMATION RETRIEVAL: Never guess, hallucinate, or make up phone specifications, prices, or availability. "
        "Whenever a customer asks about a specific phone, price range, brand, or feature, you MUST immediately call the "
        "`search_smartphones` tool to fetch real-time accurate data from the store database.\n"
        
        "2. HANDLING OUT-OF-STOCK OR UNAVAILABLE ITEMS: If the user asks for a specific model that is NOT in the database, "
        "or if their budget doesn't match the requested model, do NOT simply say 'We don't have it'. Instead:\n"
        "   - Acknowledge the request politely.\n"
        "   - Immediately offer 1-2 close alternatives that are currently AVAILABLE in the database.\n"
        "   - Match alternatives based on: similar price point, similar brand, or comparable specifications (e.g., if iPhone 15 Pro is missing, suggest a Galaxy S24 or iPhone 15).\n"
        "   - Highlight the benefits of the alternative model to guide the customer toward a purchase.\n\n"
        
        "3. TONE AND STYLE:\n"
        "   - Keep your responses clear, concise, and highly professional.\n"
        "   - Always communicate in the language the customer uses (default to Uzbek if they speak Uzbek).\n"
        "   - CRITICAL FORMATTING RULE: You MUST format your response using standard Telegram HTML tags. "
        "Do NOT use Markdown (like #, ##, **, or __). Use ONLY these tags:\n"
        "     * <b>bold text</b> for phone names or important metrics\n"
        "     * <i>italic text</i> for highlights\n"
        "     * Standard dashes (-) for bullet points.\n"
        "     Example: <b>iPhone 13</b>\n"
        "     - Price: 650 USD\n"
        "     - RAM: 4GB"
    )
}

class AIAgent:
    def __init__(self, db: Database):
        self.client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        self.db = db

        self.system_prompt = SYSTEM_PROMPT

        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_smartphones",
                    "description": "Search the shop database for smartphones by model name, brand, or specifications to get accurate price, stock status, and features.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The smartphone model or brand name to search for (e.g., 'iPhone 15', 'Samsung', 'Xiaomi')."
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        ]

    async def get_response(self, telegram_id: int, user_message: str) -> str:
        await self.db.save_message(telegram_id, "user", user_message)

        history = await self.db.get_chat_history(telegram_id, limit=10)
        
        messages = [self.system_prompt] + history

        response = await self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            tools=self.tools,
            tool_choice="auto"
        )
        
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        if tool_calls:
            messages.append(response_message)
            
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)
                
                if function_name == "search_smartphones":
                    db_results = await self.db.search_smartphones(query=function_args.get("query"))
                    
                    tool_result_str = json.dumps(db_results, ensure_ascii=False)
                    
                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": tool_result_str
                    })
            
            second_response = await self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages
            )
            ai_reply = second_response.choices[0].message.content
        else:
            ai_reply = response_message.content

        await self.db.save_message(telegram_id, "assistant", ai_reply)
        return ai_reply