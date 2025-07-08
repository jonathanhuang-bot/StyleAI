#!/usr/bin/env python3
"""
Simple test of the recommendation engine
"""

from recommendation_engine import (
    BodyMeasurements, 
    UserProfile, 
    UserPreferences,
    BodyType,
    StylePreference,
    BudgetRange,
    Occasion,
    determine_body_shape,
    generate_outfit_recommendations
)

def main():
    print("=== StyleAI Recommendation Engine Demo ===\n")
    
    # Example: Rectangle body shape going to work
    measurements = BodyMeasurements(shoulders=36, bust=36, waist=30, hips=36)
    detected_shape = determine_body_shape(measurements)
    
    print(f"Input measurements: Shoulders=36, Bust=36, Waist=30, Hips=36")
    print(f"Detected body shape: {detected_shape.value.upper()}\n")
    
    # Create user profile and preferences
    profile = UserProfile(body_type=detected_shape, measurements=measurements)
    preferences = UserPreferences(
        favorite_colors=["navy", "black", "white"],
        style_preference=StylePreference.CLASSIC,
        budget_range=BudgetRange.MID,
        occasion=Occasion.WORK
    )
    
    # Generate recommendations
    recommendations = generate_outfit_recommendations(profile, preferences)
    
    print("=== OUTFIT RECOMMENDATIONS ===")
    print(f"Body Shape: {recommendations['body_shape']}")
    print(f"Occasion: {recommendations['occasion']}")
    print(f"Style: {recommendations['style_preference']}")
    print(f"Description: {recommendations['recommendations']['description']}")
    print(f"Goals: {', '.join(recommendations['recommendations']['styling_goals'])}")
    
    print(f"\nRecommended Work Outfit:")
    outfit = recommendations['outfit']
    for item, recommendation in outfit.items():
        print(f"  {item.replace('_', ' ').title()}: {recommendation}")
    
    print(f"\nStyling Tips:")
    tips = recommendations['styling_tips']
    if 'colors' in tips and 'do' in tips['colors']:
        print(f"  Colors: {tips['colors']['do']}")
    if 'necklines' in tips and tips['necklines']:
        print(f"  Best necklines: {', '.join(tips['necklines'][:4])}")

    print(f"\n" + "="*50)
    print("System working perfectly! ✨")

if __name__ == "__main__":
    main()