#!/usr/bin/env python3
"""
Simple test of computer vision body measurement
"""

import os
import sys
from body_scanner import BodyScanner, PhotoAngle

# Add style_engine to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'style_engine'))
from recommendation_engine import UserProfile, UserPreferences, StylePreference, BudgetRange, Occasion, generate_outfit_recommendations

def main():
    print("=== Computer Vision Body Measurement Demo ===\n")
    
    scanner = BodyScanner()
    test_image_path = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "testimage.JPG")
    
    print(f"Analyzing body from image...")
    
    # Simulate multi-angle analysis
    photo_paths = {PhotoAngle.FRONT: test_image_path}
    results = scanner.analyze_body_shape_from_photos(photo_paths, reference_measurement=36.0)
    
    if results["success"]:
        print("[SUCCESS] Computer vision analysis complete!")
        print(f"Confidence: {results['confidence']:.2f}")
        print(f"Detected Body Shape: {results['body_shape'].value.upper()}")
        
        measurements = results["measurements"]
        print(f"\nMeasurements from Computer Vision:")
        print(f"Shoulders: {measurements.shoulders:.1f} inches")
        print(f"Bust: {measurements.bust:.1f} inches") 
        print(f"Waist: {measurements.waist:.1f} inches")
        print(f"Hips: {measurements.hips:.1f} inches")
        
        # Generate outfit recommendation
        profile = UserProfile(body_type=results['body_shape'], measurements=measurements)
        preferences = UserPreferences(
            favorite_colors=["navy", "black", "white"],
            style_preference=StylePreference.CASUAL,
            budget_range=BudgetRange.MID,
            occasion=Occasion.WORK
        )
        
        recommendations = generate_outfit_recommendations(profile, preferences)
        
        print(f"\n=== AI OUTFIT RECOMMENDATIONS ===")
        print(f"For {results['body_shape'].value} body shape:")
        
        outfit = recommendations['outfit']
        for item, rec in outfit.items():
            print(f"  {item.replace('_', ' ').title()}: {rec}")
        
        print(f"\nStyling Goals: {', '.join(recommendations['recommendations']['styling_goals'])}")
        
        print(f"\n=== SYSTEM SUMMARY ===")
        print("Computer Vision -> Body Analysis -> Fashion Recommendations")
        print("[COMPLETE] End-to-end AI fashion system working!")
        
    else:
        print("[ERROR] Analysis failed:")
        for error in results["errors"]:
            print(f"  {error}")

if __name__ == "__main__":
    main()