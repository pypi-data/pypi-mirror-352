from nacos_ai.common.ai_client_config import AIClientConfig
from nacos_ai.common.ai_client_config_builder import AIClientConfigBuilder
from nacos_ai.mcp.nacos_mcp_service import NacosMcpService


async def main():
	ai_client_config = AIClientConfigBuilder().server_address("11.161.207.61:8848").username('nacos').password('nacosopensource').build()
	mcp_service = await NacosMcpService.create_mcp_service(ai_client_config)
	return await mcp_service.list_mcp_servers("public", "", 1, 10)

if __name__ == '__main__':
	import asyncio
	print(asyncio.run(main()))
