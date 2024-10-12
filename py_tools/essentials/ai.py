from langchain_groq import ChatGroq
try:
    from .env_to_var import env_to_var
except:
    from env_to_var import env_to_var

class groq:
    def __init__(self):
        self.llm = ChatGroq(
            model="llama-3.1-70b-versatile",
            temperature=0.3,
            max_tokens=8000,
            groq_api_key = env_to_var("GROQ_KEY")
        )
        
    def send_message(self, messages):
        messages = [
        (
            "system",
            "",
        ),
        ("human", messages),
        ]
        
        ai_msg = self.llm.invoke(messages)
        
        return ai_msg.content

if __name__ == "__main__":
    ai = groq()
    print(ai.send_message("hey"))