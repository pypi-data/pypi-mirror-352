import os
import questionary
import platform
import subprocess # Added for potential direct execution if ever needed from here

# Assuming config.py is in the same directory or accessible via PYTHONPATH
try:
    from .config import AnsiColors, Theme # For direct print statements if any non-v_print
except ImportError:
    from config import AnsiColors, Theme


# Helper for verbose printing, passed from main.py
V_PRINT_FUNC = lambda msg, **kwargs: None # This will be config.v_print

def _ask(message, type='text', choices=None, default=None, validate=None, **prompt_specific_kwargs):
    """Wrapper for questionary prompts, handles potential None returns.
    Passes prompt_specific_kwargs to the underlying questionary function.
    """
    global V_PRINT_FUNC
    # V_PRINT_FUNC is already styled by config.v_print definition
    V_PRINT_FUNC(f"Asking user: {message} (type: {type}, default: {default}, extra_args: {prompt_specific_kwargs})")

    question_map = {
        'text': questionary.text,
        'select': questionary.select,
        'confirm': questionary.confirm,
        'path': questionary.path,
    }

    if type not in question_map:
        raise ValueError(f"Unsupported questionary type: {type}")

    question_constructor = question_map[type]

    # Styling questionary itself can be more complex, involves prompt_toolkit styles.
    # For now, relying on questionary's default good styling.
    # The surrounding text (e.g. print() calls) is what we will style primarily.
    constructor_kwargs = {"message": message}


    if default is not None:
        constructor_kwargs["default"] = default
    if validate is not None:
        constructor_kwargs["validate"] = validate

    if type == 'select':
        if choices is None:
             raise ValueError("The 'choices' argument is required for 'select' type prompts.")
        constructor_kwargs['choices'] = choices

    constructor_kwargs.update(prompt_specific_kwargs)

    question_instance = question_constructor(**constructor_kwargs)

    try:
        answer = question_instance.ask()
    except KeyboardInterrupt:
        V_PRINT_FUNC("User cancelled with KeyboardInterrupt.")
        print(f"\n{Theme.F(Theme.WARNING, 'Input cancelled by user.')}") # User feedback
        return None

    if answer is None:
        V_PRINT_FUNC(f"User cancelled prompt: {message}")
        # Optionally print a message here if desired, but questionary usually handles "no answer" well
        # print(f"{Theme.F(Theme.WARNING, 'Prompt cancelled.')}")
    return answer

def _generate_default_dockerignore_content():
    return """\
# Git files
.git/
.gitignore

# Python specific
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
pip-log.txt
pip-delete-this-directory.txt
celerybeat-schedule
*.egg-info/
.project
.pydevproject
.settings/

# Node specific
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
package-lock.json
yarn.lock

# IDE / OS specific
.env
.env.*
!.env.example
.vscode/
.idea/
*.swp
*~
.DS_Store
Thumbs.db

# Build artifacts
dist/
build/
target/
out/

# Logs
*.log
logs/

# Static site specific (often served from root or specific folders like public/dist)
# Add any build output folders here if they are not meant to be in the image directly,
# but rather their contents are copied from. Example:
# assets_source/
"""

def _get_common_details(project_dir):
    global V_PRINT_FUNC
    V_PRINT_FUNC("Gathering common project details.")
    details = {}

    default_project_name = os.path.basename(project_dir)
    project_name = _ask(f"Enter a name for your application/image (e.g., {Theme.F(Theme.HIGHLIGHT, 'my-app')}):", default=default_project_name)
    if project_name is None: return None
    details['project_name'] = project_name

    details['project_type'] = _ask(
        "Select project type:",
        type='select',
        choices=["Python", "Node.js", "Vanilla HTML/CSS/JS", "Generic (manual setup)"]
    )
    if details['project_type'] is None: return None

    return details

def _get_python_details(common_details, project_dir):
    global V_PRINT_FUNC
    V_PRINT_FUNC("Gathering Python specific details.")
    py_details = common_details.copy()

    py_version_choices = ["3.12-slim", "3.11-slim", "3.10-slim", "3.9-slim", "3.12", "3.11", "3.10", "3.9", "Custom"]
    base_image_choice = _ask("Select Python base image version (slim is recommended):", type='select', choices=py_version_choices, default="3.12-slim")
    if base_image_choice is None: return None
    if base_image_choice == "Custom":
        custom_image = _ask(f"Enter custom Python base image (e.g., {Theme.F(Theme.HIGHLIGHT, 'python:3.10-buster')}):")
        if custom_image is None: return None
        py_details['base_image'] = custom_image
    else:
        py_details['base_image'] = f"python:{base_image_choice}"

    default_req_file = "requirements.txt"
    req_file_path = os.path.join(project_dir, default_req_file)
    has_req_file = os.path.exists(req_file_path)

    use_req_file_msg = f"Do you have a '{Theme.F(Theme.HIGHLIGHT, default_req_file)}' file for dependencies?"
    use_req_file_msg += Theme.F(Theme.SUCCESS if has_req_file else Theme.WARNING, f" ({'Found' if has_req_file else 'Not found'})")
    use_req_file = _ask(use_req_file_msg, type='confirm', default=has_req_file)

    if use_req_file is None: return None
    if use_req_file:
        py_details['requirements_file'] = default_req_file
    else:
        py_details['requirements_file'] = None
        V_PRINT_FUNC(f"User indicated no {default_req_file} or will add it manually.")


    main_app_file = _ask(f"Enter the name of your main Python application file (e.g., {Theme.F(Theme.HIGHLIGHT, 'app.py, main.py')}):", default="app.py")
    if main_app_file is None: return None
    py_details['app_file'] = main_app_file
    if not os.path.exists(os.path.join(project_dir, main_app_file)):
        V_PRINT_FUNC(f"Warning: Main application file '{main_app_file}' not found in {project_dir}.")
        warning_msg = Theme.F(Theme.WARNING, f"Main file '{main_app_file}' not found. Continue anyway?")
        if not _ask(warning_msg, type='confirm', default=True):
            return None

    app_port_msg = f"What port does your application listen on inside the container (e.g., {Theme.F(Theme.HIGHLIGHT, '5000, 8000')})? Leave blank if none."
    app_port = _ask(app_port_msg, default="5000")
    if app_port is None and app_port != "": return None
    py_details['app_port'] = app_port if app_port else None

    return py_details

def _get_nodejs_details(common_details, project_dir):
    global V_PRINT_FUNC
    V_PRINT_FUNC("Gathering Node.js specific details.")
    node_details = common_details.copy()

    node_version_choices = ["20-alpine", "18-alpine", "20", "18", "Custom"]
    base_image_choice = _ask("Select Node.js base image version (alpine is recommended):", type='select', choices=node_version_choices, default="20-alpine")
    if base_image_choice is None: return None
    if base_image_choice == "Custom":
        custom_image = _ask(f"Enter custom Node.js base image (e.g., {Theme.F(Theme.HIGHLIGHT, 'node:18-buster')}):")
        if custom_image is None: return None
        node_details['base_image'] = custom_image
    else:
        node_details['base_image'] = f"node:{base_image_choice}"

    default_pkg_file = "package.json"
    pkg_file_path = os.path.join(project_dir, default_pkg_file)
    has_pkg_file = os.path.exists(pkg_file_path)

    if not has_pkg_file:
        V_PRINT_FUNC(f"Warning: '{default_pkg_file}' not found in {project_dir}.")
        warning_msg = Theme.F(Theme.WARNING, f"'{default_pkg_file}' not found. This is crucial for Node.js projects. Continue anyway?")
        if not _ask(warning_msg, type='confirm', default=False):
            return None
    node_details['package_file'] = default_pkg_file

    main_app_file = _ask(f"Enter the name of your main Node.js application file (e.g., {Theme.F(Theme.HIGHLIGHT, 'server.js, index.js')}):", default="index.js")
    if main_app_file is None: return None
    node_details['app_file'] = main_app_file
    if not os.path.exists(os.path.join(project_dir, main_app_file)):
         V_PRINT_FUNC(f"Warning: Main application file '{main_app_file}' not found in {project_dir}.")
         warning_msg = Theme.F(Theme.WARNING, f"Main file '{main_app_file}' not found. Continue anyway?")
         if not _ask(warning_msg, type='confirm', default=True):
            return None

    app_port_msg = f"What port does your application listen on inside the container (e.g., {Theme.F(Theme.HIGHLIGHT, '3000, 8080')})? Leave blank if none."
    app_port = _ask(app_port_msg, default="3000")
    if app_port is None and app_port != "": return None
    node_details['app_port'] = app_port if app_port else None

    node_details['install_command'] = _ask(
        "Which command to use for installing dependencies?",
        type='select',
        choices=["npm ci", "npm install", "yarn install"],
        default="npm ci"
    )
    if node_details['install_command'] is None: return None

    return node_details

def _get_html_css_js_details(common_details, project_dir):
    global V_PRINT_FUNC
    V_PRINT_FUNC("Gathering Vanilla HTML/CSS/JS specific details.")
    html_details = common_details.copy()

    web_server_choices = [
        questionary.Choice("nginx:alpine (recommended, lightweight)", value="nginx:alpine"),
        questionary.Choice("httpd:alpine (Apache, lightweight)", value="httpd:alpine"),
        "nginx:latest",
        "httpd:latest",
        "Custom"
    ]
    base_image_choice = _ask("Select base web server image:", type='select', choices=web_server_choices, default="nginx:alpine")
    if base_image_choice is None: return None
    if base_image_choice == "Custom":
        custom_image = _ask(f"Enter custom web server base image (e.g., {Theme.F(Theme.HIGHLIGHT, 'my-custom-nginx:tag')}):")
        if custom_image is None: return None
        html_details['base_image'] = custom_image
    else:
        html_details['base_image'] = base_image_choice

    html_details['base_server_type'] = 'nginx' if 'nginx' in html_details['base_image'] else \
                                     'apache' if 'httpd' in html_details['base_image'] else \
                                     'unknown'

    static_dir_msg = f"Enter the directory containing your static HTML/CSS/JS files (e.g., {Theme.F(Theme.HIGHLIGHT, 'public, dist, .')} for current dir):"
    static_dir = _ask(static_dir_msg, default=".")
    if static_dir is None: return None
    html_details['static_dir'] = static_dir.strip() if static_dir else "." # Ensure it's never empty string, default to .

    # Check if index.html exists in the specified static_dir
    index_html_path = os.path.join(project_dir, html_details['static_dir'], "index.html")
    if not os.path.exists(index_html_path):
        V_PRINT_FUNC(f"Warning: 'index.html' not found in '{os.path.join(html_details['static_dir'])}'.")
        warning_msg = Theme.F(Theme.WARNING, f"'index.html' not found in the specified directory '{html_details['static_dir']}'. Continue anyway?")
        if not _ask(warning_msg, type='confirm', default=True):
            return None

    app_port_msg = f"What port will the web server listen on inside the container (usually {Theme.F(Theme.HIGHLIGHT, '80')})?"
    app_port = _ask(app_port_msg, default="80")
    if app_port is None and app_port != "": return None # Allow empty for no EXPOSE
    html_details['app_port'] = app_port if app_port else None

    return html_details


def _get_generic_details(common_details, project_dir):
    global V_PRINT_FUNC
    V_PRINT_FUNC("Gathering Generic project details.")
    gen_details = common_details.copy()

    gen_details['base_image'] = _ask(f"Enter the base image for your project (e.g., {Theme.F(Theme.HIGHLIGHT, 'ubuntu:latest, alpine:3.18')}):")
    if not gen_details['base_image']: return None

    gen_details['workdir'] = _ask("Set the working directory inside the container:", default="/app")
    if gen_details['workdir'] is None: return None

    copy_source_msg = f"What to copy from your project directory into the container's working directory? (e.g., {Theme.F(Theme.HIGHLIGHT, '.')}) for all, '{Theme.F(Theme.HIGHLIGHT, 'app/')}' for a subfolder)"
    copy_source = _ask(copy_source_msg, default=".")
    if copy_source is None: return None
    gen_details['copy_source'] = copy_source
    gen_details['copy_destination'] = "."

    build_commands_str = _ask(f"Enter any build commands to run after copying files (one per line, or leave blank if none):", type='text', multiline=True) # prompt_toolkit multiline
    gen_details['build_commands'] = [cmd.strip() for cmd in build_commands_str.splitlines() if cmd.strip()] if build_commands_str else []


    run_command_str = _ask(f"Enter the command to run your application (e.g., {Theme.F(Theme.HIGHLIGHT, './mybinary -p 80')}, '{Theme.F(Theme.HIGHLIGHT, 'java -jar app.jar')}'):")
    if not run_command_str: return None
    gen_details['run_command_array'] = [part.strip() for part in run_command_str.split()]


    app_port = _ask("What port does your application listen on (for EXPOSE)? Leave blank if none.", default="")
    if app_port is None and app_port != "": return None
    gen_details['app_port'] = app_port if app_port else None

    return gen_details

def _generate_dockerfile_content(details):
    global V_PRINT_FUNC
    V_PRINT_FUNC(f"Generating Dockerfile for project type: {details['project_type']}")
    lines = []
    project_type = details['project_type']

    if project_type == "Python":
        lines.append(f"# Use an official Python runtime as a parent image")
        lines.append(f"FROM {details['base_image']}")
        lines.append(f"\n# Set the working directory in the container")
        lines.append(f"WORKDIR /app")
        if details.get('requirements_file'):
            lines.append(f"\n# Copy the dependencies file to the working directory")
            lines.append(f"COPY {details['requirements_file']} .")
            lines.append(f"\n# Install any needed packages specified in {details['requirements_file']}")
            lines.append(f"RUN pip install --no-cache-dir -r {details['requirements_file']}")
        else:
            lines.append(f"\n# No requirements file specified. Skipping pip install step.")
            lines.append(f"# If you have dependencies, add a COPY and RUN pip install command here.")
        lines.append(f"\n# Copy the current directory contents into the container at /app")
        lines.append(f"COPY . .")
        if details.get('app_port'):
            lines.append(f"\n# Make port {details['app_port']} available to the world outside this container")
            lines.append(f"EXPOSE {details['app_port']}")
        lines.append(f"\n# Define environment variable")
        lines.append(f"ENV PYTHONUNBUFFERED=1")
        lines.append(f"\n# Run {details['app_file']} when the container launches")
        lines.append(f'CMD ["python", "{details["app_file"]}"]')

    elif project_type == "Node.js":
        lines.append(f"# Use an official Node.js runtime as a parent image")
        lines.append(f"FROM {details['base_image']}")
        lines.append(f"\n# Set the working directory")
        lines.append(f"WORKDIR /usr/src/app")
        lines.append(f"\n# Copy package.json and package-lock.json (or yarn.lock)")
        lines.append(f"COPY {details['package_file']} .")
        project_dir_for_check = details.get('project_dir', '.')
        if "npm ci" in details['install_command'] or "npm install" in details['install_command']:
            if os.path.exists(os.path.join(project_dir_for_check, "package-lock.json")):
                 lines.append(f"COPY package-lock.json .")
        elif "yarn install" in details['install_command']:
            if os.path.exists(os.path.join(project_dir_for_check, "yarn.lock")):
                 lines.append(f"COPY yarn.lock .")

        lines.append(f"\n# Install dependencies")
        lines.append(f"RUN {details['install_command']}")
        lines.append(f"\n# Bundle app source")
        lines.append(f"COPY . .")
        if details.get('app_port'):
            lines.append(f"\nEXPOSE {details['app_port']}")
        lines.append(f'\nCMD [ "node", "{details["app_file"]}" ]')

    elif project_type == "Vanilla HTML/CSS/JS":
        lines.append(f"# Use {details['base_server_type']} server as a parent image")
        lines.append(f"FROM {details['base_image']}")

        doc_root = "/usr/share/nginx/html" # Default for Nginx
        if details['base_server_type'] == 'apache':
            doc_root = "/usr/local/apache2/htdocs"
        elif details['base_server_type'] == 'unknown':
            V_PRINT_FUNC(f"Warning: Unknown web server type for base image {details['base_image']}. Assuming Nginx-like doc root: {doc_root}. You may need to adjust.")
            lines.append(f"\n# NOTE: Document root for {details['base_image']} is assumed to be {doc_root}. Adjust if necessary.")


        lines.append(f"\n# Remove default static content from the server image (if any)")
        lines.append(f"RUN rm -rf {doc_root}/*") # Be careful with rm -rf

        source_dir = details['static_dir']
        # Ensure source_dir ends with a slash if it's a directory, for rsync-like behavior of COPY
        if source_dir != "." and not source_dir.endswith('/'):
            source_dir_for_copy = source_dir + "/"
        else:
            source_dir_for_copy = source_dir

        lines.append(f"\n# Copy static files from '{source_dir}' to '{doc_root}'")
        lines.append(f"COPY {source_dir_for_copy} {doc_root}/")

        if details.get('app_port'):
            lines.append(f"\n# Expose port {details['app_port']}")
            lines.append(f"EXPOSE {details['app_port']}")

        lines.append(f"\n# The base image ({details['base_image']}) should handle starting the server.")
        lines.append(f"# For Nginx, the default CMD is usually `nginx -g 'daemon off;'`")
        lines.append(f"# For Apache (httpd), it's usually `httpd-foreground`")

    elif project_type == "Generic (manual setup)":
        lines.append(f"# Base image")
        lines.append(f"FROM {details['base_image']}")
        lines.append(f"\n# Set working directory")
        lines.append(f"WORKDIR {details['workdir']}")
        lines.append(f"\n# Copy application files")
        lines.append(f"COPY {details['copy_source']} {details['copy_destination']}")
        if details['build_commands']:
            lines.append(f"\n# Run build commands")
            for cmd in details['build_commands']:
                lines.append(f"RUN {cmd}")
        if details.get('app_port'):
            lines.append(f"\n# Expose port")
            lines.append(f"EXPOSE {details['app_port']}")
        cmd_str = ", ".join([f'"{p}"' for p in details['run_command_array']])
        lines.append(f"\n# Run command")
        lines.append(f"CMD [{cmd_str}]")

    return "\n".join(lines)

def create_docker_project_interactive(project_dir: str, v_print_func_param):
    global V_PRINT_FUNC
    V_PRINT_FUNC = v_print_func_param

    V_PRINT_FUNC(f"Starting interactive Docker project creation in: {project_dir}")
    results = {
        "dockerfile_path": None, "dockerignore_path": None,
        "dockerfile_content": None, "dockerignore_content": None,
        "build_command": None, "run_command": None,
        "summary_message": "", "error_message": None,
        "actions_log": [] # To log build/run actions
    }

    print(f"\n{Theme.F(Theme.SECTION_HEADER, f'--- Docker Project Initialization for: {Theme.H_TEXT(project_dir)} ---')}")
    print("Let's gather some information to create a Dockerfile and .dockerignore file.")

    common_details = _get_common_details(project_dir)
    if not common_details:
        results['error_message'] = "Project creation cancelled during common details."
        results['summary_message'] = Theme.F(Theme.WARNING,"Project creation cancelled.")
        return results

    common_details['project_dir'] = project_dir

    project_details = None
    if common_details['project_type'] == "Python":
        project_details = _get_python_details(common_details, project_dir)
    elif common_details['project_type'] == "Node.js":
        project_details = _get_nodejs_details(common_details, project_dir)
    elif common_details['project_type'] == "Vanilla HTML/CSS/JS":
        project_details = _get_html_css_js_details(common_details, project_dir)
    elif common_details['project_type'] == "Generic (manual setup)":
        project_details = _get_generic_details(common_details, project_dir)

    if not project_details:
        results['error_message'] = "Project creation cancelled during type-specific details."
        results['summary_message'] = Theme.F(Theme.WARNING, "Project creation cancelled.")
        return results

    dockerfile_content = _generate_dockerfile_content(project_details)
    results['dockerfile_content'] = dockerfile_content
    print(f"\n{Theme.F(Theme.SECTION_HEADER, '--- Generated Dockerfile ---')}")
    print(Theme.F(AnsiColors.DIM, dockerfile_content))
    print(f"{Theme.F(Theme.SECTION_HEADER, '--- End of Dockerfile ---')}")


    if _ask("\nWrite this Dockerfile?", type='confirm', default=True):
        dockerfile_path = os.path.join(project_dir, "Dockerfile")
        try:
            with open(dockerfile_path, "w") as f:
                f.write(dockerfile_content)
            results['dockerfile_path'] = dockerfile_path
            msg = f"Dockerfile saved to: {dockerfile_path}"
            results['actions_log'].append(msg)
            print(Theme.F(Theme.SUCCESS, msg))
        except IOError as e:
            results['error_message'] = f"Error writing Dockerfile: {e}"
            print(Theme.F(Theme.ERROR, f"ERROR: Could not write Dockerfile: {e}"))
            return results
    else:
        msg = "Dockerfile creation skipped by user."
        results['actions_log'].append(msg)
        print(Theme.F(Theme.WARNING, msg))


    if _ask("\nCreate a .dockerignore file? (Recommended)", type='confirm', default=True):
        dockerignore_content = _generate_default_dockerignore_content()
        results['dockerignore_content'] = dockerignore_content

        print(f"\n{Theme.F(Theme.SECTION_HEADER, '--- Default .dockerignore ---')}")
        print(Theme.F(AnsiColors.DIM, dockerignore_content))
        print(f"{Theme.F(Theme.SECTION_HEADER, '--- End of .dockerignore ---')}")


        if _ask("Write this .dockerignore file?", type='confirm', default=True):
            dockerignore_path = os.path.join(project_dir, ".dockerignore")
            try:
                with open(dockerignore_path, "w") as f:
                    f.write(dockerignore_content)
                results['dockerignore_path'] = dockerignore_path
                msg = f".dockerignore saved to: {dockerignore_path}"
                results['actions_log'].append(msg)
                print(Theme.F(Theme.SUCCESS, msg))
            except IOError as e:
                err_msg = f"Error writing .dockerignore: {e}"
                print(Theme.F(Theme.WARNING, f"Warning: Could not write .dockerignore: {err_msg}"))
                results['actions_log'].append(f"Failed to write .dockerignore: {err_msg}")
                if results['error_message']: results['error_message'] += f"; {err_msg}"
                else: results['error_message'] = err_msg
        else:
            msg = ".dockerignore creation skipped by user."
            results['actions_log'].append(msg)
            print(Theme.F(Theme.WARNING, msg))
    else:
        msg = ".dockerignore creation skipped by user."
        results['actions_log'].append(msg)
        print(Theme.F(Theme.WARNING, msg))


    image_name = project_details['project_name']
    build_command = f"docker build -t {image_name} ."
    results['build_command'] = build_command

    run_command_parts = ["docker run -d"] # Default to detached
    host_port = project_details.get('app_port') # This is the container port
    container_port = project_details.get('app_port')

    if container_port:
        # For static sites, common host ports are 80, 8080, or similar.
        default_host_port_suggestion = "8080" # A common alternative if 80 is taken
        if str(container_port) == "80": # If container exposes 80
             # Suggest 8080 by default if container port is 80, otherwise suggest the container port itself.
             pass # default_host_port_suggestion is already 8080
        elif container_port:
             default_host_port_suggestion = str(container_port)

        ask_msg = f"Host port to map to container port {Theme.F(Theme.HIGHLIGHT, str(container_port))}? (e.g., {Theme.F(Theme.HIGHLIGHT, default_host_port_suggestion)} or blank to skip)"
        asked_host_port_answer = _ask(
            ask_msg,
            default=default_host_port_suggestion
        )

        if asked_host_port_answer is None: # User pressed Esc
            msg = "Port mapping setup cancelled for run command."
            results['actions_log'].append(msg)
            print(Theme.F(Theme.WARNING, msg))
        elif asked_host_port_answer.strip():
            try:
                int(asked_host_port_answer) # Validate it's a number
                run_command_parts.append(f"-p {asked_host_port_answer.strip()}:{container_port}")
            except ValueError:
                msg = f"Invalid host port '{asked_host_port_answer}'. Port mapping skipped."
                results['actions_log'].append(msg)
                print(Theme.F(Theme.WARNING, msg))
        else: # User entered blank
            msg = "Port mapping skipped for run command."
            results['actions_log'].append(msg)
            print(Theme.F(Theme.MUTED_SYSTEM_INFO, msg))


    run_command_parts.append(f"--name {image_name}-container") # Add a default name
    run_command_parts.append(image_name)
    run_command = " ".join(run_command_parts)
    results['run_command'] = run_command

    summary = []
    if results['dockerfile_path']:
        summary.append(Theme.F(Theme.SUCCESS, f"Dockerfile created at: {results['dockerfile_path']}"))
    else:
        summary.append(Theme.F(Theme.WARNING,"Dockerfile was not created or creation was skipped."))

    if results['dockerignore_path']:
        summary.append(Theme.F(Theme.SUCCESS, f".dockerignore created at: {results['dockerignore_path']}"))
    else:
        summary.append(Theme.F(Theme.WARNING,".dockerignore was not created (or failed/skipped)."))

    summary.append(f"\nSuggested command to build your Docker image:\n  {Theme.F(Theme.COMMAND, build_command)}")
    summary.append(f"Suggested command to run your Docker container (adjust as needed):\n  {Theme.F(Theme.COMMAND, run_command)}")

    results['summary_message'] = "\n".join(summary)
    if not results['summary_message'].strip() and results.get('error_message'):
        # Error message already themed from where it was set
        results['summary_message'] = results['error_message']
    elif not results['summary_message'].strip():
        results['summary_message'] = Theme.F(Theme.MUTED_SYSTEM_INFO,"Project setup process completed or cancelled without creating files.")

    print(f"\n{Theme.F(Theme.SECTION_HEADER, '--- Docker Project Setup Complete ---')}")
    print(results['summary_message']) # Already themed parts

    if results['actions_log']:
        V_PRINT_FUNC("Actions Log from Creator:") # v_print itself is themed
        for log_entry in results['actions_log']:
            if "ERROR:" in log_entry or "Failed to" in log_entry or "Warning:" in log_entry :
                 V_PRINT_FUNC(f"- {Theme.F(Theme.WARNING, log_entry)}") # Warning for verbose log
            elif "saved to" in log_entry or "created at" in log_entry:
                 V_PRINT_FUNC(f"- {Theme.F(Theme.SUCCESS, log_entry)}")
            else:
                 V_PRINT_FUNC(f"- {log_entry}")


    return results

if __name__ == '__main__':
    try:
        import colorama
        colorama.init(autoreset=True)
    except ImportError:
        pass

    def _test_v_print(message, **kwargs):
        exc_info_flag = kwargs.pop('exc_info', False)
        print(f"{Theme.VERBOSE_PREFIX}[V_TEST] {message}{AnsiColors.RESET}", **kwargs)
        if exc_info_flag:
            import traceback
            traceback.print_exc()

    test_dir = "test_docker_project"
    os.makedirs(test_dir, exist_ok=True)
    print(f"Testing Docker project creator in: {Theme.F(Theme.HIGHLIGHT, os.path.abspath(test_dir))}")

    # Create dummy files for different project types to test auto-detection/warnings
    # Python
    if not os.path.exists(os.path.join(test_dir, "requirements.txt")):
        with open(os.path.join(test_dir, "requirements.txt"), "w") as f:
            f.write("flask\n")
    if not os.path.exists(os.path.join(test_dir, "app.py")):
        with open(os.path.join(test_dir, "app.py"), "w") as f:
            f.write("print('hello from app.py')\n")

    # Node.js
    if not os.path.exists(os.path.join(test_dir, "package.json")):
        with open(os.path.join(test_dir, "package.json"), "w") as f:
            f.write('{ "name": "test-node-app", "main": "index.js" }')
    if not os.path.exists(os.path.join(test_dir, "index.js")):
        with open(os.path.join(test_dir, "index.js"), "w") as f:
            f.write("console.log('hello from index.js');\n")
    
    # HTML/CSS/JS
    html_static_dir = os.path.join(test_dir, "public_html")
    os.makedirs(html_static_dir, exist_ok=True)
    if not os.path.exists(os.path.join(html_static_dir, "index.html")):
        with open(os.path.join(html_static_dir, "index.html"), "w") as f:
            f.write("<h1>Hello from HTML!</h1>")


    output_results = create_docker_project_interactive(test_dir, _test_v_print)

    print(f"\n{Theme.F(Theme.SECTION_HEADER, '--- Function Output (from docker_project_creator) ---')}")
    for key, value in output_results.items():
        if key.endswith('_content') and value:
            print(f"{Theme.F(Theme.MUTED_SYSTEM_INFO, f'{key}: Present (content not shown)')}")
        else:
            print(f"{Theme.F(Theme.MUTED_SYSTEM_INFO, f'{key}: {value}')}")

    # import shutil
    # shutil.rmtree(test_dir)
    # print(f"\nCleaned up {test_dir}")
