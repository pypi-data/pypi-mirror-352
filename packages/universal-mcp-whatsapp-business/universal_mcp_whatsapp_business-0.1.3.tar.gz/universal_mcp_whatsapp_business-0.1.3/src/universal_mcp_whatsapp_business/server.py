
from universal_mcp.integrations import ApiKeyIntegration
from universal_mcp.servers import SingleMCPServer
from universal_mcp.stores import EnvironmentStore

from universal_mcp_whatsapp_business.app import WhatsappBusinessApp

env_store = EnvironmentStore()
integration_instance = ApiKeyIntegration(name="WHATSAPP_BUSINESS_API_KEY", store=env_store)
app_instance = WhatsappBusinessApp(integration=integration_instance)

mcp = SingleMCPServer(
    app_instance=app_instance,
)

if __name__ == "__main__":
    mcp.run()


