# 
# from docxtpl import DocxTemplate
# import pypandoc
#
# # Interpolate jinja2 style
# doc = DocxTemplate("custom-reference.docx")
# context = { 
#     "doc_id" : "DOC-0034 rec C",
#     "project_id" : "PROJ-0001",
#     "doc_name" : "Pandoctylus -- A crazy and opinionated way of generating documents",
# }

# doc.render(context)
# doc.save("preprocessed-reference.docx")

# # Now run pandoc.
# output = pypandoc.convert_file(
#     "my_doc.md",
#     "docx",
#     outputfile="final.docx",
#     extra_args = [
#         "--reference-doc=preprocessed-reference.docx",
#         "--toc",
#         "--toc-depth=3",
#     ],
# )

from docxtpl import DocxTemplate
import pypandoc

import yaml
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from dataclasses import dataclass
import logging
import argparse
from functools import partial

logger = logging.getLogger(__name__)


# Allow including files inside templates
def include(base_path: Path, rel_path_or_pathlike):
    """
    Load and return the contents of a relative file path.
    Supports plain string paths from the YAML or static includes.
    """
    path = Path(rel_path_or_pathlike)
    if not path.is_absolute():
        path = base_path / path
    if not path.exists():
        raise FileNotFoundError(f"Included file not found: {path}")
    return path.read_text()


@dataclass
class PDPaths:
    """Convenience class to store all paths."""
    root_dir: Path
    docs_dir: Path
    common_dir: Path
    templates_dir: Path
    output_dir: Path


def render_markdown_doc(yaml_path: Path, pd_paths: PDPaths) -> Path:
    """Render one document from a YAML definition file to Markdown
    """
    doc = yaml.safe_load(yaml_path.read_text())
    
    # Get template and output file
    template_name = doc["template"]
    output_name = doc["output"]

    env = Environment(
        loader=FileSystemLoader(pd_paths.templates_dir),
        undefined=StrictUndefined
    )
    env.globals["include"] = partial(include, pd_paths.root_dir)

    template = env.get_template(template_name)

    # Render with metadata and content
    context = {
        "metadata": doc.get("metadata", {}),
        "content": doc.get("content", {})
    }

    rendered = template.render(**context)

    output_path = pd_paths.output_dir / output_name
    output_path.write_text(rendered)
    logger.info(f"✔ Rendered {output_path}")
    return output_path


def render_docx_doc(markdown_file: Path, yaml_path: Path, pd_paths: PDPaths) -> Path:
    """Render one document from a markdown file file to a Docx file
    considering the YAML definition file.
    """
    doc = yaml.safe_load(yaml_path.read_text())
    output_name = doc["output"]
    reference_doc = pd_paths.templates_dir / doc["reference"]
    
    # Interpolate the docx 

    doc_template = DocxTemplate(reference_doc)
    doc_template.render(doc.get("metadata", {}))
    # Save the document to a temporary file
    temp_reference_doc = pd_paths.output_dir / "temp-preprocessed-reference.docx"
    doc_template.save(temp_reference_doc)
   
    output_path = (pd_paths.output_dir / output_name).with_suffix(".docx")

    output = pypandoc.convert_file(
        str(markdown_file),
        "docx",
        outputfile=str(output_path),
        extra_args = [
            f"--reference-doc={str(temp_reference_doc)}",
            "--toc",
            "--toc-depth=3",
        ]
    )

def main():
    parser = argparse.ArgumentParser(description="Process YAML files in a specified directory.")
    parser.add_argument("--root-dir", type=str, help="Root directory containing YAML files")
    args = parser.parse_args()

    pd_paths = PDPaths(
        root_dir=Path(args.root_dir),
        docs_dir=Path(args.root_dir) / "docs",
        common_dir=Path(args.root_dir) / "common",
        templates_dir=Path(args.root_dir) / "templates",
        output_dir=Path(args.root_dir) / "output"
    )

    doc_files = sorted(pd_paths.docs_dir.glob("*.yml"))
    if not doc_files:
        logger.warning(f"No YAML files found in {args.root_dir}")
        return
    for yaml_path in doc_files:
        try:
            markdown_file = render_markdown_doc(yaml_path, pd_paths)
            render_docx_doc(markdown_file, yaml_path, pd_paths)
        except Exception as e:
            logger.exception(f"Error rendering {yaml_path.name}: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
