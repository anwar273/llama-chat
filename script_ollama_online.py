import streamlit as st
import requests
from serpapi import GoogleSearch
import time

# Set up Streamlit app
st.title("LLaMA 3.2 Chat with Internet Access")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Function to fetch data from the internet using SerpAPI
def fetch_search_results(query):
    params = {
        "q": query,
        "api_key": "a2205de7569b07f398c30135578bc7d2ac44d4ff1799ec0d028ea6bdc103c52c"  # Replace with your SerpAPI key
    }
    search = GoogleSearch(params)
    results = search.get_dict()
    return results.get("organic_results", [])

# Function to generate a response using Ollama and LLaMA 3.2
def generate_response_with_ollama(query, context):
    # Combine the query and context
    input_text = f"Answer the following question based on the context: {query}\nContext: {context}"

    # Send the input to Ollama's API
    ollama_url = "http://localhost:11434/api/generate"  # Ollama's local API endpoint
    payload = {
        "model": "llama3.2",  # Replace with your Ollama model name
        "prompt": input_text,
        "stream": False  # Set to True if you want streaming responses
    }
    response = requests.post(ollama_url, json=payload)

    if response.status_code == 200:
        return response.json()["response"]
    else:
        return "Error: Unable to generate a response."

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("Ask me anything..."):
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Fetch data from the internet
    with st.spinner("Fetching data from the internet..."):
        search_results = fetch_search_results(prompt)
        context = " ".join([result.get("snippet", "") for result in search_results])

    # Generate and stream the assistant's response
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""

        # Generate the response using Ollama
        response = generate_response_with_ollama(prompt, context)

        # Simulate streaming by displaying the response word by word
        for chunk in response.split():
            full_response += chunk + " "
            time.sleep(0.05)  # Simulate typing delay
            response_placeholder.markdown(full_response + "▌")

        response_placeholder.markdown(full_response)

    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": full_response})