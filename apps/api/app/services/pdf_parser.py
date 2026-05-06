from dataclasses import dataclass

import fitz


class PdfParsingError(ValueError):
    pass


class EmptyPdfTextError(PdfParsingError):
    pass


@dataclass(frozen=True, slots=True)
class PdfExtractionResult:
    raw_text: str
    page_count: int


def extract_pdf_text(pdf_bytes: bytes) -> PdfExtractionResult:
    if not pdf_bytes:
        raise PdfParsingError("The uploaded PDF is empty.")

    try:
        with fitz.open(stream=pdf_bytes, filetype="pdf") as document:
            page_count = document.page_count
            if page_count < 1:
                raise EmptyPdfTextError("The PDF does not contain any pages.")

            page_texts = []
            for page in document:
                page_text = page.get_text("text").strip()
                if page_text:
                    page_texts.append(page_text)
    except EmptyPdfTextError:
        raise
    except Exception as exc:
        raise PdfParsingError("Failed to parse the PDF document.") from exc

    raw_text = "\n\n".join(page_texts).strip()
    if not raw_text:
        raise EmptyPdfTextError("No extractable text was found in the PDF.")

    return PdfExtractionResult(raw_text=raw_text, page_count=page_count)
