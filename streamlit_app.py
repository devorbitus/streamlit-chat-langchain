# Import necessary libraries
import streamlit as st

# Import Langchain modules
from langchain.tools import DuckDuckGoSearchRun
from langchain.agents.tools import Tool
from langchain import OpenAI
from langchain.agents import initialize_agent, AgentType
# Streamlit UI Callback
from langchain.callbacks import StreamlitCallbackHandler
from langchain.chains import LLMMathChain
from langchain.memory import ConversationBufferMemory



# Import modules related to streaming response
import time

# ---
# Set up the Streamlit app
st.title("Internet-Connected Math Solving Chat Assistant")


st.write(
    """
    👋 Welcome to the 'Internet-Connected Math Solving Chat Assistant'.
    Your personal math-solving chat assistant, connected to the internet world.🌎
"""
)


# Get the user's question input
question = st.chat_input("Simplify: (4 – 5) – (13 – 18 + 2).")

# Get the API key from the secrets manager
if "OPENAI_API_KEY" in st.secrets:
    openai_api_key = st.secrets.OPENAI_API_KEY
else:
    openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Enter an OpenAI API Key to continue")
    st.stop()


# Initialize chat history if it doesn't already exist
if "messages" not in st.session_state:
    st.session_state.messages = []


# Initialize the OpenAI language model and search tool

llm = OpenAI(temperature=0)
search = DuckDuckGoSearchRun()
llm_math_chain = LLMMathChain(llm=llm, verbose=True)

if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferMemory(memory_key="chat_history")


# Set up the tool for responding to general questions
tools = [
    Tool(
        name="Calculator",
        func=llm_math_chain.run,
        description="useful for when you need to answer questions about math.",
    )
]

# Set up the tool for performing internet searches
search_tool = Tool(
    name="DuckDuckGo Search",
    func=search.run,
    description="Useful for when you need to do a search on the internet to find information that another tool can't find. Be specific with your input or ask about something that is new and latest.",
)
tools.append(search_tool)

# Initialize the Zero-shot agent with the tools and language model
conversational_agent = initialize_agent(
    agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
    tools=tools,
    llm=llm,
    verbose=True,
    max_iterations=10,
    memory = st.session_state.memory
)

# Display previous chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Process the user's question and generate a response
if question:
    # Display the user's question in the chat message container
    with st.chat_message("user"):
        st.markdown(question)

    # Add the user's question to the chat history
    st.session_state.messages.append({"role": "user", "content": question})

    # Generate the assistant's response
    with st.chat_message("assistant"):
        # Set up the Streamlit callback handler
        st_callback = StreamlitCallbackHandler(st.container())
        message_placeholder = st.empty()
        full_response = ""
        assistant_response = conversational_agent.run(question, callbacks=[st_callback])

        # Simulate a streaming response with a slight delay
        for chunk in assistant_response.split():
            full_response += chunk + " "
            time.sleep(0.05)

            # Add a blinking cursor to simulate typing
            message_placeholder.markdown(full_response + "▌")

        # Display the full response
        message_placeholder.info(full_response)

    # Add the assistant's response to the chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})
