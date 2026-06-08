from app import create_app
app = create_app()
print("Flask app created successfully!")
print("Testing skill extractor...")
from app.core.skill_extractor import SkillExtractor
se = SkillExtractor()
skills = se.extract_skills("I know Python, React, machine learning, and SQL")
print(f"  Extracted {len(skills)} skills: {[s['name'] for s in skills]}")

print("Testing section detector...")
from app.core.section_detector import SectionDetector
text = "Experience\nBuilt a web app\nSkills\nPython, SQL\nEducation\nBS Computer Science"
sections = SectionDetector.detect_sections(text)
print(f"  Detected sections: {list(sections.keys())}")

print("Testing quality analyzer...")
from app.core.quality_analyzer import QualityAnalyzer
qa = QualityAnalyzer()
quality = qa.analyze(text, sections)
print(f"  Quality score: {quality['score']}")

print("\nAll modules initialized successfully!")
