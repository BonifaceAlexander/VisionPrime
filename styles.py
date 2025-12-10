
CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Main Container Padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* Titles and Headers */
    h1, h2, h3 {
        font-weight: 800 !important;
        color: #FFFFFF;
    }
    
    h1 {
        background: -webkit-linear-gradient(45deg, #FF4B4B, #FF914D);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem !important;
        margin-bottom: 0.5rem !important;
    }

    /* Subheaders */
    .stSubheader {
        color: #E0E0E0 !important;
        font-weight: 600 !important;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        border: none;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }

    /* Primary Buttons (Streamlit generic logic, targeting first button usually) */
    /* Note: Streamlit classes change, general styling is safer */

    /* Cards / Images */
    .stImage {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transition: transform 0.2s;
    }
    
    .stImage:hover {
        transform: scale(1.02);
    }

    /* Sidebar tweaks */
    [data-testid="stSidebar"] {
        background-color: #1E1E1E;
        border-right: 1px solid #333;
    }
    
    /* Inputs */
    .stTextInput > div > div > input, .stTextArea > div > div > textarea {
        background-color: #2D2D2D;
        color: white;
        border-radius: 8px;
        border: 1px solid #444;
    }
    
    .stSelectbox > div > div > div {
        background-color: #2D2D2D;
        color: white;
        border-radius: 8px;
    }

</style>
"""
