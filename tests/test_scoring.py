from services.scoring import calculate_result, validate_paper

def test_result():
    r=calculate_result("1","Test","Math",80,100,"Standard (A+ ≥90, A ≥80, B ≥70, C ≥60, D ≥50)")
    assert r["percentage"] == 80
    assert r["grade"] == "A"

def test_validate_attempt():
    p={"questions":[{"type":"MCQ","question":"x","options":["a"],"marks":2}],
       "sections":[{"name":"A","attempt":2,"count":1}],"total_marks":2}
    assert len(validate_paper(p)) >= 2
