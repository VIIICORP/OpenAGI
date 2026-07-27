import click
import sys
from .chat import AGIChat

@click.group()
def main():
    """OpenAGI Command Line Interface"""
    pass

@main.command()
@click.option('--model', default='gpt2', help='HuggingFace model to use for the AGI chat')
def chat(model):
    """Start an interactive AGI Chat session."""
    click.echo(f"Initializing AGI Chat with model: {model}...")
    try:
        agi_chat = AGIChat(model_name=model)
    except Exception as e:
        click.echo(f"Error initializing AGI Chat: {e}", err=True)
        sys.exit(1)

    click.echo("\n" + "="*50)
    click.echo("Welcome to OpenAGI Chat.")
    click.echo("This AGI mimics human cognitive abilities, including:")
    click.echo("- Generalization (transferring knowledge across domains)")
    click.echo("- Common Sense (reasoning based on worldly facts)")
    click.echo("Type 'quit' or 'exit' to end the session.")
    click.echo("Type 'clear' to clear the AGI's short-term memory.")
    click.echo("="*50 + "\n")

    while True:
        try:
            user_input = input("You: ")

            if user_input.strip().lower() in ['quit', 'exit']:
                click.echo("Ending session. Goodbye!")
                break

            if user_input.strip().lower() == 'clear':
                agi_chat.clear_memory()
                click.echo("[Memory cleared]")
                continue

            if not user_input.strip():
                continue

            response = agi_chat.generate_response(user_input)
            print(f"AGI: {response}\n")

        except KeyboardInterrupt:
            click.echo("\nEnding session. Goodbye!")
            break
        except Exception as e:
            click.echo(f"\nError processing input: {e}", err=True)

if __name__ == '__main__':
    main()
