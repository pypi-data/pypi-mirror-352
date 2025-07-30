import winzy
import pypdf
from urllib.parse import urlparse
import requests
from io import BytesIO


def pdf_to_text(file_path_or_url, page_range=None):
    """Convert PDF to text from a file path or URL"""
    parsed = urlparse(file_path_or_url)
    is_url = parsed.scheme in ("http", "https")

    if is_url:
        response = requests.get(file_path_or_url)
        response.raise_for_status()
        file = BytesIO(response.content)
    else:
        file = open(file_path_or_url, "rb")

    with file:
        reader = pypdf.PdfReader(file)
        pages = [page.extract_text() for page in reader.pages]

        if page_range:
            if "-" in page_range:
                start, end = map(int, page_range.split("-"))
            else:
                start = end = int(page_range)
            return "\n".join(pages[start - 1 : end])
        else:
            return "\n".join(pages)

    file.close()


def create_parser(subparser):
    parser = subparser.add_parser(
        "pdf2txt", description="Extract text from a given pdf"
    )
    # Add subprser arguments here.
    parser.add_argument("file_path", type=str, help="Path to the PDF file")
    parser.add_argument(
        "-p",
        "--pages",
        type=str,
        nargs="+",
        help="Page numbers to extract example: 1-4 for  1 to 4. or just a single page",
    )

    return parser


class HelloWorld:
    """An example plugin"""

    __name__ = "pdf2txt"

    @winzy.hookimpl
    def register_commands(self, subparser):
        parser = create_parser(subparser)
        parser.set_defaults(func=self.run)

    def run(self, args):
        pdf_path = args.file_path
        if args.pages:
            print(pdf_to_text(pdf_path, ",".join(args.pages)))
        else:
            print(pdf_to_text(pdf_path))

    def hello(self, args):
        # this routine will be called when "winzy "pdf2txt is called."
        print("Hello! This is an example ``winzy`` plugin.")


pdf2txt_plugin = HelloWorld()
