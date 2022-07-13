import enum

from reportlab.pdfgen import canvas

class Annotation: 
    '''Base Annotation Class'''

    pos = None
    text = None
    alt_text = None
    leader_pos = None

    def __init__(self, pos, params, text, alt_text='', leader_pos=None) -> None:
        self.params = params
        self.pos = pos
        self.text = text
        self.alt_text = alt_text
        self.leader_pos = leader_pos

    def annotate(self, annotation_canvas=canvas.Canvas):
        annotation_canvas.drawString(*self.pos, self.text)


class ActorEntrance(Annotation):

    pass

class ActorLine(Annotation):

    pass

class SoundCue(Annotation):

    pass

class WarningNote(Annotation):

    pass

class Note(Annotation):

    pass

class AnnotationParameters:
    
    margins = None

    positions = {
        ActorEntrance: ["left", None],
        ActorLine: ["left", None],
        SoundCue: ["right", None],
        WarningNote: [None, None],
        Note: [None, None]
    }

    def __init__(self, margins, positions = None, sqprefix, colors) -> None:
        self.margins = margins
        if positions is not None:
            self.positions = positions

    def get_snapped_coordinates()
