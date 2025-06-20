# Prompts Management Extension for text-generation-webui

A powerful extension for [oobabooga's text-generation-webui](https://github.com/oobabooga/text-generation-webui) that enables users to create, manage, and quickly access custom prompts through an intuitive interface and slash commands.


## 🌟 Features

### Prompt Management
- **Create & Edit**: Design custom prompts with titles, slash commands, and content
- **Organize**: View all your prompts in a clean, organized interface
- **Delete**: Remove prompts you no longer need
- **Persistence**: All prompts are automatically saved and persist between sessions

### Slash Command System
- **Quick Access**: Type `/` in the chat to see all available prompts
- **Autocomplete**: Smart dropdown shows matching prompts as you type
- **Instant Fill**: Select a prompt to instantly fill the chat input
- **Dynamic Placeholders**: Use `{input}` in prompts for dynamic content insertion

### User Experience
- **Keyboard Navigation**: Use arrow keys to navigate suggestions, Enter to select
- **Mouse Support**: Click on any suggestion to use it
- **Real-time Updates**: Autocomplete list updates instantly when prompts change
- **Clean UI**: Intuitive interface that matches the webui theme

## 📦 Installation

1. Navigate to your text-generation-webui extensions folder:
   ```bash
   cd text-generation-webui/extensions
   ```

2. Create a new folder for the extension:
   ```bash
   mkdir prompts
   ```

3. Download the extension file:
   ```bash
   cd prompts
   wget https://raw.githubusercontent.com/hashms0a/prompts-extension/main/script.py
   ```
   Or
   Clone this GitHub repository into the extension folder.
   ```bash
   git clone https://github.com/hashms0a/prompts.git
   ```

5. Launch text-generation-webui with the extension:

   Edit the CMD_FLAGS.txt file in the user_data directory.
   ```bash
   --extensions prompts
   ```

## 🚀 Usage

### Creating a Prompt

1. Navigate to the **Prompts** tab in the web interface
2. Fill in the following fields:
   - **Title**: A descriptive name for your prompt
   - **Command**: The slash command trigger (e.g., `/summarize`)
   - **Prompt Content**: The actual prompt text
3. Click **Create New**

### Using Prompts in Chat

1. In the chat input, type `/` to see all available prompts
2. Continue typing to filter results (e.g., `/sum` for summarize)
3. Use arrow keys or mouse to select a prompt
4. Press Enter or click to fill the chat with the prompt content

## 📝 Examples

### Summarization Prompt
- **Title**: Summarize Text
- **Command**: `/summarize`
- **Content**: `Please provide a concise summary of the following text, highlighting the key points:`

### Translation Prompt
- **Title**: Spanish Translation
- **Command**: `/spanish`
- **Content**: `Translate the following text to Spanish: {input}`

### Code Explanation
- **Title**: Explain Code
- **Command**: `/explain`
- **Content**: `Please explain the following code in simple terms, describing what it does and how it works:`

### Creative Writing
- **Title**: Story Continuation
- **Command**: `/continue`
- **Content**: `Continue this story in a creative and engaging way: {input}`

## 🔧 Configuration

The extension stores all prompts in `extensions/prompts/prompts.json`. This file is automatically created and managed by the extension.

### File Structure
```json
{
  "Summarize Text": {
    "title": "Summarize Text",
    "command": "/summarize",
    "content": "Please provide a concise summary...",
    "creator": "default_user",
    "created": "2024-01-01T00:00:00",
    "modified": "2024-01-01T00:00:00"
  }
}
```

## 🎨 Customization

### Modifying Styles

The extension includes custom CSS that can be modified in the `custom_css()` function:

```python
def custom_css():
    return """
    /* Your custom styles here */
    """
```

### Extending Functionality

You can extend the extension by modifying these key functions:
- `create_prompt()`: Add validation or preprocessing
- `chat_input_modifier()`: Customize how prompts are processed
- `custom_js()`: Enhance the autocomplete behavior
