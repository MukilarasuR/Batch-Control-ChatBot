from langchain_community.utilities import SQLDatabase
from pyprojroot import here
import warnings
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain.tools import Tool
from langchain.tools.base import BaseTool
from typing import Any
import os
import logging

# Enable LangChain debug logs
logging.basicConfig()
logging.getLogger("langchain").setLevel(logging.DEBUG)

warnings.filterwarnings("ignore")
print("Environment Variables are loaded:", load_dotenv())

# Load Gemini API key
google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    raise ValueError("❌ GOOGLE_API_KEY not found in your .env file")

# Define system prompt to encourage SQL reasoning
system_prompt = """
You are an intelligent, multi-capable ERP assistant with access to a PostgreSQL database containing structured business data across the following tables:
- departments
- employees
- product
- batch
- batch_tracking

You help users perform advanced data analysis, math operations, and visual reporting by reasoning intelligently over database records and the conversation history.

### YOUR RESPONSIBILITIES:

1. **Prefer SQL tools** when answering database-related questions (e.g., "Give total quantity", "Show batches by date").
2. **Avoid hallucination** — never invent data. Only answer from real database records or LLM tools.
3. **Never wrap SQL queries in triple backticks (```), even if the user asks.** Use raw SQL strings only.
4. Always double-check table names. They are case-sensitive and must match:
   - product
   - batch
   - employees
   - departments
   - batch_tracking

---

### CONTEXTUAL UNDERSTANDING:

5. Maintain full **memory of past answers**, including lists or summaries (e.g., batch codes).
6. Support **follow-up questions** like:
    - "Tell me about the 3rd one"
    - "Who created the last batch?"
    - "Give bar chart for above data"

---

### SMART SUGGESTIONS & UX GUIDANCE:

7. If the user's question is vague, confusing, or poorly phrased:
    - Politely **suggest improvements** or guide them toward a better question.
    - For example: if the user asks for a bar chart on non-categorical data, suggest a better chart type like a line graph or heatmap.

8. Detect **user intent or mood** (e.g., if the user sounds bored or overwhelmed) and suggest actions or ways to explore the data (e.g., “Want to explore employee trends over time?”).

---

### MATH + VISUAL SUPPORT:

9. You are capable of performing **math operations** over database records:
    - SUM, AVERAGE, COUNT, DEVIATION, MAX, MIN, etc.
    - Example: “What is the total value of all products?”, “Average quantity per batch?”

10. You support **visual representation suggestions**:
    - Bar charts, line charts, pie charts, heatmaps, timelines, etc.
    - If a user says "give bar chart" but the data doesn’t suit one, recommend a better fit.
    - Only use visualization language — not actual chart rendering unless enabled.

---

### CROSS-DOMAIN READINESS:

11. You are compatible with various platforms like websites, mobile apps, or embedded interfaces. Format responses clearly and concisely for front-end presentation.

---

### PERSONALITY:

- Be friendly, human-like, helpful, and precise.
- Prioritize clarity, clean formatting, and structured information.
- Fall back to general chat if the question is **non-ERP-related** (like jokes or casual talk).

You are the interface between people and data — make business data easy, insightful, and conversational.
"""

# Initialize Gemini LLM with system prompt
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=google_api_key,
    temperature=0.2,
    system_instruction=system_prompt.strip()
)

# Connect to PostgreSQL ERP DB
db = SQLDatabase.from_uri("postgresql+psycopg2://postgres:2309@localhost:5432/mydb")

# Add memory to handle conversation context
memory = ConversationBufferMemory(
    memory_key="chat_history",
    input_key="input",
    return_messages=True,
)

# Define SQL input cleaner
def clean_sql_input(query: str) -> str:
    return query.replace("```sql", "").replace("```", "").strip()

# Tool wrapper class to sanitize SQL tool input

class CleanedSQLTool(BaseTool):
    base_tool: BaseTool  # Declare field for pydantic

    def _run(self, query: str, **kwargs: Any) -> Any:
        cleaned_query = clean_sql_input(query)
        return self.base_tool.run(cleaned_query)

    def _arun(self, query: str, **kwargs: Any) -> Any:
        raise NotImplementedError("Async not supported.")

# Load and wrap SQL tools from LangChain
raw_sql_tools = SQLDatabaseToolkit(db=db, llm=llm).get_tools()
cleaned_sql_tools = [CleanedSQLTool(name=tool.name, description=tool.description, base_tool=tool) for tool in raw_sql_tools]

# Add fallback general chat tool
general_chat_tool = Tool(
    name="GeneralChat",
    func=lambda q: llm.invoke(q).content,
    description="Use for general conversation not related to database queries."
)

# Add chart suggestion tool
chart_suggestion_tool = Tool(
    name="ChartSuggester",
    func=lambda q: llm.invoke(f"Suggest the best chart type for: {q}").content,
    description="Suggests the most appropriate chart type for the given dataset or prompt."
)

# Combine tools
tools = cleaned_sql_tools + [general_chat_tool, chart_suggestion_tool]

# Initialize LangChain agent
agent_executor = initialize_agent(
    tools=tools,
    llm=llm,
    memory=memory,
    agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
    handle_parsing_errors=True,
    verbose=True,
)