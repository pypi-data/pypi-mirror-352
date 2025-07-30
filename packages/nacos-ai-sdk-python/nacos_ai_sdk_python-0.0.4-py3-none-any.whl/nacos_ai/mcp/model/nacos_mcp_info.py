from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

from nacos_ai.mcp.model.registry_mcp_info import Repository, ServerVersionDetail


class McpCapability(Enum):
	TOOL = "TOOL"
	PROMPT = "PROMPT"
	RESOURCE = "RESOURCE"


class McpEndpointInfo(BaseModel):
	address: Optional[str]
	port: Optional[int]
	path: Optional[str]


class McpServiceRef(BaseModel):
	namespaceId: Optional[str]
	groupName: Optional[str]
	serviceName: Optional[str]


class McpEndpointSpec(BaseModel):
	type: Optional[str]
	data: Optional[Dict[str, str]]


class McpServerRemoteServiceConfig(BaseModel):
	serviceRef: Optional[McpServiceRef]
	exportPath: Optional[str]


class McpServerBasicInfo(BaseModel):
	id: Optional[str]
	name: Optional[str]
	protocol: Optional[str]
	frontProtocol: Optional[str]
	description: Optional[str]
	repository: Optional[Repository]
	versionDetail: Optional[ServerVersionDetail]
	version: Optional[str]
	remoteServerConfig: Optional[McpServerRemoteServiceConfig]
	localServerConfig: Optional[Dict[str, Any]]
	enabled: Optional[bool]
	capabilities: Optional[List[McpCapability]]


class McpServerVersionInfo(McpServerBasicInfo):
	latestPublishedVersion: Optional[str]
	versionDetails: Optional[List[ServerVersionDetail]]


class McpTool(BaseModel):
	name: Optional[str]
	description: Optional[str]
	inputSchema: Optional[Dict[str, Any]]


class McpToolMeta(BaseModel):
	invokeContext: Optional[Dict[str, Any]]
	enabled: Optional[bool]
	templates: Optional[Dict[str, Any]]


class McpToolSpecification(BaseModel):
	tools: Optional[List[McpTool]]
	toolsMeta: Optional[Dict[str, McpToolMeta]]


class McpServerDetailInfo(McpServerBasicInfo):
	backendEndpoints: Optional[List[McpEndpointInfo]]
	toolSpec: Optional[McpToolSpecification]
	allVersions: Optional[List[ServerVersionDetail]]
	namespaceId: Optional[str]
