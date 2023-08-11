from .ml.text_detection import confirm_name_and_dob


class DOB:
    def __init__(self, dd, mm, yy):
        self.day = dd
        self.month = mm
        self.year = yy


def perform_verification(instance):
    Klass = instance.__class__  # it allows you to set 'Klass' to the actual class of any instance
    # qs_exists = Klass.objects.filter(key=key).exists()
