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

class WarnActorEntrance(ActorEntrance):

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
        Annotation: [None, None],
        ActorEntrance: ["left", None],
        WarnActorEntrance: ["left", None],
        ActorLine: ["left", None],
        SoundCue: ["right", None],
        WarningNote: [None, None],
        Note: [None, None]
    }
    margin_map = None

    def __init__(self, margins, positions = None) -> None:
        self.margins = margins
        if positions is not None:
            self.positions = positions
        self.margin_map = {
            "left": margins[0]/2,
            "right": margins[1]/2,
            "top": margins[2]/2,
            "bottom": margins[3]/2
        }

    def get_snapped_coordinates(self, object: Annotation, page_size):
        #TODO: COntinue
        prototypes = self.positions[type(object)]
        if prototypes is None: 
            return object.pos
        new_pos = None
        for elem, prototype, size in zip(object.pos, prototypes, page_size):
            if prototype is None:
                new_pos.append(elem)
            else:
                new_pos.append(size)
        return new_pos