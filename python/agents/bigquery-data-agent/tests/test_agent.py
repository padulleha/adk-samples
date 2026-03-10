import pytest
from bigquery_data_agent.agent import app

def test_app_initialization():
    """Test that the application and agent initialize correctly."""
    assert app is not None
    assert app.name == "bigquery_data_agent"
    assert app.root_agent is not None
    assert app.root_agent.name == "bigquery_data_agent"

def test_plugins_and_tools():
    """Test that the BigQuery analytics plugin and BigQuery toolset are configured."""
    # Ensure plugins are attached
    assert len(app.plugins) > 0
    
    # Ensure BigQueryToolset is attached to the root agent
    assert len(app.root_agent.tools) > 0

def test_plugin_configuration():
    """Test that the BigQuery analytics plugin is properly configured."""
    from google.adk.plugins.bigquery_agent_analytics_plugin import BigQueryAgentAnalyticsPlugin
    
    # Assert that at least one plugin is the analytics plugin
    analytics_plugins = [p for p in app.plugins if isinstance(p, BigQueryAgentAnalyticsPlugin)]
    assert len(analytics_plugins) == 1
    
    plugin = analytics_plugins[0]
    assert plugin.dataset_id is not None
    assert plugin.project_id is not None
