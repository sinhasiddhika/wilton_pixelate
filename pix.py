import streamlit as st
import numpy as np
import cv2
from PIL import Image
from io import BytesIO

# Set page config
st.set_page_config(page_title="Perfect Pixel Art Generator", layout="wide")

# App title
st.title("Perfect Pixel Art Generator")
st.markdown("Create crisp, perfect pixel art from any image!")

# Image uploader
uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Load image using PIL
    image = Image.open(uploaded_file)
    img_array = np.array(image)
    
    # Convert to RGB if it has alpha channel
    if img_array.shape[2] == 4:
        img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)
    
    # Show original image
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Original Image")
        st.image(img_array, caption=f"Size: {img_array.shape[1]}×{img_array.shape[0]}", use_container_width=True)
    
    # Get original dimensions
    orig_height, orig_width = img_array.shape[:2]
    
    # Pixelation parameters
    st.subheader("Pixelation Controls")
    
    # Two modes: Simple and Advanced
    mode = st.radio("Choose control mode:", ["Simple Mode", "Advanced Mode"], horizontal=True)
    
    if mode == "Simple Mode":
        st.markdown("**Quick presets for perfect pixel art:**")
        preset = st.selectbox(
            "Choose a preset:",
            ["Custom", "Tiny (32×32)", "Small (64×64)", "Medium (128×128)", "Large (256×256)"]
        )
        
        if preset == "Custom":
            pixel_width = st.slider("Pixel Art Width", min_value=16, max_value=512, value=90, step=2)
            pixel_height = st.slider("Pixel Art Height", min_value=16, max_value=512, value=120, step=2)
        else:
            size_map = {
                "Tiny (32×32)": (32, 32),
                "Small (64×64)": (64, 64),
                "Medium (128×128)": (128, 128),
                "Large (256×256)": (256, 256)
            }
            pixel_width, pixel_height = size_map[preset]
            st.info(f"Selected: {pixel_width}×{pixel_height} pixels")
        
        # Calculate optimal pixel size for display
        display_width = min(pixel_width * 4, 1300)
        display_height = min(pixel_height * 4, 1300)
        
    else:  # Advanced Mode
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.markdown("**Pixel Art Dimensions:**")
            pixel_width = st.number_input(
                "Pixel Art Width (in pixels)",
                min_value=16,
                max_value=512,
                value=90,
                step=2,
                help="This is the actual pixel count in your pixel art"
            )
            pixel_height = st.number_input(
                "Pixel Art Height (in pixels)",
                min_value=16,
                max_value=512,
                value=120,
                step=2,
                help="This is the actual pixel count in your pixel art"
            )
        
        with col_b:
            st.markdown("**Display Size (optional):**")
            pixel_size = st.slider(
                "Pixel Size Multiplier", 
                min_value=1, 
                max_value=20, 
                value=4, 
                step=1,
                help="How big each pixel appears in the final image"
            )
            
            display_width = min(pixel_width * pixel_size, 1300)
            display_height = min(pixel_height * pixel_size, 1300)
    
    # Show current settings
    st.info(f"Pixel Art: {pixel_width}×{pixel_height} pixels | Display: {display_width}×{display_height} pixels")
    
    # Perform perfect pixelation
    def create_perfect_pixel_art(img, target_width, target_height, display_width, display_height):
        """Create perfect pixel art with exact pixel dimensions"""
        
        # Step 1: Resize to exact pixel art dimensions using area interpolation for best quality
        pixel_art = cv2.resize(img, (target_width, target_height), interpolation=cv2.INTER_AREA)
        
        # Step 2: Scale up to display size using nearest neighbor to maintain sharp pixels
        if display_width != target_width or display_height != target_height:
            display_img = cv2.resize(pixel_art, (display_width, display_height), interpolation=cv2.INTER_NEAREST)
        else:
            display_img = pixel_art.copy()
        
        return pixel_art, display_img
    
    # Generate the pixel art
    pixel_art, display_img = create_perfect_pixel_art(
        img_array, pixel_width, pixel_height, display_width, display_height
    )
    
    # Show pixelated image
    with col2:
        st.subheader("Pixel Art Result")
        st.image(
            display_img, 
            caption=f"Pixel Art: {pixel_width}×{pixel_height} | Display: {display_width}×{display_height}",
            use_container_width=False
        )
    
    # Download options
    st.subheader(" Download Options")
    
    col_d1, col_d2 = st.columns(2)
    
    with col_d1:
        # Download original pixel art (small file)
        result_original = Image.fromarray(pixel_art)
        buf_original = BytesIO()
        result_original.save(buf_original, format="PNG")
        byte_original = buf_original.getvalue()
        
        st.download_button(
            label=f" Download Pixel Art ({pixel_width}×{pixel_height})",
            data=byte_original,
            file_name=f"pixel_art_{pixel_width}x{pixel_height}.png",
            mime="image/png",
            help="Small file size, perfect for games/web"
        )
    
    with col_d2:
        # Download display version (larger file)
        result_display = Image.fromarray(display_img)
        buf_display = BytesIO()
        result_display.save(buf_display, format="PNG")
        byte_display = buf_display.getvalue()
        
        st.download_button(
            label=f"Download Display Version ({display_width}×{display_height})",
            data=byte_display,
            file_name=f"pixel_art_display_{display_width}x{display_height}.png",
            mime="image/png",
            help="Larger file, better for printing/viewing"
        )
    
    # Show some stats
    st.subheader("Image Statistics")
    col_s1, col_s2, col_s3 = st.columns(3)
    
    with col_s1:
        st.metric("Original Size", f"{orig_width}×{orig_height}")
    with col_s2:
        st.metric("Pixel Art Size", f"{pixel_width}×{pixel_height}")
    with col_s3:
        reduction_factor = (orig_width * orig_height) / (pixel_width * pixel_height)
        st.metric("Size Reduction", f"{reduction_factor:.1f}x smaller")

else:
    st.info("Please upload an image to start creating pixel art!")
    
    # Show some example information
    st.subheader(" How it works:")
    st.markdown("""
    1. **Upload** any image (JPG, PNG)
    2. **Choose** your desired pixel art dimensions (e.g., 90×120 pixels)
    3. **Get** perfect, crisp pixel art with no blurriness
    4. **Download** in original pixel size or scaled-up display version
    
    **Perfect for:** Game sprites, retro art, NFT projects, social media avatars
    """)
