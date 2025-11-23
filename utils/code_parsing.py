import os

def extract_components(repo_path):
    """
    Dummy static code component extractor with stub descriptions,
    Should parse and return list of components with metadata.
    Example output: [{"name": "UserService", "type": "class", "description": "..."}]
    """
    # For demo, list Python files and mock components
    components = []
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith(".py"):
                components.append({
                    "name": file,
                    "type": "Python Module",
                    "description": f"Parsed module from {file}"
                })
    return components

def extract_api_inventory(repo_path):
    """
    Scan for API endpoints: For example, inspect Flask/Django decorators or Java Spring controllers.
    Here we mock results for demonstration.
    """
    apis = [
        {"endpoint": "/api/v1/users", "method": "GET", "description": "Fetch users"},
        {"endpoint": "/api/v1/orders", "method": "POST", "description": "Create new order"}
    ]
    return apis

def extract_configs(repo_path):
    """
    Scan for typical config files and return their contents.
    """
    configs = []
    for root, _, files in os.walk(repo_path):
        for file in files:
            if file.endswith((".yaml", ".yml", ".json", ".env")):
                try:
                    with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                        content = f.read()
                    configs.append({
                        "filename": file,
                        "content": content
                    })
                except Exception as e:
                    continue
    return configs