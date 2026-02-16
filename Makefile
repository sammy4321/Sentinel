# Sentinel Makefile
#
# Usage:
#   make up                                        # Default: Powered by AI
#   make up MODEL=gpt-4 API_KEY=sk-xxx             # Custom model + key
#   make up MODEL=claude-3 API_KEY=sk-ant-xxx      # Another example

MODEL ?= AI
API_KEY ?=

up:
	bash startup.sh --model "$(MODEL)" --api_key "$(API_KEY)"
