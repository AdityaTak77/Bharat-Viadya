import os
from langchain_community.vectorstores import Milvus
from langchain_openai import OpenAIEmbeddings
from pdf_to_json.src.services.grobid_service import GrobidService
from dotenv import load_dotenv
import logging

load_dotenv()

class Document:
    def __init__(self, content, metadata=None):
        self.page_content = content
        self.metadata = metadata if metadata is not None else {}

def custom_text_splitter(documents, chunk_size=2000, max_length=65535):
    chunks = []
    for doc in documents:
        text = doc.page_content
        title = doc.metadata.get('title', '')  # Get the title from metadata if available
        for i in range(0, len(text), chunk_size):
            chunk = text[i:i + chunk_size]
            chunk_metadata = {'title': title}  # Include title in each chunk's metadata
            if len(chunk) > max_length:
                for j in range(0, len(chunk), max_length):
                    sub_chunk = chunk[j:j + max_length]
                    chunks.append(Document(sub_chunk, metadata=chunk_metadata))
            else:
                chunks.append(Document(chunk, metadata=chunk_metadata))
    return chunks

def create_db(pdf_paths=None, use_ocr=False, ocr_lang='eng'):
    logging.info("Starting database creation process...")
    documents = []

    if pdf_paths:  # Check if pdf_paths is not None and not empty
        grobid_service = GrobidService()
        tei_paths = [
            f"/Users/rohitrathi/Downloads/Ayurvedic ayush portal bot/BharatVaidya/BharatVaidya/pdf_to_json/output_xmls/{os.path.basename(pdf_path).replace('.pdf', '.xml')}"
            for pdf_path in pdf_paths
        ]

        # Check if XML files already exist
        xml_files_exist = all(os.path.exists(tei_path) for tei_path in tei_paths)

        if xml_files_exist:
            logging.info("XML files already exist. Skipping PDF to XML conversion...")
        else:
            logging.info("Converting PDFs to TEI XML...")
            grobid_service.process_multiple_pdfs(pdf_paths, tei_paths, use_ocr=use_ocr, lang=ocr_lang)

        for tei_path in tei_paths:
            if os.path.exists(tei_path):
                with open(tei_path, "r") as file:
                    documents.append(Document(file.read()))

    else:
        output_xml_dir = "//pdf_to_json/output_xmls/"
        tei_paths = [os.path.join(output_xml_dir, filename) for filename in os.listdir(output_xml_dir) if filename.endswith('.xml')]

        logging.info("No PDF paths provided. Using existing XML files...")

        for tei_path in tei_paths:
            with open(tei_path, "r") as file:
                documents.append(Document(file.read()))

    logging.info("Splitting documents into chunks...")
    texts = custom_text_splitter(documents, chunk_size=2000, max_length=65535)

    logging.info("Creating embeddings and storing them in Milvus...")
    embeddings = OpenAIEmbeddings(openai_api_key=os.environ.get("OPENAI_API_KEY"))

    # Attempt to create the Milvus collection
    try:
        milvus_collection = Milvus.from_documents(texts, embeddings, collection_name="ayurvedic_diagnosis", connection_args={"host": "localhost", "port": 19530})
        logging.info("Embeddings successfully stored in Milvus.")
    except Exception as e:
        logging.error(f"Failed to create Milvus collection or store data: {e}")

    logging.info("Database creation process completed.")

if __name__ == '__main__':
    pdf_files = None  # Set this to None or [] to skip PDF processing and use existing XMLs

    create_db(pdf_files, use_ocr=True, ocr_lang='eng+hin')
