from typing import Dict, Any
import json
from datetime import datetime
import os

class ReportGenerator:
    def __init__(self, output_dir: str = "reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def generate_report(self, analysis_results: Dict[str, Any], 
                       repository_name: str,
                       format: str = "json") -> str:
        """Generate a comprehensive report from analysis results."""
        # Generate report filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"{repository_name}_{timestamp}_report"
        
        if format.lower() == "markdown":
            # Generate markdown report
            md_content = self._generate_markdown_report(analysis_results)
            filename = f"{self.output_dir}/{base_filename}.md"
            with open(filename, 'w') as f:
                f.write(md_content)
        else:
            # Generate JSON report
            filename = f"{self.output_dir}/{base_filename}.json"
            with open(filename, 'w') as f:
                json.dump(analysis_results, f, indent=2)
            
        return filename

    def _generate_markdown_report(self, report_data: dict) -> str:
        """Generate a markdown formatted report."""
        md = []
        
        # Header
        md.append(f"# Technical Challenges Analysis: {report_data['repository']}")
        md.append(f"\nGenerated at: {report_data['generated_at']}")
        
        # Analysis Period
        if report_data['analysis_period']['start'] or report_data['analysis_period']['end']:
            md.append("\n## Analysis Period")
            period = []
            if report_data['analysis_period']['start']:
                period.append(f"From: {report_data['analysis_period']['start']}")
            if report_data['analysis_period']['end']:
                period.append(f"To: {report_data['analysis_period']['end']}")
            md.append("\n".join(period))
        
        # Technical Context (First)
        if 'llm_analysis' in report_data and report_data['llm_analysis'].get('technical_context'):
            md.append("\n## Technical Context")
            md.append(report_data['llm_analysis']['technical_context'])
        
        # Technical Challenges (Second)
        if 'llm_analysis' in report_data and report_data['llm_analysis'].get('technical_challenges'):
            md.append("\n## Technical Challenges")
            md.append(report_data['llm_analysis']['technical_challenges'])
        
        # Implementation Details (Third)
        if 'llm_analysis' in report_data and report_data['llm_analysis'].get('implementation_details'):
            md.append("\n## Implementation Details")
            md.append(report_data['llm_analysis']['implementation_details'])
        
        # Repository Statistics (Last)
        md.append("\n## Repository Statistics")
        md.append(f"- Total Commits: {report_data['total_commits']}")
        md.append(f"- Total Authors: {report_data['total_authors']}")
        md.append(f"- Total Files Changed: {report_data['total_files_changed']}")
        md.append(f"- Total Insertions: {report_data['total_insertions']}")
        md.append(f"- Total Deletions: {report_data['total_deletions']}")
        
        return "\n".join(md) 