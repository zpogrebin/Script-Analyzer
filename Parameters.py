class AnnotationParameters:

    margins = None
    positions = {
        ActorEntrance
        ActorLine
        SoundCue
        Warning
        Note
    }

    def __init__(self, margins) -> None:
        self.margins = margins

    