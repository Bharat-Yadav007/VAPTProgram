# utils/report.py
from datetime import datetime
import json

class Finding:
    def __init__(self, title, description, severity="INFO", recommendations=None):
        self.title = title
        self.description = description
        self.severity = severity.upper()
        self.recommendations = recommendations or []
        self.timestamp = datetime.now()

    def to_dict(self):
        return {
            "title": self.title,
            "description": self.description,
            "severity": self.severity,
            "recommendations": self.recommendations,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }

def severity_to_color(severity):
    colors = {
        "CRITICAL": "#FF0000",
        "HIGH": "#FF4500",
        "MEDIUM": "#FFA500",
        "LOW": "#FFD700",
        "INFO": "#00FF00"
    }
    return colors.get(severity.upper(), "#808080")

def generate_html_report(results, filename="output/report.html"):
    print(f"\n[+] Generating report to {filename}...")
    
    import os
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"""<!DOCTYPE html>
<html>
<head>
    <title>VAPT Scan Report</title>
    <style>
        body {{ 
            font-family: Arial, sans-serif;
            background: #f9f9f9;
            padding: 20px;
            line-height: 1.6;
        }}
        h1 {{ 
            color: #2c3e50;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }}
        .section {{ 
            margin-bottom: 30px;
            padding: 20px;
            background: #fff;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .finding {{
            margin: 10px 0;
            padding: 15px;
            border-left: 5px solid #3498db;
            background: #f8f9fa;
        }}
        .severity {{
            display: inline-block;
            padding: 5px 10px;
            border-radius: 3px;
            color: white;
            font-weight: bold;
            margin: 5px 0;
        }}
        .timestamp {{
            color: #666;
            font-size: 0.9em;
        }}
        .recommendations {{
            margin-top: 10px;
            padding: 10px;
            background: #e8f4f8;
            border-radius: 3px;
        }}
        pre {{ 
            background: #f8f9fa;
            padding: 15px;
            border-radius: 3px;
            overflow-x: auto;
        }}
    </style>
</head>
<body>
    <h1>VAPT Scan Report</h1>
    <div class="section">
        <h2>Executive Summary</h2>
        <p>Scan completed on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    </div>
""")

        for section_title, content in results.items():
            f.write(f'<div class="section">\n<h2>{section_title}</h2>\n')
            
            if isinstance(content, list) and all(isinstance(item, Finding) for item in content):
                for finding in content:
                    f.write(f"""
                    <div class="finding">
                        <h3>{finding.title}</h3>
                        <div class="severity" style="background-color: {severity_to_color(finding.severity)}">
                            {finding.severity}
                        </div>
                        <div class="timestamp">{finding.timestamp.strftime("%Y-%m-%d %H:%M:%S")}</div>
                        <pre>{finding.description}</pre>
                        """)
                    if finding.recommendations:
                        f.write("""
                        <div class="recommendations">
                            <h4>Recommendations:</h4>
                            <ul>
                        """)
                        for rec in finding.recommendations:
                            f.write(f"<li>{rec}</li>")
                        f.write("</ul></div>")
                    f.write("</div>")
            else:
                f.write(f'<pre>{content}</pre>')
            
            f.write('</div>\n')

        f.write("</body></html>")
    
    print("[✓] Report generated successfully")