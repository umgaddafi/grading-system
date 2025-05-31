class Student:
    def __init__(self, name, id_number, ca, practical, exam):
        self.name = name
        self.id_number = id_number.upper()
        self.ca = ca
        self.practical = practical
        self.exam = exam
        self.total = ca + practical + exam
        self.grade = self.calculate_grade()

    def calculate_grade(self):
        if self.total >= 70:
            return "A"
        elif self.total >= 60:
            return "B"
        elif self.total >= 50:
            return "C"
        elif self.total >= 45:
            return "D"
        elif self.total >= 40:
            return "E"
        else:
            return "F"
