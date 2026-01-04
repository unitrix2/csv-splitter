import streamlit as st
import pandas as pd
import io
import zipfile

# Page title aur layout
st.set_page_config(page_title="Big CSV Splitter", layout="wide")

st.title("📂 400MB+ CSV File Splitter")
st.write("Ye tool badi files ko 9,99,999 rows ke parts mein tod deta hai taaki Excel mein pura data dikhe.")

# File browse karne ka option (No rename needed)
uploaded_file = st.file_uploader("Apni CSV file select karein", type=["csv"])

if uploaded_file is not None:
    # Original file ka naam lena
    original_name = uploaded_file.name.rsplit('.', 1)[0]
    st.info(f"File '{uploaded_file.name}' upload ho gayi hai.")
    
    if st.button("Split and Create ZIP"):
        with st.spinner("Processing... Isme thoda samay lag sakta hai..."):
            try:
                zip_buffer = io.BytesIO()
                # Excel ki safe limit
                chunk_size = 999999
                
                with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as zip_file:
                    # Chunks mein read karna taaki memory crash na ho
                    reader = pd.read_csv(uploaded_file, chunksize=chunk_size, low_memory=False)
                    
                    for i, chunk in enumerate(reader):
                        # Chunk ko CSV mein convert karke zip mein daalna
                        csv_content = chunk.to_csv(index=False).encode('utf-8')
                        zip_file.writestr(f"{original_name}_part_{i+1}.csv", csv_content)
                
                st.success("Success! Saare parts taiyar hain.")
                st.download_button(
                    label="📥 Download All Parts (ZIP File)",
                    data=zip_buffer.getvalue(),
                    file_name=f"{original_name}_split_files.zip",
                    mime="application/zip"
                )
            except Exception as e:
                st.error(f"Ek galti hui: {e}")

st.divider()
st.caption("Note: Ye app totally free hai aur GitHub/Streamlit par chal rahi hai.")
