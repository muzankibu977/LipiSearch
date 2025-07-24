import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import os
from typing import List, Union
import streamlit as st


class BanglaPDFTextExtractor:
    def __init__(self, pdf_path: str):
        """
        Initialize the PDF text extractor
        
        Args:
            pdf_path (str): Path to the PDF file
        """
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)
        
        # Configure Tesseract for Bangla OCR
        # You might need to adjust the path based on your system
        pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"  # Windows
        
    def extract_text_from_page(self, page_number: int) -> str:
        """
        Extract text from a specific page number (1-indexed)
        
        Args:
            page_number (int): Page number (starting from 1)
            
        Returns:
            str: Extracted text from the page
        """
        if page_number < 1 or page_number > len(self.doc):
            raise ValueError(f"Page number must be between 1 and {len(self.doc)}")
        
        page = self.doc[page_number - 1]  # Convert to 0-indexed
        
        # Try to extract text directly first
        text = page.get_text()
        
        # If no text found or very little text, try OCR
        if len(text.strip()) < 10:
            print(f"Page {page_number}: Limited text found, attempting OCR...")
            ocr_text = self._extract_text_with_ocr(page)
            if ocr_text:
                text = ocr_text
        
        return text.strip()
    
    def extract_text_from_pages(self, page_numbers: List[int]) -> dict:
        """
        Extract text from multiple pages
        
        Args:
            page_numbers (List[int]): List of page numbers (1-indexed)
            
        Returns:
            dict: Dictionary with page numbers as keys and extracted text as values
        """
        results = {}
        for page_num in page_numbers:
            try:
                results[page_num] = self.extract_text_from_page(page_num)
                print(f"✓ Successfully extracted text from page {page_num}")
            except Exception as e:
                results[page_num] = f"Error: {str(e)}"
                print(f"✗ Failed to extract text from page {page_num}: {e}")
        
        return results
    
    def _extract_text_with_ocr(self, page) -> str:
        """
        Extract text using OCR for image-based content
        
        Args:
            page: PyMuPDF page object
            
        Returns:
            str: OCR extracted text
        """
        try:
            # Convert page to image
            mat = fitz.Matrix(2.0, 2.0)  # Increase resolution for better OCR
            pix = page.get_pixmap(matrix=mat)
            img_data = pix.tobytes("png")
            
            # Convert to PIL Image
            image = Image.open(io.BytesIO(img_data))
            
            # Perform OCR with Bangla language
            # 'ben' is the language code for Bengali/Bangla
            text = pytesseract.image_to_string(image, lang='ben+eng', config='--psm 6')
            
            return text
        except Exception as e:
            print(f"OCR failed: {e}")
            return ""
    
    def get_page_info(self, page_number: int) -> dict:
        """
        Get information about a specific page
        
        Args:
            page_number (int): Page number (1-indexed)
            
        Returns:
            dict: Page information
        """
        if page_number < 1 or page_number > len(self.doc):
            raise ValueError(f"Page number must be between 1 and {len(self.doc)}")
        
        page = self.doc[page_number - 1]
        
        # Get basic text
        direct_text = page.get_text()
        
        # Get images on the page
        image_list = page.get_images()
        
        # Get text blocks
        text_blocks = page.get_text("dict")
        
        return {
            "page_number": page_number,
            "direct_text_length": len(direct_text.strip()),
            "has_images": len(image_list) > 0,
            "image_count": len(image_list),
            "text_blocks_count": len(text_blocks.get("blocks", [])),
            "page_type": self._determine_page_type(direct_text, image_list)
        }
    
    def _determine_page_type(self, text: str, images: list) -> str:
        """Determine the type of page based on content"""
        has_text = len(text.strip()) > 10
        has_images = len(images) > 0
        
        if has_text and has_images:
            return "mixed (text + images)"
        elif has_text:
            return "text-only"
        elif has_images:
            return "image-only"
        else:
            return "empty"
    
    def save_extracted_text(self, page_numbers: List[int], output_file: str):
        """
        Save extracted text to a file
        
        Args:
            page_numbers (List[int]): List of page numbers to extract
            output_file (str): Output file path
        """
        results = self.extract_text_from_pages(page_numbers)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("Extracted Text from Bangla PDF\n")
            f.write("=" * 50 + "\n\n")
            
            for page_num, text in results.items():
                f.write(f"Page {page_num}:\n")
                f.write("-" * 20 + "\n")
                f.write(text + "\n\n")
        
        print(f"Text saved to {output_file}")
    
    def close(self):
        """Close the PDF document"""
        self.doc.close()

if __name__ == "__main__":
    # Example usage
    pdf_path = "C:\\Users\\sihab\\Downloads\\Documents\\মকতুবাত শরীফ ০৪.pdf"  # Replace with your PDF path
    # pdf_path = "C:\\Users\\sihab\\Downloads\\Documents\\Vol-30.pdf"  # Replace with your PDF path
    
    try:
        extractor = BanglaPDFTextExtractor(pdf_path)
        
        # Extract text from specific page
        page_number = int(input("Enter a valid page number: "))  # Change this to your desired page
        text = extractor.extract_text_from_page(page_number)
        print(f"Text from page {page_number}:")
        print(text)
        print("\n" + "="*50 + "\n")
        
        # # Extract text from multiple pages
        # pages_to_extract = [1, 2, 3]  # Change these to your desired pages
        # all_texts = extractor.extract_text_from_pages(pages_to_extract)
        
        # for page_num, text in all_texts.items():
        #     print(f"Page {page_num}: {len(text)} characters extracted")
        
        # Get page information
        page_info = extractor.get_page_info(page_number)
        print(f"\nPage info: {page_info}")

        st.text(text)
        
        # # Save to file
        # extractor.save_extracted_text(pages_to_extract, "extracted_text.txt")
        
        extractor.close()
        
    except Exception as e:
        print(f"Error: {e}")