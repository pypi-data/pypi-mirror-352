Here are some use cases for the Vigi CLI application:

**Identifier** UC-1
**Purpose** To engage in an interactive, multi-turn conversation with the AI assistant.
**Priority** High
**Pre-conditions**
*   The Vigi application is installed.
*   The Vigi application is configured with necessary API keys.
**Post-conditions**
*   The user has received responses from the AI assistant.
*   The conversation history (if a session ID is used or implied by `.talk`) is updated.
**Typical Course of Action**
| S# | Actor Action                                                                | System Response                                                                                                                                                                                                                                                           |
| :-- | :-------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| S1 | User types `vg .talk` in the terminal and presses Enter.                    | System displays a welcome message from the default AI persona (e.g., "Vigi") and a prompt indicating it's ready for input (e.g., "USERNAME ➤ ").                                                                                                                               |
| S2 | User types their first question or statement (e.g., "Tell me about LLMs") and presses Enter. | System displays the user's input. System then streams the AI's response to the console. The AI's response is formatted (e.g., markdown if applicable). After the response, a new prompt appears (e.g., "USERNAME ➤ ").                                                     |
| S3 | User types a follow-up question (e.g., "How are they trained?") and presses Enter. | System displays the user's input. System streams the AI's response, taking into account the previous conversation context. After the response, a new prompt appears.                                                                                                       |
| S4 | User types `exit` and presses Enter.                                        | System displays an exit message (e.g., "Exiting chat.") and terminates the interactive session, returning the user to the shell prompt.                                                                                                                                       |
**Alternate Course of Action**
| S#  | Actor Action                                                                      | System Response                                                                                                                                                                                                                                                           |
| :--- | :-------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| S1a | User types `vg .talk "Initial question"` and presses Enter.                       | System displays the user's initial question. System then streams the AI's response to the console. After the response, the AI provides its standard greeting and asks how it can assist further. A new prompt for user input appears (e.g., "USERNAME ➤ ").                   |
| S2a | User starts typing a multiline input by first typing `"""` and pressing Enter.    | System displays a prompt for multiline input (e.g., "└─ Typing (end with \"\"\" on a new line):").                                                                                                                                                                            |
| S3a | User types several lines of text, and then types `"""` on a new line and presses Enter. | System displays the fully submitted multiline message from the user. System then streams the AI's response to this multiline input. After the response, a new prompt appears.                                                                                        |

---

**Identifier** UC-2
**Purpose** To interactively select or create an AI persona and then start a chat session with that persona.
**Priority** Medium
**Pre-conditions**
*   The Vigi application is installed.
*   The Vigi application is configured with necessary API keys.
**Post-conditions**
*   If a new persona is created, it is saved for future use.
*   An interactive chat session is started with the selected or newly created persona.
**Typical Course of Action**
| S# | Actor Action                                                                     | System Response                                                                                                                                                                                                                               |
| :-- | :------------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| S1 | User types `vg .prs` in the terminal and presses Enter.                            | System clears the screen and displays an interactive menu with options like "Create New Persona", "Choose Existing Persona" (if any exist), and "Exit".                                                                                          |
| S2 | User navigates using arrow keys and selects "Choose Existing Persona" and presses Enter. | System clears the screen and displays a list of available personas, along with "Back" and "Exit" options.                                                                                                                                    |
| S3 | User selects a specific persona (e.g., "Code Generator") from the list and presses Enter. | System confirms the selection implicitly and starts an interactive chat session. The chat interface indicates it's chatting with the "Code Generator" persona. The AI (as "Code Generator") greets the user. A prompt for user input appears. |
| S4 | User interacts with the selected persona by typing questions/prompts.              | System (via the selected persona) responds to the user's inputs.                                                                                                                                                                              |
| S5 | User types `exit` and presses Enter.                                             | System displays an exit message and terminates the interactive session.                                                                                                                                                                       |
**Alternate Course of Action**
| S#  | Actor Action                                                                                   | System Response                                                                                                                                                                                                                                                             |
| :--- | :--------------------------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| S2a | User selects "Create New Persona" from the main menu and presses Enter.                        | System clears the screen and prompts the user to enter a name for the new persona.                                                                                                                                                                                            |
| S3a | User types a name for the persona (e.g., "StoryWriter") and presses Enter.                     | System clears the screen and prompts the user to enter the blueprint/description for the "StoryWriter" persona.                                                                                                                                                                   |
| S4a | User types a description for the persona's capabilities and limitations and presses Enter.     | System creates and saves the "StoryWriter" persona. System displays a success message. System then automatically starts an interactive chat session with the newly created "StoryWriter" persona. The AI (as "StoryWriter") greets the user. A prompt for user input appears. |

---

**Identifier** UC-3
**Purpose** To get a quick, single-shot answer from the AI for a specific question without entering an interactive chat mode.
**Priority** High
**Pre-conditions**
*   The Vigi application is installed.
*   The Vigi application is configured with necessary API keys.
**Post-conditions**
*   The user has received a single response from the AI.
*   The application exits back to the shell prompt.
**Typical Course of Action**
| S# | Actor Action                                                                          | System Response                                                                                                                                                            |
| :-- | :------------------------------------------------------------------------------------ | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| S1 | User types `vg "What is the capital of Australia?"` in the terminal and presses Enter. | System displays a "Loading..." indicator (or similar). System then streams/displays the AI's answer directly to the console. After the response, the application terminates. |
**Alternate Course of Action**
| S#  | Actor Action                                                                                               | System Response                                                                                                                                                                                                                         |
| :--- | :--------------------------------------------------------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| S1a | User types `vg --describe-shell "find . -name '*.txt' -mtime -7"` in the terminal and presses Enter.          | System displays a "Loading..." indicator. System then streams/displays a description of the provided shell command, as generated by the specialized "Shell Command Descriptor" persona. After the response, the application terminates. |
| S1b | User pipes content into the application: `echo "Summarize this text" | vg`                                  | System uses the piped "Summarize this text" as the prompt. System displays a "Loading..." indicator. System then streams/displays the AI's summary. After the response, the application terminates.                                     |

---

**Identifier** UC-4
**Purpose** To manage and review past chat conversations.
**Priority** Medium
**Pre-conditions**
*   The Vigi application is installed.
*   There are existing saved chat sessions.
**Post-conditions**
*   The user has viewed the list of chat IDs or the content of a specific chat session.
**Typical Course of Action**
| S# | Actor Action                                                            | System Response                                                                                                                                                              |
| :-- | :---------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| S1 | User types `vg --list-chats` in the terminal and presses Enter.         | System displays a list of available chat session IDs, typically sorted by modification time. The application then terminates.                                                 |
| S2 | User notes a chat ID (e.g., "my_project_chat") from the list.           | (No system response)                                                                                                                                                         |
| S3 | User types `vg --show-chat my_project_chat` in the terminal and presses Enter. | System displays a formatted history of the "my_project_chat" session, including user messages, AI responses, and system/function messages. The application then terminates. |
**Alternate Course of Action**
| S#  | Actor Action                                                            | System Response                                                                   |
| :--- | :---------------------------------------------------------------------- | :-------------------------------------------------------------------------------- |
| S1a | User types `vg --list-chats` when no chat sessions exist.               | System displays a message like "No chat sessions found." The application terminates. |
| S3a | User types `vg --show-chat non_existent_chat`                            | System displays a message like "No messages found for chat ID: non_existent_chat". |

---

**Identifier** UC-5
**Purpose** To interactively chat with the "Code Generator" persona, have it generate Python code, and see the system attempt to execute that code.
**Priority** Medium
**Pre-conditions**
*   The Vigi application is installed and configured.
*   The "Code Generator" persona exists (either default or created by the user).
*   The system environment is capable of executing Python code.
**Post-conditions**
*   The user has received Python code from the AI.
*   The system has attempted to execute the generated Python code, and the output/error of the execution is displayed.
**Typical Course of Action**
| S# | Actor Action                                                                                                     | System Response                                                                                                                                                                                                                                                                        |
| :-- | :--------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| S1 | User types `vg .prs` and selects the "Code Generator" persona, then starts the chat.                             | System starts an interactive chat session with the "Code Generator" persona. The AI (as "Code Generator") greets the user. A prompt for user input appears.                                                                                                                                   |
| S2 | User types a request for Python code, e.g., `Write a Python script to print 'Hello, Vigi!'` and presses Enter.   | System displays the user's request. The "Code Generator" persona responds with the Python code (e.g., `print('Hello, Vigi!')`). The code is displayed.                                                                                                                                       |
| S3 | (After AI response)                                                                                              | System automatically attempts to execute the Python code provided by the AI. System then displays a section titled "Execution Result" (or similar) followed by the actual output from the executed code (e.g., `Hello, Vigi!`). A new prompt for user input appears.                               |
| S4 | User types another request, e.g., `Create a function that adds two numbers and call it with 5 and 3`.             | System displays the user's request. The "Code Generator" persona responds with Python code for the function and the call. The code is displayed.                                                                                                                                             |
| S5 | (After AI response)                                                                                              | System attempts to execute the new Python code. System displays the "Execution Result" (e.g., `8`). A new prompt for user input appears.                                                                                                                                                  |
| S6 | User types `exit` and presses Enter.                                                                             | System displays an exit message and terminates the interactive session.                                                                                                                                                                                                                  |
**Alternate Course of Action**
| S#  | Actor Action                                                                                     | System Response                                                                                                                                                                                                                                                                         |
| :--- | :----------------------------------------------------------------------------------------------- | :---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| S3a | AI generates Python code that results in an error during execution (e.g., `print(undefined_variable)`). | System attempts to execute the Python code. System displays the "Execution Result" section, which contains the error message from the Python interpreter (e.g., `NameError: name 'undefined_variable' is not defined`). A new prompt for user input appears.                                  |
| S3b | AI generates code that does not produce any standard output (e.g., just a function definition).      | System attempts to execute the Python code. System displays the "Execution Result" section, which might be empty or indicate no output. A new prompt for user input appears.                                                                                                               |