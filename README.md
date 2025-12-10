# Nano Banana Image Studio (GenAI / Gemini)
This Streamlit app uses the Google GenAI SDK to talk to Gemini image models (e.g., Gemini 3 Pro Image / Nano Banana Pro).
It supports text-to-image generation and text+image editing.

## Setup
1. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Set environment variables (or use Streamlit secrets):
   - `GEMINI_API_KEY` — your API key (Google AI Studio / Gemini)
   - `GEMINI_BASE_URL` — optional custom base URL

   Example:
   ```
   export GEMINI_API_KEY="your_api_key_here"
   export GEMINI_BASE_URL="https://generativelanguage.googleapis.com/v1beta"
   ```

3. Run Streamlit:
   ```
   streamlit run app.py
   ```

## Notes
- The `genai_client.py` wraps `google.genai` SDK and extracts images from `response.parts`.
- For multi-turn editing, the SDK may return thought signatures. This simple wrapper does not surface thought signatures; if you need conversational state preservation, we can add a Conversation wrapper.
- The app expects the GenAI SDK to be installed (`pip install google-genai`).
