"""
Core functionality for Promptplex - AI prompt management library.
"""

import json
import os
import hashlib
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import yaml
from datetime import datetime


@dataclass
class PromptTemplate:
    """A prompt template with versioning and validation."""
    
    name: str
    template: str
    variables: List[str]
    version: str = "1.0"
    description: str = ""
    tags: List[str] = None
    created_at: str = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
            
    def render(self, **kwargs) -> str:
        """Render the template with provided variables."""
        missing_vars = set(self.variables) - set(kwargs.keys())
        if missing_vars:
            raise ValueError(f"Missing required variables: {missing_vars}")
            
        extra_vars = set(kwargs.keys()) - set(self.variables)
        if extra_vars:
            raise ValueError(f"Unknown variables provided: {extra_vars}")
            
        return self.template.format(**kwargs)
    
    def validate(self) -> bool:
        """Validate that template contains all declared variables."""
        try:
            # Try to format with dummy values to check for syntax errors
            dummy_values = {var: f"__{var}__" for var in self.variables}
            self.template.format(**dummy_values)
            return True
        except (KeyError, ValueError) as e:
            raise ValueError(f"Template validation failed: {e}")
    
    def get_hash(self) -> str:
        """Get a hash of the template content for change detection."""
        content = f"{self.template}{self.variables}{self.version}"
        return hashlib.md5(content.encode()).hexdigest()


class PromptManager:
    """Manages prompt templates with versioning and persistence."""
    
    def __init__(self, storage_path: str = ".promptplex"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)
        self.templates: Dict[str, PromptTemplate] = {}
        self.load_templates()
    
    def add_template(self, template: PromptTemplate) -> None:
        """Add a new template or update existing one."""
        template.validate()
        self.templates[template.name] = template
        self.save_template(template)
    
    def get_template(self, name: str, version: Optional[str] = None) -> PromptTemplate:
        """Get a template by name and optionally version."""
        if name not in self.templates:
            raise ValueError(f"Template '{name}' not found")
            
        template = self.templates[name]
        if version and template.version != version:
            # Try to load specific version from storage
            versioned_template = self.load_template_version(name, version)
            if versioned_template:
                return versioned_template
            raise ValueError(f"Version '{version}' of template '{name}' not found")
            
        return template
    
    def list_templates(self) -> List[str]:
        """List all available template names."""
        return list(self.templates.keys())
    
    def delete_template(self, name: str) -> None:
        """Delete a template."""
        if name in self.templates:
            del self.templates[name]
            template_file = self.storage_path / f"{name}.yaml"
            if template_file.exists():
                template_file.unlink()
    
    def save_template(self, template: PromptTemplate) -> None:
        """Save template to storage."""
        template_file = self.storage_path / f"{template.name}.yaml"
        with open(template_file, 'w') as f:
            yaml.dump(asdict(template), f, default_flow_style=False)
    
    def load_templates(self) -> None:
        """Load all templates from storage."""
        for template_file in self.storage_path.glob("*.yaml"):
            try:
                with open(template_file, 'r') as f:
                    data = yaml.safe_load(f)
                    template = PromptTemplate(**data)
                    self.templates[template.name] = template
            except Exception as e:
                print(f"Warning: Could not load template from {template_file}: {e}")
    
    def load_template_version(self, name: str, version: str) -> Optional[PromptTemplate]:
        """Load a specific version of a template."""
        # This would be enhanced to support actual version history
        # For now, just return None if version doesn't match current
        return None
    
    def export_templates(self, filepath: str) -> None:
        """Export all templates to a file."""
        export_data = {name: asdict(template) for name, template in self.templates.items()}
        with open(filepath, 'w') as f:
            if filepath.endswith('.json'):
                json.dump(export_data, f, indent=2)
            else:
                yaml.dump(export_data, f, default_flow_style=False)
    
    def import_templates(self, filepath: str) -> None:
        """Import templates from a file."""
        with open(filepath, 'r') as f:
            if filepath.endswith('.json'):
                data = json.load(f)
            else:
                data = yaml.safe_load(f)
        
        for name, template_data in data.items():
            template = PromptTemplate(**template_data)
            self.add_template(template)


class PromptTester:
    """Test prompt templates with different inputs and track results."""
    
    def __init__(self, manager: PromptManager):
        self.manager = manager
        self.test_results = []
    
    def test_template(self, template_name: str, test_cases: List[Dict[str, Any]], 
                     evaluator: Optional[callable] = None) -> List[Dict]:
        """Test a template with multiple input cases."""
        template = self.manager.get_template(template_name)
        results = []
        
        for i, test_case in enumerate(test_cases):
            try:
                rendered = template.render(**test_case)
                result = {
                    'test_case': i,
                    'inputs': test_case,
                    'output': rendered,
                    'success': True,
                    'error': None
                }
                
                if evaluator:
                    result['evaluation'] = evaluator(rendered, test_case)
                    
                results.append(result)
                
            except Exception as e:
                results.append({
                    'test_case': i,
                    'inputs': test_case,
                    'output': None,
                    'success': False,
                    'error': str(e)
                })
        
        self.test_results.extend(results)
        return results
    
    def compare_templates(self, template_names: List[str], test_cases: List[Dict[str, Any]]) -> Dict:
        """Compare multiple templates with the same test cases."""
        comparison = {}
        
        for template_name in template_names:
            comparison[template_name] = self.test_template(template_name, test_cases)
        
        return comparison


# Convenience functions
def create_template(name: str, template: str, variables: List[str], **kwargs) -> PromptTemplate:
    """Quick way to create a template."""
    return PromptTemplate(name=name, template=template, variables=variables, **kwargs)


def quick_render(template_str: str, **kwargs) -> str:
    """Quick way to render a template string without creating a PromptTemplate object."""
    return template_str.format(**kwargs)


# Example usage and built-in templates
BUILTIN_TEMPLATES = {
    "code_review": PromptTemplate(
        name="code_review",
        template="""Review this {language} code and provide feedback:

{code}

Focus on: {focus_areas}

Provide specific suggestions for improvement.""",
        variables=["language", "code", "focus_areas"],
        description="Template for code review prompts",
        tags=["code", "review", "development"]
    ),
    
    "summarize": PromptTemplate(
        name="summarize",
        template="""Summarize the following text in {length} sentences:

{text}

Summary:""",
        variables=["text", "length"],
        description="Template for text summarization",
        tags=["summarization", "text"]
    ),
    
    "chat_assistant": PromptTemplate(
        name="chat_assistant",
        template="""You are a helpful assistant with expertise in {domain}.

User: {user_message}

Please provide a helpful, accurate response. {additional_instructions}""",
        variables=["domain", "user_message", "additional_instructions"],
        description="Template for chat assistant prompts",
        tags=["chat", "assistant", "general"]
    )
}


def setup_builtin_templates(manager: PromptManager) -> None:
    """Add built-in templates to a manager."""
    for template in BUILTIN_TEMPLATES.values():
        manager.add_template(template)