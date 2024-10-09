import uvicorn

from src.core.config import settings
from src.core.utils.helpers import parse_arguments

if __name__ == "__main__":

    args = parse_arguments()
    reload_option = args.reload

    uvicorn.run(
        'src.server:app',
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=reload_option,
    )
