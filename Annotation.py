from __future__ import annotations
import enum
import math

import numpy as np
from reportlab.pdfgen import canvas

_ALIGN_MARK = '\u3000'
_BLACK = (0, 0, 0)
_WHITE = (0, 0, 0)

def reset_colors(canv: canvas.Canvas):
    canv.setFillColorRGB(*_BLACK)
    canv.setStrokeColorRGB(*_BLACK)

def grey(percent: float):
    return (int(percent*255) for _ in range(3))

class Annotation:
    '''Base Annotation Class'''

    pos = None
    text = None
    alt_text = None
    leader_pos = None

    def __init__(self, pos, text, alt_text='', leader_pos=None) -> None:
        self.pos = pos
        self.text = text
        self.alt_text = alt_text
        self.leader_pos = leader_pos

    def annotate(self, canv: canvas.Canvas, params: AnnotationParameters):
        pos = params.get_snapped_coordinates(self, canv._pagesize)
        canv.setFontSize(params.smallFontSize)
        canv.drawString(*pos, self.text)

    def _polygon(self, canv: canvas.Canvas, points, fill=None, stroke=None):
        poly = canv.beginPath()
        poly.moveTo(*points[0])
        for i, point in enumerate(points[1:]):
            poly.lineTo(*points[i+1])
        poly.lineTo(*points[0])
        if fill is not None:
            canv.setFillColorRGB(*fill)
        if stroke is not None:
            canv.setStrokeColorRGB(*stroke)
        canv.drawPath(poly, stroke=stroke is not None, fill=fill is not None)
        reset_colors(canv)

class ActorMovement(Annotation):

    actor = None

    def __init__(self, pos, actor) -> None:
        # TODO Define actor class
        self.actor = actor
        super().__init__(pos, actor.number, actor.name)

    def _draw_triangle(self, canv: canvas.Canvas, pos,
                       params: AnnotationParameters, rotation=0, size=1):
        base = params.itemSize*size
        height = base*math.sqrt(3)/2
        points = [
            np.array([0, -base/2]),
            np.array([0, base/2]),
            np.array([height, 0])
        ]
        vtrans = [
            np.array(pos),
            np.array(pos),
            np.array(pos) + np.array([height,0]),
            np.array(pos)
        ]
        rotations = [
            np.array([[1, 0], [0, 1]]),
            np.array([[0, -1], [1, 0]]),
            np.array([[-1, 0], [0, -1]]),
            np.array([[0, 1], [-1, 0]])
        ]
        transform = lambda p, r: rotations[r]@p.transpose() + vtrans[r].transpose()
        t_points = [transform(p, rotation) for p in points]
        self._polygon(canv, t_points, (255, 255, 0),(255, 0, 0))

    def annotate(self, canv: canvas.Canvas, params: AnnotationParameters, rot=0, size=1):
        pos = np.array(params.get_snapped_coordinates(self, canv._pagesize))
        canv.setFontSize(params.bigFontSize)
        text_pos = (pos+np.array([0, -params.bigFontSize/2/1.2]))
        canv.drawRightString(*text_pos, f"{self.actor.number} ")
        self._draw_triangle(canv, pos, params, rot, size)
        # self._polygon(canv, [[0, pos[1]], [200, pos[1]]], stroke=(0, 0, 0))

class ActorEntrance(ActorMovement):

    def annotate(self, canv: canvas.Canvas, params: AnnotationParameters):
        return super().annotate(canv, params, 0)

class ActorExit(ActorMovement):

    def annotate(self, canv: canvas.Canvas, params: AnnotationParameters):
        return super().annotate(canv, params, 2, 0.5)

class WarnActorEntrance(ActorMovement):

    def annotate(self, canv: canvas.Canvas, params: AnnotationParameters):
        pos = np.array(params.get_snapped_coordinates(self, canv._pagesize))
        canv.setFontSize(params.bigFontSize)
        text_pos = (pos+np.array([0, params.bigFontSize/5]))
        self._draw_triangle(canv, pos, params, 3, 1)
        canv.drawCentredString(*text_pos, self.actor.number)


class ActorLine(Annotation):

    pass

class SoundCue(Annotation):

    pass

class SoundSnap(SoundCue):

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
        ActorExit: ["left", None],
        WarnActorEntrance: ["right", None],
        ActorLine: ["left", None],
        SoundCue: ["right", None],
        WarningNote: [None, None],
        Note: [None, None]
    }
    margin_map = None

    itemSize = 24
    bigFontSize = 20
    smallFontSize = 15

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

    def get_snapped_coordinates(self, obj: Annotation, page_size):
        prototypes = self.positions[type(obj)]
        if prototypes is None:
            return obj.pos
        new_pos = []
        for elem, prototype, size in zip(obj.pos, prototypes, page_size):
            if prototype is None:
                new_pos.append(elem)
            else:
                new_pos.append(self._margin_pos(prototype, size))
        return new_pos

    def _margin_pos(self, margin_str, page_length):
        margin = self.margin_map[margin_str]
        if margin_str in ("left", "top"):
            return margin
        return page_length - margin

class Actor:

    name = None
    number = None
    color = None

    def __init__(self, number: str, name: str, color=None) -> None:
        self.name = name
        self.number = number
        self.color = color