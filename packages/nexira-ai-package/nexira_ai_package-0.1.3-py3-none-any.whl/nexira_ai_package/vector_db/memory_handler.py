from nexira_ai_package.db_handler import DocumentDBHandler
import logging
import markdown
from bs4 import BeautifulSoup
import io
from PyPDF2 import PdfReader
import docx
from nexira_ai_package.vector_db.data_parser import DataParser
from langchain_core.tools import tool
from importlib.resources import files
import re
import os
from typing import List, Dict, Optional

class MemoryHandler(DocumentDBHandler):
    def __init__(self, connection_string: str, username: str, password: str, db_name: str, collection_name: str):
        super().__init__(connection_string, username, password, db_name, collection_name)

    def get_search_tool(self):        
        @tool("mini_mavia_search_tool", parse_docstring=True)
        def mini_mavia_search_tool(query: str, limit: int = 5) -> list[str]:
            """Search DocumentDB for relevant document chunks for Mini Mavia.

            Args:
                query: The search query string.
                limit: Number of results to return (default: 5).

            Returns:
                A list of relevant information for the query on Mini Mavia.
            """
            results = self.search_similar(query, limit)
            tool_results = []
            for doc in results:
                text = doc["text"]
                images = doc["payload"]["images"] if "images" in doc["payload"] else []
                text += "\n\n" + "\n".join(images)
                tool_results.append(text)
            return tool_results

        @tool("block_clans_search_tool", parse_docstring=True)
        def block_clans_search_tool(query: str, limit: int = 5) -> list[str]:
            """Search DocumentDB for relevant document chunks for Block Clans.

            Args:
                query: The search query string.
                limit: Number of results to return (default: 5).

            Returns:
                A list of relevant information for the query on Block Clans.
            """
            results = self.search_similar(query, limit)
            tool_results = []
            for doc in results:
                text = doc["text"]
                images = doc["payload"]["images"] if "images" in doc["payload"] else []
                text += "\n\n" + "\n".join(images)
                tool_results.append(text)
            return tool_results
        return [mini_mavia_search_tool, block_clans_search_tool]

    def read_markdown_file(self, file_path: str) -> dict:
        """Read and parse markdown file content."""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                images = re.findall(r'!\[[^\]]*\]\(.*\)', content)
                # Convert markdown to HTML
                html = markdown.markdown(content)
                # Extract text from HTML
                soup = BeautifulSoup(html, 'html.parser')
                text = soup.get_text()
                return {"text": text, "images": images}
        except Exception as e:
            logging.error(f"❌ Error reading file {file_path}: {e}")
            return {"text": "", "images": []}

    def process_markdown_directory(self, directory_path: str) -> List[Dict]:
        points = []        
        for filename in os.listdir(directory_path):
            if filename.endswith('.md'):
                file_path = os.path.join(directory_path, filename)
                content = self.read_markdown_file(file_path)
                if content.get("text"):
                    doc_id = self.generate_doc_id(filename)
                    points.append(
                        {
                            "text": content.get("text"),
                            "images": content.get("images"),
                            "filename": filename,
                            "file_path": file_path,
                            "source_type": "markdown"
                        }
                    )
        return points

    def insert_markdown_directory(self, directory_path: str, topic: str = "") -> bool:
        if not self.client:
            logging.error("❌ No Qdrant connection")
            return False

        if not os.path.exists(directory_path):
            logging.error(f"❌ Directory {directory_path} does not exist")
            return False

        try:
            points = self.process_markdown_directory(directory_path)
            logging.info(f"✅ Found {len(points)} markdown files to process")
            success = True
            for point in points:
                if not self.insert_vector_document(
                    text=point["text"],
                    metadata={
                        "filename": point["filename"],
                        "file_path": point["file_path"],
                        "source_type": "markdown",
                        "tags": topic,
                        "images": point["images"]
                    }
                ):
                    success = False
                    logging.error(f"❌ Failed to insert document: {point['filename']}")
                else:
                    logging.info(f"✅ Successfully inserted document: {point['filename']}")

            return success
        except Exception as e:
            logging.error(f"❌ Error processing markdown directory: {e}")
            return False

    def insert_nexira_document(self):
        pdf_folder = files("nexira_ai_package.vector_db") / "nexira_docs"
        output_folder = pdf_folder / "dataset"
        output_folder.mkdir(exist_ok=True)
        parser = DataParser()
        md_paths = parser.process_folder(pdf_folder, output_folder)

        for path, topic in md_paths:
            print(f"Inserting {path} with topic {topic}")
            self.insert_markdown_directory(path, topic)

    def call_tool(self, query: str, agent_type: int):
        tools = self.get_search_tool()[agent_type]
        return tools(query)

    def insert_user_document(self, file_bytes: bytes, file_name: str, metadata: dict):
        file_name = file_name.lower()

        handlers = {
            ".md": self.insert_markdown,
            ".txt": self.insert_text,
            ".pdf": self.insert_pdf,
            ".docx": self.insert_docx,
        }

        for ext, handler in handlers.items():
            if file_name.endswith(ext):
                return handler(file_bytes, file_name, metadata)


    def insert_text(self, file_bytes: bytes, file_name: str, metadata: dict):
        try:
            text = file_bytes.decode("utf-8")
            self.insert_vector_document(
                text=text,
                metadata=metadata
            )
            return True
        except Exception as e:
            logging.error(f"❌ Error processing plain text file: {e}")
            return False

    def insert_markdown(self, file_bytes: bytes, file_name: str, metadata: dict):
        try:
            content = file_bytes.decode("utf-8")
            html = markdown.markdown(content)
            text = BeautifulSoup(html, "html.parser").get_text()

            self.insert_document(
                text=text,
                metadata=metadata
            )
            return True
        except Exception as e:
            logging.error(f"❌ Error processing markdown file: {e}")
            return False

    def insert_pdf(self, file_bytes: bytes, file_name: str, metadata: dict):
        try:
            pdf_reader = PdfReader(io.BytesIO(file_bytes))
            full_text = "\n".join(page.extract_text() for page in pdf_reader.pages if page.extract_text())

            self.insert_document(
                text=full_text,
                metadata=metadata
            )
            return True
        except Exception as e:
            logging.error(f"❌ Error processing PDF file: {e}")
            return False

    def insert_docx(self, file_bytes: bytes, file_name: str, metadata: dict):
        try:
            doc = docx.Document(io.BytesIO(file_bytes))
            full_text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])

            self.insert_document(
                text=full_text,
                metadata=metadata
            )
            return True
        except Exception as e:
            logging.error(f"❌ Error processing DOCX file: {e}")
            return False
