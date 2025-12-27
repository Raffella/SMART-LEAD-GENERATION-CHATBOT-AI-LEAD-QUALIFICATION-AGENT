import puter

try:
    print("Attempting to call Claude-3.5-Sonnet via Puter...")
    # Assuming similar API to OpenAI as per common wrappers
    response = puter.ChatCompletion.create(
        model="claude-3-5-sonnet",
        messages=[{"role": "user", "content": "Hello, are you Claude?"}]
    )
    print("Success!")
    print(response)
except Exception as e:
    print(f"Error: {e}")
