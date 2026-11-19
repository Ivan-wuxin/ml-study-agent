"""Project adapter: run real agent handler for exactly three smoke requests.
Finite request loop avoids shell child cleanup differences on Windows.
"""
import sys
import agent
class FiniteServer(agent.HTTPServer):
    def serve_forever(self):
        try:
            for _ in range(4): self.handle_request()
        finally:self.server_close()
agent.HTTPServer=FiniteServer
sys.argv=['agent.py','--serve','--port','8766']
agent.main()
