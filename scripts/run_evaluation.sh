#!/bin/bash
# Run evaluation with environment variables from .env.local

cd "$(dirname "$0")/.."

# Load environment variables
if [ -f .env.local ]; then
    export $(cat .env.local | grep -v '^#' | xargs)
fi

# Run evaluation
cd evaluation
python run_evaluation.py
