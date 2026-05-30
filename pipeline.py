"""
Lead Pipeline Module
Orchestrates the entire lead generation process
"""

import asyncio
import logging
from typing import List, Callable, Optional
from dataclasses import dataclass, field
from concurrent.futures import ThreadPoolExecutor, as_completed
from config import config
from serp_collector import SERPCollector, BusinessURL
from web_scraper import WebScraper, ContactInfo
from ai_scorer import AIScorer, LeadScore

logger = logging.getLogger(__name__)


@dataclass
class Lead:
    """Complete lead data structure"""
    business_name: str
    website_url: str
    niche: str
    city: str
    email: str = ""
    phone: str = ""
    whatsapp: str = ""
    has_chatbot: bool = False
    problem_detected: str = ""
    suggested_service: str = ""
    pitch_message: str = ""
    lead_score: int = 0
    score_category: str = "Low"
    technologies: List[str] = field(default_factory=list)
    services: List[str] = field(default_factory=list)


class LeadPipeline:
    """Orchestrates the lead generation pipeline"""
    
    def __init__(self, config_obj=None):
        """Initialize pipeline with all components"""
        self.config = config_obj or config
        
        # Initialize components
        self.serp_collector = SERPCollector()
        self.web_scraper = WebScraper()
        self.ai_scorer = AIScorer()
        
        self.max_concurrent = self.config.get_max_concurrent()
        
        logger.info("Lead pipeline initialized")
    
    def run(self, niche: str, city: str, service: str, count: int, 
            progress_callback: Optional[Callable] = None) -> List[Lead]:
        """
        Run the complete lead generation pipeline
        
        Args:
            niche: Business niche (Real Estate, Schools, etc.)
            city: Target city
            service: Service to offer (AI Chatbot, etc.)
            count: Number of leads to generate
            progress_callback: Optional callback for progress updates
        
        Returns:
            List of Lead objects
        """
        logger.info(f"Starting pipeline: {niche} in {city}, target: {count} leads")
        
        try:
            # Phase 1: Search for business URLs
            self._update_progress(progress_callback, "Searching for businesses...", 10)
            business_urls = self._search_phase(niche, city, service, count)
            logger.info(f"Found {len(business_urls)} business URLs")
            
            if not business_urls:
                logger.warning("No business URLs found")
                return []
            
            # Phase 2: Extract contact information
            self._update_progress(progress_callback, "Extracting contact information...", 30)
            contact_infos = self._extraction_phase(business_urls, progress_callback)
            logger.info(f"Extracted contact info from {len(contact_infos)} websites")
            
            if not contact_infos:
                logger.warning("No contact information extracted")
                return []
            
            # Phase 3: AI analysis and scoring
            self._update_progress(progress_callback, "Analyzing leads with AI...", 60)
            leads = self._analysis_phase(contact_infos, niche, city, service, progress_callback)
            logger.info(f"Analyzed {len(leads)} leads")
            
            # Phase 4: Sort and finalize
            self._update_progress(progress_callback, "Finalizing results...", 90)
            leads = self._finalize_leads(leads)
            
            self._update_progress(progress_callback, f"Complete! Found {len(leads)} leads", 100)
            logger.info(f"Pipeline complete: {len(leads)} leads generated")
            
            return leads
            
        except Exception as e:
            logger.error(f"Pipeline error: {e}")
            raise
    
    def _search_phase(self, niche: str, city: str, service: str, count: int) -> List[BusinessURL]:
        """Phase 1: Search for business URLs"""
        try:
            # Generate search queries
            queries = self.serp_collector.generate_queries(niche, city, service)
            
            # Collect URLs
            business_urls = self.serp_collector.collect_urls(queries, count)
            
            return business_urls
            
        except Exception as e:
            logger.error(f"Search phase error: {e}")
            return []
    
    def _extraction_phase(self, business_urls: List[BusinessURL], 
                         progress_callback: Optional[Callable] = None) -> List[ContactInfo]:
        """Phase 2: Extract contact information (concurrent)"""
        contact_infos = []
        total = len(business_urls)
        
        # Process URLs concurrently
        with ThreadPoolExecutor(max_workers=self.max_concurrent) as executor:
            # Submit all tasks
            future_to_url = {
                executor.submit(self._extract_single_url, url): url 
                for url in business_urls
            }
            
            # Process completed tasks
            for i, future in enumerate(as_completed(future_to_url), 1):
                url = future_to_url[future]
                
                try:
                    contact_info = future.result()
                    if contact_info:
                        contact_infos.append(contact_info)
                    
                    # Update progress
                    progress = 30 + int((i / total) * 30)  # 30-60%
                    self._update_progress(progress_callback, 
                                        f"Extracted {i}/{total} websites...", 
                                        progress)
                    
                except Exception as e:
                    logger.error(f"Error extracting {url.url}: {e}")
                    continue
        
        return contact_infos
    
    def _extract_single_url(self, business_url: BusinessURL) -> Optional[ContactInfo]:
        """Extract contact info from single URL"""
        try:
            # Fetch HTML
            html = self.web_scraper.fetch_url(business_url.url)
            
            # Extract contact info
            contact_info = self.web_scraper.extract_contact_info(html, business_url.url)
            
            # Merge SERP data
            if not contact_info.business_name or contact_info.business_name == business_url.url:
                contact_info.business_name = business_url.business_name
            
            if business_url.phone and not contact_info.phones:
                contact_info.phones = [business_url.phone]
            
            return contact_info
            
        except Exception as e:
            logger.error(f"Failed to extract {business_url.url}: {e}")
            return None
    
    def _analysis_phase(self, contact_infos: List[ContactInfo], niche: str, 
                       city: str, service: str, 
                       progress_callback: Optional[Callable] = None) -> List[Lead]:
        """Phase 3: AI analysis and scoring"""
        leads = []
        total = len(contact_infos)
        
        for i, contact_info in enumerate(contact_infos, 1):
            try:
                # Score lead with AI
                lead_score = self.ai_scorer.score_lead(contact_info, niche, service)
                
                # Create Lead object
                lead = self._create_lead(contact_info, lead_score, niche, city)
                leads.append(lead)
                
                # Update progress
                progress = 60 + int((i / total) * 30)  # 60-90%
                self._update_progress(progress_callback, 
                                    f"Analyzed {i}/{total} leads...", 
                                    progress)
                
            except Exception as e:
                logger.error(f"Error analyzing {contact_info.url}: {e}")
                # Create lead with default score
                lead = self._create_lead_without_score(contact_info, niche, city, service)
                leads.append(lead)
        
        return leads
    
    def _create_lead(self, contact_info: ContactInfo, lead_score: LeadScore, 
                    niche: str, city: str) -> Lead:
        """Create Lead object from contact info and score"""
        return Lead(
            business_name=contact_info.business_name,
            website_url=contact_info.url,
            niche=niche,
            city=city,
            email=contact_info.emails[0] if contact_info.emails else "",
            phone=contact_info.phones[0] if contact_info.phones else "",
            whatsapp=contact_info.whatsapp or "",
            has_chatbot=contact_info.has_chatbot,
            problem_detected=lead_score.problem_detected,
            suggested_service=lead_score.suggested_service,
            pitch_message=lead_score.pitch_urdu,  # Default to Urdu
            lead_score=lead_score.score,
            score_category=lead_score.category,
            technologies=contact_info.technologies,
            services=contact_info.services
        )
    
    def _create_lead_without_score(self, contact_info: ContactInfo, 
                                   niche: str, city: str, service: str) -> Lead:
        """Create Lead with default values when scoring fails"""
        return Lead(
            business_name=contact_info.business_name,
            website_url=contact_info.url,
            niche=niche,
            city=city,
            email=contact_info.emails[0] if contact_info.emails else "",
            phone=contact_info.phones[0] if contact_info.phones else "",
            whatsapp=contact_info.whatsapp or "",
            has_chatbot=contact_info.has_chatbot,
            problem_detected="Analysis incomplete",
            suggested_service=service,
            pitch_message="Contact for AI services",
            lead_score=0,
            score_category="Low",
            technologies=contact_info.technologies,
            services=contact_info.services
        )
    
    def _finalize_leads(self, leads: List[Lead]) -> List[Lead]:
        """Sort and finalize leads"""
        # Sort by score (highest first)
        leads.sort(key=lambda x: x.lead_score, reverse=True)
        return leads
    
    def _update_progress(self, callback: Optional[Callable], message: str, percent: int):
        """Update progress via callback"""
        if callback:
            try:
                callback(message, percent)
            except Exception as e:
                logger.error(f"Progress callback error: {e}")


# Example usage
if __name__ == "__main__":
    def progress_callback(message, percent):
        print(f"[{percent}%] {message}")
    
    pipeline = LeadPipeline()
    leads = pipeline.run(
        niche="Real Estate",
        city="Islamabad",
        service="AI Chatbot",
        count=10,
        progress_callback=progress_callback
    )
    
    print(f"\nGenerated {len(leads)} leads:")
    for lead in leads[:5]:
        print(f"- {lead.business_name}: {lead.lead_score}/100 ({lead.score_category})")
