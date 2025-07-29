import os
import tempfile

import streamlit as st
from PIL import Image
from transformers import AutoModel, AutoTokenizer

st.set_page_config(
    page_title="GOT-OCR Demo",
    # layout="wide"
)

MODEL_NAME = "/home/kunyuan/models/stepfun-ai/GOT-OCR2_0"


@st.cache_resource
def load_model():
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    model = AutoModel.from_pretrained(
        MODEL_NAME,
        trust_remote_code=True,
        low_cpu_mem_usage=True,
        device_map="cuda",
        use_safetensors=True,
        pad_token_id=tokenizer.eos_token_id,
    )
    model = model.eval().cuda()
    return tokenizer, model


st.title("GOT-OCR Demo")

# Load model
with st.spinner("Loading model..."):
    tokenizer, model = load_model()

# File uploader
uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Display image
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=False)

    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
        tmp_file.write(uploaded_file.getvalue())
        image_path = tmp_file.name

    # OCR Type selection
    ocr_type = st.selectbox(
        "Select OCR Type",
        ["Plain Text OCR", "Format Text OCR"],
    )

    # Additional options
    with st.expander("Advanced Options"):
        use_box = st.checkbox("Use Bounding Box")
        use_color = st.checkbox("Use Color Detection")
        use_multicrop = st.checkbox("Use Multi-crop")
        render_output = st.checkbox("Render Formatted Output")

    if st.button("Process Image"):
        with st.spinner("Processing..."):
            try:
                kwargs = {
                    "ocr_type": "format" if ocr_type == "Format Text OCR" else "ocr",
                }

                if use_box:
                    kwargs["ocr_box"] = ""
                if use_color:
                    kwargs["ocr_color"] = ""

                if render_output and ocr_type == "Format Text OCR":
                    render_file = "./output.html"
                    kwargs["render"] = True
                    kwargs["save_render_file"] = render_file

                if use_multicrop:
                    result = model.chat_crop(tokenizer, image_path, **kwargs)
                else:
                    result = model.chat(tokenizer, image_path, **kwargs)

                st.text_area("Results:", result, height=300)

                if render_output and ocr_type == "Format Text OCR":
                    with open(render_file) as f:
                        html_content = f.read()
                    st.components.v1.html(html_content, height=600)
                    os.remove(render_file)

            except Exception as e:
                st.error(f"Error occurred: {e!s}")
            finally:
                # Clean up temp file
                os.unlink(image_path)

st.markdown("""
### Usage Instructions:
1. Upload an image containing text
2. Select OCR type (Plain Text or Formatted)
3. Configure advanced options if needed
4. Click "Process Image" to start OCR
""")
