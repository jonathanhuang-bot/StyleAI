import { useState } from "react"

function UserPreferences({ onPreferencesChange }) {
    const [preferences, setPreferences] = useState({
        favorite_colors: 'blue,black,white',
        style_preference: 'casual',
        budget_range: 'mid',
        occasion: 'everyday'
    })

    const handleInputChange = (field, value) => {
        const newPreferences = { ...preferences, [field]: value }
        setPreferences(newPreferences)
        onPreferencesChange(newPreferences)
    }

    return (
        <div style={{
            border: '1px solid #ddd',
            padding: '20px',
            margin: '20px 0',
            borderRadius: '5px',
            backgroundColor: '#f9f9f9'
        }}>
            <h3>Style Preferences</h3>
            <p style={{ fontSize: '0.9em', color: '#666', marginBottom: '20px' }}>
                Tell us about your style preferences to get personalized recommendations
            </p>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                {/* Style Preference */}
                <div>
                    <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                        Style Preference:
                    </label>
                    <select 
                        value={preferences.style_preference}
                        onChange={(e) => handleInputChange('style_preference', e.target.value)}
                        style={{
                            width: '100%',
                            padding: '8px',
                            borderRadius: '3px',
                            border: '1px solid #ccc'
                        }}
                    >
                        <option value="casual">Casual</option>
                        <option value="formal">Formal</option>
                        <option value="trendy">Trendy</option>
                        <option value="minimalist">Minimalist</option>
                        <option value="bohemian">Bohemian</option>
                        <option value="classic">Classic</option>
                    </select>
                </div>

                {/* Occasion */}
                <div>
                    <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                        Occasion:
                    </label>
                    <select 
                        value={preferences.occasion}
                        onChange={(e) => handleInputChange('occasion', e.target.value)}
                        style={{
                            width: '100%',
                            padding: '8px',
                            borderRadius: '3px',
                            border: '1px solid #ccc'
                        }}
                    >
                        <option value="everyday">Everyday</option>
                        <option value="work">Work</option>
                        <option value="date">Date</option>
                        <option value="party">Party</option>
                        <option value="formal_event">Formal Event</option>
                        <option value="workout">Workout</option>
                    </select>
                </div>

                {/* Budget Range */}
                <div>
                    <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                        Budget Range:
                    </label>
                    <select 
                        value={preferences.budget_range}
                        onChange={(e) => handleInputChange('budget_range', e.target.value)}
                        style={{
                            width: '100%',
                            padding: '8px',
                            borderRadius: '3px',
                            border: '1px solid #ccc'
                        }}
                    >
                        <option value="low">Low (Under $50 per item)</option>
                        <option value="mid">Mid ($50-150 per item)</option>
                        <option value="high">High ($150+ per item)</option>
                    </select>
                </div>

                {/* Favorite Colors */}
                <div>
                    <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
                        Favorite Colors:
                    </label>
                    <input 
                        type="text"
                        value={preferences.favorite_colors}
                        onChange={(e) => handleInputChange('favorite_colors', e.target.value)}
                        placeholder="e.g., blue, black, white, red"
                        style={{
                            width: '100%',
                            padding: '8px',
                            borderRadius: '3px',
                            border: '1px solid #ccc'
                        }}
                    />
                    <small style={{ color: '#666', fontSize: '0.8em' }}>
                        Enter colors separated by commas
                    </small>
                </div>
            </div>

            {/* Preview */}
            <div style={{ 
                marginTop: '15px', 
                padding: '10px', 
                backgroundColor: '#fff', 
                borderRadius: '3px',
                fontSize: '0.9em'
            }}>
                <strong>Current Preferences:</strong> {preferences.style_preference} style for {preferences.occasion}, 
                {preferences.budget_range} budget, favorite colors: {preferences.favorite_colors}
            </div>
        </div>
    )
}

export default UserPreferences