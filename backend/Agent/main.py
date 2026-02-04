from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain.messages import SystemMessage,HumanMessage
import os
from dotenv import load_dotenv
load_dotenv()

class QuestionAgentError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)

sysMsg = '''
You are a Senior QA Engineer. Your only job is to add Google-Style Docstrings and Type Hints to the following code. 
Do NOT refactor the logic. Output only the valid Python code.
'''


class Agent:
    def __init__(self):
        try: 
            if os.getenv("GROQ_API_KEY"):
                os.environ['GROQ_API_KEY'] = os.getenv("GROQ_API_KEY") #type:ignore
            self.model = ChatGroq(
                model=os.getenv("GROQ_MODEL"), #type:ignore
                temperature=0.8,
            )
            self.agent = create_agent(
                self.model,
                system_prompt=SystemMessage(sysMsg),
            )
        except Exception as e:
            raise QuestionAgentError(f"Failed to initialize agent: {e}")
        
    def getQuestion(self, input: str):
        try:
            result = self.agent.invoke(
                {"messages": HumanMessage(input)}, #type:ignore
            )
            return result['messages'][1].content
        except Exception as e:
            raise QuestionAgentError(f"Failed to generate questions: {e}")
            