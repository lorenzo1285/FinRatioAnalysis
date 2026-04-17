"""Test Anthropic API connection

Simple script to verify ANTHROPIC_API_KEY is set and working.
Run with: uv run python scripts/test_anthropic_connection.py
"""
import os
import sys


def test_connection():
    """Test if Anthropic API key is set and working"""
    
    # Check if API key is set
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key:
        print("❌ ERROR: ANTHROPIC_API_KEY not found in environment variables")
        print("\nMake sure to load your .env file:")
        print("  PowerShell: Get-Content .env | ForEach-Object { if($_ -match '^([^#][^=]+)=(.*)$') { [Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process') } }")
        print("  Or set directly: $env:ANTHROPIC_API_KEY='your-key-here'")
        return False
    
    print(f"✓ API key found: {api_key[:20]}...")
    
    # Try to import anthropic
    try:
        from anthropic import Anthropic
        print("✓ Anthropic SDK imported successfully")
    except ImportError:
        print("❌ ERROR: anthropic package not installed")
        print("\nInstall it with: uv pip install anthropic")
        return False
    
    # Test API connection
    try:
        print("\n🔄 Testing API connection...")
        client = Anthropic(api_key=api_key)
        
        # Try latest Claude models (April 2026)
        # From https://platform.claude.com/docs/en/docs/about-claude/models
        # Using Haiku for cost efficiency: $1/MTok input, $5/MTok output
        models_to_try = [
            "claude-haiku-4-5",       # Fastest and cheapest model
            "claude-sonnet-4-6",      # Best speed/intelligence balance
            "claude-opus-4-7",        # Most capable model (fallback)
        ]
        
        response = None
        model_used = None
        
        for model in models_to_try:
            try:
                print(f"  Trying model: {model}...")
                response = client.messages.create(
                    model=model,
                    max_tokens=50,
                    messages=[
                        {"role": "user", "content": "Reply with just 'OK' if you can read this."}
                    ]
                )
                model_used = model
                print(f"    ✓ Model {model} worked!")
                break
            except Exception as e:
                error_str = str(e)
                print(f"    Error: {error_str[:100]}...")
                if "not_found_error" in error_str:
                    continue
                elif "invalid_api_key" in error_str or "authentication" in error_str.lower():
                    print(f"❌ API Key Error: {e}")
                    return False
                else:
                    # Some other error - print it and continue trying
                    print(f"    Unexpected error, trying next model...")
                    continue
        
        if not response:
            print("❌ ERROR: No valid models found")
            return False
        
        result = response.content[0].text.strip()
        print(f"✓ API Response: {result}")
        print("\n✅ SUCCESS: Anthropic API connection is working!")
        print(f"   Model: {model_used}")
        print(f"   Usage: {response.usage.input_tokens} input tokens, {response.usage.output_tokens} output tokens")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: API call failed: {e}")
        return False


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
