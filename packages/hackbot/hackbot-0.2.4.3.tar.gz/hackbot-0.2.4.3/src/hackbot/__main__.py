import traceback
from hackbot.commands import get_args, hackbot_run, learn_run, show_selectable_models, Endpoint
from hackbot.log_utils import setup_loguru
from loguru import logger as log


def _run():
    setup_loguru()
    args = get_args()
    # Error code from get_args
    if isinstance(args, int):
        exit(args)

    try:
        if args.command == Endpoint.LEARN.value:
            exit_code = learn_run(args)
        elif args.command in Endpoint.__members__.values():
            exit_code = hackbot_run(args)
        elif args.command == "models":
            exit_code = show_selectable_models(args.api_key)
        else:
            log.error(f"❌ Error: Invalid command: {args.command}")
            exit(1)
    except Exception as e:
        log.error(f"❌ Error: {e}")
        log.error(traceback.format_exc())
        exit_code = 1

    # We fail with working+error if nonzero exit code
    exit_emoji = "✅" if exit_code == 0 else "⚠️"
    log.info(
        f"\n{exit_emoji} Hackbot done!{' (with exit code ' + str(exit_code) + ')' if exit_code != 0 else ''}"
    )


if __name__ == "__main__":
    _run()
