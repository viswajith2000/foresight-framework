from typing import Dict, Any, List
from main import DRIForesightProcessor
import json

class PolicyStressTestProcessor:
    def __init__(self, processor: DRIForesightProcessor):
        self.processor = processor
        
    def run_comprehensive_analysis(self, domain: str, project_name: str, document_text: str) -> Dict[str, Any]:
        """
        Run complete stress test analysis combining all phases.
        Returns comprehensive results for display in single view.
        """
        results = {
            "project_name": project_name,
            "domain": domain,
            "framing_results": {},
            "scanning_results": {},
            "futuring_results": {},
            "processing_status": "starting"
        }
        
        try:
            # Phase 1: Framing Analysis
            results["processing_status"] = "framing"
            framing_data = self._run_framing_phase(domain, project_name, document_text)
            results["framing_results"] = framing_data
            
            # Phase 2: Scanning Analysis  
            results["processing_status"] = "scanning"
            scanning_data = self._run_scanning_phase(domain, document_text)
            results["scanning_results"] = scanning_data
            
            # Phase 3: Futuring Analysis
            results["processing_status"] = "futuring"
            futuring_data = self._run_futuring_phase(domain, scanning_data, document_text)
            results["futuring_results"] = futuring_data
            
            results["processing_status"] = "completed"
            return results
            
        except Exception as e:
            results["processing_status"] = "error"
            results["error"] = str(e)
            return results
    
    # def _run_framing_phase(self, domain: str, project_name: str, document_text: str) -> Dict[str, Any]:
    #     """Execute framing phase analysis."""
    #     # Domain Map Generation
    #     domain_map = self.processor.generate_domain_map(domain, document_text, project_name)
        
    #     # Format domain map for display
    #     central_domain = domain_map.get('central_domain', domain)
    #     sub_domains = domain_map.get('sub_domains', [])
        
    #     return {
    #         "domain_map": {
    #             "central_domain": central_domain,
    #             "sub_domains": [
    #                 {
    #                     "name": sd.get('name', ''),
    #                     "description": sd.get('description', ''),
    #                     "issue_areas": sd.get('issue_areas', [])
    #                 } for sd in sub_domains
    #             ]
    #         },
    #         "description": domain_map.get('description', ''),
    #         "success": True
    #     }
    
    def _run_framing_phase(self, domain: str, project_name: str, document_text: str) -> Dict[str, Any]:
        """Execute framing phase analysis."""
        
        # Check if we have substantial document content
        has_substantial_content = document_text and len(document_text.strip()) > 200
        
        if has_substantial_content:
            # Use document-first approach - pass the actual document text
            domain_map = self.processor.generate_domain_map(domain, document_text, project_name)
        else:
            # Use domain-based approach with empty string to trigger domain-based generation
            domain_map = self.processor.generate_domain_map(domain, "", project_name)
        
        # Format domain map for display
        central_domain = domain_map.get('central_domain', domain)
        sub_domains = domain_map.get('sub_domains', [])
        
        return {
            "domain_map": {
                "central_domain": central_domain,
                "sub_domains": [
                    {
                        "name": sd.get('name', ''),
                        "description": sd.get('description', ''),
                        "relevance": sd.get('relevance', 'Medium'),
                        "issue_areas": sd.get('issue_areas', [])
                    } for sd in sub_domains
                ]
            },
            "description": domain_map.get('description', ''),
            "document_analyzed": has_substantial_content,
            "success": True
        }
    
    def _run_scanning_phase(self, domain: str, document_text: str) -> Dict[str, Any]:
        """Execute scanning phase analysis."""
        # Generate Signals
        signals_data = self.processor.generate_signals(domain, document_text)
        
        # Generate STEEPV Analysis
        steepv_data = self.processor.generate_steepv_analysis(domain, signals_data, document_text)
        
        # Generate Futures Triangle
        futures_triangle = self.processor.generate_futures_triangle(domain, signals_data, steepv_data, document_text)
        
        return {
            "signals": {
                "strong_signals": signals_data.get('strong_signals', []),
                "weak_signals": signals_data.get('weak_signals', [])
            },
            "steepv_analysis": steepv_data,
            "futures_triangle": futures_triangle,
            "success": True
        }
    
    def _run_futuring_phase(self, domain: str, scanning_data: Dict, document_text: str) -> Dict[str, Any]:
        """Execute futuring phase analysis."""
        # Phase data preparation
        phase1_data = {"project_name": domain, "final_domain": domain}
        phase2_data = {
            "signals_data": scanning_data.get("signals", {}),
            "steepv_data": scanning_data.get("steepv_analysis", {}),
            "futures_triangle_data": scanning_data.get("futures_triangle", {})
        }
        
        # Generate Futures Triangle 2.0
        triangle_2_0 = self.processor.generate_futures_triangle_2_0(domain, phase1_data, phase2_data, document_text)
        
        # Generate Baseline Scenario
        baseline_scenario = self.processor.generate_baseline_scenario(domain, triangle_2_0, phase1_data)
        
        # Generate Driver Outcomes
        driver_outcomes = self.processor.generate_driver_outcomes(domain, triangle_2_0, baseline_scenario, phase1_data)
        
        # Generate Alternative Scenarios (1 of each type)
        alternative_scenarios = self.processor.generate_alternative_scenarios(
            domain, 
            {"Collapse": 1, "New Equilibrium": 1, "Transformation": 1},
            baseline_scenario,
            driver_outcomes,
            triangle_2_0
        )
        
        return {
            "futures_triangle_2_0": triangle_2_0,
            "baseline_scenario": baseline_scenario,
            "driver_outcomes": driver_outcomes,
            "alternative_scenarios": alternative_scenarios,
            "success": True
        }

def create_stress_test_processor() -> PolicyStressTestProcessor:
    """Factory function to create stress test processor."""
    from main import initialize_processor
    base_processor = initialize_processor()
    return PolicyStressTestProcessor(base_processor)