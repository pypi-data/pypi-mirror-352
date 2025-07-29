import pymupdf4llm
import os
import re

class DataParser:
    def __init__(self):
        pass

    def split_markdown_on_standalone_bold(self, md_text: str, topic: str = "") -> list[dict]:
        bold_heading_pattern = re.compile(r'^\s*\*\*(.+?)\*\*\s*[:：]?\s*$')
        lines = md_text.splitlines()
        chunks = []
        current_chunk = {"title": "Introduction", "content": []}

        for line in lines:
            stripped = line.strip()
            match = bold_heading_pattern.match(stripped)
            if match and not stripped.startswith(("-", "•")):
                if current_chunk["content"]:
                    chunks.append({
                        "title": current_chunk["title"],
                        "content": "\n".join(current_chunk["content"]).strip()
                    })
                heading_text = match.group(1).strip()

                title = f"**{topic} {heading_text}**" if topic else f"**{heading_text}**"
                current_chunk = {"title": title, "content": []}
            else:
                current_chunk["content"].append(line)

        if current_chunk["content"]:
            chunks.append({
                "title": current_chunk["title"],
                "content": "\n".join(current_chunk["content"]).strip()
            })

        return chunks

    def pdf_to_markdown(self, pdf_path, filename, md_dir, images_dir, topic: str = ""):
        os.makedirs(md_dir, exist_ok=True)
        os.makedirs(images_dir, exist_ok=True)
        md_text = pymupdf4llm.to_markdown(pdf_path, write_images=True, image_path=images_dir)
        chunks = self.split_markdown_on_standalone_bold(md_text, topic)

        file_name = filename.replace(".pdf", "")
        for i, chunk in enumerate(chunks):
            chunk_name = f"{file_name}_chunk_{i+1}.md"
            file_path = os.path.join(md_dir, chunk_name)

            if not all(s.strip() == "" for s in chunk["content"]):
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(chunk["title"] + "\n\n" + chunk["content"])

    def process_folder(self, folder_path, output_dir) -> list[tuple[str, str]]:
        all_md_paths = []
        for filename in os.listdir(folder_path):
            if filename.endswith('.pdf'):
                topic = ""
                if "mini_mavia" in filename.lower():
                    topic = "Mini Mavia"
                elif "block_clans" in filename.lower():
                    topic = "Block Clans"
                elif "turbo" in filename.lower():
                    topic = "Turbo"

                pdf_path = os.path.join(folder_path, filename)
                md_dir = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}_md")
                images_dir = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}_images")
                all_md_paths.append((md_dir, topic))
                self.pdf_to_markdown(pdf_path, filename, md_dir, images_dir, topic,)
        return all_md_paths