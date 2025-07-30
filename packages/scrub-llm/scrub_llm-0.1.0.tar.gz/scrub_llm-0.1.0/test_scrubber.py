#!/usr/bin/env python3
from scrub_llm import Scrubber, OpenAIScrubber
from openai import OpenAI

# Test the API key you provided
api_key = "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"

print("Testing scrub-llm with OpenAI API key detection...\n")

# Test 1: Direct scrubbing
scrubber = Scrubber()
test_text = f"My OpenAI API key is {api_key}"

print("1. Direct scrubbing test:")
print(f"Original: {test_text}")
scrubbed, mappings = scrubber.scrub_prompt(test_text)
print(f"Scrubbed: {scrubbed}")
print(f"Mappings: {list(mappings.keys())}\n")

# Test 2: Response scrubbing
response_text = f"Here's your generated API key: {api_key}"
print("2. Response scrubbing test:")
print(f"Original: {response_text}")
scrubbed_response = scrubber.scrub_response(response_text)
print(f"Scrubbed: {scrubbed_response}\n")

# Test 3: CLI test
print("3. Testing CLI with echo:")
import subprocess
result = subprocess.run(
    f"echo 'My key is {api_key}' | source venv/bin/activate && scrub-llm",
    shell=True,
    capture_output=True,
    text=True
)
print(f"CLI output: {result.stdout}")
print(f"CLI detected secrets: {result.returncode == 1}\n")

# Test 4: Test with mixed content
mixed_text = f"""
Here's a log file with various secrets:
OpenAI Key: {api_key}
AWS Key: AKIAIOSFODNN7EXAMPLE
GitHub Token: ghp_1234567890abcdefghijklmnopqrstuvwxyz
High entropy string: 9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08
"""

print("4. Mixed content test:")
matches = scrubber.scan(mixed_text)
print(f"Found {len(matches)} secrets:")
for match in matches:
    print(f"  - {match.pattern_name}: {match.value[:30]}...")

# Test 5: OpenAI wrapper simulation
print("\n5. OpenAI wrapper test (simulated):")
try:
    # This would normally connect to OpenAI
    client = OpenAI(api_key=api_key)
    scrubbed_client = OpenAIScrubber(client)
    print("✓ OpenAIScrubber initialized successfully")
    print("  Would scrub prompts containing:", api_key[:20] + "...")
except Exception as e:
    print(f"Note: {e}")

print("\n✅ All tests completed!")