"""
Sanctions Compliance Agent
Simple offline checking using hardcoded sanctions database
No API calls required - fast and reliable!
"""

import os
from datetime import datetime
from typing import Dict, Optional
from dotenv import load_dotenv
from app.utils.sanctions_data import (
    check_country_sanctions,
    check_port_sanctions,
    is_dual_use_product,
    normalize_country_name
)

load_dotenv()


class SanctionsAgent:
    def __init__(self):
        """Initialize Sanctions Checking Agent with offline sanctions database"""
        # Offline sanctions checking - no API required!
        # Simple, fast, reliable
        pass

    async def check_lc_compliance(self, lc_data: dict) -> dict:
        """
        Check LC transaction against sanctions using offline database

        Simple, fast, reliable - no API calls required!

        Args:
            lc_data: Extracted LC data from OCR agent

        Returns:
            {
                "compliant": bool,
                "risk_level": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
                "blocked": bool,
                "reason": str,
                "details": str,
                "sources": list[str],
                "checked_at": str
            }
        """

        # Extract relevant fields
        beneficiary_country = lc_data.get('exporter_info', {}).get('beneficiary_country')
        issuing_country = lc_data.get('lc_details', {}).get('issuing_bank_country')
        port_loading = lc_data.get('shipment_details', {}).get('port_of_loading')
        port_destination = lc_data.get('shipment_details', {}).get('port_of_destination')
        product = lc_data.get('shipment_details', {}).get('product_description')
        amount = lc_data.get('amount_and_payment', {}).get('amount_usd')

        # Check sanctions using offline database
        result = {
            "compliant": True,
            "risk_level": "LOW",
            "blocked": False,
            "reason": "",
            "details": "",
            "sources": [],
            "recommendations": "",
            "checked_at": datetime.now().isoformat(),
            "lc_reference": {
                'amount': amount,
                'countries': [beneficiary_country, issuing_country],
                'ports': [port_loading, port_destination],
                'product': product
            },
            "check_method": "offline_database"
        }

        issues = []

        # Check beneficiary country
        if beneficiary_country:
            country_sanctions = check_country_sanctions(beneficiary_country)
            if country_sanctions:
                issues.append(f"Beneficiary country ({country_sanctions['name']}) is under {country_sanctions['status']}")
                result['risk_level'] = country_sanctions['risk_level']
                result['blocked'] = country_sanctions['blocked']
                result['compliant'] = False
                result['sources'].extend(country_sanctions['sources'])
                result['details'] += f"\n\n**{country_sanctions['name']} Sanctions:**\n{country_sanctions['details']}"

        # Check issuing country
        if issuing_country:
            issuing_sanctions = check_country_sanctions(issuing_country)
            if issuing_sanctions:
                issues.append(f"Issuing bank country ({issuing_sanctions['name']}) is under {issuing_sanctions['status']}")
                if issuing_sanctions['risk_level'] == "CRITICAL":
                    result['risk_level'] = "CRITICAL"
                elif result['risk_level'] != "CRITICAL":
                    result['risk_level'] = issuing_sanctions['risk_level']
                result['compliant'] = False
                result['sources'].extend(issuing_sanctions['sources'])

        # Check port of destination
        if port_destination:
            port_sanctions = check_port_sanctions(port_destination)
            if port_sanctions:
                issues.append(f"Port of destination ({port_destination}) is in high-risk area: {port_sanctions['reason']}")
                if port_sanctions['risk'] == "CRITICAL":
                    result['risk_level'] = "CRITICAL"
                    result['blocked'] = True
                result['compliant'] = False

        # Check port of loading
        if port_loading:
            loading_sanctions = check_port_sanctions(port_loading)
            if loading_sanctions:
                issues.append(f"Port of loading ({port_loading}) is in high-risk area: {loading_sanctions['reason']}")
                if result['risk_level'] != "CRITICAL":
                    result['risk_level'] = "HIGH"

        # Check for dual-use products
        if product and is_dual_use_product(product):
            issues.append(f"Product ({product}) may be dual-use goods requiring export controls")
            if result['risk_level'] == "LOW":
                result['risk_level'] = "MEDIUM"
            result['details'] += f"\n\n**Dual-Use Product Alert:**\nProduct description contains keywords suggesting potential dual-use (civilian + military) applications. Export licenses may be required. Verify Commerce Control List (CCL) classification."

        # Build final response
        if issues:
            result['reason'] = "; ".join(issues)
            if result['blocked']:
                result['recommendations'] = "Transaction CANNOT proceed. Contact compliance team."
            elif result['risk_level'] == "HIGH":
                result['recommendations'] = "Manual compliance review required before proceeding."
            else:
                result['recommendations'] = "Proceed with caution. Verify export control requirements."
        else:
            result['reason'] = "No sanctions detected. Transaction appears compliant."
            result['recommendations'] = "Transaction can proceed. Standard due diligence recommended."
            result['details'] = f"Checked against offline sanctions database (updated Nov 2025). No matches found for {beneficiary_country or 'specified country'}."

        return result

    async def quick_country_check(self, country: str) -> dict:
        """
        Quick check if a specific country is sanctioned

        Args:
            country: Country name to check

        Returns:
            Sanctions check result for the country
        """
        lc_data = {
            "exporter_info": {"beneficiary_country": country},
            "shipment_details": {},
            "lc_details": {},
            "amount_and_payment": {},
            "importer_info": {}
        }

        return await self.check_lc_compliance(lc_data)

    async def quick_port_check(self, port: str, country: Optional[str] = None) -> dict:
        """
        Quick check if a specific port is sanctioned

        Args:
            port: Port name to check
            country: Optional country where port is located

        Returns:
            Sanctions check result for the port
        """
        lc_data = {
            "exporter_info": {"beneficiary_country": country} if country else {},
            "shipment_details": {"port_of_destination": port},
            "lc_details": {},
            "amount_and_payment": {},
            "importer_info": {}
        }

        return await self.check_lc_compliance(lc_data)
