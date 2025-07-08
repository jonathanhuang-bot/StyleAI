"""
StyleAI Recommendation Engine
Generates personalized outfit recommendations based on body shape analysis and user preferences
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

# Define possible values for each input

class StylePreference(Enum):
    CASUAL = "casual"
    FORMAL = "formal"
    TRENDY = "trendy"
    MINIMALIST = "minimalist"
    BOHEMIAN = "bohemian"
    CLASSIC = "classic"

class BudgetRange(Enum):
    LOW = "low"          # Under $50 per item
    MID = "mid"          # $50-150 per item
    HIGH = "high"        # $150+ per item

class BodyType(Enum):
    TRIANGLE = "triangle"
    HOURGLASS = "hourglass"
    RECTANGLE = "rectangle"
    INVERTED_TRIANGLE = "inverted_triangle"

class SkinTone(Enum):
    WARM = "warm"
    COOL = "cool"
    NEUTRAL = "neutral"

class Occasion(Enum):
    EVERYDAY = "everyday"
    WORK = "work"
    DATE = "date"
    PARTY = "party"
    FORMAL_EVENT = "formal_event"
    WORKOUT = "workout"

@dataclass
class BodyMeasurements:
    """User body measurements in inches"""
    shoulders: float
    bust: float
    waist: float
    hips: float

@dataclass
class UserProfile:
    """Semi-permanent user attributes"""
    body_type: BodyType
    measurements: Optional[BodyMeasurements] = None
    skin_tone: Optional[SkinTone] = None
    age_range: Optional[str] = None  # "18-25", "26-35", etc.
    gender_style: Optional[str] = None  # "feminine", "masculine", "neutral"

@dataclass
class UserPreferences:
    """Changeable user choices and context"""
    favorite_colors: List[str]  # ["blue", "green", "red"]
    style_preference: StylePreference
    budget_range: BudgetRange
    occasion: Occasion
    disliked_colors: Optional[List[str]] = None
    preferred_brands: Optional[List[str]] = None
    avoided_brands: Optional[List[str]] = None

#in the future instead of having the user manually input their body measurements, we can use a body scanner to get the measurements automatically
def determine_body_shape(measurements: BodyMeasurements) -> BodyType:
    """
    Determine body shape based on measurements using StyleDNA formulas
    
    Args:
        measurements: User's body measurements
        
    Returns:
        Detected body type
    """
    shoulders = measurements.shoulders
    bust = measurements.bust
    waist = measurements.waist
    hips = measurements.hips
    
    # Calculate ratios
    waist_to_shoulders_ratio = waist / shoulders if shoulders > 0 else 1
    waist_to_hips_ratio = waist / hips if hips > 0 else 1
    hips_to_shoulders_ratio = hips / shoulders if shoulders > 0 else 1
    
    # Calculate percentage differences
    shoulder_hip_diff = abs(shoulders - hips) / max(shoulders, hips) * 100
    waist_reduction_shoulders = (1 - waist_to_shoulders_ratio) * 100
    waist_reduction_hips = (1 - waist_to_hips_ratio) * 100
    hips_larger_than_shoulders = (hips_to_shoulders_ratio - 1) * 100
    
    # Rectangle: Waist < 25% smaller than shoulders AND all measurements within 5%
    if (waist_reduction_shoulders < 25 and 
        shoulder_hip_diff <= 5 and
        abs(shoulders - bust) / max(shoulders, bust) * 100 <= 5):
        return BodyType.RECTANGLE
    
    # Hourglass: Waist ~25% smaller than shoulders/bust AND hips/shoulders within 5%
    elif (waist_reduction_shoulders >= 25 and 
          waist_reduction_hips >= 25 and
          shoulder_hip_diff <= 5):
        return BodyType.HOURGLASS
    
    # Triangle (Pear): Hips 5% bigger than shoulders/bust
    elif hips_larger_than_shoulders >= 5:
        return BodyType.TRIANGLE
    
    # Inverted Triangle: Shoulders significantly broader than hips
    elif shoulders > hips and (shoulders - hips) / hips * 100 >= 5:
        return BodyType.INVERTED_TRIANGLE
    
    # Default to rectangle if unclear
    return BodyType.RECTANGLE

# Structured styling rules extracted from StyleDNA guides
STYLING_RULES = {
    BodyType.RECTANGLE: {
        "description": "Straight silhouette with similar bust and hip measurements",
        "goals": ["Create curves", "Define waist", "Add volume to upper and lower body"],
        "tops": {
            "best": ["tank tops", "wrap tops", "cowl camisole", "belted tops", "button-downs"],
            "necklines": ["scoop", "v-neck", "bateau", "off-shoulder", "sweetheart", "halter", "turtleneck", "crew", "cowl"],
            "avoid": ["shapeless oversized pieces", "cropped tops at waist"]
        },
        "bottoms": {
            "pants": ["cargo pants", "harem pants", "wide leg", "bootcut", "turn-up"],
            "jeans": ["slim", "straight", "bootcut", "wide leg", "trouser style"],
            "skirts": ["circle", "a-line", "bubble", "layered", "pencil", "pleated", "paneled", "trumpet", "straight", "gathered waist"],
            "shorts": ["bubble", "flared", "belted", "patterned", "loose", "turn-up", "paperbag waist"]
        },
        "dresses": ["wrap", "x-line", "shift", "empire", "princess seam", "a-line", "fit and flared", "one shoulder", "puff sleeves", "ruched waist"],
        "blazers": ["straight", "peplum", "structured", "double-breasted", "moto-jacket", "safari jacket", "empire waist"],
        "colors": {
            "do": "Bold and bright colors for upper and lower body, dark belts for waist definition",
            "avoid": "Bold colors around waist area"
        }
    },
    
    BodyType.HOURGLASS: {
        "description": "Balanced shoulders and hips with defined waist",
        "goals": ["Maintain natural curves", "Accentuate waist", "Keep proportions balanced"],
        "tops": {
            "best": ["fitted shirts", "wrap shirts", "belted shirts", "peplum", "keyhole"],
            "necklines": ["scoop", "v-neck", "off-shoulder", "jewel", "oval", "sweetheart", "queen anne"],
            "sleeves": ["set-in", "fitted", "bishop", "sleeveless"],
            "avoid": ["heavy embroidery", "shoulder pads", "bulky details around bust"]
        },
        "bottoms": {
            "jeans": ["straight", "bootleg", "wide", "slim", "flared", "high/mid-rise"],
            "pants": ["high/mid-rise styles that define waist"],
            "skirts": ["full", "pencil", "gored", "a-line", "tulip"],
            "shorts": ["tapered", "structured", "bermuda", "flared", "loose"]
        },
        "dresses": ["bias", "peplum", "shift", "wrap", "corset", "sheath"],
        "jumpsuits": ["wide leg", "strapless", "belted", "flaring"],
        "coats": ["a-line", "princess", "wrap", "belted", "trench", "swing", "capelet"],
        "colors": {
            "do": "Simple, minimalistic pieces in solid colors",
            "avoid": "Overwhelming patterns that hide natural curves"
        }
    },
    
    BodyType.TRIANGLE: {
        "description": "Hips wider than shoulders with defined waist",
        "goals": ["Balance proportions", "Add volume to upper body", "Minimize lower body volume"],
        "tops": {
            "best": ["wrap bust", "slim fit", "cropped around hipline", "tie necks"],
            "necklines": ["bateau", "boat", "cowl", "off-shoulder", "heart", "sabrina", "sweetheart", "crew", "slash", "turtle"],
            "sleeves": ["petal", "batwing", "cap", "tapered", "flutter", "juliet"],
            "details": ["horizontal stripes", "bold patterns", "shoulder details"]
        },
        "bottoms": {
            "pants": ["high/mid rise", "flare", "bootcut", "straight", "wide-leg"],
            "jeans": ["straight", "bootcut", "flare leg", "high/mid-rise", "wide-leg"],
            "skirts": ["a-line", "bias", "tulip", "straight", "wrap", "asymmetrical", "circle"],
            "shorts": ["high/mid-rise", "belted", "flare", "straight"]
        },
        "dresses": ["tulip", "a-line", "x-line", "empire", "off-shoulder", "wrap", "belted"],
        "outerwear": {
            "jackets": ["long shearling", "shrug", "trapeze", "cropped", "belted", "bolero"],
            "coats": ["a-line", "empire", "princess", "belted", "trench", "wrap"]
        },
        "colors": {
            "do": "Light and bright colors for upper body, darker shades for lower body",
            "avoid": "Bold details around hips"
        }
    },
    
    BodyType.INVERTED_TRIANGLE: {
        "description": "Shoulders broader than hips with athletic build",
        "goals": ["Balance broad shoulders", "Add volume to lower body", "Create hip curves"],
        "tops": {
            "best": ["soft flowing fabrics", "minimal shoulder details", "v-necks", "scoop necks"],
            "avoid": ["shoulder pads", "boat necks", "off-shoulder", "horizontal stripes on top"]
        },
        "bottoms": {
            "pants": ["wide leg", "flare", "bootcut", "palazzo", "straight with details"],
            "jeans": ["flare", "wide leg", "bootcut", "boyfriend", "baggy"],
            "skirts": ["a-line", "circle", "pleated", "flare", "full", "layered"],
            "shorts": ["wide", "flare", "pleated", "cargo", "palazzo"]
        },
        "dresses": ["a-line", "fit and flare", "empire waist", "wrap", "off-shoulder (if balancing with volume below)"],
        "outerwear": {
            "jackets": ["peplum", "belted", "cropped", "fitted at waist"],
            "coats": ["a-line", "flare", "princess", "wrap", "trench"]
        },
        "colors": {
            "do": "Darker colors on top, brighter colors on bottom",
            "avoid": "Bold patterns or light colors that emphasize shoulders"
        }
    }
}

def generate_outfit_recommendations(user_profile: UserProfile, preferences: UserPreferences) -> Dict:
    """
    Generate personalized outfit recommendations based on body shape and preferences
    
    Args:
        user_profile: User's physical attributes and body shape
        preferences: User's current preferences and context
        
    Returns:
        Dictionary containing outfit recommendations
    """
    body_shape = user_profile.body_type
    occasion = preferences.occasion
    style_pref = preferences.style_preference
    colors = preferences.favorite_colors
    
    # Get styling rules for body shape
    rules = STYLING_RULES.get(body_shape)
    if not rules:
        return {"error": f"No styling rules found for body shape: {body_shape}"}
    
    # Generate outfit based on occasion
    outfit = {
        "body_shape": body_shape.value,
        "occasion": occasion.value,
        "style_preference": style_pref.value,
        "recommendations": {
            "description": rules["description"],
            "styling_goals": rules["goals"]
        }
    }
    
    # Basic outfit generation based on occasion
    if occasion in [Occasion.WORK, Occasion.FORMAL_EVENT]:
        outfit["outfit"] = {
            "top": _select_from_list(rules["tops"]["best"], "blazer or button-down"),
            "bottom": _select_from_list(rules["bottoms"].get("pants", []), "tailored pants"),
            "dress_alternative": _select_from_list(rules.get("dresses", []), "sheath dress"),
            "shoes": "professional heels or flats",
            "accessories": "minimal jewelry, structured bag"
        }
    elif occasion == Occasion.PARTY:
        outfit["outfit"] = {
            "dress": _select_from_list(rules.get("dresses", []), "cocktail dress"),
            "top_alternative": _select_from_list(rules["tops"]["best"], "dressy top"),
            "bottom_alternative": _select_from_list(rules["bottoms"].get("skirts", []), "dressy skirt"),
            "shoes": "heels or dressy sandals",
            "accessories": "statement jewelry"
        }
    elif occasion == Occasion.DATE:
        outfit["outfit"] = {
            "dress": _select_from_list(rules.get("dresses", []), "wrap dress"),
            "top_alternative": _select_from_list(rules["tops"]["best"], "fitted top"),
            "bottom_alternative": _select_from_list(rules["bottoms"].get("jeans", []), "nice jeans"),
            "shoes": "heels or ankle boots",
            "accessories": "delicate jewelry"
        }
    else:  # EVERYDAY, WORKOUT
        outfit["outfit"] = {
            "top": _select_from_list(rules["tops"]["best"], "casual top"),
            "bottom": _select_from_list(rules["bottoms"].get("jeans", []), "jeans"),
            "shoes": "sneakers or comfortable flats",
            "accessories": "casual bag, minimal jewelry"
        }
    
    # Add styling tips
    outfit["styling_tips"] = {
        "colors": rules.get("colors", {}),
        "necklines": rules["tops"].get("necklines", []),
        "avoid": rules["tops"].get("avoid", [])
    }
    
    return outfit

def _select_from_list(items: List[str], default: str) -> str:
    """Helper function to select first item from list or return default"""
    return items[0] if items else default

