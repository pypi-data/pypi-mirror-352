class PromptGenerator:
    """
    A utility class for generating prompts based on a provided dictionary of prompts.
    """

    def __init__(self, prompts_dict: dict):
        """
        Initialize the PromptGenerator with a dictionary of prompts.

        Args:
            prompts_dict (dict): A dictionary where the keys are prompt names and the values
                                 are dictionaries with language-specific prompts and a shared output parser.
        """
        self.prompts_dict = prompts_dict

    def generate_prompt(self, prompt_name: str, language: str):
        """
        Generate a prompt based on the prompt name and language.

        Args:
            prompt_name (str): The name of the prompt to generate.
            language (str): The language of the prompt to generate.

        Returns:
            dict: A dictionary containing the prompt and its associated output parser.

        Raises:
            ValueError: If the prompt name or language is not supported.
        """
        if prompt_name not in self.prompts_dict:
            raise ValueError(f"Prompt '{prompt_name}' is not supported in this prompt generator.")

        prompt_data = self.prompts_dict[prompt_name]

        if language not in prompt_data["languages"]:
            raise ValueError(f"Language '{language}' is not supported for prompt '{prompt_name}'.")

        return {
            "prompt": prompt_data["languages"][language],
            "output_parser": prompt_data["output_parser"]
        }
