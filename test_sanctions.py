#!/usr/bin/env python3
"""
Test script for Sanctions Agent
Tests the sanctions checking functionality with sample data
"""

import asyncio
import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app.agents.sanctions_agent import SanctionsAgent


async def test_safe_country():
    """Test with a safe country (UAE)"""
    print("\n" + "="*70)
    print("TEST 1: Safe Country - United Arab Emirates")
    print("="*70)

    agent = SanctionsAgent()

    lc_data = {
        "exporter_info": {
            "beneficiary_country": "United Arab Emirates",
            "beneficiary_name": "ABC Trading LLC"
        },
        "shipment_details": {
            "port_of_destination": "Jebel Ali, Dubai",
            "port_of_loading": "Singapore Port",
            "product_description": "Electronics"
        },
        "lc_details": {
            "issuing_bank_country": "Singapore"
        },
        "amount_and_payment": {
            "amount_usd": 100000
        },
        "importer_info": {
            "applicant_name": "Tech Imports Ltd"
        }
    }

    result = await agent.check_lc_compliance(lc_data)

    print(f"\nResult:")
    print(f"  Compliant: {result.get('compliant')}")
    print(f"  Risk Level: {result.get('risk_level')}")
    print(f"  Blocked: {result.get('blocked')}")
    print(f"  Reason: {result.get('reason')}")
    print(f"  Recommendations: {result.get('recommendations')}")

    if result.get('sources'):
        print(f"  Sources: {len(result.get('sources', []))} sources found")

    return result


async def test_sanctioned_country():
    """Test with a sanctioned country (Iran)"""
    print("\n" + "="*70)
    print("TEST 2: Sanctioned Country - Iran")
    print("="*70)

    agent = SanctionsAgent()

    lc_data = {
        "exporter_info": {
            "beneficiary_country": "Iran",
            "beneficiary_name": "Tehran Trading Co"
        },
        "shipment_details": {
            "port_of_destination": "Bandar Abbas",
            "port_of_loading": "Dubai",
            "product_description": "Industrial equipment"
        },
        "lc_details": {
            "issuing_bank_country": "Iran"
        },
        "amount_and_payment": {
            "amount_usd": 500000
        },
        "importer_info": {
            "applicant_name": "Middle East Imports"
        }
    }

    result = await agent.check_lc_compliance(lc_data)

    print(f"\nResult:")
    print(f"  Compliant: {result.get('compliant')}")
    print(f"  Risk Level: {result.get('risk_level')}")
    print(f"  Blocked: {result.get('blocked')}")
    print(f"  Reason: {result.get('reason')}")
    print(f"  Recommendations: {result.get('recommendations')}")

    if result.get('sources'):
        print(f"  Sources: {len(result.get('sources', []))} sources found")

    return result


async def test_quick_country_check():
    """Test quick country check"""
    print("\n" + "="*70)
    print("TEST 3: Quick Country Check - Russia")
    print("="*70)

    agent = SanctionsAgent()
    result = await agent.quick_country_check("Russia")

    print(f"\nResult:")
    print(f"  Compliant: {result.get('compliant')}")
    print(f"  Risk Level: {result.get('risk_level')}")
    print(f"  Blocked: {result.get('blocked')}")
    print(f"  Reason: {result.get('reason')}")

    return result


async def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("SANCTIONS AGENT TEST SUITE")
    print("="*70)
    print("\nThis will test the sanctions checking agent with:")
    print("1. A safe country (UAE)")
    print("2. A sanctioned country (Iran)")
    print("3. Quick country check (Russia)")
    print("\nNote: Each test performs real-time web searches and may take 5-10 seconds")
    print("="*70)

    try:
        # Test 1: Safe country
        result1 = await test_safe_country()

        # Test 2: Sanctioned country
        result2 = await test_sanctioned_country()

        # Test 3: Quick check
        result3 = await test_quick_country_check()

        # Summary
        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        print(f"\nTest 1 (UAE): {'✓ PASSED' if result1.get('compliant') else '✗ FAILED'}")
        print(f"Test 2 (Iran): {'✓ PASSED' if result2.get('blocked') else '✗ FAILED'}")
        print(f"Test 3 (Russia): {'✓ PASSED' if result3.get('risk_level') in ['HIGH', 'CRITICAL'] else '✗ FAILED'}")

        print("\n" + "="*70)
        print("All tests completed successfully!")
        print("="*70)

    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
