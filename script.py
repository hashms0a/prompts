"""
Prompts Management Extension for text-generation-webui
Allows users to create, manage, and share custom prompts with slash command support
"""

import gradio as gr
import json
import os
from datetime import datetime
from pathlib import Path

from modules import chat, shared, ui_chat
from modules.text_generation import generate_reply

# Extension parameters
params = {
    "display_name": "Prompts",
    "is_tab": True,
}

# Global variables
prompts_file = Path("extensions/prompts/prompts.json")
prompts_data = {}
current_user = "default_user"  # In a real implementation, this would be dynamic

def setup():
    """Initialize the extension and load existing prompts"""
    global prompts_data
    
    # Create extension directory if it doesn't exist
    extension_dir = Path("extensions/prompts")
    extension_dir.mkdir(exist_ok=True)
    
    # Load existing prompts or create empty file
    if prompts_file.exists():
        try:
            with open(prompts_file, 'r') as f:
                prompts_data = json.load(f)
        except:
            prompts_data = {}
    else:
        prompts_data = {}
        save_prompts()

def save_prompts():
    """Save prompts to JSON file"""
    with open(prompts_file, 'w') as f:
        json.dump(prompts_data, f, indent=2)

def create_prompt(title, command, content):
    """Create a new prompt"""
    if not title or not command or not content:
        return "Error: All fields are required", get_prompts_list()
    
    # Ensure command starts with /
    if not command.startswith('/'):
        command = '/' + command
    
    # Check if command already exists
    for prompt_id, prompt in prompts_data.items():
        if prompt['command'] == command and prompt_id != title:
            return f"Error: Command {command} already exists", get_prompts_list()
    
    prompts_data[title] = {
        'title': title,
        'command': command,
        'content': content,
        'creator': current_user,
        'created': datetime.now().isoformat(),
        'modified': datetime.now().isoformat()
    }
    
    save_prompts()
    return f"Prompt '{title}' created successfully!", get_prompts_list()

def update_prompt(selected_prompt, title, command, content):
    """Update an existing prompt"""
    if not selected_prompt or selected_prompt not in prompts_data:
        return "Error: Please select a prompt to update", get_prompts_list()
    
    if not title or not command or not content:
        return "Error: All fields are required", get_prompts_list()
    
    # Ensure command starts with /
    if not command.startswith('/'):
        command = '/' + command
    
    # Check if command already exists (excluding current prompt)
    for prompt_id, prompt in prompts_data.items():
        if prompt['command'] == command and prompt_id != selected_prompt:
            return f"Error: Command {command} already exists", get_prompts_list()
    
    # If title changed, we need to update the key
    if selected_prompt != title:
        prompts_data[title] = prompts_data.pop(selected_prompt)
    
    prompts_data[title].update({
        'title': title,
        'command': command,
        'content': content,
        'modified': datetime.now().isoformat()
    })
    
    save_prompts()
    return f"Prompt '{title}' updated successfully!", get_prompts_list()

def delete_prompt(selected_prompt):
    """Delete a prompt"""
    if not selected_prompt or selected_prompt not in prompts_data:
        return "Error: Please select a prompt to delete", get_prompts_list()
    
    del prompts_data[selected_prompt]
    save_prompts()
    return f"Prompt '{selected_prompt}' deleted successfully!", get_prompts_list()

def get_prompts_list():
    """Get list of all prompts"""
    return list(prompts_data.keys())

def load_prompt_details(selected_prompt):
    """Load details of selected prompt for editing"""
    if not selected_prompt or selected_prompt not in prompts_data:
        return "", "", ""
    
    prompt = prompts_data[selected_prompt]
    return prompt['title'], prompt['command'], prompt['content']

def get_available_commands():
    """Get list of available commands for display"""
    commands = []
    for prompt in prompts_data.values():
        commands.append(f"{prompt['command']} - {prompt['title']}")
    return "\n".join(commands) if commands else "No prompts available"

def get_accessible_prompts_json():
    """Get all prompts as JSON for JavaScript"""
    accessible = {}
    for title, prompt in prompts_data.items():
        accessible[prompt['command']] = {
            'title': prompt['title'],
            'content': prompt['content'],
            'command': prompt['command']
        }
    return json.dumps(accessible)

def chat_input_modifier(text, visible_text, state):
    """Process slash commands in chat input"""
    if text.startswith('/'):
        # Extract command
        parts = text.split(' ', 1)
        command = parts[0]
        user_input = parts[1] if len(parts) > 1 else ""
        
        # Find matching prompt
        for prompt in prompts_data.values():
            if prompt['command'] == command:
                # Replace {input} placeholder with user input if present
                prompt_content = prompt['content']
                if '{input}' in prompt_content and user_input:
                    prompt_content = prompt_content.replace('{input}', user_input)
                elif user_input:
                    # If no placeholder, append user input
                    prompt_content = f"{prompt_content}\n\n{user_input}"
                
                return prompt_content, prompt_content
    
    return text, visible_text

def ui():
    """Create the UI for the Prompts tab"""
    with gr.Tab("Prompts"):
        gr.Markdown("# Prompts Management")
        gr.Markdown("Create, manage, and share custom prompts with slash command support.")
        
        # Hidden component to store prompts data for JavaScript
        prompts_json_store = gr.Textbox(
            value=get_accessible_prompts_json(),
            visible=False,
            elem_id="prompts-data-store"
        )
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### Available Commands")
                available_commands = gr.Textbox(
                    value=get_available_commands(),
                    label="Your accessible prompts",
                    lines=10,
                    interactive=False
                )
                
                refresh_btn = gr.Button("🔄 Refresh", size="sm")
            
            with gr.Column(scale=2):
                gr.Markdown("### Prompt Editor")
                
                with gr.Row():
                    prompts_dropdown = gr.Dropdown(
                        choices=get_prompts_list(),
                        label="Select prompt to edit",
                        interactive=True
                    )
                    load_btn = gr.Button("📂 Load", size="sm")
                
                title_input = gr.Textbox(
                    label="Title",
                    placeholder="Enter a descriptive title for your prompt"
                )
                
                command_input = gr.Textbox(
                    label="Command",
                    placeholder="/mycommand (will be used as slash command)"
                )
                
                content_input = gr.Textbox(
                    label="Prompt Content",
                    placeholder="Enter your prompt text here. Use {input} as a placeholder for user input.",
                    lines=10
                )
                
                with gr.Row():
                    create_btn = gr.Button("➕ Create New", variant="primary")
                    update_btn = gr.Button("💾 Update", variant="secondary")
                    delete_btn = gr.Button("🗑️ Delete", variant="stop")
                
                status_output = gr.Textbox(label="Status", interactive=False)
        
        gr.Markdown("""
        ### Usage Instructions
        1. **Create a prompt**: Fill in all fields and click "Create New"
        2. **Edit a prompt**: Select from dropdown, click "Load", modify, then "Update"
        3. **Use in chat**: Type "/" to see available prompts, select one to fill the chat box
        4. **Dynamic input**: Use `{input}` in your prompt content as a placeholder
        
        ### Examples
        - `/summarize` - Summarize the following text
        - `/translate` - Translate to Spanish
        - `/explain` - Explain this concept in simple terms
        """)
        
        # Event handlers
        def refresh_ui():
            return get_available_commands(), gr.update(choices=get_prompts_list()), get_accessible_prompts_json()
        
        refresh_btn.click(
            refresh_ui,
            outputs=[available_commands, prompts_dropdown, prompts_json_store]
        )
        
        load_btn.click(
            load_prompt_details,
            inputs=[prompts_dropdown],
            outputs=[title_input, command_input, content_input]
        )
        
        create_btn.click(
            create_prompt,
            inputs=[title_input, command_input, content_input],
            outputs=[status_output, prompts_dropdown]
        ).then(
            refresh_ui,
            outputs=[available_commands, prompts_dropdown, prompts_json_store]
        )
        
        update_btn.click(
            update_prompt,
            inputs=[prompts_dropdown, title_input, command_input, content_input],
            outputs=[status_output, prompts_dropdown]
        ).then(
            refresh_ui,
            outputs=[available_commands, prompts_dropdown, prompts_json_store]
        )
        
        delete_btn.click(
            delete_prompt,
            inputs=[prompts_dropdown],
            outputs=[status_output, prompts_dropdown]
        ).then(
            refresh_ui,
            outputs=[available_commands, prompts_dropdown, prompts_json_store]
        )

def custom_css():
    """Add custom CSS for the extension"""
    return """
    .prompts-container {
        background-color: var(--block-background-fill);
        padding: 20px;
        border-radius: 8px;
        margin: 10px 0;
    }
    
    .prompt-command {
        font-family: monospace;
        background-color: var(--neutral-200);
        padding: 2px 6px;
        border-radius: 4px;
    }
    
    /* Autocomplete dropdown styles */
    #prompts-autocomplete {
        position: absolute;
        background-color: var(--background-fill-primary);
        border: 1px solid var(--border-color-primary);
        border-radius: 4px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        max-height: 200px;
        overflow-y: auto;
        z-index: 1000;
        display: none;
        min-width: 300px;
    }
    
    .prompt-suggestion {
        padding: 8px 12px;
        cursor: pointer;
        border-bottom: 1px solid var(--border-color-secondary);
    }
    
    .prompt-suggestion:hover,
    .prompt-suggestion.selected {
        background-color: var(--button-primary-background-fill);
        color: var(--button-primary-text-color);
    }
    
    .prompt-suggestion:last-child {
        border-bottom: none;
    }
    
    .prompt-command-inline {
        font-family: monospace;
        font-weight: bold;
        margin-right: 8px;
    }
    
    .prompt-title {
        color: var(--body-text-color-subdued);
        font-size: 0.9em;
    }
    """

def custom_js():
    """Add JavaScript for autocomplete functionality"""
    return """
    (function() {
        let autocompleteContainer = null;
        let selectedIndex = -1;
        let promptsData = {};
        
        // Wait for the page to load
        const initPromptAutocomplete = () => {
            // Get the chat input textarea
            const chatInput = document.querySelector('#chat-input textarea');
            if (!chatInput) {
                setTimeout(initPromptAutocomplete, 500);
                return;
            }
            
            // Create autocomplete container
            autocompleteContainer = document.createElement('div');
            autocompleteContainer.id = 'prompts-autocomplete';
            document.body.appendChild(autocompleteContainer);
            
            // Load prompts data
            const updatePromptsData = () => {
                const dataStore = document.querySelector('#prompts-data-store textarea');
                if (dataStore && dataStore.value) {
                    try {
                        promptsData = JSON.parse(dataStore.value);
                    } catch (e) {
                        console.error('Failed to parse prompts data:', e);
                    }
                }
            };
            
            // Initial load
            updatePromptsData();
            
            // Update when data changes
            const observer = new MutationObserver(updatePromptsData);
            const dataStore = document.querySelector('#prompts-data-store textarea');
            if (dataStore) {
                observer.observe(dataStore, { attributes: true, childList: true, characterData: true });
            }
            
            // Position autocomplete dropdown
            const positionAutocomplete = () => {
                const rect = chatInput.getBoundingClientRect();
                const caretCoords = getCaretCoordinates(chatInput, chatInput.selectionEnd);
                
                autocompleteContainer.style.left = (rect.left + caretCoords.left) + 'px';
                autocompleteContainer.style.top = (rect.top + caretCoords.top + 20) + 'px';
            };
            
            // Get caret coordinates (simplified version)
            const getCaretCoordinates = (element, position) => {
                const div = document.createElement('div');
                const style = getComputedStyle(element);
                const properties = ['font', 'letterSpacing', 'wordSpacing', 'textIndent', 'textTransform'];
                
                properties.forEach(prop => {
                    div.style[prop] = style[prop];
                });
                
                div.style.position = 'absolute';
                div.style.visibility = 'hidden';
                div.style.whiteSpace = 'pre-wrap';
                div.style.width = element.offsetWidth + 'px';
                
                div.textContent = element.value.substring(0, position);
                document.body.appendChild(div);
                
                const span = document.createElement('span');
                span.textContent = element.value.substring(position) || '.';
                div.appendChild(span);
                
                const coords = {
                    top: span.offsetTop,
                    left: span.offsetLeft
                };
                
                document.body.removeChild(div);
                return coords;
            };
            
            // Show autocomplete
            const showAutocomplete = (filter = '') => {
                const suggestions = Object.entries(promptsData)
                    .filter(([cmd, data]) => cmd.toLowerCase().includes(filter.toLowerCase()))
                    .slice(0, 10);
                
                if (suggestions.length === 0) {
                    hideAutocomplete();
                    return;
                }
                
                autocompleteContainer.innerHTML = suggestions.map(([cmd, data], index) => `
                    <div class="prompt-suggestion" data-index="${index}" data-command="${cmd}">
                        <span class="prompt-command-inline">${cmd}</span>
                        <span class="prompt-title">${data.title}</span>
                    </div>
                `).join('');
                
                autocompleteContainer.style.display = 'block';
                positionAutocomplete();
                selectedIndex = -1;
                
                // Add click handlers
                autocompleteContainer.querySelectorAll('.prompt-suggestion').forEach(el => {
                    el.addEventListener('click', () => {
                        selectPrompt(el.dataset.command);
                    });
                });
            };
            
            // Hide autocomplete
            const hideAutocomplete = () => {
                autocompleteContainer.style.display = 'none';
                selectedIndex = -1;
            };
            
            // Select prompt
            const selectPrompt = (command) => {
                const prompt = promptsData[command];
                if (prompt) {
                    chatInput.value = prompt.content;
                    chatInput.dispatchEvent(new Event('input', { bubbles: true }));
                    chatInput.focus();
                    hideAutocomplete();
                }
            };
            
            // Handle input
            chatInput.addEventListener('input', (e) => {
                const value = e.target.value;
                const cursorPosition = e.target.selectionStart;
                
                // Check if we're at the start or after a newline
                const textBefore = value.substring(0, cursorPosition);
                const lastNewline = textBefore.lastIndexOf('\\n');
                const currentLine = textBefore.substring(lastNewline + 1);
                
                if (currentLine.startsWith('/')) {
                    const filter = currentLine.substring(1);
                    showAutocomplete(filter);
                } else {
                    hideAutocomplete();
                }
            });
            
            // Handle keyboard navigation
            chatInput.addEventListener('keydown', (e) => {
                if (autocompleteContainer.style.display === 'none') return;
                
                const suggestions = autocompleteContainer.querySelectorAll('.prompt-suggestion');
                
                switch(e.key) {
                    case 'ArrowDown':
                        e.preventDefault();
                        selectedIndex = Math.min(selectedIndex + 1, suggestions.length - 1);
                        updateSelection(suggestions);
                        break;
                        
                    case 'ArrowUp':
                        e.preventDefault();
                        selectedIndex = Math.max(selectedIndex - 1, -1);
                        updateSelection(suggestions);
                        break;
                        
                    case 'Enter':
                        if (selectedIndex >= 0) {
                            e.preventDefault();
                            const selected = suggestions[selectedIndex];
                            selectPrompt(selected.dataset.command);
                        }
                        break;
                        
                    case 'Escape':
                        hideAutocomplete();
                        break;
                }
            });
            
            // Update visual selection
            const updateSelection = (suggestions) => {
                suggestions.forEach((el, index) => {
                    el.classList.toggle('selected', index === selectedIndex);
                });
            };
            
            // Hide on click outside
            document.addEventListener('click', (e) => {
                if (!chatInput.contains(e.target) && !autocompleteContainer.contains(e.target)) {
                    hideAutocomplete();
                }
            });
            
            // Handle focus
            chatInput.addEventListener('focus', (e) => {
                if (e.target.value.startsWith('/')) {
                    showAutocomplete(e.target.value.substring(1));
                }
            });
        };
        
        // Initialize when DOM is ready
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', initPromptAutocomplete);
        } else {
            initPromptAutocomplete();
        }
    })();
    """
