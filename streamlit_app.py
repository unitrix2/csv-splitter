import streamlit as st
import pandas as pd
import io
import zipfile
import math

# Page setup
st.set_page_config(page_title="Ultimate CSV Splitter", layout="wide", page_icon="✂️")

st.title("✂️ Ultimate CSV Splitter")
st.markdown("### Badi files ko asani se Excel-friendly banayein")

# File uploader
uploaded_file = st.file_uploader("Apni CSV file browse karein", type=["csv"])

if uploaded_file is not None:
    # Original file details
    original_name = uploaded_file.name.rsplit('.', 1)[0]
    
    st.sidebar.header("Split Settings")
    
    # User choice: Rows or Parts
    split_mode = st.sidebar.radio(
        "Splitting ka tarika chunein:",
        ["Rows ke hisab se (Fixed Rows)", "Barabar hisson mein (Equal Parts)"]
    )
    
    chunk_size = 0
    
    try:
        if split_mode == "Rows ke hisab se (Fixed Rows)":
            chunk_size = st.sidebar.number_input(
                "Har file mein kitni rows honi chahiye?", 
                min_value=1, 
                value=999999,
                help="Excel ke liye 1,000,000 se kam rakhein."
            )
        else:
            num_parts = st.sidebar.number_input(
                "Kitne barabar parts mein todna hai?", 
                min_value=2, 
                max_value=500, 
                value=2
            )
            # Total rows count karna bina memory crash kiye
            with st.spinner("File analyze ki ja rahi hai..."):
                count_reader = pd.read_csv(uploaded_file, usecols=[0])
                total_rows = len(count_reader)
                chunk_size = math.ceil(total_rows / num_parts)
                st.sidebar.success(f"Total Rows: {total_rows:,}")
                st.sidebar.info(f"Har part mein ~{chunk_size:, } rows hongi.")
                # Pointer reset for main reading
                uploaded_file.seek(0)

        if st.button("Split Process Shuru Karein"):
            zip_buffer = io.BytesIO()
            
            with st.status("Data process ho raha hai...", expanded=True) as status:
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                    # Optimized reading
                    reader = pd.read_csv(uploaded_file, chunksize=chunk_size, low_memory=False)
                    
                    for i, chunk in enumerate(reader):
                        status.write(f"Part {i+1} taiyar ho raha hai...")
                        # CSV to bytes
                        csv_data = chunk.to_csv(index=False).encode('utf-8')
                        zip_file.writestr(f"{original_name}_part_{i+1}.csv", csv_data)
                        del chunk # Memory management
                
                status.update(label="Processing Puri Ho Gayi!", state="complete", expanded=False)
            
            # Download Button
            st.success("Aapki ZIP file taiyar hai!")
            st.download_button(
                label="📥 Download ZIP File",
                data=zip_buffer.getvalue(),
                file_name=f"{original_name}_split_archive.zip",
                mime="application/zip"
            )

    except Exception as e:
        st.error(f"Galti: {e}")
        st.info("Tip: Check karein ki CSV file sahi format mein hai ya nahi.")

st.sidebar.divider()
st.sidebar.caption("Made with ❤️ for Large Data Handling")
