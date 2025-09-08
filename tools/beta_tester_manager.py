#!/usr/bin/env python3
"""
OpenAGI Beta Tester Application Management Tool

This script helps manage the beta testing application process,
including application review, tester onboarding, and tracking.
"""

import json
import csv
import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class BetaTesterApplication:
    """Beta tester application data structure."""
    
    # Personal Information
    name: str
    email: str
    
    # Professional Background
    job_title: str
    company: str
    years_experience: int
    primary_expertise: List[str]
    
    # Technical Experience
    ai_ml_experience: str
    programming_languages: List[str]
    frameworks_used: List[str]
    previous_testing_experience: str
    
    # Availability and Commitment
    hours_per_week: int
    preferred_testing_areas: List[str]
    communication_preference: str
    timezone: str
    
    # Motivation and Goals
    motivation: str
    specific_interests: str
    expected_outcomes: str
    
    # Application Metadata
    application_date: str
    
    # Optional fields with defaults
    github_username: Optional[str] = None
    linkedin_profile: Optional[str] = None
    status: str = "pending"  # pending, approved, rejected, waitlist
    reviewer_notes: str = ""
    onboarding_completed: bool = False
    
    def __post_init__(self):
        """Set application date if not provided."""
        if not self.application_date:
            self.application_date = datetime.datetime.now().isoformat()


class BetaTesterManager:
    """Manages beta tester applications and onboarding."""
    
    def __init__(self, data_dir: str = "beta_testing_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.applications_file = self.data_dir / "applications.json"
        self.testers_file = self.data_dir / "active_testers.json"
        self.feedback_file = self.data_dir / "feedback_tracking.json"
        
        self.applications = self._load_applications()
        self.active_testers = self._load_active_testers()
        self.feedback_tracking = self._load_feedback_tracking()
    
    def _load_applications(self) -> List[BetaTesterApplication]:
        """Load applications from JSON file."""
        if self.applications_file.exists():
            with open(self.applications_file, 'r') as f:
                data = json.load(f)
                return [BetaTesterApplication(**app) for app in data]
        return []
    
    def _load_active_testers(self) -> List[Dict]:
        """Load active testers data."""
        if self.testers_file.exists():
            with open(self.testers_file, 'r') as f:
                return json.load(f)
        return []
    
    def _load_feedback_tracking(self) -> Dict:
        """Load feedback tracking data."""
        if self.feedback_file.exists():
            with open(self.feedback_file, 'r') as f:
                return json.load(f)
        return {"bug_reports": [], "feature_feedback": [], "usability_reports": []}
    
    def save_data(self):
        """Save all data to files."""
        # Save applications
        with open(self.applications_file, 'w') as f:
            json.dump([asdict(app) for app in self.applications], f, indent=2)
        
        # Save active testers
        with open(self.testers_file, 'w') as f:
            json.dump(self.active_testers, f, indent=2)
        
        # Save feedback tracking
        with open(self.feedback_file, 'w') as f:
            json.dump(self.feedback_tracking, f, indent=2)
    
    def submit_application(self, application_data: Dict) -> str:
        """Submit a new beta tester application."""
        try:
            application = BetaTesterApplication(**application_data)
            self.applications.append(application)
            self.save_data()
            return f"Application submitted successfully for {application.name}"
        except Exception as e:
            return f"Error submitting application: {str(e)}"
    
    def review_application(self, email: str, status: str, notes: str = "") -> str:
        """Review and update application status."""
        for app in self.applications:
            if app.email == email:
                app.status = status
                app.reviewer_notes = notes
                
                if status == "approved":
                    self._onboard_tester(app)
                
                self.save_data()
                return f"Application for {app.name} updated to {status}"
        
        return f"Application not found for email: {email}"
    
    def _onboard_tester(self, application: BetaTesterApplication):
        """Move approved applicant to active testers."""
        tester_data = {
            "name": application.name,
            "email": application.email,
            "github_username": application.github_username,
            "expertise": application.primary_expertise,
            "testing_areas": application.preferred_testing_areas,
            "onboarding_date": datetime.datetime.now().isoformat(),
            "contributions": {
                "bug_reports": 0,
                "feature_feedback": 0,
                "usability_reports": 0,
                "testing_sessions": 0
            },
            "status": "active",
            "recognition_level": "explorer"
        }
        self.active_testers.append(tester_data)
    
    def get_application_stats(self) -> Dict:
        """Get statistics about applications."""
        total = len(self.applications)
        if total == 0:
            return {"total": 0, "pending": 0, "approved": 0, "rejected": 0, "waitlist": 0}
        
        stats = {"total": total}
        for status in ["pending", "approved", "rejected", "waitlist"]:
            stats[status] = len([app for app in self.applications if app.status == status])
        
        return stats
    
    def get_tester_stats(self) -> Dict:
        """Get statistics about active testers."""
        total = len(self.active_testers)
        if total == 0:
            return {"total": 0, "active": 0, "total_contributions": 0}
        
        active = len([t for t in self.active_testers if t["status"] == "active"])
        total_contributions = sum(
            sum(t["contributions"].values()) for t in self.active_testers
        )
        
        return {
            "total": total,
            "active": active,
            "total_contributions": total_contributions,
            "avg_contributions": total_contributions / total if total > 0 else 0
        }
    
    def export_applications_csv(self, filename: Optional[str] = None) -> str:
        """Export applications to CSV file."""
        if not filename:
            filename = f"applications_export_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        filepath = self.data_dir / filename
        
        with open(filepath, 'w', newline='') as csvfile:
            if not self.applications:
                return f"No applications to export to {filepath}"
            
            fieldnames = list(asdict(self.applications[0]).keys())
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for app in self.applications:
                writer.writerow(asdict(app))
        
        return f"Applications exported to {filepath}"
    
    def generate_recruitment_report(self) -> str:
        """Generate a recruitment status report."""
        app_stats = self.get_application_stats()
        tester_stats = self.get_tester_stats()
        
        report = f"""
OpenAGI Beta Testing Recruitment Report
Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

APPLICATION STATISTICS:
- Total Applications: {app_stats['total']}
- Pending Review: {app_stats['pending']}
- Approved: {app_stats['approved']}
- Rejected: {app_stats['rejected']}
- Waitlisted: {app_stats['waitlist']}

ACTIVE TESTER STATISTICS:
- Total Testers: {tester_stats['total']}
- Active Testers: {tester_stats['active']}
- Total Contributions: {tester_stats['total_contributions']}
- Average Contributions per Tester: {tester_stats['avg_contributions']:.1f}

RECRUITMENT RECOMMENDATIONS:
"""
        
        # Add recommendations based on stats
        if app_stats['total'] < 20:
            report += "- PRIORITY: Increase recruitment efforts - low application volume\n"
        if app_stats['pending'] > app_stats['approved'] * 2:
            report += "- Review pending applications to maintain pipeline flow\n"
        if tester_stats['total'] < 10:
            report += "- Focus on approving qualified applicants to build core testing team\n"
        if tester_stats['avg_contributions'] < 5:
            report += "- Improve tester engagement and feedback collection processes\n"
        
        return report


def create_sample_application() -> Dict:
    """Create a sample application for testing."""
    return {
        "name": "Dr. Alice Johnson",
        "email": "alice.johnson@university.edu",
        "github_username": "alice_ai_researcher",
        "linkedin_profile": "https://linkedin.com/in/alice-johnson-ai",
        "job_title": "AI Research Scientist",
        "company": "University AI Lab",
        "years_experience": 5,
        "primary_expertise": ["Natural Language Processing", "Machine Learning", "Deep Learning"],
        "ai_ml_experience": "PhD in AI, 5 years research experience, published 15 papers on NLP and ML",
        "programming_languages": ["Python", "R", "Julia", "C++"],
        "frameworks_used": ["TensorFlow", "PyTorch", "scikit-learn", "Hugging Face", "spaCy"],
        "previous_testing_experience": "Beta tested 3 ML platforms, contributed to open source AI projects",
        "hours_per_week": 4,
        "preferred_testing_areas": ["Natural Language Processing", "Machine Learning", "API Design"],
        "communication_preference": "Discord",
        "timezone": "EST",
        "motivation": "Want to contribute to making AI more accessible and improve my research workflow",
        "specific_interests": "Interested in NLP features and integration with research pipelines",
        "expected_outcomes": "Help improve platform usability and discover features for my research",
        "application_date": ""
    }


def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="OpenAGI Beta Tester Management Tool")
    parser.add_argument("--action", choices=["stats", "export", "report", "sample"], 
                       default="stats", help="Action to perform")
    parser.add_argument("--data-dir", default="beta_testing_data", 
                       help="Directory for data storage")
    
    args = parser.parse_args()
    
    manager = BetaTesterManager(args.data_dir)
    
    if args.action == "stats":
        app_stats = manager.get_application_stats()
        tester_stats = manager.get_tester_stats()
        print("Application Stats:", app_stats)
        print("Tester Stats:", tester_stats)
    
    elif args.action == "export":
        result = manager.export_applications_csv()
        print(result)
    
    elif args.action == "report":
        report = manager.generate_recruitment_report()
        print(report)
    
    elif args.action == "sample":
        # Create sample data for demonstration
        sample_app = create_sample_application()
        result = manager.submit_application(sample_app)
        print(result)
        
        # Review the sample application
        review_result = manager.review_application(
            sample_app["email"], 
            "approved", 
            "Strong AI background, perfect fit for NLP testing"
        )
        print(review_result)
        
        print("\nGenerated sample data. Run with --action stats to see results.")


if __name__ == "__main__":
    main()