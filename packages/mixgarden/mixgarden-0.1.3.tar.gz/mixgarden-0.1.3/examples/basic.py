from mixgarden import MixgardenSDK

sdk = MixgardenSDK()

models = sdk.get_models()
print("Models:", models)

chat = sdk.chat(
    model=models[0]["id"] if models else "mistral-small",
    content="hello mixgarden!",
    pluginId="tone-pro",
    pluginSettings={
        "emotion-type": "neutral",
        "emotion-intensity": 6,
        "personality-type": "friendly",
    },
)
print("Chat:", chat)

plugins = sdk.get_plugins()
print("Plugins:", plugins)

conversations = sdk.get_conversations()
print("Conversations:", conversations)

if conversations:
    conv = sdk.get_conversation(conversations[0]["id"])
    print("First conversation:", conv)
