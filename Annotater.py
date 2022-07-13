# Standard Imports
from pathlib import Path
import io

# External imports
import jsonpickle
import PyPDF4 as pdf
from reportlab.pdfgen import canvas

# Main Imports
import Annotation

class Annotater:
    '''
    Wrapper class for actual annotation features and drawing
    '''

    # Data
    cues = None
    pages = None
    params = None

    # PDF and Paths
    pdf_path = None
    pdf_output_path = None
    old_pdf = None
    output_pdf = None
    path = None

    def __init__(self, pdf_path: Path, params: Annotation.AnnotationParameters) -> None:
        self.cues = []
        self.pages = []
        self.path = pdf_path.parent
        self.pdf_path = pdf_path
        self.pdf_output_path = self.path/"modified.pdf"
        self.params = params

    def load_file(self):
        '''Loads the PDF file and creates the annotations file'''
        self.old_pdf = pdf.PdfFileReader(str(self.pdf_path.absolute()))
        self.output_pdf = pdf.PdfFileWriter()

    def make_pages(self):
        '''Creates blank page objects'''
        self.pages = [Page(self) for _ in range(self.old_pdf.getNumPages())]

    def output(self):
        '''Exports the updated pdf'''
        self.merge_pages_with_annotations()
        output_stream = open(self.pdf_output_path, "wb")
        self.output_pdf.write(output_stream)

    def merge_pages_with_annotations(self):
        for page, old_page_obj in zip(self.pages, self.old_pdf.pages):
            new_page_obj = page.annotate(old_page_obj)
            if new_page_obj is None:
                self.output_pdf.addPage(old_page_obj)
            else:
                new_page_obj.mergePage(old_page_obj)
                self.output_pdf.addPage(new_page_obj)

    def get_dimensions(self, page_obj: pdf.pdf.PageObject):
        dims = page_obj.cropBox
        width = dims[2]-dims[0]
        height = dims[3]-dims[1]
        return width, height

    def save(self):
        path = self.path/"annotations.json"
        data = jsonpickle.encode(self)
        with open(path) as file:
            file.write(data)

class Page:
    '''
    Class for holding all annotations on a page
    '''

    annotations = None
    parent = None

    def __init__(self, parent: Annotater) -> None:
        self.annotations = []
        self.parent = parent

    def annotate(self, old_page_obj: pdf.pdf.PageObject):
        packet = io.BytesIO()
        dimensions = self.parent.get_dimensions(old_page_obj)
        annotation_canvas = canvas.Canvas(packet, dimensions)
        for annotation in self.annotations:
            annotation.annotate(annotation_canvas, self.parent.params)
        annotation_canvas.save()
        packet.seek(0)
        new_page_pdf = pdf.PdfFileReader(packet)
        if new_page_pdf.numPages == 0:
            return None
        return new_page_pdf.pages[0]

    def add_annotation(self, annotation: Annotation.Annotation):
        self.annotations.append(annotation)

if __name__ == "__main__":
    PARAMS = Annotation.AnnotationParameters(
        [72 for _ in range(4)]
    )
    TEST_PATH = '/Users/zpogrebin/Google Drive/Homework:Assignments/220712ScriptAnalyzer/Package'
    ANNOTATER = Annotater(Path(TEST_PATH)/"Script.pdf", PARAMS)
    ANNOTATER.load_file()
    ANNOTATER.make_pages()
    ANNOTATER.pages[0].add_annotation(Annotation.ActorEntrance([200,20],Annotation.Actor('5', 'Anna')))
    ANNOTATER.output()
    print("DONE")
