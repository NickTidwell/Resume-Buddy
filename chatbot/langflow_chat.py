from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from langchain_core.messages import SystemMessage, HumanMessage, RemoveMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import MessagesState, StateGraph, START, END
from langchain_huggingface import HuggingFacePipeline
from typing import Literal

# Initialize the tokenizer and model
model_name = "google/gemma-2-2b-it"  # Replace with a valid model name
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    device_map="auto",  # Automatically detect CUDA devices
    torch_dtype="auto",
    trust_remote_code=True,
)

# Create the pipeline
pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, max_new_tokens=256)
hf_llm = HuggingFacePipeline(pipeline=pipe)

memory = MemorySaver()

class State(MessagesState):
    summary: str

def call_model(state: State):
    summary = state.get("summary", "")
    system_prompt = "You are a helpful assistant. Please provide clear and concise responses."
    system_message = SystemMessage(content=system_prompt)
    
    if summary:
        summary_message = SystemMessage(content=f"Summary of conversation earlier: {summary}")
        messages = [system_message, summary_message] + state["messages"]
    else:
        messages = [system_message] + state["messages"]
    
    # Use the HuggingFacePipeline to generate a response
    response = hf_llm.invoke(messages)
    
    return {"messages": [HumanMessage(content=response)]}

def should_continue(state: State) -> Literal["summarize_conversation", END]:
    messages = state["messages"]
    if len(messages) > 6:
        return "summarize_conversation"
    return END

def summarize_conversation(state: State):
    summary = state.get("summary", "")
    if summary:
        summary_message = (
            f"This is summary of the conversation to date: {summary}\n\n"
            "Extend the summary by taking into account the new messages above:"
        )
    else:
        summary_message = "Create a summary of the conversation above:"

    messages = state["messages"] + [HumanMessage(content=summary_message)]
    
    # Use the HuggingFacePipeline to generate a summary
    response = hf_llm.invoke(messages)
    
    delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]
    return {"summary": response, "messages": delete_messages}

def post_process_response(state: State):
    # Example post-processing: Convert response to uppercase
    response_message = state["messages"][-1]
    processed_content = response_message.content.upper()
    processed_message = HumanMessage(content=processed_content)
    
    return {"messages": [processed_message]}

workflow = StateGraph(State)
workflow.add_node("conversation", call_model)
workflow.add_node(summarize_conversation)
workflow.add_node("post_process", post_process_response)
workflow.add_edge(START, "conversation")
workflow.add_edge("conversation", "post_process")
workflow.add_conditional_edges("conversation", should_continue)
workflow.add_edge("summarize_conversation", END)

app = workflow.compile(checkpointer=memory)

def print_update(update):
    for k, v in update.items():
        for m in v["messages"]:
            m.pretty_print()
        if "summary" in v:
            print(v["summary"])

config = {"configurable": {"thread_id": "4"}}

def chat_with_bot():
    state = State(messages=[])
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        input_message = HumanMessage(content=user_input)
        input_message.pretty_print()
        for event in app.stream({"messages": [input_message]}, config, stream_mode="updates"):
            print_update(event)

if __name__ == "__main__":
    chat_with_bot()
