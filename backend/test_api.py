import requests
url = "http://localhost:5000/api/analyze/improve"
files = {'resume': open('C:\\Users\\sachi\\AAT\\test_resume_v2.pdf', 'rb')}
data = {'jd_text': 'React Developer Needed', 'parent_id': '5ee77fcd-bc1f-47bc-aa37-857b8d8dbde2'}
res = requests.post(url, files=files, data=data)
if res.status_code == 200:
    print("Success:", res.json().get('analysis_id') or "No ID returned")
else:
    print("Error:", res.status_code, res.text)
