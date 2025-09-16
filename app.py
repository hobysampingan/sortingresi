import streamlit as st
import pdfplumber
from PyPDF2 import PdfReader, PdfWriter
import re
import tempfile
import os
from collections import defaultdict

def extract_text_from_pdf(pdf_path):
    """Extract text from each page of the PDF."""
    texts = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                texts.append(text)
    return texts

def extract_order_id(text):
    """Extract Order ID from text using regex."""
    match = re.search(r'Order ID:\s*(\d+)', text)
    return match.group(1) if match else None

def extract_seller_sku(text):
    """Extract Seller SKU from text."""
    # Look for DM- patterns in lines
    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        # Look for DM- patterns
        if 'DM-' in line:
            # Extract DM-XXXX pattern (may be incomplete)
            match = re.search(r'DM-([A-Z]+)', line)
            if match:
                sku_part = match.group(1)
                # If we have more context, try to get the full SKU
                if '-' in line:
                    parts = line.split('-')
                    if len(parts) >= 3:
                        return f"DM-{parts[1]}-{parts[2]}"
                sku = f"DM-{sku_part}"
                # Clean up trailing characters
                sku = re.sub(r'[-\s\d]+$', '', sku)
                return sku
        # Look for ELIA- patterns
        elif 'ELIA-' in line:
            match = re.search(r'ELIA-([A-Z]+)', line)
            if match:
                return f"ELIA-{match.group(1)}"

    # Fallback: look for any SKU-like patterns
    matches = re.findall(r'\b(DM-[A-Z]+|ELIA-[A-Z]+)\b', text)
    if matches:
        sku = matches[0]
        # Clean up trailing numbers and spaces
        sku = re.sub(r'\s*\d+\s*$', '', sku)
        return sku
    return None

def group_pages_by_order_id(texts):
    """Group page texts by Order ID."""
    groups = defaultdict(list)
    for i, text in enumerate(texts):
        order_id = extract_order_id(text)
        if order_id:
            groups[order_id].append((i, text))
    return groups

def sort_by_seller_sku(groups):
    """Sort groups by Seller SKU. For multi-page receipts, only use first page's SKU for sorting."""
    sorted_groups = {}
    sku_to_order_ids = defaultdict(list)

    # First, identify the first page for each Order ID and its SKU
    for order_id, pages in groups.items():
        if pages:  # Make sure there are pages
            # Sort pages by page index to get the first page
            pages_sorted = sorted(pages, key=lambda x: x[0])
            first_page_idx, first_page_text = pages_sorted[0]

            sku = extract_seller_sku(first_page_text)
            if sku:
                # Clean SKU
                sku = re.sub(r'[-\s\d]+$', '', sku)
                sku_to_order_ids[sku].append(order_id)

    # Sort SKUs alphabetically
    for sku in sorted(sku_to_order_ids.keys()):
        order_ids = sku_to_order_ids[sku]
        # For each Order ID, collect all its pages in original order
        all_pages = []
        for order_id in order_ids:
            if order_id in groups:
                # Sort pages by page index to maintain original order
                pages_sorted = sorted(groups[order_id], key=lambda x: x[0])
                all_pages.extend(pages_sorted)
        sorted_groups[sku] = all_pages

    return sorted_groups

def create_sorted_pdf(input_pdf_path, sorted_pages, output_pdf_path):
    """Create a new PDF with pages sorted by Seller SKU."""
    reader = PdfReader(input_pdf_path)
    writer = PdfWriter()

    for sku, pages in sorted_pages.items():
        for page_idx, text in pages:
            writer.add_page(reader.pages[page_idx])

    with open(output_pdf_path, 'wb') as output_file:
        writer.write(output_file)

def main():
    st.title("PDF Resi Sorter")
    st.write("Upload a PDF file containing multiple receipts to sort them by Seller SKU.")

    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    if uploaded_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(uploaded_file.read())
            temp_pdf_path = temp_file.name

        try:
            # Extract texts
            texts = extract_text_from_pdf(temp_pdf_path)
            st.write(f"Extracted {len(texts)} pages from the PDF.")

            # Group by Order ID
            groups = group_pages_by_order_id(texts)
            st.write(f"Found {len(groups)} unique Order IDs.")

            # Sort by Seller SKU
            sorted_groups = sort_by_seller_sku(groups)
            st.write(f"Sorted into {len(sorted_groups)} Seller SKU groups.")

            # Create sorted PDF
            output_pdf_path = tempfile.mktemp(suffix=".pdf")
            create_sorted_pdf(temp_pdf_path, sorted_groups, output_pdf_path)

            # Provide download link
            with open(output_pdf_path, "rb") as file:
                btn = st.download_button(
                    label="Download Sorted PDF",
                    data=file,
                    file_name="sorted_resi.pdf",
                    mime="application/pdf"
                )

        except Exception as e:
            st.error(f"Error processing PDF: {str(e)}")
        finally:
            # Clean up temp files
            os.unlink(temp_pdf_path)
            if 'output_pdf_path' in locals():
                os.unlink(output_pdf_path)

if __name__ == "__main__":
    main()