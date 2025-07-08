#!/usr/bin/env python3
"""
Test script for the StyleAI recommendation engine
"""

from recommendation_engine import (
    BodyMeasurements, 
    UserProfile, 
    UserPreferences,
    BodyType,
    StylePreference,
    BudgetRange,
    Occasion,
    SkinTone,
    determine_body_shape,
    generate_outfit_recommendations
)

def test_body_shape_detection():
    """Test the body shape detection algorithm"""
    print("=== BODY SHAPE DETECTION TESTS ===\n")
    
    # Test cases based on StyleDNA formulas
    test_cases = [
        {
            "name": "Rectangle Example",
            "measurements": BodyMeasurements(shoulders=36, bust=36, waist=30, hips=36),
            "expected": BodyType.RECTANGLE
        },
        {
            "name": "Hourglass Example", 
            "measurements": BodyMeasurements(shoulders=36, bust=36, waist=26, hips=36),
            "expected": BodyType.HOURGLASS
        },
        {
            "name": "Triangle (Pear) Example",
            "measurements": BodyMeasurements(shoulders=34, bust=34, waist=28, hips=38),
            "expected": BodyType.TRIANGLE
        },
        {
            "name": "Inverted Triangle Example",
            "measurements": BodyMeasurements(shoulders=38, bust=36, waist=30, hips=34),
            "expected": BodyType.INVERTED_TRIANGLE
        }
    ]
    
    for test in test_cases:
        detected = determine_body_shape(test["measurements"])
        status = "[PASS]" if detected == test["expected"] else "[FAIL]"
        print(f"{status} {test['name']}")
        print(f"   Measurements: S:{test['measurements'].shoulders} B:{test['measurements'].bust} W:{test['measurements'].waist} H:{test['measurements'].hips}")
        print(f"   Expected: {test['expected'].value}, Detected: {detected.value}")
        print()

def test_outfit_recommendations():
    """Test outfit recommendation generation"""
    print("=== OUTFIT RECOMMENDATION TESTS ===\n")
    
    # Test different body shapes and occasions
    test_scenarios = [
        {
            "name": "Rectangle Body - Work Outfit",
            "profile": UserProfile(
                body_type=BodyType.RECTANGLE,
                measurements=BodyMeasurements(36, 36, 30, 36)
            ),
            "preferences": UserPreferences(
                favorite_colors=["navy", "black", "white"],
                style_preference=StylePreference.CLASSIC,
                budget_range=BudgetRange.MID,
                occasion=Occasion.WORK
            )
        },
        {
            "name": "Hourglass Body - Date Night",
            "profile": UserProfile(
                body_type=BodyType.HOURGLASS,
                measurements=BodyMeasurements(36, 36, 26, 36)
            ),
            "preferences": UserPreferences(
                favorite_colors=["red", "black"],
                style_preference=StylePreference.TRENDY,
                budget_range=BudgetRange.HIGH,
                occasion=Occasion.DATE
            )
        },
        {
            "name": "Triangle Body - Party Outfit",
            "profile": UserProfile(
                body_type=BodyType.TRIANGLE,
                measurements=BodyMeasurements(34, 34, 28, 38)
            ),
            "preferences": UserPreferences(
                favorite_colors=["blue", "white", "gold"],
                style_preference=StylePreference.TRENDY,
                budget_range=BudgetRange.MID,
                occasion=Occasion.PARTY
            )
        }
    ]
    
    for scenario in test_scenarios:
        print(f"--- {scenario['name']} ---")
        
        # Generate recommendations
        recommendations = generate_outfit_recommendations(
            scenario["profile"], 
            scenario["preferences"]
        )
        
        # Display results
        print(f"Body Shape: {recommendations['body_shape']}")
        print(f"Description: {recommendations['recommendations']['description']}")
        print(f"Styling Goals: {', '.join(recommendations['recommendations']['styling_goals'])}")
        print("\nRecommended Outfit:")
        
        outfit = recommendations['outfit']
        for item, recommendation in outfit.items():
            print(f"  {item.replace('_', ' ').title()}: {recommendation}")
        
        print("\nStyling Tips:")
        tips = recommendations['styling_tips']
        if 'colors' in tips:
            colors = tips['colors']
            if 'do' in colors:
                print(f"  Colors: {colors['do']}")
            if 'avoid' in colors:
                print(f"  Avoid: {colors['avoid']}")
        
        if 'necklines' in tips and tips['necklines']:
            print(f"  Best Necklines: {', '.join(tips['necklines'][:5])}")  # Show first 5
        
        print("\n" + "="*50 + "\n")

def interactive_body_shape_detector():
    """Interactive body shape detector"""
    print("=== INTERACTIVE BODY SHAPE DETECTOR ===\n")
    print("Enter your measurements in inches:")
    
    try:
        shoulders = float(input("Shoulder width: "))
        bust = float(input("Bust measurement: "))
        waist = float(input("Waist measurement: "))
        hips = float(input("Hip measurement: "))
        
        measurements = BodyMeasurements(shoulders, bust, waist, hips)
        detected_shape = determine_body_shape(measurements)
        
        print(f"\nDetected Body Shape: {detected_shape.value.upper()}")
        
        # Get user preferences for outfit recommendation
        print("\nLet's generate an outfit recommendation!")
        print("Occasions: everyday, work, date, party, formal_event, workout")
        occasion_input = input("Enter occasion: ").lower()
        
        try:
            occasion = Occasion(occasion_input)
        except ValueError:
            occasion = Occasion.EVERYDAY
            print("Invalid occasion, using 'everyday'")
        
        # Create user profile and preferences
        profile = UserProfile(body_type=detected_shape, measurements=measurements)
        preferences = UserPreferences(
            favorite_colors=["blue", "black", "white"],
            style_preference=StylePreference.CLASSIC,
            budget_range=BudgetRange.MID,
            occasion=occasion
        )
        
        # Generate and display recommendations
        recommendations = generate_outfit_recommendations(profile, preferences)
        
        print(f"\n=== PERSONALIZED RECOMMENDATIONS ===")
        print(f"Body Shape: {recommendations['body_shape']}")
        print(f"Occasion: {recommendations['occasion']}")
        print(f"Description: {recommendations['recommendations']['description']}")
        
        print(f"\nRecommended Outfit:")
        outfit = recommendations['outfit']
        for item, recommendation in outfit.items():
            print(f"  • {item.replace('_', ' ').title()}: {recommendation}")
        
    except ValueError:
        print("Invalid input. Please enter numeric values for measurements.")
    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    # Run all tests
    test_body_shape_detection()
    test_outfit_recommendations()
    
    # Interactive mode
    print("Would you like to try the interactive body shape detector? (y/n)")
    if input().lower().startswith('y'):
        interactive_body_shape_detector()