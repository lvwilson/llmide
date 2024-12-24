import os
import anthropic

class AIClient():
    MODEL_PRICING = {
        "claude-3-5-sonnet-20240620": {"input_token_cost": 3.00, "output_token_cost": 15.00},
        "claude-3-5-sonnet-20241022": {"input_token_cost": 3.00, "output_token_cost": 15.00}
    }

    def __init__(self, model="claude-3-5-sonnet-20241022"):
        api_key = os.getenv("CLAUDE_API_KEY")
        if not api_key:
            raise Exception("CLAUDE_API_KEY Environment Variable Unset")
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.cost = 0.0

    def _get_response(self, system_prompt, context, max_retries=3):
        response = None
        retries = 0
        
        while retries < max_retries:
            try:
                with self.client.messages.stream(
                    model=self.model,
                    max_tokens=8192,
                    temperature=0.5,
                    system=system_prompt,
                    messages=context,
                    extra_headers={"anthropic-beta": "max-tokens-3-5-sonnet-2024-07-15"}
                ) as stream:
                    for text in stream.text_stream:
                        safe_console_print(text, style="cyan", end="")
                response = stream.get_final_message()
                if response:  # If a valid response is received, return it
                    return response
            except anthropic.RateLimitError as e:
                retries += 1
                if hasattr(e, 'response') and e.response is not None:
                    headers = e.response.headers
                    retry_after = int(headers.get('retry-after', 1))  # Default to 1 second if header is missing
                    safe_console_print(f"Rate limit exceeded, retrying in: {retry_after}s", style="yellow")
                    time.sleep(retry_after + 1)
            except Exception as e:
                retries += 1
                # Log or handle the exception as needed
                safe_console_print(f"Attempt {retries} failed: {e}", style="red")
        
        raise Exception("Maximum retries exceeded on response request")
                    

    def generate_response(self, system_prompt, context):
        response = self._get_response(system_prompt, context)
        input_tokens = response.usage.input_tokens
        output_tokens = response.usage.output_tokens
        self.cost += self.calculate_cost(input_tokens, output_tokens)
        return response.content[0].text

    def calculate_cost(self, input_tokens, output_tokens):
        pricing = self.MODEL_PRICING[self.model]
        cost = (input_tokens * pricing['input_token_cost'] + output_tokens * pricing['output_token_cost']) / 1_000_000
        return cost

    @staticmethod
    def form_message(role, content):
        message = {
            "role":role,
            "content":convert_string_to_dict(content)
        }
        return message