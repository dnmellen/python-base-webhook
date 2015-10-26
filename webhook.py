#!/usr/bin/python -tt

import sys
import argparse
import json
import logging
import logging.handlers
import ssl
from pprint import pprint  # Only used for this dummy example
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer


WEBHOOK_NAME = 'untitled'  # Please give your webhook a name


class Webhook(BaseHTTPRequestHandler):

    def do_POST(self):
        """
        Handle POST data
        """

        message = 'OK'
        self.rfile._sock.settimeout(5)
        data_string = self.rfile.read(int(self.headers['Content-Length']))
        self.send_response(200)
        self.send_header("Content-type", "text")
        self.send_header("Content-length", str(len(message)))
        self.end_headers()
        self.wfile.write(message)

        # parse data
        data = json.loads(data_string)

        # Process here sent data
        pprint(data)


    def log_message(self, format, *args):
        """
        Disable printing to stdout/stderr for every post
        """
        return


if __name__ == '__main__':
    # Parse arguments
    parser = argparse.ArgumentParser(description='{} Webhook'.format(WEBHOOK_NAME))

    # Prepare settings
    default_port = 8000  # Webhook server port
    default_log_max_size = 50 * 1048576  # 50 MB
    default_backup_count = 4  # Number of historical data logs

    parser.add_argument('-p', '--port', help='Server port ({} will be used by default)'.format(default_port), default=default_port, type=int)
    parser.add_argument('-l', '--log', help='Specify a log file otherwise stdout will be used', required=False)
    parser.add_argument('-c', '--certfile', help='SSL certificate file', required=False, default=None)
    parser.add_argument('-k', '--keyfile', help='SSL key file', required=False, default=None)
    parser.add_argument('--log-level', help='Logging level (INFO by default)', default=logging.INFO)
    parser.add_argument('--log-max-size', help='Log max size ({} bytes by default)'.format(default_log_max_size), default=default_log_max_size)
    parser.add_argument('--log-backup-count', help='Number of historical data logs ({} by default)'.format(default_backup_count), default=default_backup_count)

    args = parser.parse_args()

    log = logging.getLogger('webhook_log')
    log.setLevel(args.log_level)
    if args.log:
        log_handler = logging.handlers.RotatingFileHandler(args.log_file,
                                                           maxBytes=args.log_max_size,
                                                           backupCount=args.backup_count)
    else:
        log_handler = logging.StreamHandler(sys.stdout)
    f = logging.Formatter("%(asctime)s %(filename)s %(levelname)s %(message)s",
                          "%B %d %H:%M:%S")
    log_handler.setFormatter(f)
    log.addHandler(log_handler)

    # SSL files
    ssl_data = {}
    if args.keyfile:
        ssl_data['keyfile'] = str(args.keyfile)
    if args.certfile:
        ssl_data['certfile'] = str(args.certfile)

    # Launch server
    try:
        server = HTTPServer(('', args.port), Webhook)
        if ssl_data:
            server.socket = ssl.wrap_socket(server.socket, server_side=True, **ssl_data)
        log.info('Starting webhook server ({}) on port {}...'.format(WEBHOOK_NAME, args.port))
        server.serve_forever()
    except KeyboardInterrupt:
        log.info('CTRL-C pressed, closing webhook...')
        server.socket.close()
