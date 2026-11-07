def calculate_result(roll, student, subject, obtained, total, grade_scale):
    pct = (obtained / total) * 100 if total > 0 else 0
    if "Pass" in grade_scale:
        grade = "Pass" if pct >= 50 else "Fail"
    else:
        if pct >= 90: grade = "A+"
        elif pct >= 80: grade = "A"
        elif pct >= 70: grade = "B"
        elif pct >= 60: grade = "C"
        elif pct >= 50: grade = "D"
        else: grade = "F"
    return {
        "roll": roll,
        "student": student,
        "subject": subject,
        "obtained": obtained,
        "total": total,
        "percentage": pct,
        "grade": grade
    }

def validate_paper(paper):
    issues = []
    total_q_marks = sum(q.get("marks", 0) for q in paper.get("questions", []))
    if abs(total_q_marks - paper.get("total_marks", 0)) > 1.0:
        issues.append(f"Sum of question marks ({total_q_marks}) differs from configured total paper marks ({paper.get('total_marks')}).")
    return issues
