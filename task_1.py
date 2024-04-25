import argparse
import asyncio
import logging

from aiopath import AsyncPath
from aioshutil import copyfile


def parse_args():
    parser = argparse.ArgumentParser(description="Sort files")
    parser.add_argument(
        "-S", "--source", type=AsyncPath, help="Path to the source directory."
    )
    parser.add_argument(
        "-D",
        "--destination",
        type=AsyncPath,
        nargs="?",
        default=AsyncPath("dist"),
        help="Path to the destination directory.",
    )
    return parser.parse_args()


async def get_folders(path: AsyncPath, output: AsyncPath):
    """
    Asynchronously retrieves all folders in the provided path and copies files within each folder to the output directory.

    Args:
        path (AsyncPath): The path to search for folders.
        output (AsyncPath): The destination directory to copy the files.
    """
    # Creating a list of tasks for each folder to run in parallel
    tasks = []
    async for f in path.iterdir():
        if await f.is_dir():
            task = asyncio.create_task(get_folders(f, output))
            tasks.append(task)
            logging.info(f"Found folder: {f}")

        else:
            await copy_files(f, output)
    await asyncio.gather(*tasks)
    logging.info(f"Files copied to: {output}")


async def copy_files(file: AsyncPath, output: AsyncPath):
    """
    Copy a file to a specified output directory.

    Args:
        file (AsyncPath): The path of the file to be copied.
        output (AsyncPath): The destination directory where the file will be copied to.
    """

    ext = file.suffix[1:]
    ext_folder = output / ext
    try:
        await ext_folder.mkdir(exist_ok=True, parents=True)
        await copyfile(file, ext_folder / file.name)
    except OSError as err:
        logging.error(err)


async def main(args):
    await get_folders(args.source, args.destination)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(threadName)s %(asctime)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    args = parse_args()
    asyncio.run(main(args))
    logging.info("All files sorted!")
