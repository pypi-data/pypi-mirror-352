"""
Core functionality for image tag helper.
"""
import requests
import logging
from tenacity import retry, stop_after_attempt
from .config import config


logger = logging.getLogger(__name__)


@retry(stop=stop_after_attempt(7))
def get_image_tag_by_short_name(tag, arch, registry_url=None, repository=None, use_proxy=None):
    """
    Get the full image tag by short name.
    
    Args:
        tag: Short tag name
        arch: Architecture (e.g., amd64, arm64)
        registry_url: Registry URL, defaults to harbor.milvus.io
        repository: Repository path, defaults to milvus/milvus
        use_proxy: Override proxy setting (True/False/None for config default)
        
    Returns:
        Full tag name
    """
    registry_url = registry_url or "harbor.milvus.io"
    repository = repository or "milvus/milvus"
    
    logger.debug(f"Getting image tag for: tag={tag}, arch={arch}, registry={registry_url}, repository={repository}")
    
    # Split repository into project and repo
    repo_parts = repository.split('/')
    if len(repo_parts) != 2:
        error_msg = "Repository should be in format 'project/repository'"
        logger.error(error_msg)
        raise ValueError(error_msg)
    
    project, repo = repo_parts
    prefix = tag.split("-")[0]
    
    # Determine proxy settings
    proxies = _get_proxy_settings(use_proxy)
    
    # Different handling based on registry type
    if "harbor" in registry_url:
        logger.debug("Using Harbor registry API")
        return _get_harbor_tag(registry_url, project, repo, prefix, tag, arch, proxies)
    elif "docker" in registry_url:
        logger.debug("Using Docker Hub API")
        return _get_docker_tag(registry_url, repository, prefix, tag, arch, proxies)
    else:
        logger.debug("Using default Harbor-like API")
        return _get_harbor_tag(registry_url, project, repo, prefix, tag, arch, proxies)


def _get_proxy_settings(use_proxy):
    """
    Get proxy settings based on configuration and override.
    
    Args:
        use_proxy: Override proxy setting (True/False/None for config default)
        
    Returns:
        Proxy dictionary for requests
    """
    if use_proxy is False:
        # Explicit disable proxy
        return {'http': None, 'https': None}
    elif use_proxy is True:
        # Force enable proxy, use config settings
        proxy_settings = config.get_proxy_settings()
        if proxy_settings and proxy_settings.get('http') is None:
            # If config says disabled, return empty dict (use system proxy)
            return {}
        return proxy_settings or {}
    else:
        # Use config default
        return config.get_proxy_settings() or {}


def _get_harbor_tag(registry_url, project, repo, prefix, tag, arch, proxies):
    """Get tag from Harbor registry"""
    url = f"https://{registry_url}/api/v2.0/projects/{project}/repositories/{repo}/artifacts?with_tag=true&q=tags%253D~{prefix}-&page_size=100&page=1"
    
    logger.debug(f"Requesting Harbor API: {url}")
    if proxies:
        logger.debug(f"Using proxy settings: {proxies}")
    response = requests.get(url, proxies=proxies)
    response.raise_for_status()
    
    rsp = response.json()
    tag_list = []
    
    for r in rsp:
        tags = r["tags"]
        for t in tags:
            tag_list.append(t["name"])
    
    logger.debug(f"Found {len(tag_list)} tags matching prefix {prefix}")
    
    # First try: match both four-segment format and arch
    tag_candidates = []
    for t in tag_list:
        r = t.split("-")
        if len(r) == 4 and arch in t:  # version-date-commit-arch
            tag_candidates.append(t)
    
    tag_candidates.sort()
    if len(tag_candidates) > 0:
        logger.debug(f"Found {len(tag_candidates)} tags matching 4-segment format with arch {arch}")
        return tag_candidates[-1]
    
    # Second try: only match three-segment format if no matches found
    tag_candidates = []
    for t in tag_list:
        r = t.split("-")
        if len(r) == 3:  # version-date-commit
            tag_candidates.append(t)
    
    tag_candidates.sort()
    if len(tag_candidates) == 0:
        logger.warning(f"No matching tags found for prefix {prefix}, returning original tag")
        return tag
    else:
        logger.debug(f"Found {len(tag_candidates)} tags matching 3-segment format")
        return tag_candidates[-1]


def _get_docker_tag(registry_url, repository, prefix, tag, arch, proxies):
    """Get tag from Docker Hub or compatible registry"""
    # Docker Hub API v2
    url = f"https://hub.docker.com/v2/repositories/{repository}/tags"
    
    logger.debug(f"Requesting Docker Hub API: {url}")
    if proxies:
        logger.debug(f"Using proxy settings: {proxies}")
    response = requests.get(url, proxies=proxies)
    response.raise_for_status()
    
    rsp = response.json()
    tag_list = []
    
    for result in rsp.get("results", []):
        tag_name = result.get("name")
        last_updated = result.get("last_updated")
        if tag_name and last_updated:
            if tag_name.startswith(prefix) and tag_name.endswith(arch):
                r = tag_name.split("-")
                if len(r) == 4:  # version-date-commit-arch
                    tag_list.append((tag_name, last_updated))
    
    if not tag_list:
        logger.warning(f"No matching tags found for prefix {prefix} and arch {arch}, returning original tag")
        return tag
    
    # 按更新时间排序，返回最新的标签
    tag_list.sort(key=lambda x: x[1], reverse=True)
    logger.debug(f"Found {len(tag_list)} tags matching criteria, returning latest")
    return tag_list[0][0]
