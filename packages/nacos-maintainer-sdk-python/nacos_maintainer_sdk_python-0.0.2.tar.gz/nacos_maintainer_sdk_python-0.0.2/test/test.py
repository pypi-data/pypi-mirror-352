from maintainer.common.ai_maintainer_client_config import AIMaintainerClientConfig
from maintainer.common.ai_maintainer_client_config_builder import AIMaintainerClientConfigBuilder
from maintainer.ai.model.nacos_mcp_info import McpServerBasicInfo
from maintainer.ai.nacos_mcp_service import NacosAIMaintainerService


async def main():
	ai_client_config = AIMaintainerClientConfigBuilder().server_address("11.161.207.61:8848").username('nacos').password('nacosopensource').build()
	mcp_service = await NacosAIMaintainerService.create_mcp_service(ai_client_config)
	a=await mcp_service.get_mcp_server_detail("public", "amap-mcp-server", "0.1.0")
	# await mcp_service.create_mcp_server("public","public",McpServerBasicInfo(),None,None)
	print(a)
	return await mcp_service.list_mcp_servers("public", "", 1, 10)

if __name__ == '__main__':
	import asyncio
	print(asyncio.run(main()))
