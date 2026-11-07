def calculate_result(roll, student, subject, obtained, total, scale):
    pct = (obtained/total*100) if total else 0
    if scale.startswith("Pass"):
        grade = "Pass" if pct >= 50 else "Fail"
    elif pct >= 90: grade="A+"
    elif pct >= 80: grade="A"
    elif pct >= 70: grade="B"
    elif pct >= 60: grade="C"
    elif pct >= 50: grade="D"
    else: grade="F"
    return {"roll_no":roll,"student":student,"subject":subject,"obtained":obtained,"total":total,
            "percentage":round(pct,2),"grade":grade,"status":"Pass" if pct>=50 else "Fail"}

def validate_paper(paper):
    issues=[]
    qs=paper.get("questions",[])
    if not qs: issues.append("No questions were generated.")
    for q in qs:
        if q.get("type")=="MCQ" and len(q.get("options",[]))<2:
            issues.append(f"MCQ has fewer than two options: {q.get('question','')[:50]}")
    for s in paper.get("sections",[]):
        if s["attempt"]>s["count"]: issues.append(f"{s['name']}: attempted count exceeds generated count.")
    total=sum(float(q.get("marks",0) or 0) for q in qs)
    if total and abs(total-float(paper.get("total_marks",total)))>0.01:
        issues.append(f"Sum of all generated question marks ({total:g}) differs from configured total marks ({paper.get('total_marks')}). Check optional-question and attempt rules.")
    return list(dict.fromkeys(issues))
