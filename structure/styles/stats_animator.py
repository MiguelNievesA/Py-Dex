from PyQt5.QtCore import QPropertyAnimation, QEasingCurve

class StatsAnimator:
    def __init__(self, parent):
        self.parent = parent
        self.animations = []

    def prepare_bar(self, bar, qss, max_value):

        bar.setRange(0, max_value)
        bar.setValue(0)
        bar.setFormat("%v")
        bar.setStyleSheet(qss)
        bar.style().unpolish(bar)
        bar.style().polish(bar)

    def animate_bar(self, bar, end_value, duration=800, easing=QEasingCurve.OutCubic):

        anim = QPropertyAnimation(bar, b"value", self.parent)
        anim.setDuration(duration)
        anim.setStartValue(0)
        anim.setEndValue(end_value)
        anim.setEasingCurve(easing)

        anim.start()
        self.animations.append(anim)

    def clear(self):
        self.animations.clear()