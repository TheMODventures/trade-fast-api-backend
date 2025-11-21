"""
Offline Sanctions Data
Hardcoded list of sanctioned countries and high-risk entities
Updated: November 2025
"""

from typing import Dict, List

# Comprehensive list of sanctioned countries
SANCTIONED_COUNTRIES = {
    # OFAC Comprehensive Sanctions (US Treasury)
    "iran": {
        "name": "Iran",
        "status": "COMPREHENSIVE_SANCTIONS",
        "risk_level": "CRITICAL",
        "sanctioning_authorities": ["OFAC", "UN", "EU"],
        "reason": "Comprehensive US sanctions under Executive Orders 13846, 13902",
        "blocked": True,
        "details": "Comprehensive trade embargo. Virtually all transactions prohibited.",
        "sources": [
            "https://ofac.treasury.gov/sanctions-programs-and-country-information/iran-sanctions",
            "https://www.un.org/securitycouncil/sanctions/2231"
        ]
    },
    "north korea": {
        "name": "North Korea",
        "status": "COMPREHENSIVE_SANCTIONS",
        "risk_level": "CRITICAL",
        "sanctioning_authorities": ["OFAC", "UN", "EU"],
        "reason": "Comprehensive sanctions under Executive Order 13810",
        "blocked": True,
        "details": "Complete trade embargo. All transactions prohibited.",
        "sources": [
            "https://ofac.treasury.gov/sanctions-programs-and-country-information/north-korea-sanctions"
        ]
    },
    "syria": {
        "name": "Syria",
        "status": "COMPREHENSIVE_SANCTIONS",
        "risk_level": "CRITICAL",
        "sanctioning_authorities": ["OFAC", "UN", "EU"],
        "reason": "Syria sanctions under Executive Order 13894",
        "blocked": True,
        "details": "Comprehensive sanctions due to Syrian government actions.",
        "sources": [
            "https://ofac.treasury.gov/sanctions-programs-and-country-information/syria-sanctions"
        ]
    },
    "cuba": {
        "name": "Cuba",
        "status": "COMPREHENSIVE_SANCTIONS",
        "risk_level": "CRITICAL",
        "sanctioning_authorities": ["OFAC"],
        "reason": "Cuban Assets Control Regulations",
        "blocked": True,
        "details": "US embargo on Cuba. Comprehensive trade restrictions.",
        "sources": [
            "https://ofac.treasury.gov/sanctions-programs-and-country-information/cuba-sanctions"
        ]
    },

    # Sectoral/Targeted Sanctions
    "russia": {
        "name": "Russia",
        "status": "SECTORAL_SANCTIONS",
        "risk_level": "HIGH",
        "sanctioning_authorities": ["OFAC", "EU"],
        "reason": "Sectoral sanctions related to Ukraine invasion (2022)",
        "blocked": False,
        "details": "Sectoral sanctions targeting financial, energy, and defense sectors. Not comprehensive embargo.",
        "sources": [
            "https://ofac.treasury.gov/sanctions-programs-and-country-information/ukraine-russia-related-sanctions"
        ]
    },
    "belarus": {
        "name": "Belarus",
        "status": "SECTORAL_SANCTIONS",
        "risk_level": "HIGH",
        "sanctioning_authorities": ["OFAC", "EU"],
        "reason": "Sanctions related to support for Russia's invasion of Ukraine",
        "blocked": False,
        "details": "Targeted sanctions on specific sectors and entities.",
        "sources": [
            "https://ofac.treasury.gov/sanctions-programs-and-country-information/belarus-sanctions"
        ]
    },
    "venezuela": {
        "name": "Venezuela",
        "status": "SECTORAL_SANCTIONS",
        "risk_level": "HIGH",
        "sanctioning_authorities": ["OFAC"],
        "reason": "Sanctions on Venezuelan government and oil sector",
        "blocked": False,
        "details": "Targeted sanctions on government officials and petroleum sector.",
        "sources": [
            "https://ofac.treasury.gov/sanctions-programs-and-country-information/venezuela-related-sanctions"
        ]
    },
    "myanmar": {
        "name": "Myanmar (Burma)",
        "status": "SECTORAL_SANCTIONS",
        "risk_level": "HIGH",
        "sanctioning_authorities": ["OFAC", "EU"],
        "reason": "Military coup and human rights violations",
        "blocked": False,
        "details": "Targeted sanctions on military regime and associates.",
        "sources": [
            "https://ofac.treasury.gov/sanctions-programs-and-country-information/burma-sanctions"
        ]
    },
    "burma": {
        "name": "Myanmar (Burma)",
        "status": "SECTORAL_SANCTIONS",
        "risk_level": "HIGH",
        "sanctioning_authorities": ["OFAC", "EU"],
        "reason": "Military coup and human rights violations",
        "blocked": False,
        "details": "Targeted sanctions on military regime and associates.",
        "sources": [
            "https://ofac.treasury.gov/sanctions-programs-and-country-information/burma-sanctions"
        ]
    },

    # Regional Conflicts
    "crimea": {
        "name": "Crimea Region of Ukraine",
        "status": "REGIONAL_SANCTIONS",
        "risk_level": "CRITICAL",
        "sanctioning_authorities": ["OFAC", "EU"],
        "reason": "Crimea-related sanctions",
        "blocked": True,
        "details": "Comprehensive sanctions on Crimea region. New investment prohibited.",
        "sources": [
            "https://ofac.treasury.gov/sanctions-programs-and-country-information/ukraine-russia-related-sanctions"
        ]
    },
    "donetsk": {
        "name": "Donetsk Region of Ukraine",
        "status": "REGIONAL_SANCTIONS",
        "risk_level": "CRITICAL",
        "sanctioning_authorities": ["OFAC", "EU"],
        "reason": "DNR/LNR region sanctions",
        "blocked": True,
        "details": "Sanctions on so-called Donetsk People's Republic.",
        "sources": [
            "https://ofac.treasury.gov/sanctions-programs-and-country-information/ukraine-russia-related-sanctions"
        ]
    },
    "luhansk": {
        "name": "Luhansk Region of Ukraine",
        "status": "REGIONAL_SANCTIONS",
        "risk_level": "CRITICAL",
        "sanctioning_authorities": ["OFAC", "EU"],
        "reason": "DNR/LNR region sanctions",
        "blocked": True,
        "details": "Sanctions on so-called Luhansk People's Republic.",
        "sources": [
            "https://ofac.treasury.gov/sanctions-programs-and-country-information/ukraine-russia-related-sanctions"
        ]
    },

    # Other Sanctioned Countries
    "sudan": {
        "name": "Sudan",
        "status": "SECTORAL_SANCTIONS",
        "risk_level": "MEDIUM",
        "sanctioning_authorities": ["OFAC"],
        "reason": "Darfur sanctions",
        "blocked": False,
        "details": "Targeted sanctions related to Darfur conflict.",
        "sources": [
            "https://ofac.treasury.gov/sanctions-programs-and-country-information/sudan-sanctions"
        ]
    },
    "south sudan": {
        "name": "South Sudan",
        "status": "SECTORAL_SANCTIONS",
        "risk_level": "MEDIUM",
        "sanctioning_authorities": ["OFAC"],
        "reason": "Sanctions on specific individuals",
        "blocked": False,
        "details": "Targeted sanctions on individuals undermining peace.",
        "sources": [
            "https://ofac.treasury.gov/sanctions-programs-and-country-information/south-sudan-sanctions"
        ]
    },
    "zimbabwe": {
        "name": "Zimbabwe",
        "status": "SECTORAL_SANCTIONS",
        "risk_level": "MEDIUM",
        "sanctioning_authorities": ["OFAC", "EU"],
        "reason": "Sanctions on government officials",
        "blocked": False,
        "details": "Targeted sanctions on specific individuals and entities.",
        "sources": [
            "https://ofac.treasury.gov/sanctions-programs-and-country-information/zimbabwe-sanctions"
        ]
    },
    "lebanon": {
        "name": "Lebanon",
        "status": "TARGETED_SANCTIONS",
        "risk_level": "MEDIUM",
        "sanctioning_authorities": ["OFAC"],
        "reason": "Hezbollah-related sanctions",
        "blocked": False,
        "details": "Targeted sanctions related to Hezbollah. Normal trade generally permitted.",
        "sources": [
            "https://ofac.treasury.gov/sanctions-programs-and-country-information/lebanon-related-sanctions"
        ]
    },
    "iraq": {
        "name": "Iraq",
        "status": "PARTIAL_SANCTIONS",
        "risk_level": "MEDIUM",
        "sanctioning_authorities": ["OFAC"],
        "reason": "Sanctions on certain Iraqi entities and individuals",
        "blocked": False,
        "details": "Targeted sanctions. Normal trade generally permitted with restrictions.",
        "sources": [
            "https://ofac.treasury.gov/sanctions-programs-and-country-information/iraq-related-sanctions"
        ]
    },
    "somalia": {
        "name": "Somalia",
        "status": "TARGETED_SANCTIONS",
        "risk_level": "MEDIUM",
        "sanctioning_authorities": ["UN"],
        "reason": "UN arms embargo",
        "blocked": False,
        "details": "Arms embargo and targeted sanctions. Normal trade may be permitted.",
        "sources": [
            "https://www.un.org/securitycouncil/sanctions/751"
        ]
    },
    "libya": {
        "name": "Libya",
        "status": "TARGETED_SANCTIONS",
        "risk_level": "MEDIUM",
        "sanctioning_authorities": ["OFAC", "UN", "EU"],
        "reason": "Sanctions on specific entities",
        "blocked": False,
        "details": "Targeted sanctions. Arms embargo. Normal trade may be permitted with due diligence.",
        "sources": [
            "https://ofac.treasury.gov/sanctions-programs-and-country-information/libya-sanctions"
        ]
    },
    "yemen": {
        "name": "Yemen",
        "status": "TARGETED_SANCTIONS",
        "risk_level": "MEDIUM",
        "sanctioning_authorities": ["UN"],
        "reason": "Sanctions related to conflict",
        "blocked": False,
        "details": "Targeted sanctions. Arms embargo. Humanitarian exceptions.",
        "sources": [
            "https://www.un.org/securitycouncil/sanctions/2140"
        ]
    },
    "afghanistan": {
        "name": "Afghanistan",
        "status": "TARGETED_SANCTIONS",
        "risk_level": "HIGH",
        "sanctioning_authorities": ["OFAC", "UN"],
        "reason": "Taliban-related sanctions",
        "blocked": False,
        "details": "Targeted sanctions on Taliban. Humanitarian trade may be permitted.",
        "sources": [
            "https://ofac.treasury.gov/sanctions-programs-and-country-information/afghanistan-related-sanctions"
        ]
    }
}

# High-risk ports
HIGH_RISK_PORTS = {
    # Iran
    "bandar abbas": {"country": "Iran", "risk": "CRITICAL", "reason": "Major Iranian port under US sanctions"},
    "bushehr": {"country": "Iran", "risk": "CRITICAL", "reason": "Iranian port under sanctions"},
    "chabahar": {"country": "Iran", "risk": "CRITICAL", "reason": "Iranian port under sanctions"},

    # North Korea
    "nampo": {"country": "North Korea", "risk": "CRITICAL", "reason": "North Korean port - comprehensive sanctions"},
    "chongjin": {"country": "North Korea", "risk": "CRITICAL", "reason": "North Korean port - comprehensive sanctions"},

    # Syria
    "latakia": {"country": "Syria", "risk": "CRITICAL", "reason": "Syrian port under sanctions"},
    "tartus": {"country": "Syria", "risk": "CRITICAL", "reason": "Syrian port under sanctions"},

    # Russia (High-risk but not blocked)
    "novorossiysk": {"country": "Russia", "risk": "HIGH", "reason": "Russian port - sectoral sanctions may apply"},
    "st. petersburg": {"country": "Russia", "risk": "HIGH", "reason": "Russian port - sectoral sanctions may apply"},
    "vladivostok": {"country": "Russia", "risk": "HIGH", "reason": "Russian port - sectoral sanctions may apply"},

    # Crimea
    "sevastopol": {"country": "Crimea", "risk": "CRITICAL", "reason": "Crimean port - comprehensive sanctions"},
}

# Dual-use products that require extra scrutiny
DUAL_USE_PRODUCTS = [
    "petrochemical", "chemical", "nuclear", "military", "defense", "weapons",
    "missile", "drone", "surveillance", "encryption", "semiconductor",
    "supercomputer", "aircraft", "helicopter", "tank", "ammunition"
]


def normalize_country_name(country: str) -> str:
    """Normalize country name for lookup"""
    if not country:
        return ""
    return country.lower().strip()


def check_country_sanctions(country: str) -> Dict:
    """
    Check if a country is sanctioned
    Returns sanctions information or None
    """
    normalized = normalize_country_name(country)
    return SANCTIONED_COUNTRIES.get(normalized)


def check_port_sanctions(port: str) -> Dict:
    """
    Check if a port is in a high-risk or sanctioned area
    """
    if not port:
        return None
    normalized = port.lower().strip()
    return HIGH_RISK_PORTS.get(normalized)


def is_dual_use_product(product_description: str) -> bool:
    """
    Check if product may be dual-use (civilian + military applications)
    """
    if not product_description:
        return False

    product_lower = product_description.lower()
    return any(keyword in product_lower for keyword in DUAL_USE_PRODUCTS)


def get_all_sanctioned_countries() -> List[str]:
    """Get list of all sanctioned countries"""
    return [info["name"] for info in SANCTIONED_COUNTRIES.values()]


def get_critical_risk_countries() -> List[str]:
    """Get list of countries with CRITICAL risk level"""
    return [
        info["name"]
        for info in SANCTIONED_COUNTRIES.values()
        if info["risk_level"] == "CRITICAL"
    ]
