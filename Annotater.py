# Standard Imports
from pathlib import Path
import io
import os

# External imports
import jsonpickle
import PyPDF4 as pdf
from reportlab.pdfgen import canvas

# Main Imports
import Annotation

class AllUserData:
    '''
    Contains all annotation data
    '''

    # Data
    cues = None
    snaps = None
    pages = None
    params = None
    actors = None

    def __init__(self, params: Annotation.AnnotationParameters) -> None:
        self.params = params
        self.cues = {}
        self.snaps = {}
        self.pages = []

    def register_cue(self, number: float, annotation: Annotation.SoundCue):
        if number in self.cues: return False
        self.cues[number] = annotation
        return True

    def register_snap(self, number: float, annotation: Annotation.SoundSnap):
        if number in self.snaps: return False
        self.snaps[number] = annotation
        return True

class Annotater:
    '''
    Wrapper class for actual annotation features and drawing
    '''

    user_data = None

    # PDF and Paths
    pdf_path = None
    pdf_output_path = None
    old_pdf = None
    output_pdf = None
    path = None

    def __init__(self, pdf_path: Path, params: Annotation.AnnotationParameters) -> None:
        self.user_data = AllUserData(params)
        self.path = pdf_path.parent
        self.pdf_path = pdf_path
        self.pdf_output_path = self.path/"modified.pdf"

    def load_file(self):
        '''Loads the PDF file and creates the annotations file'''
        self.old_pdf = pdf.PdfFileReader(str(self.pdf_path.absolute()))
        self.output_pdf = pdf.PdfFileWriter()

    def make_pages(self):
        '''Creates blank page objects'''
        pages = [Page() for _ in range(self.old_pdf.getNumPages())]
        self.user_data.pages = pages

    def output(self):
        '''Exports the updated pdf'''
        self.merge_pages_with_annotations()
        output_stream = open(self.pdf_output_path, "wb")
        self.output_pdf.write(output_stream)

    def merge_pages_with_annotations(self):
        for page, old_page_obj in zip(self.user_data.pages, self.old_pdf.pages):
            new_page_obj = page.annotate(old_page_obj, self)
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

    def save_annotations(self):
        path = self.path/"annotations.json"
        data = jsonpickle.encode(self.user_data, indent=4)
        if os.path.isfile(path):
            mode = 'w'
        else:
            mode = 'x'
        with open(path, mode) as file:
            file.write(data)

    def get_page(self, page: int):
        return self.user_data.pages[page]

    def get_params(self):
        return self.user_data.params

    def load_annotations(self):
        path = self.path/"annotations.json"
        with open(path, 'r') as file:
            data = file.read()
            self.user_data = jsonpickle.decode(data)

class Page:
    '''
    Class for holding all annotations on a page
    '''

    annotations = None

    def __init__(self) -> None:
        self.annotations = []

    def annotate(self, old_page_obj: pdf.pdf.PageObject, parent: Annotater):
        packet = io.BytesIO()
        dimensions = parent.get_dimensions(old_page_obj)
        annotation_canvas = canvas.Canvas(packet, dimensions)
        for annotation in self.annotations:
            annotation.annotate(annotation_canvas, parent.get_params())
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
    # ANNOTATER.load_annotations()
    ANNOTATER.get_page(0).add_annotation(Annotation.ActorEntrance([200,20],Annotation.Actor('5', 'Anna')))
    ANNOTATER.get_page(0).add_annotation(Annotation.ActorExit([50,200],Annotation.Actor('5', 'Anna')))
    ANNOTATER.get_page(0).add_annotation(Annotation.WarnActorEntrance([100,100],Annotation.Actor('5', 'Anna')))
    ANNOTATER.get_page(0).add_annotation(Annotation.SoundCue([100,500],"SQ171", "Sound Cue", [300, 120]))
    ANNOTATER.get_page(0).add_annotation(Annotation.SoundCue([100,400],"SN201"))
    ANNOTATER.output()
    ANNOTATER.save_annotations()
    print("DONE")
