"""
CSV Exporter Module
Exports leads to CSV format
"""

import pandas as pd
import logging
from typing import List
from datetime import datetime
from pipeline import Lead

logger = logging.getLogger(__name__)


class CSVExporter:
    """Exports leads to CSV file"""
    
    def export_to_csv(self, leads: List[Lead], filename: str = None) -> str:
        """
        Export leads to CSV file
        
        Args:
            leads: List of Lead objects
            filename: Output filename (optional, auto-generated if not provided)
        
        Returns:
            Path to created CSV file
        """
        if not leads:
            logger.warning("No leads to export")
            return ""
        
        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"leads_{timestamp}.csv"
        
        # Ensure .csv extension
        if not filename.endswith('.csv'):
            filename += '.csv'
        
        logger.info(f"Exporting {len(leads)} leads to {filename}")
        
        try:
            # Convert to DataFrame
            df = self._format_data(leads)
            
            # Validate
            if not self._validate_csv(df):
                raise ValueError("CSV validation failed")
            
            # Export to CSV
            df.to_csv(filename, index=False, encoding='utf-8')
            
            logger.info(f"Successfully exported to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error exporting CSV: {e}")
            raise
    
    def _format_data(self, leads: List[Lead]) -> pd.DataFrame:
        """Convert Lead objects to DataFrame"""
        data = []
        
        for lead in leads:
            row = {
                'business_name': self._clean_for_csv(lead.business_name),
                'website_url': self._clean_for_csv(lead.website_url),
                'niche': self._clean_for_csv(lead.niche),
                'city': self._clean_for_csv(lead.city),
                'email': self._clean_for_csv(lead.email),
                'phone': self._clean_for_csv(lead.phone),
                'whatsapp': self._clean_for_csv(lead.whatsapp),
                'has_chatbot': lead.has_chatbot,
                'problem_detected': self._clean_for_csv(lead.problem_detected),
                'suggested_service': self._clean_for_csv(lead.suggested_service),
                'pitch_message': self._clean_for_csv(lead.pitch_message),
                'lead_score': lead.lead_score,
                'score_category': lead.score_category,
                'technologies': self._clean_for_csv(', '.join(lead.technologies)),
                'services': self._clean_for_csv(', '.join(lead.services[:5]))  # Limit to 5
            }
            data.append(row)
        
        df = pd.DataFrame(data)
        return df
    
    def _clean_for_csv(self, value: any) -> str:
        """Clean value for CSV export"""
        if value is None:
            return ""
        
        # Convert to string
        value = str(value)
        
        # Remove problematic characters
        value = value.replace('\n', ' ').replace('\r', ' ')
        
        # Normalize whitespace
        value = ' '.join(value.split())
        
        return value.strip()
    
    def _validate_csv(self, df: pd.DataFrame) -> bool:
        """Validate CSV data"""
        required_columns = [
            'business_name', 'website_url', 'niche', 'city',
            'email', 'phone', 'lead_score', 'score_category'
        ]
        
        # Check required columns exist
        for col in required_columns:
            if col not in df.columns:
                logger.error(f"Missing required column: {col}")
                return False
        
        # Check not empty
        if len(df) == 0:
            logger.error("DataFrame is empty")
            return False
        
        return True
    
    def get_summary_stats(self, leads: List[Lead]) -> dict:
        """Get summary statistics for leads"""
        if not leads:
            return {}
        
        total = len(leads)
        high_score = sum(1 for lead in leads if lead.score_category == 'High')
        medium_score = sum(1 for lead in leads if lead.score_category == 'Medium')
        low_score = sum(1 for lead in leads if lead.score_category == 'Low')
        
        avg_score = sum(lead.lead_score for lead in leads) / total
        
        with_email = sum(1 for lead in leads if lead.email)
        with_phone = sum(1 for lead in leads if lead.phone)
        with_whatsapp = sum(1 for lead in leads if lead.whatsapp)
        with_chatbot = sum(1 for lead in leads if lead.has_chatbot)
        
        return {
            'total_leads': total,
            'high_score_leads': high_score,
            'medium_score_leads': medium_score,
            'low_score_leads': low_score,
            'average_score': round(avg_score, 1),
            'leads_with_email': with_email,
            'leads_with_phone': with_phone,
            'leads_with_whatsapp': with_whatsapp,
            'leads_with_chatbot': with_chatbot
        }


# Example usage
if __name__ == "__main__":
    from pipeline import Lead
    
    # Sample leads
    sample_leads = [
        Lead(
            business_name="ABC Real Estate",
            website_url="https://abc.pk",
            niche="Real Estate",
            city="Islamabad",
            email="info@abc.pk",
            phone="+92-51-1234567",
            whatsapp="+923001234567",
            has_chatbot=False,
            problem_detected="No chatbot for customer queries",
            suggested_service="AI Customer Support Chatbot",
            pitch_message="Assalamualaikum! Aapki website ke liye chatbot...",
            lead_score=87,
            score_category="High",
            technologies=["WordPress"],
            services=["Property Listings", "Sales"]
        )
    ]
    
    exporter = CSVExporter()
    filename = exporter.export_to_csv(sample_leads, "test_leads.csv")
    print(f"Exported to: {filename}")
    
    stats = exporter.get_summary_stats(sample_leads)
    print(f"Stats: {stats}")
