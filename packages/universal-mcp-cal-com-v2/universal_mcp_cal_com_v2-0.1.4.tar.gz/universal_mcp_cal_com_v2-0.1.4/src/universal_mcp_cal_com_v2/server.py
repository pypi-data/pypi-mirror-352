
from universal_mcp.servers import SingleMCPServer
from universal_mcp.integrations import ApiKeyIntegration
from universal_mcp.stores import EnvironmentStore

from universal_mcp_cal_com_v2.app import CalComV2App

env_store = EnvironmentStore()
integration_instance = ApiKeyIntegration(name="CAL_COM_V2_API_KEY", store=env_store)
app_instance = CalComV2App(integration=integration_instance)

mcp = SingleMCPServer(
    app_instance=app_instance,
)

if __name__ == "__main__":
    mcp.run()


