from langchain.memory import ConversationBufferMemory
from langchain_huggingface import HuggingFacePipeline
from langchain_core.runnables.history import RunnableWithMessageHistory
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate

# Load the LLaMA model and tokenizer
model_name = "google/gemma-2-2b-it"  # Replace with a valid model name
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="auto",  # Automatically detect CUDA devices
    torch_dtype="auto",
    trust_remote_code=True,
)

# Wrap the model with HuggingFacePipeline
pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, max_new_tokens=512)
hf_llm = HuggingFacePipeline(pipeline=pipe)

# Initialize conversation memory
chat_history = ChatMessageHistory()

# Define a function to get session history

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a Resume Assistant. Answer all questions to the best of your ability.",
        ),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
    ]
)

chain = prompt | hf_llm


# Create a conversation chain using RunnableWithMessageHistory
# conversation = RunnableWithMessageHistory(runnable=hf_llm, memory=memory, get_session_history=get_session_history)
conversation = RunnableWithMessageHistory(
    chain,
    lambda session_id: chat_history,
    input_messages_key="input",
    history_messages_key="chat_history",
)

def chat():
    print("Chatbot is running. Type 'exit' to quit.")
    while True:
        user_input = input("")
        if user_input.lower() == 'exit':
            break
        try:
            # response = conversation.invoke(user_input)
            response = conversation.invoke(
                {"input": user_input},
                {"configurable": {"session_id": "unused"}},
            )
            print(f"{response}")
        except KeyError as e:
            print(f"An error occurred: {e}")
            # Optionally print stack trace for debugging
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    chat()
