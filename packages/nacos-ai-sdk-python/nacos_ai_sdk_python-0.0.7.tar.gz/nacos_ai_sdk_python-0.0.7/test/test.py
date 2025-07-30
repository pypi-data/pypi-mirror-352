from nacos_ai.common.ai_client_config import AIClientConfig
from nacos_ai.common.ai_client_config_builder import AIClientConfigBuilder
from nacos_ai.mcp.model.nacos_mcp_info import McpServerBasicInfo
from nacos_ai.mcp.nacos_mcp_service import NacosMcpService


async def main():
	ai_client_config = AIClientConfigBuilder().server_address("11.161.207.61:8848").username('nacos').password('nacosopensource').build()
	mcp_service = await NacosMcpService.create_mcp_service(ai_client_config)
	# a=await mcp_service.get_mcp_server_detail("public", "amap-mcp-server", "0.1.1")
	await mcp_service.create_mcp_server("public","public",McpServerBasicInfo(),None,None)
	# print(a)
	# return await mcp_service.list_mcp_servers("public", "", 1, 10)

if __name__ == '__main__':
	import asyncio
	print(asyncio.run(main()))
