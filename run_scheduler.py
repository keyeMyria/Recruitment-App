#!/usr/bin/env python

import argparse
import urlparse
import sys
import os

from redis import Redis
from rq_scheduler.scheduler import Scheduler

from recruit_app.app import create_app
from recruit_app.settings import DevConfig, ProdConfig

from rq.logutils import setup_loghandlers


def main():
    parser = argparse.ArgumentParser(description='Runs RQ scheduler')
    parser.add_argument('-H', '--host',
                        default=os.environ.get('RQ_REDIS_HOST', 'localhost'),
                        help="Redis host")
    parser.add_argument('-p', '--port',
                        default=int(os.environ.get('RQ_REDIS_PORT', 6379)),
                        type=int,
                        help="Redis port number")
    parser.add_argument('-d', '--db',
                        default=int(os.environ.get('RQ_REDIS_DB', 0)),
                        type=int, help="Redis database")
    parser.add_argument('-P', '--password',
                        default=os.environ.get('RQ_REDIS_PASSWORD'),
                        help="Redis password")
    parser.add_argument('--verbose', '-v',
                        action='store_true',
                        default=False,
                        help='Show more output')
    parser.add_argument('--url', '-u',
                        default=os.environ.get('RQ_REDIS_URL'),
                        help='URL describing Redis connection details. \
            Overrides other connection arguments if supplied.')
    parser.add_argument('-i', '--interval',
                        default=60.0,
                        type=float,
                        help="How often the scheduler checks for new jobs to add to the \
            queue (in seconds, can be floating-point for more precision).")
    parser.add_argument('--path',
                        default='.',
                        help='Specify the import path.')
    parser.add_argument('--pid',
                        help='A filename to use for the PID file.',
                        metavar='FILE')

    args = parser.parse_args()

    if args.path:
        sys.path = args.path.split(':') + sys.path

    if args.pid:
        pid = str(os.getpid())
        filename = args.pid
        with open(filename, 'w') as f:
            f.write(pid)

    if args.url is not None:
        connection = Redis.from_url(args.url)

    elif os.getenv('REDISTOGO_URL'):
        redis_url = os.getenv('REDISTOGO_URL')
        if not redis_url:
            raise RuntimeError('Set up Redis To Go first.')

        urlparse.uses_netloc.append('redis')
        url = urlparse.urlparse(redis_url)
        connection = Redis(host=url.hostname, port=url.port, db=0, password=url.password)
    elif args.host is not None:
        connection = Redis(args.host, args.port, args.db, args.password)
    else:
        connection = Redis()

    if args.verbose:
        level = 'DEBUG'
    else:
        level = 'INFO'
    setup_loghandlers(level)

    scheduler = Scheduler(connection=connection, interval=args.interval)
    scheduler.run()

if __name__ == '__main__':
    if os.environ.get("RECRUIT_APP_ENV") == 'prod':
        app = create_app(ProdConfig)
    else:
        app = create_app(DevConfig)

    with app.app_context():
        main()

