# This code is meant to be run in a local environment where Streamlit is installed.
# It cannot be executed in environments where `streamlit` or `openai` are not available.

try:
    import streamlit as st
    from openai import OpenAI
    from config import load_api_key, save_api_key, load_system_prompt, save_system_prompt
except ModuleNotFoundError as e:
    print("This script requires Streamlit and OpenAI packages to run.")
    print("Please install them using 'pip install streamlit openai'")
    raise SystemExit(e)

# Set page config
st.set_page_config(page_title="LLM Feedback Loop", layout="wide")
st.title("Feedback Loop on LLM Outputs")

# Load API key
api_key = load_api_key()
if not api_key:
    st.warning("Enter your OpenAI API key to get started.")
    api_key_input = st.text_input("OpenAI API Key", type="password")
    if st.button("Save API Key") and api_key_input:
        save_api_key(api_key_input)
        st.success("API key saved. Please refresh the page.")
        st.stop()

# Load system prompt (persisted across sessions)
system_prompt = load_system_prompt()

# File upload
uploaded_file = st.file_uploader("Upload a context file (e.g. Indian Constitution)", type=["txt"])

# User prompt
user_input = st.text_area("Enter your question (vague is okay)")

# History state
if "history" not in st.session_state:
    st.session_state.history = []

# Submit
if st.button("Get Response"):
    if not uploaded_file or not user_input:
        st.warning("Please upload a file and enter a prompt.")
    else:
        file_text = uploaded_file.read().decode("utf-8")
        full_prompt = f"{system_prompt}\n\n[File Content]\n{file_text[:2000]}\n\n[User Input]\n{user_input}"

        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": full_prompt}
            ]
        )
        answer = response.choices[0].message.content

        st.session_state.history.append({
            "prompt": user_input,
            "response": answer
        })

        st.success("Response received.")
        st.write("### Assistant Response:")
        st.write(answer)

# Feedback Section
if st.session_state.history:
    st.write("---")
    st.write("### Previous Responses")
    for idx, interaction in enumerate(reversed(st.session_state.history)):
        prompt_number = len(st.session_state.history) - idx
        st.write(f"**Prompt #{prompt_number}:** {interaction['prompt']}")
        st.write(f"**Response:** {interaction['response']}")

        rating = st.slider(f"How many stars for Prompt #{prompt_number}?", 1, 5, key=f"rating_{idx}")
        
        if rating <= 3:
            feedback = st.text_input(f"Feedback for Prompt #{prompt_number} (since rating is low)", key=f"fb_{idx}")
            if feedback:
                st.info("Rewriting system prompt using feedback...")
                client = OpenAI(api_key=api_key)
                rewrite_response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an assistant that rewrites system prompts based on user feedback."},
                        {"role": "user", "content": f"Original system prompt: {system_prompt}\n\nFeedback: {feedback}\n\nPlease rewrite the system prompt accordingly."}
                    ]
                )
                new_prompt = rewrite_response.choices[0].message.content.strip()
                save_system_prompt(new_prompt)
                system_prompt = new_prompt
                st.success("System prompt updated and saved permanently.")
                st.write("### New System Prompt:")
                st.code(new_prompt)

# Optional CLI entrypoint
def main():
    import streamlit.web.cli as stcli
    import sys
    sys.argv = ["streamlit", "run", __file__]
    sys.exit(stcli.main())
