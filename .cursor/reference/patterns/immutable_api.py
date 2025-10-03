"""
Immutable API Pattern Examples

This demonstrates the MappingProxyType pattern used throughout the
Config package to create immutable public APIs that prevent accidental
modification while providing clean access to configuration data.
"""

from __future__ import annotations
from types import MappingProxyType
import numpy as np

#%% BASIC IMMUTABLE BUNDLE PATTERN

def create_basic_bundle():
    """Example of creating a basic immutable bundle."""
    
    # Internal mutable dict for assembly
    _internal = {
        "CONSTANT_A": "value_a",
        "CONSTANT_B": 42,
        "CONSTANT_C": [1, 2, 3],
    }
    
    # Export as immutable
    BUNDLE = MappingProxyType(_internal)
    return BUNDLE

#%% SCIENTIFIC DATA BUNDLE PATTERN

def create_scientific_bundle():
    """Example with scientific data structures."""
    
    # Process some scientific data
    time_points = np.linspace(0, 10, 100)
    measurements = np.sin(time_points) + 0.1 * np.random.randn(100)
    
    _scientific_data = {
        # Constants
        "SAMPLE_RATE": 10.0,  # Hz
        "DURATION": 10.0,     # seconds
        "N_SAMPLES": 100,
        
        # Data arrays
        "TIME_POINTS": time_points,
        "MEASUREMENTS": measurements,
        
        # Derived values
        "MEAN_VALUE": float(np.mean(measurements)),
        "STD_VALUE": float(np.std(measurements)),
        
        # Functions
        "get_sample": lambda i: measurements[i] if 0 <= i < len(measurements) else None,
        "get_time_range": lambda start, end: time_points[(time_points >= start) & (time_points <= end)],
    }
    
    return MappingProxyType(_scientific_data)

#%% CONFIGURATION BUNDLE PATTERN

def create_config_bundle(user_params: dict):
    """Example of configuration bundle with user parameters."""
    
    # Validate user parameters
    required_keys = {"frame_rate", "duration", "output_format"}
    if not required_keys.issubset(user_params.keys()):
        missing = required_keys - user_params.keys()
        raise ValueError(f"Missing required parameters: {missing}")
    
    # Process user parameters
    frame_rate = float(user_params["frame_rate"])
    duration = float(user_params["duration"])
    output_format = str(user_params["output_format"])
    
    # Derive additional values
    total_frames = int(frame_rate * duration)
    frame_times = np.arange(total_frames) / frame_rate
    
    _config = {
        # User inputs (preserved exactly)
        "FRAME_RATE": frame_rate,
        "DURATION": duration,
        "OUTPUT_FORMAT": output_format,
        
        # Derived values
        "TOTAL_FRAMES": total_frames,
        "FRAME_TIMES": frame_times,
        "SEC_PER_FRAME": 1.0 / frame_rate,
        
        # Utility functions
        "frame_to_time": lambda f: f / frame_rate,
        "time_to_frame": lambda t: int(t * frame_rate),
        "is_valid_frame": lambda f: 0 <= f < total_frames,
    }
    
    return MappingProxyType(_config)

#%% NESTED BUNDLE PATTERN

def create_nested_bundle():
    """Example with nested immutable structures."""
    
    # Create sub-bundles
    _colors = MappingProxyType({
        "PRIMARY": "#FF0000",
        "SECONDARY": "#00FF00", 
        "ACCENT": "#0000FF",
    })
    
    _fonts = MappingProxyType({
        "TITLE": {"family": "Arial", "size": 16, "weight": "bold"},
        "BODY": {"family": "Arial", "size": 12, "weight": "normal"},
        "CODE": {"family": "Courier", "size": 10, "weight": "normal"},
    })
    
    _layout = MappingProxyType({
        "WIDTH": 800,
        "HEIGHT": 600,
        "MARGIN": 20,
        "PADDING": 10,
    })
    
    # Main bundle with nested immutable structures
    _theme = {
        "NAME": "Default Theme",
        "VERSION": "1.0.0",
        "COLORS": _colors,
        "FONTS": _fonts,
        "LAYOUT": _layout,
        
        # Functions that use nested data
        "get_color": lambda name: _colors.get(name, _colors["PRIMARY"]),
        "get_font": lambda style: _fonts.get(style, _fonts["BODY"]),
    }
    
    return MappingProxyType(_theme)

#%% USAGE EXAMPLES

def demonstrate_immutability():
    """Demonstrate that the bundles are truly immutable."""
    
    print("=== Immutable API Pattern Demonstration ===\n")
    
    # Create a bundle
    bundle = create_basic_bundle()
    print(f"Original CONSTANT_B: {bundle['CONSTANT_B']}")
    
    # Try to modify (this will fail)
    try:
        bundle["CONSTANT_B"] = 999
        print("❌ Modification succeeded (this shouldn't happen!)")
    except TypeError as e:
        print(f"✅ Modification blocked: {e}")
    
    # Try to add new key (this will also fail)
    try:
        bundle["NEW_KEY"] = "new_value"
        print("❌ Addition succeeded (this shouldn't happen!)")
    except TypeError as e:
        print(f"✅ Addition blocked: {e}")
    
    print(f"CONSTANT_B is still: {bundle['CONSTANT_B']}")
    print()

def demonstrate_scientific_usage():
    """Demonstrate scientific data bundle usage."""
    
    print("=== Scientific Data Bundle ===\n")
    
    bundle = create_scientific_bundle()
    
    print(f"Sample rate: {bundle['SAMPLE_RATE']} Hz")
    print(f"Duration: {bundle['DURATION']} seconds")
    print(f"Number of samples: {bundle['N_SAMPLES']}")
    print(f"Mean measurement: {bundle['MEAN_VALUE']:.3f}")
    print(f"Std measurement: {bundle['STD_VALUE']:.3f}")
    
    # Use functions
    sample_10 = bundle['get_sample'](10)
    print(f"Sample at index 10: {sample_10:.3f}")
    
    time_range = bundle['get_time_range'](2.0, 4.0)
    print(f"Time points between 2-4s: {len(time_range)} points")
    print()

def demonstrate_config_usage():
    """Demonstrate configuration bundle usage."""
    
    print("=== Configuration Bundle ===\n")
    
    user_params = {
        "frame_rate": 30.0,
        "duration": 5.0,
        "output_format": "mp4"
    }
    
    config = create_config_bundle(user_params)
    
    print(f"Frame rate: {config['FRAME_RATE']} fps")
    print(f"Total frames: {config['TOTAL_FRAMES']}")
    print(f"Seconds per frame: {config['SEC_PER_FRAME']:.4f}")
    
    # Use utility functions
    frame_100_time = config['frame_to_time'](100)
    time_3s_frame = config['time_to_frame'](3.0)
    
    print(f"Frame 100 occurs at: {frame_100_time:.2f} seconds")
    print(f"Time 3.0s corresponds to frame: {time_3s_frame}")
    print()

def demonstrate_nested_usage():
    """Demonstrate nested bundle usage."""
    
    print("=== Nested Bundle ===\n")
    
    theme = create_nested_bundle()
    
    print(f"Theme: {theme['NAME']} v{theme['VERSION']}")
    print(f"Primary color: {theme['COLORS']['PRIMARY']}")
    print(f"Title font: {theme['FONTS']['TITLE']['family']} {theme['FONTS']['TITLE']['size']}pt")
    print(f"Layout width: {theme['LAYOUT']['WIDTH']}px")
    
    # Use helper functions
    accent_color = theme['get_color']('ACCENT')
    code_font = theme['get_font']('CODE')
    
    print(f"Accent color: {accent_color}")
    print(f"Code font: {code_font['family']} {code_font['size']}pt")
    print()

#%% MAIN DEMONSTRATION

if __name__ == "__main__":
    demonstrate_immutability()
    demonstrate_scientific_usage()
    demonstrate_config_usage()
    demonstrate_nested_usage()
    
    print("=== Key Benefits ===")
    print("✅ Prevents accidental modification")
    print("✅ Clear, clean API")
    print("✅ Thread-safe sharing")
    print("✅ Predictable behavior")
    print("✅ Scientific reproducibility")
