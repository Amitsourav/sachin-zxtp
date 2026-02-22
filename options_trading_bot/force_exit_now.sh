#!/bin/bash
# Force Exit - Immediately close paper trading position

echo "🔴 TRIGGERING FORCE EXIT..."
touch FORCE_EXIT.txt
echo "✅ Force exit signal sent!"
echo "Position will close within 2 seconds."