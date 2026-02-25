# import fitz  # PyMuPDF
# import os

# def extract_text_from_pdf(pdf_path):
#     if not os.path.exists(pdf_path):
#         raise FileNotFoundError(f"PDF not found: {pdf_path}")

#     doc = fitz.open(pdf_path)
#     file_name = os.path.basename(pdf_path)

#     extracted_text = []
#     extracted_text.append(f"--- FILE NAME: {file_name} ---\n")

#     for page_num, page in enumerate(doc, start=1):
#         page_text = page.get_text("text").strip()
#         if page_text:
#             extracted_text.append(f"\n--- PAGE {page_num} ---\n")
#             extracted_text.append(page_text)

#     final_text = "\n".join(extracted_text)

#     if len(final_text.strip()) < 50:
#         print("⚠️ Warning: Very little text extracted (might be scanned PDF)")

#     return final_text


# # Example usage:
# if __name__ == "__main__":
#     pdf_path = r"C:\Users\ashis\Downloads\Ashish Rajendra Khedkar 5.pdf"
#     try:
#         text = extract_text_from_pdf(pdf_path)
#         print(text[:5000])  # Print the first 500 characters of extracted text
#     except Exception as e:
#         print(f"Error: {e}")