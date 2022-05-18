"""
    service manager
"""
import argparse

# actions for app
actions = ['start', 'stop']

# registered services
services = ['etf50','t0client']

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=actions)
    parser.add_argument('service', choices=services)
    parser.add_argument('port', type=int)

    args = parser.parse_args()

    action, service, port = args.action, args.service, args.port

    if action == 'start':
        if service == 'etf50':
            import etf50
            etf50.service.start(port)
        elif service == 't0client':
            import t0client
            t0client.service.start(port)
        else:
            pass
    elif action == 'stop':
        if service == 'etf50':
            pass
        else:
            pass
    else:
        pass
