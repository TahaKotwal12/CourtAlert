from openai import OpenAI

client = OpenAI(
    base_url="https://api.featherless.ai/v1",
    api_key="ypur-api-key"  # ← Nayi key yahan
)

try:
    response = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-V3.2",
        messages=[
            {
                "role": "system",
                "content": "You are a legal assistant for Indian courts. Write simple, clear reminders in Hindi."
            },
            {
                "role": "user",
                "content": "Court reminder likho: 10 May 2026, District Court Pune, Final Arguments hearing."
            }
        ],
        max_tokens=300
    )
    print("✅ SUCCESS!")
    print(response.choices[0].message.content)

except Exception as e:
    print(f"❌ Error: {e}")