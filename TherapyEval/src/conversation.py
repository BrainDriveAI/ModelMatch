from src.api_clients import init_clients

def structure_conversation(raw_text):
    _, anthropic_client, _ = init_clients()
    formatter_prompt = (
        "Convert this dialogue into a turn-by-turn transcript where each line "
        "starts with 'HUMAN:' or 'AI:'. Do not add any other commentary.\n\n"
        + raw_text
    )
    try:
        resp = anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            system="You are a conversation formatter.",
            messages=[{"role": "user", "content": formatter_prompt}],
            max_tokens=1000,
            temperature=0.0
        )
        return resp.content[0].text.strip()
    except Exception as e:
        raise Exception(f"Error in structuring conversation: {str(e)}")
