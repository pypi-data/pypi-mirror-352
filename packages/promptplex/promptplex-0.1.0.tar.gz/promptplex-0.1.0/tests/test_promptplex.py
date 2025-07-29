"""
Test suite for Promptplex
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from promptplex import PromptManager, PromptTemplate, PromptTester, setup_builtin_templates


class TestPromptTemplate:
    """Test PromptTemplate functionality."""
    
    def test_template_creation(self):
        """Test basic template creation."""
        template = PromptTemplate(
            name="test",
            template="Hello {name}!",
            variables=["name"]
        )
        assert template.name == "test"
        assert template.variables == ["name"]
    
    def test_template_rendering(self):
        """Test template rendering with variables."""
        template = PromptTemplate(
            name="greeting",
            template="Hello {name}, welcome to {place}!",
            variables=["name", "place"]
        )
        
        result = template.render(name="Alice", place="Wonderland")
        assert result == "Hello Alice, welcome to Wonderland!"
    
    def test_missing_variables(self):
        """Test error handling for missing variables."""
        template = PromptTemplate(
            name="test",
            template="Hello {name}!",
            variables=["name"]
        )
        
        with pytest.raises(ValueError, match="Missing required variables"):
            template.render()
    
    def test_extra_variables(self):
        """Test error handling for extra variables."""
        template = PromptTemplate(
            name="test",
            template="Hello {name}!",
            variables=["name"]
        )
        
        with pytest.raises(ValueError, match="Unknown variables provided"):
            template.render(name="Alice", extra="value")
    
    def test_template_validation(self):
        """Test template validation."""
        template = PromptTemplate(
            name="valid",
            template="Hello {name}!",
            variables=["name"]
        )
        assert template.validate() is True
    
    def test_template_hash(self):
        """Test template hash generation."""
        template = PromptTemplate(
            name="test",
            template="Hello {name}!",
            variables=["name"]
        )
        hash1 = template.get_hash()
        hash2 = template.get_hash()
        assert hash1 == hash2
        
        # Different template should have different hash
        template2 = PromptTemplate(
            name="test2",
            template="Hi {name}!",
            variables=["name"]
        )
        assert template.get_hash() != template2.get_hash()


class TestPromptManager:
    """Test PromptManager functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = PromptManager(storage_path=self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_add_template(self):
        """Test adding templates to manager."""
        template = PromptTemplate(
            name="test",
            template="Hello {name}!",
            variables=["name"]
        )
        
        self.manager.add_template(template)
        assert "test" in self.manager.list_templates()
    
    def test_get_template(self):
        """Test retrieving templates from manager."""
        template = PromptTemplate(
            name="greeting",
            template="Hello {name}!",
            variables=["name"]
        )
        
        self.manager.add_template(template)
        retrieved = self.manager.get_template("greeting")
        assert retrieved.name == "greeting"
        assert retrieved.template == "Hello {name}!"
    
    def test_template_not_found(self):
        """Test error handling for missing templates."""
        with pytest.raises(ValueError, match="Template 'nonexistent' not found"):
            self.manager.get_template("nonexistent")
    
    def test_delete_template(self):
        """Test template deletion."""
        template = PromptTemplate(
            name="to_delete",
            template="Hello {name}!",
            variables=["name"]
        )
        
        self.manager.add_template(template)
        assert "to_delete" in self.manager.list_templates()
        
        self.manager.delete_template("to_delete")
        assert "to_delete" not in self.manager.list_templates()
    
    def test_persistence(self):
        """Test template persistence across manager instances."""
        template = PromptTemplate(
            name="persistent",
            template="Hello {name}!",
            variables=["name"]
        )
        
        self.manager.add_template(template)
        
        # Create new manager with same storage path
        new_manager = PromptManager(storage_path=self.temp_dir)
        assert "persistent" in new_manager.list_templates()
        
        retrieved = new_manager.get_template("persistent")
        assert retrieved.name == "persistent"
    
    def test_export_import(self):
        """Test template export and import."""
        template = PromptTemplate(
            name="exportable",
            template="Hello {name}!",
            variables=["name"]
        )
        
        self.manager.add_template(template)
        
        export_file = Path(self.temp_dir) / "export.yaml"
        self.manager.export_templates(str(export_file))
        assert export_file.exists()
        
        # Create new manager and import
        new_manager = PromptManager(storage_path=tempfile.mkdtemp())
        new_manager.import_templates(str(export_file))
        assert "exportable" in new_manager.list_templates()


class TestPromptTester:
    """Test PromptTester functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.manager = PromptManager(storage_path=self.temp_dir)
        self.tester = PromptTester(self.manager)
    
    def teardown_method(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
    
    def test_template_testing(self):
        """Test template testing with multiple cases."""
        template = PromptTemplate(
            name="greeting",
            template="Hello {name}!",
            variables=["name"]
        )
        
        self.manager.add_template(template)
        
        test_cases = [
            {"name": "Alice"},
            {"name": "Bob"}
        ]
        
        results = self.tester.test_template("greeting", test_cases)
        assert len(results) == 2
        assert all(result['success'] for result in results)
        assert results[0]['output'] == "Hello Alice!"
        assert results[1]['output'] == "Hello Bob!"
    
    def test_template_testing_with_errors(self):
        """Test template testing with error cases."""
        template = PromptTemplate(
            name="greeting",
            template="Hello {name}!",
            variables=["name"]
        )
        
        self.manager.add_template(template)
        
        test_cases = [
            {"name": "Alice"},
            {"wrong_var": "Bob"}  # This should fail
        ]
        
        results = self.tester.test_template("greeting", test_cases)
        assert len(results) == 2
        assert results[0]['success'] is True
        assert results[1]['success'] is False
        assert results[1]['error'] is not None
    
    def test_template_comparison(self):
        """Test comparing multiple templates."""
        template1 = PromptTemplate(
            name="greeting1",
            template="Hello {name}!",
            variables=["name"]
        )
        
        template2 = PromptTemplate(
            name="greeting2",
            template="Hi {name}!",
            variables=["name"]
        )
        
        self.manager.add_template(template1)
        self.manager.add_template(template2)
        
        test_cases = [{"name": "Alice"}]
        
        comparison = self.tester.compare_templates(
            ["greeting1", "greeting2"], 
            test_cases
        )
        
        assert "greeting1" in comparison
        assert "greeting2" in comparison
        assert comparison["greeting1"][0]["output"] == "Hello Alice!"
        assert comparison["greeting2"][0]["output"] == "Hi Alice!"


class TestBuiltinTemplates:
    """Test built-in template functionality."""
    
    def test_setup_builtin_templates(self):
        """Test setting up built-in templates."""
        temp_dir = tempfile.mkdtemp()
        manager = PromptManager(storage_path=temp_dir)
        
        setup_builtin_templates(manager)
        
        templates = manager.list_templates()
        assert "code_review" in templates
        assert "summarize" in templates
        assert "chat_assistant" in templates
        
        # Test one of the templates
        code_review = manager.get_template("code_review")
        result = code_review.render(
            language="Python",
            code="def hello(): pass",
            focus_areas="style, performance"
        )
        assert "Python" in result
        assert "def hello(): pass" in result
        
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    pytest.main([__file__])