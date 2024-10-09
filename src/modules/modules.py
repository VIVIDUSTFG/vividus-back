from src.core.utils.dynamic_router import get_current_directory, search_routers

package_path = get_current_directory(__file__)

router_urls = search_routers(package_path)
