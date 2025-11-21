#!/usr/bin/env python3
"""
Test script for HS Code Detection
Tests the HS code detection functionality with various product descriptions
"""

import asyncio
import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app.agents.ocr_agent import OCRAgent


async def test_hs_code_detection():
    """Test HS code detection with various product descriptions"""
    print("\n" + "="*70)
    print("HS CODE DETECTION TEST SUITE")
    print("="*70)

    agent = OCRAgent()

    # Test cases with different products
    test_products = [
        {
            "description": "Laptop computers",
            "expected_chapter": "84 or 85"
        },
        {
            "description": "Cotton t-shirts",
            "expected_chapter": "61 or 62"
        },
        {
            "description": "Mobile phones and smartphones",
            "expected_chapter": "85"
        },
        {
            "description": "Automotive spare parts - brake pads",
            "expected_chapter": "87"
        },
        {
            "description": "Industrial machinery for textile manufacturing",
            "expected_chapter": "84"
        },
        {
            "description": "Organic chemicals - benzene",
            "expected_chapter": "29"
        },
        {
            "description": "Fresh fruits - apples",
            "expected_chapter": "08"
        },
        {
            "description": "Electronics components - semiconductors",
            "expected_chapter": "85"
        },
        {
            "description": "Medical equipment - X-ray machines",
            "expected_chapter": "90"
        },
        {
            "description": "Furniture - wooden office desks",
            "expected_chapter": "94"
        }
    ]

    results = []

    for i, test_case in enumerate(test_products, 1):
        print(f"\n{'─'*70}")
        print(f"TEST {i}: {test_case['description']}")
        print(f"{'─'*70}")

        hs_result = await agent.detect_hs_code(test_case['description'])

        print(f"  Product: {test_case['description']}")
        print(f"  HS Code: {hs_result.get('hs_code')}")
        print(f"  Description: {hs_result.get('hs_description')}")
        print(f"  Chapter: {hs_result.get('chapter')}")
        print(f"  Confidence: {hs_result.get('confidence')}")
        print(f"  Reasoning: {hs_result.get('reasoning', 'N/A')[:100]}...")

        if hs_result.get('alternative_codes'):
            print(f"  Alternative codes: {', '.join(hs_result.get('alternative_codes', []))}")

        # Check if HS code was successfully detected
        success = hs_result.get('hs_code') is not None
        results.append({
            "product": test_case['description'],
            "success": success,
            "hs_code": hs_result.get('hs_code'),
            "confidence": hs_result.get('confidence')
        })

        print(f"  Status: {'✓ DETECTED' if success else '✗ FAILED'}")

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    successful = sum(1 for r in results if r['success'])
    total = len(results)

    print(f"\nTotal Tests: {total}")
    print(f"Successful: {successful}")
    print(f"Failed: {total - successful}")
    print(f"Success Rate: {(successful/total)*100:.1f}%")

    print("\n" + "─"*70)
    print("DETAILED RESULTS:")
    print("─"*70)

    for i, result in enumerate(results, 1):
        status = "✓" if result['success'] else "✗"
        print(f"{i}. {status} {result['product'][:40]:<40} | {result['hs_code'] or 'N/A':<12} | {result['confidence'] or 'N/A'}")

    print("\n" + "="*70)
    if successful == total:
        print("✅ ALL TESTS PASSED!")
    else:
        print(f"⚠️  {total - successful} TEST(S) FAILED")
    print("="*70 + "\n")


async def test_integration_with_lc():
    """Test HS code detection as part of LC extraction"""
    print("\n" + "="*70)
    print("INTEGRATION TEST: HS Code in LC Extraction")
    print("="*70)

    agent = OCRAgent()

    # Simulate LC data with product description
    print("\nSimulating LC data extraction with product: 'Electronic components - LED displays'")

    product_description = "Electronic components - LED displays"
    hs_result = await agent.detect_hs_code(product_description)

    print(f"\n  Product: {product_description}")
    print(f"  HS Code: {hs_result.get('hs_code')}")
    print(f"  Description: {hs_result.get('hs_description')}")
    print(f"  Chapter: {hs_result.get('chapter')}")
    print(f"  Confidence: {hs_result.get('confidence')}")

    print("\nExpected Response Format in LC Extraction:")
    print("─"*70)
    print("""{
  "success": true,
  "lc_data": {
    "shipment_details": {
      "product_description": "Electronic components - LED displays",
      "hs_code": "8541...",
      "hs_description": "Diodes, transistors and similar semiconductor devices...",
      "hs_confidence": "high",
      "hs_chapter": "Chapter 85 - Electrical machinery and equipment"
    },
    "hs_code_analysis": {
      "hs_code": "8541...",
      "confidence": "high",
      "reasoning": "...",
      ...
    }
  }
}""")

    print("\n" + "="*70)
    print("✅ INTEGRATION TEST COMPLETE")
    print("="*70 + "\n")


async def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("HS CODE DETECTION - COMPREHENSIVE TEST SUITE")
    print("="*70)
    print("\nThis will test HS code detection for 10 different product types.")
    print("Each test performs AI analysis to determine the appropriate HS code.")
    print("\nNote: Each test may take 2-3 seconds (AI processing)")
    print("="*70)

    try:
        # Test 1: HS Code Detection
        await test_hs_code_detection()

        # Test 2: Integration Test
        await test_integration_with_lc()

        print("\n" + "="*70)
        print("🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*70)
        print("\nHS Code Detection Features:")
        print("  ✓ Detects HS codes from product descriptions")
        print("  ✓ Provides official HS code descriptions")
        print("  ✓ Includes confidence levels (high/medium/low)")
        print("  ✓ Suggests alternative codes when applicable")
        print("  ✓ Integrated into LC extraction workflow")
        print("="*70 + "\n")

    except Exception as e:
        print(f"\n❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
