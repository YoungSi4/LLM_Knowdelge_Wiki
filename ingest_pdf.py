import pymupdf4llm
import sys
import os

def convert_pdf_to_md(pdf_path, output_path):
    md_text = pymupdf4llm.to_markdown(pdf_path)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(md_text)
    print(f"Successfully converted {pdf_path} to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python ingest_pdf.py <input_pdf> <output_md>")
        sys.exit(1)
    
    convert_pdf_to_md(sys.argv[1], sys.argv[2])
