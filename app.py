import os, io, time
import streamlit as st
from genai_client import GenAIClient
from pipeline import ASPECT_PRESETS, QUALITY_PROFILES, get_pixel_dimensions, apply_filters, add_watermark, contain_and_pad
from utils import slugify_filename, log_event
from styles import CUSTOM_CSS
from PIL import Image
st.set_page_config(layout="wide", page_title="VisionPrime Agent")
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
st.title("VisionPrime")

# Initialize GenAI client (reads GEMINI_API_KEY and GEMINI_BASE_URL from env or Streamlit secrets)
client = GenAIClient()

# Session state
if "history" not in st.session_state:
    st.session_state.history = []
if "active" not in st.session_state:
    st.session_state.active = None
if "ui" not in st.session_state:
    st.session_state.ui = {"aspect": "Landscape 16:9", "quality": "Standard (2K)", "style": "photorealistic", "guidance": 7.5, "seed": "", "num_variations": 1}

# Sidebar
# Sidebar
with st.sidebar:
    st.header("Control Center")
    prompt = st.text_area("Prompt", height=140, placeholder="Describe your vision...")
    
    with st.expander("Style & Dimensions", expanded=True):
        style = st.selectbox("Style", ["photorealistic", "illustration", "cinematic", "flat"], index=0)
        aspect = st.selectbox("Aspect Ratio", list(ASPECT_PRESETS.keys()), index=3)
        quality = st.selectbox("Quality Profile", list(QUALITY_PROFILES.keys()), index=1)

    with st.expander("Advanced Settings"):
        neg = st.text_area("Negative prompt", value="", height=80)
        guidance = st.slider("Guidance strength", 1.0, 20.0, 7.5)
        seed = st.text_input("Seed (optional)")
        nvar = st.slider("Number of variations", 1, 6, 1)
        enable_safety = st.checkbox("Enable safety filtering", value=True)

    with st.expander("Image Input (Img2Img)"):
        uploaded = st.file_uploader("Source image", type=["png","jpg","jpeg"])
        if uploaded:
            st.image(uploaded, caption="Source", use_container_width=True)
        use_uploaded_as_base = st.checkbox("Use as base for generation", value=False)

    with st.expander("Shot Engineering"):
        st.checkbox('Shallow DOF', key='shot_dof')
        st.checkbox('Wide angle', key='shot_wide')
        st.checkbox('Golden hour', key='shot_golden')

    st.markdown("---")
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        st.button('Generate', key='generate_btn', type="primary", use_container_width=True)
    with col_btn2:
        if st.button('Clear', use_container_width=True):
            st.session_state.history = []
            st.session_state.active = None

def build_shot_tags():
    tags = []
    if st.session_state.get('shot_dof'): tags.append('shallow depth of field, bokeh')
    if st.session_state.get('shot_wide'): tags.append('wide angle lens')
    if st.session_state.get('shot_golden'): tags.append('golden hour lighting, warm highlights')
    return tags

tabs = st.tabs(['Generate', 'Edit / Refine', 'History'])
gen_tab, edit_tab, hist_tab = tabs

# Generate tab
with gen_tab:
    # st.subheader('Generate') # Clean look
    if st.session_state.get("generate_btn"):
        with st.spinner("Dreaming up your image..."):
            final_prompt = prompt + ' ' + ' '.join(build_shot_tags())
            if enable_safety and 'nsfw' in final_prompt.lower():
                st.error('Prompt blocked by client-side safety filter. Please remove explicit content.')
            else:
                aspect_tuple = ASPECT_PRESETS[aspect]
                width, height = get_pixel_dimensions(aspect_tuple, quality)
                t0 = time.time()
                try:
                    # Check for base image
                    input_imgs = None
                    if use_uploaded_as_base and uploaded:
                        input_imgs = [Image.open(uploaded).convert('RGB')]
                    
                    imgs = client.generate_image(prompt=final_prompt, negative_prompt=neg, model='gemini-3-pro-image-preview',
                                                 aspect_ratio=f"{aspect_tuple[0]}:{aspect_tuple[1]}", image_size=quality,
                                                 guidance=guidance, seed=int(seed) if seed else None, num_images=nvar,
                                                 input_images=input_imgs)
                    for img in imgs:
                        meta = {'prompt': final_prompt, 'negative_prompt': neg, 'aspect': aspect, 'quality': quality, 'style': style, 'guidance': guidance, 'seed': seed, 'input_image_used': bool(input_imgs), 'time': time.time()}
                        st.session_state.history.insert(0, {'id': time.time(), 'image': img, 'meta': meta})
                    elapsed = time.time() - t0
                    st.success(f'Generated {len(imgs)} images in {elapsed:.1f}s')
                    log_event('generate', {'count': len(imgs), 'width': width, 'height': height, 'has_input_image': bool(input_imgs), 'time_ms': int(elapsed*1000)})
                except Exception as e:
                    st.error(f'Generation failed: {e}')

    cols = st.columns(3)
    for idx, item in enumerate(st.session_state.history[:9]):
        col = cols[idx % 3]
        with col:
            st.image(item['image'], use_container_width=True)
            if st.button('Set as active', key=f'set_active_{idx}'):
                st.session_state.active = idx

# Edit / Refine
with edit_tab:
    st.subheader('Edit / Refine')
    if st.session_state.active is None and uploaded is None:
        st.info('Set an active image from Generate tab or upload an image to edit.')
    base_img = None
    if uploaded:
        base_img = Image.open(uploaded).convert('RGB')
    elif st.session_state.active is not None and st.session_state.history:
        base_img = st.session_state.history[st.session_state.active]['image']
    if base_img:
        st.image(base_img, caption='Before', width=320)
        brightness = st.slider('Brightness', 0.2, 2.0, 1.0)
        contrast = st.slider('Contrast', 0.2, 2.0, 1.0)
        saturation = st.slider('Saturation', 0.0, 2.0, 1.0)
        apply_watermark = st.checkbox('Add watermark')
        watermark_text = st.text_input('Watermark text', value='© MyBrand')
        if st.button('Apply edits (local PIL)'):
            edited = apply_filters(base_img, brightness=brightness, contrast=contrast, saturation=saturation)
            if apply_watermark:
                edited = add_watermark(edited, watermark_text)
            st.session_state.history.insert(0, {'id': time.time(), 'image': edited, 'meta': {'edited_from': st.session_state.active}})
            st.image(edited, caption='After', width=320)

        st.markdown('### Text-driven edit (GenAI edit endpoint)')
        edit_instruction = st.text_area('What to change in the image?', height=80)
        if st.button('Apply text edit via GenAI'):
            try:
                imgs = client.generate_image(prompt=edit_instruction, input_images=[base_img], model='gemini-3-pro-image-preview',
                                             aspect_ratio=f"{aspect_tuple[0]}:{aspect_tuple[1]}", image_size=quality,
                                             guidance=guidance, seed=int(seed) if seed else None, num_images=1)
                if imgs:
                    new_img = imgs[0]
                    st.session_state.history.insert(0, {'id': time.time(), 'image': new_img, 'meta': {'prompt': edit_instruction}})
                    st.success('Edit applied')
                else:
                    st.error('No image returned from edit call.')
            except Exception as e:
                st.error(f'Edit failed: {e}')

# History tab
with hist_tab:
    st.subheader('History')
    for i, item in enumerate(st.session_state.history):
        cols = st.columns([1,3,2])
        with cols[0]:
            thumb = item['image'].copy()
            thumb.thumbnail((160,120))
            st.image(thumb, use_container_width=True)
        with cols[1]:
            st.write(item.get('meta', {}))
        with cols[2]:
            if st.button('Reload to editor', key=f'reload_{i}'):
                st.session_state.active = i
            buf = io.BytesIO()
            item['image'].save(buf, format='PNG')
            buf.seek(0)
            filename = slugify_filename(item.get('meta', {}).get('prompt','img'))[:40] + f"_{item['meta'].get('aspect','')}.png"
            st.download_button('Download PNG', data=buf, file_name=filename, mime='image/png', key=f"download_{item['id']}")
