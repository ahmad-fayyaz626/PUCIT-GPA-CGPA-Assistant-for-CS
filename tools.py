import courses
from courses import COURSES
from langchain.tools import tool

# Invalid input returns a plain error string — "Error: semester must be between 1 and 8" — rather than raising an exception.#
@tool
def marks_to_grade_points(marks: int) -> float:
    """ "This function takes in marks and returns the corresponding grade points based on the following scale:
    - 85 and above: 4.0
    - 80-84: 3.7
    - 75-79: 3.3
    - 70-74: 3.0
    - 65-69:2.7
    - 61-64:2.3
    -58-60:2.0
    -55-57:1.7
    -50-54:1.0
    -below 50:0.0
    """
    if marks >= 85:
        return 4.0
    elif marks >= 80:
        return 3.7
    elif marks >= 75:
        return 3.3
    elif marks >= 70:
        return 3.0
    elif marks >= 65:
        return 2.7
    elif marks >= 61:
        return 2.3
    elif marks >= 58:
        return 2.0
    elif marks >= 55:
        return 1.7
    elif marks >= 50:
        return 1.0
    else:
        return 0.0


# calculate the samester gpa based on the following formula
@tool
def calculate_samester_gpa(
    grade_points: list[float], credit_hours: list[float]
) -> float:
    """This function takes in a list of grade points and list of credit hours and returns the samester gpa based on the following formula"""
    if not grade_points or not credit_hours:
        return "Grade points and credit hours lists cannot be empty."
    if len(grade_points) != len(credit_hours):
        return "Grade points and credit hours lists must be of the same length."
    if any(credit_hour <= 0 for credit_hour in credit_hours):
        return "Credit hours must be positive values."

    total_credit_hours = sum(credit_hours)
    if total_credit_hours == 0:
        return "Total credit hours cannot be zero"
    total_grade_points = sum(
        [
            grade_point * credit_hour
            for grade_point, credit_hour in zip(grade_points, credit_hours)
        ]
    )
    return total_grade_points / total_credit_hours


# calculate new cgpa
@tool
def calculate_new_cgpa(
    current_cgpa: float,
    completed_credit_hours: float,
    semester_gpa: float,
    semester_credit_hours: float,
) -> float:
    "This function takes in the current cgpa, completed credit hours, semester gpa and semester credit hours and returns the new cgpa."
    if completed_credit_hours < 0 or semester_credit_hours < 0:
        return "Credit hours cannot be negative."
    if completed_credit_hours + semester_credit_hours == 0:
        return "Total credit hours cannot be zero."
    return (
        current_cgpa * completed_credit_hours + semester_gpa * semester_credit_hours
    ) / (completed_credit_hours + semester_credit_hours)


# tool for required gpa for a target
@tool
def required_gpa_for_target(
    target_cgpa: float,
    current_cgpa: float,
    completed_credit_hours: float,
    remaining_credit_hours: float,
) -> float:
    """This function calculates the required GPA for a target cgpa"""
    if completed_credit_hours < 0 or remaining_credit_hours < 0:
        return "Credit hours cannot be negative"
    if completed_credit_hours + remaining_credit_hours == 0:
        return "Total credit hours cannot be zero"
    if remaining_credit_hours == 0:
        return "Remaining credit hours cannot be zero"
    return (
        target_cgpa * (completed_credit_hours + remaining_credit_hours)
        - current_cgpa * completed_credit_hours
    ) / remaining_credit_hours


# tool for get semester courses
@tool
def get_semester_courses(semester: int) -> str:
    "Use this tool whenever the user asks for the courses/course outline of a semester. It retrieves the official course list and credit hours for semesters 1–8 from the provided curriculum data. Do not ask the user to provide the course list."
    if semester not in courses.COURSES:
        return "Error: Invalid semester number.Please enter semester between 1-8"

    course_list = COURSES[semester]
    result = ""

    for code, course, cr in course_list:
        result += f"{code} - {course} ({cr} credit hours)\n"
    return result


@tool
# get remaining credit hours
def get_remaining_credit_hours(current_semester: int) -> float:
    """This function will take the semester number and will be return the remaining credit hours for the degree compleetion"""
    if current_semester not in COURSES:
        return (
            "Error: Invalid semester number.Please enter a valid semester between 1-8"
        )
    return sum(
        course[2] for sem in range(current_semester + 1, 9) for course in COURSES[sem]
    )


# save summary to a file
@tool
def save_report(filename: str, content: str) -> str:
    """This function will save a summary and return a confirmation upon user request.The user will
    explicitly provide the filename and the content to be saved in the file."""
    if not filename.endswith(".txt"):
        filename += ".txt"
    if not content:
        return "Error:Content cannot be empty."
    with open(filename, "w") as file:
        file.write(content)
    return f"Report saved to {filename}"
